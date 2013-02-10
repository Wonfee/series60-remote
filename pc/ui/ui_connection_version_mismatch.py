# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/connection_version_mismatch.ui'
#
# Created: Wed Nov 17 12:05:58 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ConnectionVersionMismatchDialog(object):
    def setupUi(self, ConnectionVersionMismatchDialog):
        ConnectionVersionMismatchDialog.setObjectName("ConnectionVersionMismatchDialog")
        ConnectionVersionMismatchDialog.resize(501, 235)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/dialog-cancel"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ConnectionVersionMismatchDialog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(ConnectionVersionMismatchDialog)
        self.verticalLayout.setMargin(15)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(ConnectionVersionMismatchDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_2 = QtGui.QLabel(ConnectionVersionMismatchDialog)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.mobileVersionLabel = QtGui.QLabel(ConnectionVersionMismatchDialog)
        self.mobileVersionLabel.setText("unknown")
        self.mobileVersionLabel.setObjectName("mobileVersionLabel")
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.mobileVersionLabel)
        self.label_3 = QtGui.QLabel(ConnectionVersionMismatchDialog)
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_3)
        self.pcVersionLabel = QtGui.QLabel(ConnectionVersionMismatchDialog)
        self.pcVersionLabel.setText("unknown")
        self.pcVersionLabel.setObjectName("pcVersionLabel")
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.pcVersionLabel)
        self.verticalLayout.addLayout(self.formLayout)
        self.label_4 = QtGui.QLabel(ConnectionVersionMismatchDialog)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.updateButton = QtGui.QPushButton(ConnectionVersionMismatchDialog)
        self.updateButton.setObjectName("updateButton")
        self.horizontalLayout.addWidget(self.updateButton)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(ConnectionVersionMismatchDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ConnectionVersionMismatchDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ConnectionVersionMismatchDialog.reject)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ConnectionVersionMismatchDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(ConnectionVersionMismatchDialog)

    def retranslateUi(self, ConnectionVersionMismatchDialog):
        ConnectionVersionMismatchDialog.setWindowTitle(QtGui.QApplication.translate("ConnectionVersionMismatchDialog", "Version mismatch", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ConnectionVersionMismatchDialog", "The version of the <i>S60 Remote service</i> on your mobile phone isn\'t compatible with the version of your PC client.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ConnectionVersionMismatchDialog", "Mobile phone version:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("ConnectionVersionMismatchDialog", "PC version:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("ConnectionVersionMismatchDialog", "Please update the <i>S60 Remote service</i>.", None, QtGui.QApplication.UnicodeUTF8))
        self.updateButton.setText(QtGui.QApplication.translate("ConnectionVersionMismatchDialog", "Update S60 Remote service", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
