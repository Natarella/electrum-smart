
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import datetime

class Ui_SmartNewsWidget(object):
    def setupUi(self, SmartProposalWidget):

        SmartProposalWidget.setObjectName("SmartProposalWidget")
        SmartProposalWidget.resize(865, 232)
        SmartProposalWidget.setStyleSheet('#SmartProposalWidget{\n'
                                          'border: 1px solid black;\n'
                                          'border-radius: 5px;\n'
                                          'background-color: #FBFCFC;\n'
                                          '}')
        self.horizontalLayout_3 = QHBoxLayout(SmartProposalWidget)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.titleLabel = QLabel(SmartProposalWidget)
        font = QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.titleLabel.setFont(font)
        self.titleLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignTop)
        self.titleLabel.setWordWrap(True)
        self.titleLabel.setObjectName("titleLabel")
        self.verticalLayout_4.addWidget(self.titleLabel)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox_2 = QGroupBox(SmartProposalWidget)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(10)
        self.groupBox_2.setFont(font)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setContentsMargins(6, 6, 6, 6)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.label.setWordWrap(True);
        self.verticalLayout_2.addWidget(self.label)
        self.horizontalLayout.addWidget(self.groupBox_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.viewProposalButton = QPushButton(SmartProposalWidget)
        self.viewProposalButton.setAutoDefault(False)
        self.viewProposalButton.setFlat(False)
        self.viewProposalButton.setObjectName("viewProposalButton")
        self.horizontalLayout_2.addWidget(self.viewProposalButton)
        spacerItem = QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)

        self.retranslateUi(SmartProposalWidget)
        QMetaObject.connectSlotsByName(SmartProposalWidget)

    def retranslateUi(self, SmartProposalWidget):
        _translate = QCoreApplication.translate
        SmartProposalWidget.setWindowTitle(_translate("SmartProposalWidget", "Form"))
        self.titleLabel.setText(_translate("SmartProposalWidget", "SmartCash Tip Bot Makes it Easy to Tip Anyone"))
        self.groupBox_2.setTitle(_translate("SmartProposalWidget", "April 12, 2019 - coinlance.com"))
        self.label.setText(_translate("SmartProposalWidget", "A cryptocurrency themed Augmented Reality game called Crypto Hunters has been released for beta and SmartCash is on the list of currencies involved with the project! Created by SWYFT with the intent of helping to..."))
        self.viewProposalButton.setText(_translate("SmartProposalWidget", "Read more"))

    def update_proposal_details(self, news):

        # Format date
        d = news.get('date')
        if ":" == d[-3:-2]:
            d = d[:-3] + d[-2:]
        datetime_object = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S%z")

        title = news.get('title')
        description = news.get('description')
        date = datetime_object.strftime("%b %d %Y %H:%M UTC")
        source = "{} - From {}".format(date, news.get('site'))
        url = news.get('link')

        self.titleLabel.setText(title)
        self.groupBox_2.setTitle(source)
        self.label.setText(description)

        self.viewProposalButton.clicked.connect(lambda: self.open_in_browser(url))

    def open_in_browser(self, url):
        import webbrowser
        webbrowser.open(url)
