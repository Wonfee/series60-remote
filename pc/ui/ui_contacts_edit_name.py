# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/contacts_edit_name.ui'
#
# Created: Wed Nov 17 12:05:57 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ContactsEditName(object):
    def setupUi(self, ContactsEditName):
        ContactsEditName.setObjectName("ContactsEditName")
        ContactsEditName.setWindowModality(QtCore.Qt.WindowModal)
        ContactsEditName.resize(338, 215)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/contacts"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ContactsEditName.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ContactsEditName)
        self.verticalLayout.setSpacing(6)
        self.verticalLayout.setMargin(10)
        self.verticalLayout.setObjectName("verticalLayout")
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.title_label = QtGui.QLabel(ContactsEditName)
        self.title_label.setText("Title:")
        self.title_label.setObjectName("title_label")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.title_label)
        self.title = QtGui.QLineEdit(ContactsEditName)
        self.title.setObjectName("title")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.title)
        self.first_name_label = QtGui.QLabel(ContactsEditName)
        self.first_name_label.setText("First name:")
        self.first_name_label.setObjectName("first_name_label")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.first_name_label)
        self.first_name = QtGui.QLineEdit(ContactsEditName)
        self.first_name.setObjectName("first_name")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.first_name)
        self.last_name = QtGui.QLineEdit(ContactsEditName)
        self.last_name.setObjectName("last_name")
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.last_name)
        self.suffix_label = QtGui.QLabel(ContactsEditName)
        self.suffix_label.setText("Suffix:")
        self.suffix_label.setObjectName("suffix_label")
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.suffix_label)
        self.suffix = QtGui.QLineEdit(ContactsEditName)
        self.suffix.setObjectName("suffix")
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.suffix)
        self.last_name_label = QtGui.QLabel(ContactsEditName)
        self.last_name_label.setText("Last name:")
        self.last_name_label.setObjectName("last_name_label")
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.last_name_label)
        self.verticalLayout.addLayout(self.formLayout)
        self.buttonBox = QtGui.QDialogButtonBox(ContactsEditName)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.title_label.setBuddy(self.title)
        self.first_name_label.setBuddy(self.first_name)
        self.suffix_label.setBuddy(self.suffix)
        self.last_name_label.setBuddy(self.last_name)

        self.retranslateUi(ContactsEditName)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ContactsEditName.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ContactsEditName.reject)
        QtCore.QMetaObject.connectSlotsByName(ContactsEditName)

    def retranslateUi(self, ContactsEditName):
        ContactsEditName.setWindowTitle(QtGui.QApplication.translate("ContactsEditName", "Edit contact name", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
