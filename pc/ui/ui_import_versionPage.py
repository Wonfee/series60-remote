# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/import_versionPage.ui'
#
# Created: Wed Nov 17 12:05:55 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_versionPage(object):
    def setupUi(self, versionPage):
        versionPage.setObjectName("versionPage")
        versionPage.resize(500, 430)
        self.verticalLayout_2 = QtGui.QVBoxLayout(versionPage)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QtGui.QLabel(versionPage)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtGui.QLabel(versionPage)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.applicationName = QtGui.QLabel(versionPage)
        self.applicationName.setText("")
        self.applicationName.setObjectName("applicationName")
        self.verticalLayout.addWidget(self.applicationName)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        spacerItem = QtGui.QSpacerItem(20, 5, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout_2.addItem(spacerItem)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtGui.QSpacerItem(7, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.versionList = QtGui.QListWidget(versionPage)
        self.versionList.setObjectName("versionList")
        self.horizontalLayout.addWidget(self.versionList)
        spacerItem2 = QtGui.QSpacerItem(7, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem3 = QtGui.QSpacerItem(15, 10, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.notesLabel = QtGui.QLabel(versionPage)
        self.notesLabel.setText("")
        self.notesLabel.setObjectName("notesLabel")
        self.horizontalLayout_2.addWidget(self.notesLabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.retranslateUi(versionPage)
        QtCore.QMetaObject.connectSlotsByName(versionPage)

    def retranslateUi(self, versionPage):
        self.label.setText(QtGui.QApplication.translate("versionPage", "Step 2: Select application version", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("versionPage", "Please select the version of your requested application:", None, QtGui.QApplication.UnicodeUTF8))

