# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/mobileNumberNotFound.ui'
#
# Created: Wed Nov 17 12:06:00 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MobileNumberNotFoundDialog(object):
    def setupUi(self, MobileNumberNotFoundDialog):
        MobileNumberNotFoundDialog.setObjectName("MobileNumberNotFoundDialog")
        MobileNumberNotFoundDialog.resize(566, 192)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/dialog-close"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MobileNumberNotFoundDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(MobileNumberNotFoundDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtGui.QLabel(MobileNumberNotFoundDialog)
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/dialog-close"))
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.label = QtGui.QLabel(MobileNumberNotFoundDialog)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(MobileNumberNotFoundDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(MobileNumberNotFoundDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), MobileNumberNotFoundDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), MobileNumberNotFoundDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MobileNumberNotFoundDialog)

    def retranslateUi(self, MobileNumberNotFoundDialog):
        MobileNumberNotFoundDialog.setWindowTitle(QtGui.QApplication.translate("MobileNumberNotFoundDialog", "No legal number found!", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MobileNumberNotFoundDialog", "No legal telephone number found!\n"
"\n"
"Legal numbers for the reciepent input mask:\n"
" - Only a number such as: 06641234567\n"
" - Name and number such as: John Q. Public (06641234567)\n"
" - Only a name (the name MUST be in the contact list!) such as: John Q. Public\n"
"\n"
"Multiple Entries are seperated by semicolons such as: 06641234567; John Q. Public (06769876543)", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
