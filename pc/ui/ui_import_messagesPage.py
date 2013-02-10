# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/import_messagesPage.ui'
#
# Created: Wed Nov 17 12:06:01 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_messagesPage(object):
    def setupUi(self, messagesPage):
        messagesPage.setObjectName("messagesPage")
        messagesPage.resize(500, 430)
        messagesPage.setWindowTitle("")
        self.verticalLayout_2 = QtGui.QVBoxLayout(messagesPage)
        self.verticalLayout_2.setSpacing(20)
        self.verticalLayout_2.setContentsMargins(10, 10, 10, 20)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtGui.QLabel(messagesPage)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.label_2 = QtGui.QLabel(messagesPage)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_2.addWidget(self.label_2)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.messageNumberBar = QtGui.QProgressBar(messagesPage)
        self.messageNumberBar.setProperty("value", 0)
        self.messageNumberBar.setObjectName("messageNumberBar")
        self.verticalLayout.addWidget(self.messageNumberBar)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_3 = QtGui.QLabel(messagesPage)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.messageNumberLabel = QtGui.QLabel(messagesPage)
        self.messageNumberLabel.setText("")
        self.messageNumberLabel.setObjectName("messageNumberLabel")
        self.horizontalLayout.addWidget(self.messageNumberLabel)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)

        self.retranslateUi(messagesPage)
        QtCore.QMetaObject.connectSlotsByName(messagesPage)

    def retranslateUi(self, messagesPage):
        self.label.setText(QtGui.QApplication.translate("messagesPage", "Step 4: Importing messages...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("messagesPage", "All Messages are imported", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("messagesPage", "Current message:", None, QtGui.QApplication.UnicodeUTF8))

