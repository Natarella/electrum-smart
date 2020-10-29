import traceback

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electrum_smart.i18n import _
from electrum_smart import bitcoin, keystore
from electrum_smart.util import PrintError, bfh
from electrum_smart.smartnode import MasternodeAnnounce, NetworkAddress
from .smartnode_controldialog import SmartnodeControlDialog

from . import util

# Background color for enabled smartnodes.
ENABLED_SMARTNODE_BG = '#80ff80'
SMARTNODE_MIN_VERSION = '90032'
SMARTNODE_DEFAULT_PORT = '9678'

def smartnode_status(status):
    """Get a human-friendly representation of status.

    Returns a 3-tuple of (enabled, one_word_description, description).
    """
    statuses = {
        'PRE_ENABLED': (True, ('PRE_ENABLED'), ('Waiting for smartnode to enable itself.')),
        'ENABLED': (True, ('ENABLED'), ('Smartnode is enabled.')),
        'EXPIRED': (False, ('EXPIRED'), ('Smartnode failed to ping the network and was disabled.')),
        'NEW_START_REQUIRED': (False, ('NEW_START_REQUIRED'), ('Must start smartnode again.')),
        'UPDATE_REQUIRED': (False, ('UPDATE_REQUIRED'), ('Smartnode failed to ping the network and was disabled.')),
        'POSE_BAN': (False, ('POSE_BAN'), ('Smartnode failed to ping the network and was disabled.')),
        'OUTPOINT_SPENT': (False, ('OUTPOINT_SPENT'), ('Collateral payment has been spent.'))
    }
    if statuses.get(status):
        return statuses[status]
    elif status is False:
        return (False, ('MISSING'), ('Smartnode has not been seen on the network.'))
    return (False, (' '), ('Smartnode status not loaded yet'))

class SmartnodeModel(QAbstractTableModel):

    """Model for smartnodes."""

    ALIAS = 0
    ADDR = 1
    PROTOCOL_VERSION = 2
    STATUS = 3
    COLLATERAL = 4
    DELEGATE = 5
    VIN_PREVOUT_HASH = 6
    VIN_PREVOUT_N = 7
    VIN_ADDRESS = 8
    VIN_VALUE = 9
    VIN_SCRIPTSIG  = 10
    TOTAL_FIELDS = 11

    def __init__(self, manager, parent=None):
        super(SmartnodeModel, self).__init__(parent)

        self.manager = manager
        self.smartnodes = self.manager.masternodes

        headers = [
            {Qt.DisplayRole: 'Alias',},
            {Qt.DisplayRole: 'Address', },
            {Qt.DisplayRole: 'Protocol', },
            {Qt.DisplayRole: 'Status',},
            {Qt.DisplayRole: 'Payee', },
            {Qt.DisplayRole: 'Smartnode Key', },
            {Qt.DisplayRole: 'Collateral Hash',},
            {Qt.DisplayRole: 'Collateral Index', },
            {Qt.DisplayRole: 'Collateral Address', },
            {Qt.DisplayRole: 'Collateral Value', },
            {Qt.DisplayRole: 'Collateral ScriptSig', },
        ]

        for d in headers:
            d[Qt.EditRole] = d[Qt.DisplayRole]

        self.headers = headers

    def add_smartnode(self, smartnode, save=True):
        self.beginResetModel()
        self.manager.add_masternode(smartnode, save)
        self.endResetModel()

    def remove_smartnode(self, alias, save=True):
        self.beginResetModel()
        self.manager.remove_masternode(alias, save)
        self.endResetModel()

    def smartnode_for_row(self, row):
        mn = self.smartnodes[row]
        return mn

    def import_smartnode_conf_lines(self, conf_lines, pw):
        self.beginResetModel()
        num = self.manager.import_masternode_conf_lines(conf_lines, pw)
        self.endResetModel()
        return num

    def columnCount(self, parent=QModelIndex()):
        return self.TOTAL_FIELDS

    def rowCount(self, parent=QModelIndex()):
        return len(self.smartnodes)

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if role not in [Qt.DisplayRole, Qt.EditRole]: return None
        if orientation != Qt.Horizontal: return None

        data = None
        try:
            data = self.headers[section][role]
        except (IndexError, KeyError):
            pass

        return QVariant(data)

    def data(self, index, role = Qt.DisplayRole):
        data = None
        if not index.isValid():
            return QVariant(data)
        if role not in [Qt.DisplayRole, Qt.EditRole, Qt.ToolTipRole, Qt.FontRole, Qt.BackgroundRole]:
            return None

        mn = self.smartnodes[index.row()]
        i = index.column()

        if i == self.ALIAS:
            data = mn.alias
        elif i == self.STATUS:
            status = self.manager.masternode_statuses.get(mn.get_collateral_str())
            data = smartnode_status(status)
            if role == Qt.BackgroundRole:
                data = QBrush(QColor(ENABLED_SMARTNODE_BG)) if data[0] else None
            # Return the long description for data widget mappers.
            elif role == Qt.EditRole:
                data = data[2]
            else:
                data = data[1]
        elif i == self.VIN_PREVOUT_HASH:
            data = mn.vin.get('prevout_hash', '')
        elif i == self.VIN_PREVOUT_N:
            data = str(mn.vin.get('prevout_n', ''))
        elif i == self.VIN_ADDRESS:
            data = mn.vin.get('address', '')
        elif i == self.VIN_VALUE:
            data = str(mn.vin.get('value', ''))
        elif i == self.VIN_SCRIPTSIG:
            data = mn.vin.get('scriptSig', '')
        elif i == self.COLLATERAL:
            data = mn.collateral_key
            if role in [Qt.EditRole, Qt.DisplayRole, Qt.ToolTipRole] and data:
                data = bitcoin.public_key_to_p2pkh(bfh(data))
            elif role == Qt.FontRole:
                data = util.MONOSPACE_FONT
        elif i == self.DELEGATE:
            data = mn.delegate_key
            if role in [Qt.EditRole, Qt.DisplayRole, Qt.ToolTipRole] and data:
                data = self.manager.get_delegate_privkey(data)
            elif role == Qt.FontRole:
                data = util.MONOSPACE_FONT
        elif i == self.ADDR:
            data = ''
            if mn.addr.ip:
                data = str(mn.addr)
        elif i == self.PROTOCOL_VERSION:
            data = mn.protocol_version

        return QVariant(data)

    def setData(self, index, value, role = Qt.EditRole):
        if not index.isValid(): return False

        mn = self.smartnodes[index.row()]
        i = index.column()

        if i == self.ALIAS:
            mn.alias = value
        elif i == self.STATUS:
            return True
        elif i == self.VIN_PREVOUT_HASH:
            mn.vin['prevout_hash'] = value
        elif i == self.VIN_PREVOUT_N:
            mn.vin['prevout_n'] = int(value)
        elif i == self.VIN_ADDRESS:
            mn.vin['address'] = value
        elif i == self.VIN_VALUE:
            mn.vin['value'] = int(value)
        elif i == self.VIN_SCRIPTSIG:
            mn.vin['scriptSig'] = value
        elif i == self.COLLATERAL:
            mn.collateral_key = value
        elif i == self.DELEGATE:
            privkey = value
            pubkey = ''
            try:
                # Import the key if it isn't already imported.
                pubkey = self.manager.import_masternode_delegate(privkey)
            except Exception:
                # Don't fail if the key is invalid.
                pass

            mn.delegate_key = pubkey
        elif i == self.ADDR:
            s = value.split(':')
            mn.addr.ip = s[0]
            if len(s) > 1:
                mn.addr.port = int(s[1])
            else:
                mn.addr.port = int(SMARTNODE_DEFAULT_PORT)
        elif i == self.PROTOCOL_VERSION:
            try:
                version = int(value)
            except ValueError:
                return False
            mn.protocol_version = version
        else:
            return False

        self.dataChanged.emit(self.index(index.row(), index.column()), self.index(index.row(), index.column()))
        return True

class SmartnodeTab(QWidget, PrintError):
    """GUI for smartnodes tab ."""

    CREATE = 0
    EDIT = 1
    VIEW = 2

    def __init__(self, parent):
        super(SmartnodeTab, self).__init__(parent)
        self.gui = parent
        self.create_layout()

    def update_nodelist(self, wallet, config, manager):
        self.wallet = wallet
        self.config = config
        self.manager = manager

        self.smartnodes = self.manager.masternodes
        self.model = SmartnodeModel(self.manager)

        self.proxy_model = model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.tableWidgetMySmartnodes.setModel(self.proxy_model)

        header = self.tableWidgetMySmartnodes.horizontalHeader()
        header.setSectionResizeMode(SmartnodeModel.ALIAS, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(SmartnodeModel.ADDR, QHeaderView.Stretch)
        header.setSectionResizeMode(SmartnodeModel.PROTOCOL_VERSION, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(SmartnodeModel.STATUS, QHeaderView.Stretch)
        header.setSectionResizeMode(SmartnodeModel.COLLATERAL, QHeaderView.ResizeToContents)

        self.tableWidgetMySmartnodes.setColumnHidden(5, True)
        self.tableWidgetMySmartnodes.setColumnHidden(6, True)
        self.tableWidgetMySmartnodes.setColumnHidden(7, True)
        self.tableWidgetMySmartnodes.setColumnHidden(8, True)
        self.tableWidgetMySmartnodes.setColumnHidden(9, True)
        self.tableWidgetMySmartnodes.setColumnHidden(10, True)

        self.smartnode_editor = editor = SmartnodeControlDialog(self.gui)
        self.mapper = mapper = QDataWidgetMapper()
        mapper.setSubmitPolicy(QDataWidgetMapper.ManualSubmit)
        mapper.setModel(model)
        mapper.addMapping(editor.aliasField, SmartnodeModel.ALIAS)
        mapper.addMapping(editor.statusField, SmartnodeModel.STATUS)
        mapper.addMapping(editor.ipField, SmartnodeModel.ADDR)
        mapper.addMapping(editor.txCollateralKeyLabel, SmartnodeModel.COLLATERAL, b"text")
        mapper.addMapping(editor.smartnodeKeyLabel, SmartnodeModel.DELEGATE, b"text")
        mapper.addMapping(editor.addressViewLabel, SmartnodeModel.VIN_ADDRESS, b"text")
        mapper.addMapping(editor.txIndexViewLabel, SmartnodeModel.VIN_PREVOUT_N, b"text")
        mapper.addMapping(editor.txHashViewLabel, SmartnodeModel.VIN_PREVOUT_HASH, b"text")
        mapper.addMapping(editor.txValueViewLabel, SmartnodeModel.VIN_VALUE, b"text")
        mapper.addMapping(editor.txScriptSigViewLabel, SmartnodeModel.VIN_SCRIPTSIG, b"text")

        self.tableWidgetMySmartnodes.selectionModel().selectionChanged.connect(self.on_view_selection_changed)

    def setup_nodelist(self):
        self.tableWidgetMySmartnodes = QTableView()
        self.tableWidgetMySmartnodes.setMinimumSize(QSize(695, 0))
        self.tableWidgetMySmartnodes.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidgetMySmartnodes.setAlternatingRowColors(True)
        self.tableWidgetMySmartnodes.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidgetMySmartnodes.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidgetMySmartnodes.setSortingEnabled(True)
        self.tableWidgetMySmartnodes.verticalHeader().setVisible(False)
        self.tableWidgetMySmartnodes.setObjectName("tableWidgetMySmartnodes")

    def disable_node_buttons(self):
        self.EditButton.setEnabled(False)
        self.RemoveButton.setEnabled(False)
        self.ViewButton.setEnabled(False)
        self.startButton.setEnabled(False)

    def create_layout(self):
        self.setObjectName("SmartnodeList")
        self.resize(811, 457)
        self.setMinimumSize(QSize(0, 0))
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget = QWidget(self)
        self.widget.setMinimumSize(QSize(0, 0))
        self.widget.setObjectName("widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setContentsMargins(0, -1, -1, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")

        # Create Smartnode
        self.CreateButton = QPushButton(self.widget)
        self.CreateButton.setObjectName("CreateButton")
        self.horizontalLayout.addWidget(self.CreateButton)
        self.CreateButton.clicked.connect(lambda: self.show_smartnode_controldialog(self.CREATE))

        # Edit Smartnode
        self.EditButton = QPushButton(self.widget)
        self.EditButton.setEnabled(False)
        self.EditButton.setObjectName("EditButton")
        self.horizontalLayout.addWidget(self.EditButton)
        self.EditButton.clicked.connect(lambda: self.show_smartnode_controldialog(self.EDIT))

        # Remove Smartnode
        self.RemoveButton = QPushButton(self.widget)
        self.RemoveButton.setEnabled(False)
        self.RemoveButton.setObjectName("RemoveButton")
        self.horizontalLayout.addWidget(self.RemoveButton)
        self.RemoveButton.clicked.connect(self.delete_current_smartnode)

        # View Smartnode
        self.ViewButton = QPushButton(self.widget)
        self.ViewButton.setEnabled(False)
        self.ViewButton.setObjectName("ViewButton")
        self.horizontalLayout.addWidget(self.ViewButton)
        self.ViewButton.clicked.connect(lambda: self.show_smartnode_controldialog(self.VIEW))

        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout_2.addWidget(self.widget)
        self.setup_nodelist()
        self.verticalLayout_2.addWidget(self.tableWidgetMySmartnodes)
        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setContentsMargins(-1, -1, -1, 0)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")

        #Start Smartnode
        self.startButton = QPushButton(self)
        self.startButton.setObjectName("startButton")
        self.startButton.setEnabled(False)
        self.startButton.clicked.connect(self.start_current_smartnode)
        self.horizontalLayout_5.addWidget(self.startButton)

        # Update Smartnodes
        self.UpdateButton = QPushButton(self)
        self.UpdateButton.setObjectName("UpdateButton")
        self.horizontalLayout_5.addWidget(self.UpdateButton)
        self.UpdateButton.clicked.connect(lambda: self.update_smartnodes_status(True))

        #self.startMissingButton = QPushButton(self)
        #self.startMissingButton.setObjectName("startMissingButton")
        #self.horizontalLayout_5.addWidget(self.startMissingButton)
        #self.autoupdate_label = QLabel(self)
        #self.autoupdate_label.setObjectName("autoupdate_label")
        #self.horizontalLayout_5.addWidget(self.autoupdate_label)
        #self.secondsLabel = QLabel(self)
        #self.secondsLabel.setObjectName("secondsLabel")
        #self.horizontalLayout_5.addWidget(self.secondsLabel)

        spacerItem1 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_5)
        self.gridLayout.addLayout(self.verticalLayout_2, 0, 0, 1, 1)
        self.retranslateUi(self)
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, SmartnodeList):
        _translate = QCoreApplication.translate
        SmartnodeList.setWindowTitle(_translate("SmartnodeList", "Form"))
        self.CreateButton.setText(_translate("SmartnodeList", "Create Smartnode"))
        self.EditButton.setText(_translate("SmartnodeList", "Edit selected"))
        self.RemoveButton.setText(_translate("SmartnodeList", "Remove selected"))
        self.ViewButton.setText(_translate("SmartnodeList", "View selected"))
        self.tableWidgetMySmartnodes.setSortingEnabled(True)
        self.startButton.setText(_translate("SmartnodeList", "S&tart alias"))
        self.UpdateButton.setText(_translate("SmartnodeList", "&Update status"))
        # self.startMissingButton.setText(_translate("SmartnodeList", "Start &MISSING"))
        #self.autoupdate_label.setText(_translate("SmartnodeList", "Status will be updated automatically in (sec):"))
        #self.secondsLabel.setText(_translate("SmartnodeList", "0"))

    def show_smartnode_controldialog(self, action):
        d = self.smartnode_editor

        if(action == self.CREATE):
            self.add_empty_smartnode()

        d.setAction(action, self.manager, self.mapper)
        d.exec_()

        if action == self.CREATE and d.result() == QDialog.Rejected:
            self.remove_empty_smartnode()
        elif (action == self.CREATE or self.EDIT) and d.result() == QDialog.Accepted:
            self.update_smartnodes_status(False)
            # need to update utxo_list
            self.gui.need_update.set()

    def add_empty_smartnode(self):
        empty_smartnode = MasternodeAnnounce(alias='', addr=NetworkAddress())
        self.add_smartnode(empty_smartnode, save=False)
        self.select_smartnode('')

    def remove_empty_smartnode(self):
        try:
            self.remove_smartnode('', save=False)
            self.tableWidgetMySmartnodes.clearSelection()
        except:
            self.print_error("Cannot remove_empty smartnode")
        self.disable_node_buttons()

    def select_smartnode(self, alias):
        """Select the row that represents alias."""
        self.tableWidgetMySmartnodes.clearSelection()
        for i in range(self.proxy_model.rowCount()):
            idx = self.proxy_model.index(i, 0)
            mn_alias = str(self.proxy_model.data(idx))
            if mn_alias == alias:
                self.tableWidgetMySmartnodes.selectRow(i)
                break

    def refresh_items(self):
        self.model.dataChanged.emit(QModelIndex(), QModelIndex())

    def add_smartnode(self, smartnode, save=True):
        self.model.add_smartnode(smartnode, save=save)

    def remove_smartnode(self, alias, save=True):
        self.model.remove_smartnode(alias, save=save)

        # need to update utxo_list
        self.gui.need_update.set()

    def smartnode_for_row(self, row):
        idx = self.proxy_model.mapToSource(self.proxy_model.index(row, 0))
        return self.model.smartnode_for_row(idx.row())

    def selected_smartnode(self):
        """Get the currently-selected smartnode."""
        row = self.mapper.currentIndex()
        mn = self.smartnode_for_row(row)
        return mn

    def delete_current_smartnode(self):
        """Delete the smartnode that is being viewed."""
        mn = self.selected_smartnode()
        if QMessageBox.question(self, ('Remove Smartnode Entry'), ('Remove smartnode') + ' %s?' % mn.alias,
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.remove_smartnode(mn.alias)
            #self.tableWidgetMySmartnodes.selectRow(0)
            self.tableWidgetMySmartnodes.clearSelection()

    def on_view_selection_changed(self, selected, deselected):
        """Update the data widget mapper."""
        row = 0
        try:
            row = selected.indexes()[0].row()
        except Exception:
            pass
        self.mapper.setCurrentIndex(row)
        self.EditButton.setEnabled(True)
        self.CreateButton.setEnabled(True)
        self.ViewButton.setEnabled(True)
        self.RemoveButton.setEnabled(True)
        self.startButton.setEnabled(True)

    def start_current_smartnode(self):
        """Start the smartnode that is being viewed."""
        mn = self.selected_smartnode()
        if QMessageBox.question(self, ('Confirm Smartnode Start'), ('Are you sure you want to start Smartnode') + ' %s? This will reset your node in the payment queue.' % mn.alias,
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes:
            self.sign_announce(mn.alias)
            self.update_smartnodes_status(False)

    def sign_announce(self, alias):
        """Sign an announce for alias. This is called by SignAnnounceWidget."""

        pw = None
        if self.manager.wallet.has_password():
            if not isinstance(self.manager.wallet.keystore, keystore.Hardware_KeyStore):
                pw = self.gui.password_dialog(_('Please enter your password to activate smartnode "%s".' % alias))
                if pw is None:
                    return

        def sign_thread():
            return self.manager.sign_announce(alias, pw)

        def on_sign_successful(mn):
            self.print_msg('Successfully signed Smartnode Announce.')
            self.send_announce(alias)
        # Proceed to broadcasting the announcement, or re-enable the button.
        def on_sign_error(err):
            self.print_error('Error signing Smartnode Announce:')
            # Print traceback information to error log.
            self.print_error(''.join(traceback.format_tb(err[2])))
            self.print_error(''.join(traceback.format_exception_only(err[0], err[1])))
            errmsg = ''.join(traceback.format_exception_only(err[0], err[1]))
            QMessageBox.critical(self, ('Error signing Smartnode Announce'), (errmsg))

        util.WaitingDialog(self, ('Signing Smartnodenode Announce...'), sign_thread, on_sign_successful, on_sign_error)

    def send_announce(self, alias):
        """Send an announce for a smartnode."""
        def send_thread():
            return self.manager.send_announce(alias)

        def on_send_successful(result):
            errmsg, was_announced = result
            if errmsg:
                self.print_error('Failed to broadcast SmartnodeAnnounce: %s' % errmsg)
                QMessageBox.critical(self, ('Error Sending'), errmsg)
            elif was_announced:
                self.update_smartnodes_status(False)
                self.print_msg('Successfully broadcasted SmartnodeAnnounce for "%s"' % alias)

                QMessageBox.information(self, ('Success'), ('Successfully started smartnode "%s"' % alias))
            self.refresh_items()
            self.select_smartnode(alias)


        def on_send_error(err):
            self.print_error('Error sending Smartnode Announce message:')
            # Print traceback information to error log.
            self.print_error(''.join(traceback.format_tb(err[2])))
            self.print_error(''.join(traceback.format_exception_only(err[0], err[1])))
            #self.masternodes_widget.refresh_items()
            #self.masternodes_widget.select_masternode(alias)

        self.print_msg('Sending Smartnode Announce message...')
        util.WaitingDialog(self, ('Broadcasting smartnode...'), send_thread, on_send_successful, on_send_error)

    def update_smartnodes_status(self, show_message=True):
        self.manager.subscribe_to_all_masternodes()
        if(show_message):
            QMessageBox.information(self, ('Success'), ('Successfully requested %s smartnodes status from server.' % str(len(self.smartnodes))))
        self.refresh_items()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sys.exit(app.exec_())
