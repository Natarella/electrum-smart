from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from datetime import datetime
from electrum_smart import bitcoin

class Ui_SmartProposalWidget(object):
    def setupUi(self, SmartProposalWidget, proposal, selected_voting_option_map, smartvote_manager):

        self.selected_voting_option_map = selected_voting_option_map
        self.proposal = proposal
        self.manager = smartvote_manager

        SmartProposalWidget.setObjectName("SmartProposalWidget")
        SmartProposalWidget.resize(768, 203)
        SmartProposalWidget.setStyleSheet("#SmartProposalWidget{\n"
"border: 1px solid black;\n"
"border-radius: 5px;\n"
"background-color: #FBFCFC;\n"
"}\n"
"\n"
"QProgressBar {\n"
"    background-color: rgb(201, 199, 202);\n"
"    max-height:5px;\n"
"    border-radius: 2px;\n"
"    height:6px;\n"
"}\n"
"\n"
"")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(SmartProposalWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.titleLabel = QtWidgets.QLabel(SmartProposalWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout_4.addWidget(self.titleLabel)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.groupBox_4 = QtWidgets.QGroupBox(SmartProposalWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_4.setFont(font)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_3.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_3.setSpacing(6)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.amountSmartLabel = QtWidgets.QLabel(self.groupBox_4)
        self.amountSmartLabel.setObjectName("amountSmartLabel")
        self.verticalLayout_3.addWidget(self.amountSmartLabel)
        self.amountUSDLabel = QtWidgets.QLabel(self.groupBox_4)
        self.amountUSDLabel.setObjectName("amountUSDLabel")
        self.verticalLayout_3.addWidget(self.amountUSDLabel)
        self.horizontalLayout.addWidget(self.groupBox_4)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.groupBox_3 = QtWidgets.QGroupBox(SmartProposalWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_8.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_8.setSpacing(6)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.deadlineLabel = QtWidgets.QLabel(self.groupBox_3)
        self.deadlineLabel.setObjectName("deadlineLabel")
        self.verticalLayout_8.addWidget(self.deadlineLabel)
        self.deadlineProgress = QtWidgets.QProgressBar(self.groupBox_3)
        self.deadlineProgress.setStyleSheet("QProgressBar::chunk {\n"
"    background-color: #FEC60D;\n"
"}")
        self.deadlineProgress.setProperty("value", 24)
        self.deadlineProgress.setTextVisible(False)
        self.deadlineProgress.setObjectName("deadlineProgress")
        self.verticalLayout_8.addWidget(self.deadlineProgress)
        self.horizontalLayout.addWidget(self.groupBox_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.groupBox_2 = QtWidgets.QGroupBox(SmartProposalWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.votedLabel = QtWidgets.QLabel(self.groupBox_2)
        self.votedLabel.setWordWrap(True)
        self.votedLabel.setObjectName("votedLabel")
        self.verticalLayout_2.addWidget(self.votedLabel)
        self.horizontalLayout.addWidget(self.groupBox_2)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.viewProposalButton = QtWidgets.QPushButton(SmartProposalWidget)
        self.viewProposalButton.setAutoDefault(False)
        self.viewProposalButton.setFlat(False)
        self.viewProposalButton.setObjectName("viewProposalButton")
        self.horizontalLayout_2.addWidget(self.viewProposalButton)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.groupBox = QtWidgets.QGroupBox(SmartProposalWidget)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.disabledButton = QtWidgets.QRadioButton(self.groupBox)
        self.disabledButton.setChecked(True)
        self.disabledButton.setObjectName("disabledButton")
        self.horizontalLayout_4.addWidget(self.disabledButton)
        self.yesButton = QtWidgets.QRadioButton(self.groupBox)
        self.yesButton.setObjectName("yesButton")
        self.horizontalLayout_4.addWidget(self.yesButton)
        self.noButton = QtWidgets.QRadioButton(self.groupBox)
        self.noButton.setObjectName("noButton")
        self.horizontalLayout_4.addWidget(self.noButton)
        self.abstainButton = QtWidgets.QRadioButton(self.groupBox)
        self.abstainButton.setObjectName("abstainButton")
        self.horizontalLayout_4.addWidget(self.abstainButton)
        self.horizontalLayout_2.addWidget(self.groupBox)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem6)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem7)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.yesLabel = QtWidgets.QLabel(SmartProposalWidget)
        self.yesLabel.setObjectName("yesLabel")
        self.verticalLayout.addWidget(self.yesLabel)
        self.progressYes = QtWidgets.QProgressBar(SmartProposalWidget)
        self.progressYes.setStyleSheet("QProgressBar::chunk {\n"
"    background-color: rgb(156, 194, 85)\n"
"}")
        self.progressYes.setProperty("value", 24)
        self.progressYes.setTextVisible(False)
        self.progressYes.setObjectName("progressYes")
        self.verticalLayout.addWidget(self.progressYes)
        self.noLabel = QtWidgets.QLabel(SmartProposalWidget)
        self.noLabel.setObjectName("noLabel")
        self.verticalLayout.addWidget(self.noLabel)
        self.progressNo = QtWidgets.QProgressBar(SmartProposalWidget)
        self.progressNo.setStyleSheet("QProgressBar::chunk {\n"
"    background-color: rgb(179, 2, 0)\n"
"}")
        self.progressNo.setProperty("value", 24)
        self.progressNo.setTextVisible(False)
        self.progressNo.setObjectName("progressNo")
        self.verticalLayout.addWidget(self.progressNo)
        self.abstainLabel = QtWidgets.QLabel(SmartProposalWidget)
        self.abstainLabel.setObjectName("abstainLabel")
        self.verticalLayout.addWidget(self.abstainLabel)
        self.progressAbstain = QtWidgets.QProgressBar(SmartProposalWidget)
        self.progressAbstain.setStyleSheet("QProgressBar::chunk {\n"
"    background-color: rgb(131, 142, 162)\n"
"}")
        self.progressAbstain.setProperty("value", 24)
        self.progressAbstain.setTextVisible(False)
        self.progressAbstain.setObjectName("progressAbstain")
        self.verticalLayout.addWidget(self.progressAbstain)
        self.horizontalLayout_3.addLayout(self.verticalLayout)

        self.retranslateUi(SmartProposalWidget)

        self.update_proposal_details()

        QtCore.QMetaObject.connectSlotsByName(SmartProposalWidget)
        SmartProposalWidget.setTabOrder(self.viewProposalButton, self.disabledButton)
        SmartProposalWidget.setTabOrder(self.disabledButton, self.yesButton)
        SmartProposalWidget.setTabOrder(self.yesButton, self.noButton)
        SmartProposalWidget.setTabOrder(self.noButton, self.abstainButton)

    def retranslateUi(self, SmartProposalWidget):
        _translate = QtCore.QCoreApplication.translate
        SmartProposalWidget.setWindowTitle(_translate("SmartProposalWidget", "Form"))
        self.titleLabel.setText(_translate("SmartProposalWidget", "# 1000 - SmartCash 360 Video Editor & Creation Tool rtCash 360 Video Editor & Creation Tool"))
        self.groupBox_4.setTitle(_translate("SmartProposalWidget", "Requested funds"))
        self.amountSmartLabel.setText(_translate("SmartProposalWidget", "Σ 245,145.93"))
        self.amountUSDLabel.setText(_translate("SmartProposalWidget", "US$ 20,950.00"))
        self.groupBox_3.setTitle(_translate("SmartProposalWidget", "Voting deadline"))
        self.deadlineLabel.setText(_translate("SmartProposalWidget", "06 days 20:49:08"))
        self.groupBox_2.setTitle(_translate("SmartProposalWidget", "You voted"))
        self.votedLabel.setText(_translate("SmartProposalWidget", "Nothing"))
        self.viewProposalButton.setText(_translate("SmartProposalWidget", "View in browser"))
        self.groupBox.setTitle(_translate("SmartProposalWidget", "Select your vote"))
        self.disabledButton.setText(_translate("SmartProposalWidget", "Disabled"))
        self.yesButton.setText(_translate("SmartProposalWidget", "Yes"))
        self.noButton.setText(_translate("SmartProposalWidget", "No"))
        self.abstainButton.setText(_translate("SmartProposalWidget", "Abstain"))
        self.yesLabel.setText(_translate("SmartProposalWidget", "Yes ( 0000000.0000  )"))
        self.noLabel.setText(_translate("SmartProposalWidget", "No ( 0000000.0000  )"))
        self.abstainLabel.setText(_translate("SmartProposalWidget", "Abstain ( 0000000.0000  )"))

    def update_proposal_details(self):

        proposal = self.proposal

        title = "#{} - {}".format(proposal.get('proposalId'), proposal.get('title'))
        amountSmart = "{} SMART".format(self.add_thousands_spaces(proposal.get('amountSmart')))
        amountUSD = "{} USD".format(self.add_thousands_spaces(proposal.get('amountUSD')))

        voteYes = self.add_thousands_spaces(proposal.get('voteYes'))
        voteNo = self.add_thousands_spaces(proposal.get('voteNo'))
        voteAbstain = self.add_thousands_spaces(proposal.get('voteAbstain'))

        percentYes = "%.2f" % proposal.get('percentYes')
        percentNo = "%.2f" % proposal.get('percentNo')
        percentAbstain = "%.2f" % proposal.get('percentAbstain')

        votingDeadline = datetime.strptime(proposal.get('votingDeadline'), '%Y-%m-%dT%H:%M:%S')
        createdDate = datetime.strptime(proposal.get('createdDate'), '%Y-%m-%dT%H:%M:%S')
        percent_time = self.percent_time(createdDate, votingDeadline, datetime.utcnow())

        VotedYes = 0
        VotedNo = 0
        VotedAbstain = 0
        for item in proposal.get('addressStates'):
            type = item.get('type')
            amount = item.get('amount')
            if type == 'YES':
                VotedYes = VotedYes + amount
            elif type == 'NO':
                VotedNo = VotedNo + amount
            elif type == 'ABSTAIN':
                VotedAbstain = VotedAbstain + amount

        votedLabelText = ''
        if VotedYes > 0:
            votedLabelText += 'YES - {}\n'.format(int(VotedYes))
        if VotedNo > 0:
            votedLabelText += 'NO - {}\n'.format(int(VotedNo))
        if VotedAbstain > 0:
            votedLabelText += 'ABSTAIN - {}'.format(int(VotedAbstain))

        if VotedYes > 0 or VotedNo > 0 or VotedAbstain > 0:
            self.votedLabel.setText(votedLabelText)
            self.manager.voted_proposals = self.manager.voted_proposals + 1

        self.titleLabel.setText(title)
        self.amountSmartLabel.setText(amountSmart)
        self.amountUSDLabel.setText(amountUSD)

        self.progressYes.setProperty("value", int(proposal.get('percentYes')))
        self.progressNo.setProperty("value", int(proposal.get('percentNo')))
        self.progressAbstain.setProperty("value", int(proposal.get('percentAbstain')))

        self.yesLabel.setText("Yes {}%( {} SMART  )".format(percentYes, voteYes))
        self.noLabel.setText("No {}% ( {} SMART  )".format(percentNo, voteNo))
        self.abstainLabel.setText("Abstain {}% ( {} SMART  )".format(percentAbstain, voteAbstain))

        self.viewProposalButton.clicked.connect(lambda: self.open_proposal_in_browser(proposal.get('url')))

        self.deadlineLabel.setText(votingDeadline.strftime("%b %d %Y %H:%M:%S UTC"))
        self.deadlineProgress.setProperty("value", int(percent_time))

        self.yesButton.clicked.connect(lambda: self.update_vote_option("YES"))
        self.noButton.clicked.connect(lambda: self.update_vote_option("NO"))
        self.abstainButton.clicked.connect(lambda: self.update_vote_option("ABSTAIN"))
        self.disabledButton.clicked.connect(self.disable_vote_option)

    def add_thousands_spaces(self, a):
        a = int(a)
        return format(a, ',').replace(',', ' ').replace('.', ',')

    def open_proposal_in_browser(self, proposal_url):
        import webbrowser
        url = 'https://vote.smartcash.cc/Proposal/Details/{}'.format(proposal_url)
        webbrowser.open(url)

    def t(self, dt):
        import time
        return time.mktime(dt.timetuple())

    def percent_time(self, start_time, end_time, current_time):
        total = self.t(end_time) - self.t(start_time)
        current = self.t(current_time) - self.t(start_time)
        return (100.0 * current) / total

    def update_votes(self):
        total = self.t(end_time) - self.t(start_time)
        current = self.t(current_time) - self.t(start_time)
        return (100.0 * current) / total

    def update_vote_option(self, option):
        self.selected_voting_option_map[self.proposal.get("proposalId")] = option

    def disable_vote_option(self):
        self.selected_voting_option_map.pop(self.proposal.get("proposalId"), None)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SmartProposalWidget = QtWidgets.QWidget()
    ui = Ui_SmartProposalWidget()
    ui.setupUi(SmartProposalWidget)
    SmartProposalWidget.show()
    sys.exit(app.exec_())

