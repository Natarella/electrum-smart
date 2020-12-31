from collections import namedtuple, OrderedDict
import base64
import threading
import json
from decimal import Decimal
from locale import localeconv

from . import bitcoin
from .blockchain import hash_header
from .smartnode import MasternodeAnnounce, NetworkAddress
from .util import AlreadyHaveAddress, print_error, bfh, print_msg, format_satoshis_plain, format_satoshis
from .bitcoin import COIN

class SmartRewardsInfo(object):

    def __init__(self, rewards_cycle='', start_blockheight=0, start_blocktime=0,
                 end_blockheight=0, end_blocktime=0, eligible_addresses=0.0, eligible_smart=0,
                 disqualified_addresses=0, disqualified_smart=0.0,
                 estimated_rewards=0.0, estimated_percent=0.0):
        self.rewards_cycle = rewards_cycle
        self.start_blockheight = start_blockheight
        self.start_blocktime = start_blocktime
        self.end_blockheight = end_blockheight
        self.end_blocktime = end_blocktime
        self.eligible_addresses = eligible_addresses
        self.eligible_smart = eligible_smart
        self.disqualified_addresses = disqualified_addresses
        self.disqualified_smart = disqualified_smart
        self.estimated_rewards = estimated_rewards
        self.estimated_percent = estimated_percent
        self.actual_blockheight = 0

    def get_rewards_cycle(self):
        return str(self.rewards_cycle)

    def get_percent_rewards(self):
        return "{:.2%}".format(self.estimated_percent)

    def get_next_round(self):
        return '{} blocks'.format(self.end_blockheight - self.actual_blockheight)

class SmartRewardsAddress(object):

    def __init__(self, label='', address='', amount=0.0,
                 eligible_amount=0.0, estimated_reward=0):
        self.label = label
        self.address = address
        self.amount = amount
        self.eligible_amount = eligible_amount
        self.estimated_reward = estimated_reward

class SmartrewardsManager(object):
    """Smartrewards manager.

    Keeps track of smartrewards.
    """
    def __init__(self, wallet, network):
        self.network_event = threading.Event()
        self.wallet = wallet
        self.network = network

        self.rewards_info = SmartRewardsInfo()
        self.rewards_addresses = []

        self.load()

    def load(self):
        # Load smartrewards addresses
        for addr in self.wallet.get_addresses():
            balance = sum(self.wallet.get_addr_balance(addr))
            label = self.wallet.labels.get(addr)
            if not label: label = '(no label)'
            if balance >= 999 * COIN:
                self.rewards_addresses.append(SmartRewardsAddress(label, addr, balance, 0, 0))

    def reload(self):
        self.rewards_addresses = []
        self.load()
        self.send_subscriptions()

    def send_subscriptions(self):
        if not self.wallet.network.is_connected():
            print_error("Cannot update smartrewards. Wallet not connected")
            return
        self.subscribe_to_smartrewards_info()
        self.subscribe_to_smartrewards_addresses()

    def subscribe_to_smartrewards_info(self):
        req = ('smartrewards.current', [])
        self.wallet.network.send([req], self.smartrewards_info_response)

    def subscribe_to_smartrewards_addresses(self):
        requests = []

        for rw in self.rewards_addresses:
            requests.append(('smartrewards.check', [rw.address]))

        self.network.send(requests, self.smartrewards_check_response)

    def smartrewards_info_response(self, response):
        if not 'result' in response:
            print_error(response['error'])
            return response['error']

        result = response['result']
        if result is None:
            result = False

        print_msg('Received smartrewards info: "%s"' % (result))

        smartrewards_cycle = SmartRewardsInfo(**result)
        smartrewards_cycle.actual_blockheight = self.network.get_local_height()

        self.rewards_info = smartrewards_cycle

    def smartrewards_check_response(self, response):
        if not 'result' in response:
            print_error(response['error'])
            return response['error']

        result = response['result']
        addr = result.get("address")
        eligible_balance = result.get("balance_eligible")

        for reward in self.rewards_addresses:
            if addr == reward.address:
                reward.eligible_amount = eligible_balance
                reward.estimated_reward = float("{0:.8f}".format(eligible_balance * self.rewards_info.estimated_percent))
                break

        print_msg('Rewards for [{}] is [{}]'.format(addr, eligible_balance))

    def add_thousands_spaces(self, a):
        dp = localeconv()['decimal_point']
        if dp == ',':
            a = a.replace(',', '.')
        out = float(a)
        return format(out, ',').replace(',', ' ')
