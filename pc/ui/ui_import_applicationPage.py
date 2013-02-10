# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/import_applicationPage.ui'
#
# Created: Wed Nov 17 12:05:51 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_applicationPage(object):
    def setupUi(self, applicationPage):
        applicationPage.setObjectName("applicationPage")
        applicationPage.resize(500, 430)
        self.verticalLayout = QtGui.QVBoxLayout(applicationPage)
        self.verticalLayout.setSpacing(10)
        self.verticalLayout.setContentsMargins(10, 10, 10, 20)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(applicationPage)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtGui.QLabel(applicationPage)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.label_3 = QtGui.QLabel(applicationPage)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        spacerItem = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.label_4 = QtGui.QLabel(applicationPage)
        self.label_4.setWordWrap(True)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtGui.QSpacerItem(7, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.applicationList = QtGui.QListWidget(applicationPage)
        self.applicationList.setObjectName("applicationList")
        self.horizontalLayout.addWidget(self.applicationList)
        spacerItem2 = QtGui.QSpacerItem(7, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(applicationPage)
        QtCore.QMetaObject.connectSlotsByName(applicationPage)

    def retranslateUi(self, applicationPage):
        self.label.setText(QtGui.QApplication.translate("applicationPage", "Step 1: Select application", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("applicationPage", "Welcome to the Import Tool!", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("applicationPage", "This program will help you import your messages from your previous messaging program into Series60-Remote.", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("applicationPage", "Please select the program you would like to import from and then click <i>Next</i>:", None, QtGui.QApplication.UnicodeUTF8))

