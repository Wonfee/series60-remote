# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/mobileNumberSelect.ui'
#
# Created: Wed Nov 17 12:06:02 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MobileNumberSelectDialog(object):
    def setupUi(self, MobileNumberSelectDialog):
        MobileNumberSelectDialog.setObjectName("MobileNumberSelectDialog")
        MobileNumberSelectDialog.resize(400, 170)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/phone"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MobileNumberSelectDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(MobileNumberSelectDialog)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setMargin(15)
        self.verticalLayout.setObjectName("verticalLayout")
        self.contactLabel = QtGui.QLabel(MobileNumberSelectDialog)
        self.contactLabel.setText("")
        self.contactLabel.setObjectName("contactLabel")
        self.verticalLayout.addWidget(self.contactLabel)
        self.mobileBox = QtGui.QComboBox(MobileNumberSelectDialog)
        self.mobileBox.setObjectName("mobileBox")
        self.verticalLayout.addWidget(self.mobileBox)
        self.standardBox = QtGui.QCheckBox(MobileNumberSelectDialog)
        self.standardBox.setEnabled(False)
        self.standardBox.setObjectName("standardBox")
        self.verticalLayout.addWidget(self.standardBox)
        self.buttonBox = QtGui.QDialogButtonBox(MobileNumberSelectDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(MobileNumberSelectDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), MobileNumberSelectDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), MobileNumberSelectDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MobileNumberSelectDialog)

    def retranslateUi(self, MobileNumberSelectDialog):
        MobileNumberSelectDialog.setWindowTitle(QtGui.QApplication.translate("MobileNumberSelectDialog", "Select telephone number", None, QtGui.QApplication.UnicodeUTF8))
        self.standardBox.setText(QtGui.QApplication.translate("MobileNumberSelectDialog", "As standard", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
