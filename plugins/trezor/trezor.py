from binascii import hexlify, unhexlify
from typing import NamedTuple, Any

from electrum_smart.util import bfh, bh2u, versiontuple, print_error
from electrum_smart.bitcoin import (b58_address_to_hash160, xpub_from_pubkey,
                              TYPE_ADDRESS, TYPE_SCRIPT)
from electrum_smart import constants
from electrum_smart.i18n import _
from electrum_smart.plugins import BasePlugin, Device
from electrum_smart.transaction import deserialize, Transaction
from electrum_smart.keystore import Hardware_KeyStore, is_xpubkey, parse_xpubkey
from electrum_smart.base_wizard import ScriptTypeNotSupported, HWD_SETUP_NEW_WALLET

from ..hw_wallet import HW_PluginBase
from ..hw_wallet.plugin import (is_any_tx_output_on_change_branch, trezor_validate_op_return_output_and_get_data,
                                LibraryFoundButUnusable, OutdatedHwFirmwareException)

try:
    import trezorlib
    import trezorlib.transport
    from trezorlib.transport.bridge import BridgeTransport, call_bridge

    from .clientbase import TrezorClientBase

    from trezorlib.messages import (
        RecoveryDeviceType, HDNodeType, HDNodePathType,
        InputScriptType, OutputScriptType, MultisigRedeemScriptType,
        TxInputType, TxOutputType, TxOutputBinType, TransactionType, SignTx)

    RECOVERY_TYPE_SCRAMBLED_WORDS = RecoveryDeviceType.ScrambledWords
    RECOVERY_TYPE_MATRIX = RecoveryDeviceType.Matrix

    from trezorlib.client import PASSPHRASE_ON_DEVICE

    TREZORLIB = True
except Exception as e:
    print_error('error importing trezorlib')
    TREZORLIB = False

    RECOVERY_TYPE_SCRAMBLED_WORDS, RECOVERY_TYPE_MATRIX = range(2)

    PASSPHRASE_ON_DEVICE = object()

# TREZOR initialization methods
TIM_NEW, TIM_RECOVER = range(2)

TREZOR_PRODUCT_KEY = 'Trezor'

# script "generation"
SCRIPT_GEN_LEGACY, SCRIPT_GEN_P2SH_SEGWIT, SCRIPT_GEN_NATIVE_SEGWIT = range(0, 3)


class TrezorKeyStore(Hardware_KeyStore):
    hw_type = 'trezor'
    device = 'TREZOR'

    def get_derivation(self):
        return self.derivation

    def get_script_gen(self):
        return SCRIPT_GEN_LEGACY

    def get_client(self, force_pair=True):
        return self.plugin.get_client(self, force_pair)

    def decrypt_message(self, sequence, message, password):
        raise RuntimeError(_('Encryption and decryption are not implemented by {}').format(self.device))

    def sign_message(self, sequence, message, password):
        client = self.get_client()
        address_path = self.get_derivation() + "/%d/%d" % sequence
        msg_sig = client.sign_message(address_path, message)
        return msg_sig.signature

    def sign_transaction(self, tx, password):
        if tx.is_complete():
            return
        # previous transactions used as inputs
        prev_tx = {}
        # path of the xpubs that are involved
        xpub_path = {}
        for txin in tx.inputs():
            pubkeys, x_pubkeys = tx.get_sorted_pubkeys(txin)
            tx_hash = txin['prevout_hash']
            if txin.get('prev_tx') is None:
                raise Exception(_('Offline signing with {} is not supported for legacy inputs.').format(self.device))
            prev_tx[tx_hash] = txin['prev_tx']
            for x_pubkey in x_pubkeys:
                if not is_xpubkey(x_pubkey):
                    continue
                xpub, s = parse_xpubkey(x_pubkey)
                if xpub == self.get_master_public_key():
                    xpub_path[xpub] = self.get_derivation()

        self.plugin.sign_transaction(self, tx, prev_tx, xpub_path)


class TrezorInitSettings(NamedTuple):
    word_count: int
    label: str
    pin_enabled: bool
    passphrase_enabled: bool
    recovery_type: Any = None
    no_backup: bool = False

class TrezorPlugin(HW_PluginBase):
    # Derived classes provide:
    #
    #  class-static variables: client_class, firmware_URL, handler_class,
    #     libraries_available, libraries_URL, minimum_firmware,
    #     wallet_class, ckd_public, types

    firmware_URL = 'https://wallet.trezor.io'
    libraries_URL = 'https://github.com/trezor/python-trezor'
    minimum_firmware = (1, 5, 2)
    keystore_class = TrezorKeyStore
    minimum_library = (0, 12, 0)
    maximum_library = (0, 13)
    SUPPORTED_XTYPES = ('standard', 'p2wpkh-p2sh', 'p2wpkh', 'p2wsh-p2sh', 'p2wsh')
    DEVICE_IDS = (TREZOR_PRODUCT_KEY,)

    MAX_LABEL_LEN = 32

    def __init__(self, parent, config, name):
        super().__init__(parent, config, name)

        self.libraries_available = self.check_libraries_available()
        if not self.libraries_available:
            return
        self.device_manager().register_enumerate_func(self.enumerate)

    def get_library_version(self):
        import trezorlib
        try:
            version = trezorlib.__version__
        except Exception:
            version = 'unknown'
        if TREZORLIB:
            return version
        else:
            raise LibraryFoundButUnusable(library_version=version)

    def enumerate(self):
        # If there is a bridge, prefer that.
        # On Windows, the bridge runs as Admin (and Electrum usually does not),
        # so the bridge has better chances of finding devices. see #5420
        # This also avoids duplicate entries.
        try:
            call_bridge("enumerate")
        except Exception:
            devices = trezorlib.transport.enumerate_devices()
        else:
            devices = BridgeTransport.enumerate()
        return [Device(path=d.get_path(),
                       interface_number=-1,
                       id_=d.get_path(),
                       product_key=TREZOR_PRODUCT_KEY,
                       usage_page=0,
                       transport_ui_string=d.get_path())
                for d in devices]

    def create_client(self, device, handler):
        try:
            print_error(f"connecting to device at {device.path}")
            transport = trezorlib.transport.get_transport(device.path)
        except BaseException as e:
            print_error(f"cannot connect at {device.path} {e}")
            return None

        if not transport:
            print_error(f"cannot connect at {device.path}")
            return

        print_error(f"connected to device at {device.path}")
        # note that this call can still raise!
        return TrezorClientBase(transport, handler, self)

    def get_client(self, keystore, force_pair=True):
        devmgr = self.device_manager()
        handler = keystore.handler
        with devmgr.hid_lock:
            client = devmgr.client_for_keystore(self, handler, keystore, force_pair)
        # returns the client for a given keystore. can use xpub
        if client:
            client.used()
        return client

    def get_coin_name(self):
        return "Testnet" if constants.net.TESTNET else "SmartCash"

    def initialize_device(self, device_id, wizard, handler):
        # Initialization method
        msg = _("Choose how you want to initialize your {}.\n\n"
                "The first two methods are secure as no secret information "
                "is entered into your computer.\n\n"
                "For the last two methods you input secrets on your keyboard "
                "and upload them to your {}, and so you should "
                "only do those on a computer you know to be trustworthy "
                "and free of malware."
        ).format(self.device, self.device)
        choices = [
            # Must be short as QT doesn't word-wrap radio button text
            (TIM_NEW, _("Let the device generate a completely new seed randomly")),
            (TIM_RECOVER, _("Recover from a seed you have previously written down")),
            (TIM_MNEMONIC, _("Upload a BIP39 mnemonic to generate the seed")),
            (TIM_PRIVKEY, _("Upload a master private key"))
        ]
        def f(method):
            import threading
            settings = self.request_trezor_init_settings(wizard, method, self.device)
            t = threading.Thread(target = self._initialize_device, args=(settings, method, device_id, wizard, handler))
            t.setDaemon(True)
            t.start()
            wizard.loop.exec_()
        wizard.choice_dialog(title=_('Initialize Device'), message=msg, choices=choices, run_next=f)

    def _initialize_device(self, settings, method, device_id, wizard, handler):
        item, label, pin_protection, passphrase_protection = settings

        if method == TIM_RECOVER:
            # FIXME the PIN prompt will appear over this message
            # which makes this unreadable
            handler.show_error(_(
                "You will be asked to enter 24 words regardless of your "
                "seed's actual length.  If you enter a word incorrectly or "
                "misspell it, you cannot change it or go back - you will need "
                "to start again from the beginning.\n\nSo please enter "
                "the words carefully!"))

        language = 'english'
        devmgr = self.device_manager()
        client = devmgr.client_by_id(device_id)

        if method == TIM_NEW:
            strength = 64 * (item + 2)  # 128, 192 or 256
            u2f_counter = 0
            skip_backup = False
            client.reset_device(True, strength, passphrase_protection,
                                pin_protection, label, language,
                                u2f_counter, skip_backup)
        elif method == TIM_RECOVER:
            word_count = 6 * (item + 2)  # 12, 18 or 24
            client.step = 0
            client.recovery_device(word_count, passphrase_protection,
                                       pin_protection, label, language)
        elif method == TIM_MNEMONIC:
            pin = pin_protection  # It's the pin, not a boolean
            client.load_device_by_mnemonic(str(item), pin,
                                           passphrase_protection,
                                           label, language)
        else:
            pin = pin_protection  # It's the pin, not a boolean
            client.load_device_by_xprv(item, pin, passphrase_protection,
                                       label, language)
        wizard.loop.exit(0)

    def setup_device(self, device_info, wizard, purpose):
        devmgr = self.device_manager()
        device_id = device_info.device.id_
        client = devmgr.client_by_id(device_id)
        if client is None:
            raise Exception(_('Failed to create a client for this device.') + '\n' +
                                      _('Make sure it is in the correct state.'))

        if not client.is_uptodate():
            msg = (_('Outdated {} firmware for device labelled {}. Please '
                     'download the updated firmware from {}')
                   .format(self.device, client.label(), self.firmware_URL))
            raise Exception(msg)

        # fixme: we should use: client.handler = wizard
        client.handler = self.create_handler(wizard)
        if not device_info.initialized:
            self.initialize_device(device_id, wizard, client.handler)
        is_creating_wallet = purpose == HWD_SETUP_NEW_WALLET
        client.get_xpub('m', 'standard', creating=is_creating_wallet)
        client.used()

    def get_xpub(self, device_id, derivation, xtype, wizard):
        devmgr = self.device_manager()
        client = devmgr.client_by_id(device_id)
        client.handler = wizard
        xpub = client.get_xpub(derivation, xtype)
        client.used()
        return xpub

    def get_trezor_input_script_type(self, electrum_txin_type: str):
        if electrum_txin_type in ('p2wpkh', 'p2wsh'):
            return InputScriptType.SPENDWITNESS
        if electrum_txin_type in ('p2wpkh-p2sh', 'p2wsh-p2sh'):
            return InputScriptType.SPENDP2SHWITNESS
        if electrum_txin_type in ('p2pkh', ):
            return InputScriptType.SPENDADDRESS
        if electrum_txin_type in ('p2sh', ):
            return InputScriptType.SPENDMULTISIG
        raise ValueError('unexpected txin type: {}'.format(electrum_txin_type))

    def get_trezor_output_script_type(self, electrum_txin_type: str):
        if electrum_txin_type in ('p2wpkh', 'p2wsh'):
            return OutputScriptType.PAYTOWITNESS
        if electrum_txin_type in ('p2wpkh-p2sh', 'p2wsh-p2sh'):
            return OutputScriptType.PAYTOP2SHWITNESS
        if electrum_txin_type in ('p2pkh', ):
            return OutputScriptType.PAYTOADDRESS
        if electrum_txin_type in ('p2sh', ):
            return OutputScriptType.PAYTOMULTISIG
        raise ValueError('unexpected txin type: {}'.format(electrum_txin_type))

    def sign_transaction(self, keystore, tx, prev_tx, xpub_path):
        prev_tx = {bfh(txhash): self.electrum_tx_to_txtype(tx, xpub_path) for txhash, tx in prev_tx.items()}
        client = self.get_client(keystore)
        inputs = self.tx_inputs(tx, xpub_path, True)
        outputs = self.tx_outputs(keystore.get_derivation(), tx)
        details = SignTx(lock_time=tx.locktime, version=tx.version)
        signatures, _ = client.sign_tx(self.get_coin_name(), inputs, outputs, details=details, prev_txes=prev_tx)
        signatures = [(bh2u(x) + '01') for x in signatures]
        tx.update_signatures(signatures)

    def show_address(self, wallet, address, keystore=None):
        if keystore is None:
            keystore = wallet.get_keystore()
        if not self.show_address_helper(wallet, address, keystore):
            return
        deriv_suffix = wallet.get_address_index(address)
        derivation = keystore.derivation
        address_path = "%s/%d/%d"%(derivation, *deriv_suffix)
        script_type = self.get_trezor_input_script_type(wallet.txin_type)

        # prepare multisig, if available:
        xpubs = wallet.get_master_public_keys()
        if len(xpubs) > 1:
            pubkeys = wallet.get_public_keys(address)
            # sort xpubs using the order of pubkeys
            sorted_pairs = sorted(zip(pubkeys, xpubs))
            multisig = self._make_multisig(
                wallet.m,
                [(xpub, deriv_suffix) for _, xpub in sorted_pairs])
        else:
            multisig = None

        client = self.get_client(keystore)
        client.show_address(address_path, script_type, multisig)

    def tx_inputs(self, tx, xpub_path, for_sig=False):
        inputs = []
        for txin in tx.inputs():
            txinputtype = TxInputType()
            if txin['type'] == 'coinbase':
                prev_hash = b"\x00"*32
                prev_index = 0xffffffff  # signed int -1
            else:
                if for_sig:
                    x_pubkeys = txin['x_pubkeys']
                    xpubs = [parse_xpubkey(x) for x in x_pubkeys]
                    multisig = self._make_multisig(txin.get('num_sig'), xpubs, txin.get('signatures'))
                    script_type = self.get_trezor_input_script_type(txin['type'])
                    txinputtype = TxInputType(
                        script_type=script_type,
                        multisig=multisig)
                    # find which key is mine
                    for xpub, deriv in xpubs:
                        if xpub in xpub_path:
                            xpub_n = TrezorClientBase.expand_path(xpub_path[xpub])
                            txinputtype.address_n = xpub_n + deriv
                            break

                prev_hash = bfh(txin['prevout_hash'])
                prev_index = txin['prevout_n']

            if 'value' in txin:
                txinputtype.amount = txin['value']
            txinputtype.prev_hash = prev_hash
            txinputtype.prev_index = prev_index

            if txin.get('scriptSig') is not None:
                script_sig = bfh(txin['scriptSig'])
                txinputtype.script_sig = script_sig

            txinputtype.sequence = txin.get('sequence', 0xffffffff - 1)

            inputs.append(txinputtype)

        return inputs

    def _make_multisig(self, m, xpubs, signatures=None):
        if len(xpubs) == 1:
            return None

        pubkeys = [self._make_node_path(xpub, deriv) for xpub, deriv in xpubs]
        if signatures is None:
            signatures = [b''] * len(pubkeys)
        elif len(signatures) != len(pubkeys):
            raise RuntimeError('Mismatched number of signatures')
        else:
            signatures = [bfh(x)[:-1] if x else b'' for x in signatures]

        return MultisigRedeemScriptType(
            pubkeys=pubkeys,
            signatures=signatures,
            m=m)

    def tx_outputs(self, derivation, tx):

        def create_output_by_derivation():
            index, xpubs, m = info
            #script_type = self.get_trezor_output_script_type(info.script_type)
            script_type = OutputScriptType.PAYTOADDRESS
            deriv = TrezorClientBase.expand_path("/%d/%d" % index)
            multisig = self._make_multisig(m, [(xpub, deriv) for xpub in xpubs])
            txoutputtype = TxOutputType(
                multisig=multisig,
                amount=amount,
                address_n=TrezorClientBase.expand_path(derivation + "/%d/%d" % index),
                script_type=script_type)
            return txoutputtype

        def create_output_by_address():
            txoutputtype = TxOutputType()
            txoutputtype.amount = amount
            if _type == TYPE_SCRIPT:
                txoutputtype.script_type = OutputScriptType.PAYTOOPRETURN
                txoutputtype.op_return_data = trezor_validate_op_return_output_and_get_data(o)
            elif _type == TYPE_ADDRESS:
                txoutputtype.script_type = OutputScriptType.PAYTOADDRESS
                txoutputtype.address = address
            return txoutputtype

        outputs = []
        has_change = False
        any_output_on_change_branch = is_any_tx_output_on_change_branch(tx)

        for o in tx.outputs():
            (_type, address, amount, dummy) = o
            use_create_by_derivation = False

            info = tx.output_info.get(address)
            if info is not None and not has_change:
                index, xpubs, m = info
                on_change_branch = index[0] == 1
                # prioritise hiding outputs on the 'change' branch from user
                # because no more than one change address allowed
                # note: ^ restriction can be removed once we require fw
                # that has https://github.com/trezor/trezor-mcu/pull/306
                if on_change_branch == any_output_on_change_branch:
                    use_create_by_derivation = True
                    has_change = True

            if use_create_by_derivation:
                txoutputtype = create_output_by_derivation()
            else:
                txoutputtype = create_output_by_address()
            outputs.append(txoutputtype)

        return outputs

    def electrum_tx_to_txtype(self, tx, xpub_path):
        t = TransactionType()
        if tx is None:
            # probably for segwit input and we don't need this prev txn
            return t
        d = deserialize(tx.raw)
        t.version = d['version']
        t.lock_time = d['lockTime']
        t.inputs = self.tx_inputs(tx, xpub_path)
        t.bin_outputs = [
            TxOutputBinType(amount=vout['value'], script_pubkey=bfh(vout['scriptPubKey']))
            for vout in d['outputs']
        ]
        return t

    # This function is called from the TREZOR libraries (via tx_api)
    def get_tx(self, tx_hash):
        tx = self.prev_tx[tx_hash]
        return self.electrum_tx_to_txtype(tx)

