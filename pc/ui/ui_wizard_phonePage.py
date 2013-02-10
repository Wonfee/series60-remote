# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/wizard_phonePage.ui'
#
# Created: Wed Nov 17 12:05:53 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_phonePage(object):
    def setupUi(self, phonePage):
        phonePage.setObjectName("phonePage")
        phonePage.resize(590, 380)
        phonePage.setMinimumSize(QtCore.QSize(590, 380))
        self.verticalLayout = QtGui.QVBoxLayout(phonePage)
        self.verticalLayout.setContentsMargins(10, 10, 10, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(phonePage)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(558, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.devicesView = DeviceScanWidget(phonePage)
        self.devicesView.setObjectName("devicesView")
        self.verticalLayout.addWidget(self.devicesView)

        self.retranslateUi(phonePage)
        QtCore.QMetaObject.connectSlotsByName(phonePage)

    def retranslateUi(self, phonePage):
        self.label.setText(QtGui.QApplication.translate("phonePage", "Turn on bluetooth on your mobile phone and select the appropriate device:\n"
"\n"
"You don\'t need to choose one, you can configure it afterwards in the settings.", None, QtGui.QApplication.UnicodeUTF8))

from widget.DeviceWidget import DeviceScanWidget
