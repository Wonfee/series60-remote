# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/connection_failed.ui'
#
# Created: Wed Nov 17 12:05:51 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ConnectionFailedDialog(object):
    def setupUi(self, ConnectionFailedDialog):
        ConnectionFailedDialog.setObjectName("ConnectionFailedDialog")
        ConnectionFailedDialog.resize(511, 286)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/dialog-close"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ConnectionFailedDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ConnectionFailedDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(ConnectionFailedDialog)
        self.label.setTextFormat(QtCore.Qt.RichText)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_3 = QtGui.QLabel(ConnectionFailedDialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_4 = QtGui.QLabel(ConnectionFailedDialog)
        self.label_4.setObjectName("label_4")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_4)
        self.errnoLabel = QtGui.QLabel(ConnectionFailedDialog)
        self.errnoLabel.setText("unknown")
        self.errnoLabel.setObjectName("errnoLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.errnoLabel)
        self.label_5 = QtGui.QLabel(ConnectionFailedDialog)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_5)
        self.errmsgLabel = QtGui.QLabel(ConnectionFailedDialog)
        self.errmsgLabel.setText("unknown")
        self.errmsgLabel.setObjectName("errmsgLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.errmsgLabel)
        self.horizontalLayout_2.addLayout(self.formLayout)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem1 = QtGui.QSpacerItem(5, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem1)
        self.label_2 = QtGui.QLabel(ConnectionFailedDialog)
        self.label_2.setTextFormat(QtCore.Qt.RichText)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.reinstallButton = QtGui.QPushButton(ConnectionFailedDialog)
        self.reinstallButton.setObjectName("reinstallButton")
        self.horizontalLayout.addWidget(self.reinstallButton)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.buttonBox = QtGui.QDialogButtonBox(ConnectionFailedDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Retry)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ConnectionFailedDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ConnectionFailedDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ConnectionFailedDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ConnectionFailedDialog)

    def retranslateUi(self, ConnectionFailedDialog):
        ConnectionFailedDialog.setWindowTitle(QtGui.QApplication.translate("ConnectionFailedDialog", "Connection failed", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ConnectionFailedDialog", "The connection to the <i>S60 Remote Service</i> of your mobile phone failed.<br />", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ConnectionFailedDialog", "The following error was returned:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ConnectionFailedDialog", "Error number:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ConnectionFailedDialog", "Error message:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ConnectionFailedDialog", "Please make sure that you:\n"
"<ul><li>Enabled bluetooth on your mobile phone\n"
"<li>Installed the <i>S60 Remote Service</i>\n"
"<li>Started the <i>S60 Remote Service</i>\n"
"<li>and that your bluetooth mobile phone is within reach\n"
"<br />", None, QtGui.QApplication.UnicodeUTF8))
        self.reinstallButton.setText(QtGui.QApplication.translate("ConnectionFailedDialog", "Reinstall S60 Remote service", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
