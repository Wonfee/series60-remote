# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/messageQueue.ui'
#
# Created: Wed Nov 17 12:05:52 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MessageQueue(object):
    def setupUi(self, MessageQueue):
        MessageQueue.setObjectName("MessageQueue")
        MessageQueue.resize(654, 428)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/messages"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MessageQueue.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(MessageQueue)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.messageTree = QtGui.QTreeWidget(MessageQueue)
        self.messageTree.setAlternatingRowColors(True)
        self.messageTree.setAnimated(True)
        self.messageTree.setWordWrap(True)
        self.messageTree.setObjectName("messageTree")
        self.messageTree.headerItem().setText(0, " ")
        self.verticalLayout.addWidget(self.messageTree)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 0, 1, 1)
        self.refreshBox = QtGui.QCheckBox(MessageQueue)
        self.refreshBox.setChecked(True)
        self.refreshBox.setObjectName("refreshBox")
        self.gridLayout.addWidget(self.refreshBox, 0, 1, 1, 1)
        self.refreshButton = QtGui.QPushButton(MessageQueue)
        self.refreshButton.setObjectName("refreshButton")
        self.gridLayout.addWidget(self.refreshButton, 0, 2, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(MessageQueue)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 3)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(MessageQueue)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), MessageQueue.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), MessageQueue.reject)
        QtCore.QMetaObject.connectSlotsByName(MessageQueue)

    def retranslateUi(self, MessageQueue):
        MessageQueue.setWindowTitle(QtGui.QApplication.translate("MessageQueue", "Message queue", None, QtGui.QApplication.UnicodeUTF8))
        self.messageTree.headerItem().setText(1, QtGui.QApplication.translate("MessageQueue", "Date", None, QtGui.QApplication.UnicodeUTF8))
        self.messageTree.headerItem().setText(2, QtGui.QApplication.translate("MessageQueue", "Event", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshBox.setText(QtGui.QApplication.translate("MessageQueue", "Refresh automatically", None, QtGui.QApplication.UnicodeUTF8))
        self.refreshButton.setText(QtGui.QApplication.translate("MessageQueue", "Refresh", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
