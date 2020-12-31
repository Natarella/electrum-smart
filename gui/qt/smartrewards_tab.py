import os
import traceback

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from electrum_smart import bitcoin
from electrum_smart.util import PrintError, bfh, bh2u, format_satoshis, json_decode, print_error, json_encode
from electrum_smart.bitcoin import COIN

from . import util

BLOCK_TIME = 55

class SmartrewardsAddressModel(QAbstractTableModel):

    """Model for smartrewards."""

    LABEL = 0
    ADDRRESS = 1
    AMOUNT = 2
    ELIGIBLE_AMOUNT = 3
    ESTIMATED_REWARD = 4
    TOTAL_FIELDS = 5

    def __init__(self, manager, parent=None):
        super(SmartrewardsAddressModel, self).__init__(parent)

        self.manager = manager
        self.smartrewards = self.manager.rewards_addresses

        headers = [
            {Qt.DisplayRole: 'Label',},
            {Qt.DisplayRole: 'Address', },
            {Qt.DisplayRole: 'Amount', },
            {Qt.DisplayRole: 'Eligible Amount',},
            {Qt.DisplayRole: 'Estimated SmartReward', },
        ]

        for d in headers:
            d[Qt.EditRole] = d[Qt.DisplayRole]

        self.headers = headers

    def smartrewards_for_row(self, row):
        rw = self.smartrewards[row]
        return rw

    def columnCount(self, parent=QModelIndex()):
        return self.TOTAL_FIELDS

    def rowCount(self, parent=QModelIndex()):
        return len(self.smartrewards)

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

        rw = self.smartrewards[index.row()]
        i = index.column()

        if i == self.LABEL:
            data = rw.label
        elif i == self.ADDRRESS:
            data = rw.address
        elif i == self.AMOUNT:
            data = '{} SMART'.format( self.manager.add_thousands_spaces( format_satoshis(rw.amount) ) )
        elif i == self.ELIGIBLE_AMOUNT:
            data = '{} SMART'.format(rw.eligible_amount)
        elif i == self.ESTIMATED_REWARD:
            data = '{} SMART'.format(rw.estimated_reward)

        return QVariant(data)

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid(): return False

        rw = self.smartrewards[index.row()]
        i = index.column()

        if i == self.LABEL:
            rw.alias = value
        elif i == self.ADDRRESS:
            rw.address = value
        elif i == self.AMOUNT:
            rw.amount = value
        elif i == self.ELIGIBLE_AMOUNT:
            rw.eligible_amount = value
        elif i == self.ESTIMATED_REWARD:
            rw.estimated_reward = value
        else:
            return False

        self.dataChanged.emit(self.index(index.row(), index.column()), self.index(index.row(), index.column()))
        return True


class SmartrewardsTab(QWidget):
    def __init__(self, parent=None):
        super(SmartrewardsTab, self).__init__(parent)
        self.create_layout()
        self.manager = None

    def create_layout(self):
        self.setObjectName("SmartrewardsList")
        self.resize(811, 457)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(9, 0, -1, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widget = QWidget(self)
        self.widget.setMaximumSize(QSize(16777215, 16777215))
        self.widget.setObjectName("widget")
        self.verticalLayout_2 = QVBoxLayout(self.widget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget_2 = QWidget(self.widget)
        self.widget_2.setMinimumSize(QSize(0, 60))
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_11 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.label_17 = QLabel(self.widget_2)
        font = QFont()
        font.setPointSize(19)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.horizontalLayout_12.addWidget(self.label_17)
        self.roundLabel = QLabel(self.widget_2)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.roundLabel.sizePolicy().hasHeightForWidth())
        self.roundLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.roundLabel.setFont(font)
        self.roundLabel.setObjectName("roundLabel")
        self.horizontalLayout_12.addWidget(self.roundLabel)
        self.verticalLayout_5.addLayout(self.horizontalLayout_12)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.label_19 = QLabel(self.widget_2)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_19.sizePolicy().hasHeightForWidth())
        self.label_19.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(13)
        self.label_19.setFont(font)
        self.label_19.setObjectName("label_19")
        self.horizontalLayout_13.addWidget(self.label_19)
        self.nextRoundLabel = QLabel(self.widget_2)
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nextRoundLabel.sizePolicy().hasHeightForWidth())
        self.nextRoundLabel.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.nextRoundLabel.setFont(font)
        self.nextRoundLabel.setObjectName("nextRoundLabel")
        self.horizontalLayout_13.addWidget(self.nextRoundLabel)
        self.verticalLayout_5.addLayout(self.horizontalLayout_13)
        self.horizontalLayout_11.addLayout(self.verticalLayout_5)
        self.horizontalLayout_14 = QHBoxLayout()
        self.horizontalLayout_14.setObjectName("horizontalLayout_14")
        self.label_21 = QLabel(self.widget_2)
        font = QFont()
        font.setPointSize(19)
        self.label_21.setFont(font)
        self.label_21.setObjectName("label_21")
        self.horizontalLayout_14.addWidget(self.label_21)
        self.percentLabel = QLabel(self.widget_2)
        font = QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.percentLabel.setFont(font)
        self.percentLabel.setObjectName("percentLabel")
        self.horizontalLayout_14.addWidget(self.percentLabel)
        self.label_22 = QLabel(self.widget_2)
        font = QFont()
        font.setPointSize(19)
        self.label_22.setFont(font)
        self.label_22.setObjectName("label_22")
        self.horizontalLayout_14.addWidget(self.label_22)
        self.percentLabel2 = QLabel(self.widget_2)
        font = QFont()
        font.setPointSize(19)
        font.setBold(True)
        font.setWeight(75)
        self.percentLabel2.setFont(font)
        self.percentLabel2.setObjectName("percentLabel2")
        self.horizontalLayout_14.addWidget(self.percentLabel2)
        self.horizontalLayout_11.addLayout(self.horizontalLayout_14)
        self.verticalLayout_2.addWidget(self.widget_2)

        #SmartRewards Table
        self.tableWidget = QTableView()
        self.tableWidget.setMinimumSize(QSize(695, 0))
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tableWidget.setSortingEnabled(True)
        self.tableWidget.verticalHeader().setVisible(False)
        self.tableWidget.setObjectName("tableWidget")
        self.verticalLayout_2.addWidget(self.tableWidget)

        self.widget1 = QWidget(self.widget)
        self.widget1.setMinimumSize(QSize(0, 40))
        self.widget1.setObjectName("widget1")
        self.horizontalLayout_3 = QHBoxLayout(self.widget1)
        self.horizontalLayout_3.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QSpacerItem(152, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QLabel(self.widget1)
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.sumLabel = QLabel(self.widget1)
        font = QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.sumLabel.setFont(font)
        self.sumLabel.setObjectName("sumLabel")
        self.horizontalLayout_2.addWidget(self.sumLabel)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        spacerItem1 = QSpacerItem(151, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.widget1)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi()
        QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QCoreApplication.translate
        self.setWindowTitle(_translate("SmartrewardsList", "Form"))
        self.label_17.setText(_translate("SmartrewardsList", "SmartRewards Round"))
        self.roundLabel.setText(_translate("SmartrewardsList", "0"))
        self.label_19.setText(_translate("SmartrewardsList", "Round ends"))
        self.nextRoundLabel.setText(_translate("SmartrewardsList", "25.12.1999"))
        self.label_21.setText(_translate("SmartrewardsList", "SmartRewards"))
        self.percentLabel.setText(_translate("SmartrewardsList", "0.00%"))
        self.label_22.setText(_translate("SmartrewardsList", "SuperRewards"))
        self.percentLabel2.setText(_translate("SmartrewardsList", "0.00%"))
        self.label.setText(_translate("SmartrewardsList", "Estimated SmartRewards"))
        self.sumLabel.setText(_translate("SmartrewardsList", "0 SMART"))

    def load_smartrewards(self, manager):
        self.manager = manager
        self.manager.send_subscriptions()
        self.load_table()

    def update(self):
        rewards_percent = self.manager.rewards_info.estimated_percent
        self.roundLabel.setText(self.manager.rewards_info.get_rewards_cycle())
        self.percentLabel.setText("{:.2%}".format(pow( 1+(rewards_percent * .0150), 52 )-1))
        self.percentLabel2.setText("{:.2%}".format(pow( 1+(rewards_percent * .0250), 52 )-1))
        self.nextRoundLabel.setText(self.get_next_round())
        self.sumLabel.setText('{} SMART'.format(self.get_sum_estimated_rewards()))

    def get_next_round(self):
        end = self.manager.rewards_info.end_blockheight
        current = self.manager.network.get_local_height()
        progress = end - current

        if progress < 0:
            self.manager.send_subscriptions()
            #https://github.com/SmartCash/Core-Smart/blob/77aacf855de4b830564afed8be6183f575e0ae75/src/smartrewards/rewardspayments.h
            nRewardPayoutStartDelay = 200;
            return 'Snapshot has occurred. Payouts will begin at block {}'.format(end + nRewardPayoutStartDelay)

        else:

            time_to_end_in_seconds = progress * BLOCK_TIME

            t = int(time_to_end_in_seconds)
            day = t // 86400
            hour = (t - (day * 86400)) // 3600
            minute = (t - ((day * 86400) + (hour * 3600))) // 60
            seconds = t - ((day * 86400) + (hour * 3600) + (minute * 60))

            str_day = 'day' if day == 1 else 'days'
            str_hour = 'hour' if hour == 1 else 'hours'
            str_minute = 'minute' if minute == 1 else 'minutes'

            time = ''

            if day > 0:
                time += ' {}{} '.format(day, str_day)

            if hour > 0:
                time += ' {}{} '.format(hour, str_hour)

            if minute > 0 and day <= 0:
                time += ' {}{} '.format(minute, str_minute)

            if time_to_end_in_seconds > 0:
                self.label_19.show()
                return '{} blocks ( {} )'.format(str(progress), time)
            else:
                self.label_19.hide()
                return 'Snapshot in progress'

    def get_sum_estimated_rewards(self):
        return sum(addr.estimated_reward for addr in self.manager.rewards_addresses)

    def subscribe_to_smartrewards(self):
        self.manager.send_subscriptions()

    def load_table(self):
        self.model = SmartrewardsAddressModel(self.manager)
        self.proxy_model = model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.tableWidget.setModel(self.proxy_model)

        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(SmartrewardsAddressModel.LABEL, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(SmartrewardsAddressModel.ADDRRESS, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(SmartrewardsAddressModel.AMOUNT, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(SmartrewardsAddressModel.ELIGIBLE_AMOUNT, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(SmartrewardsAddressModel.ESTIMATED_REWARD, QHeaderView.Stretch)

    def reload(self):
        self.manager.reload()
        self.load_table()
