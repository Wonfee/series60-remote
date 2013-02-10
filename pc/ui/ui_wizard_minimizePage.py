# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/wizard_minimizePage.ui'
#
# Created: Wed Nov 17 12:06:00 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_minimizePage(object):
    def setupUi(self, minimizePage):
        minimizePage.setObjectName("minimizePage")
        minimizePage.resize(590, 380)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(minimizePage.sizePolicy().hasHeightForWidth())
        minimizePage.setSizePolicy(sizePolicy)
        minimizePage.setMinimumSize(QtCore.QSize(590, 380))
        self.horizontalLayout = QtGui.QHBoxLayout(minimizePage)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setContentsMargins(15, 10, 20, 10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(minimizePage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(201, 360))
        self.label.setMaximumSize(QtCore.QSize(201, 360))
        self.label.setPixmap(QtGui.QPixmap(":/mobile-2"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(minimizePage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setScaledContents(False)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(minimizePage)
        QtCore.QMetaObject.connectSlotsByName(minimizePage)

    def retranslateUi(self, minimizePage):
        self.label_2.setText(QtGui.QApplication.translate("minimizePage", "<p align=\"justify\">There is currently no easy way to minimize the application.<br />\n"
"<br />\n"
"The best way is to press the press the menu key for some seconds. When the application switcher appears select \"Standby\".<br />\n"
"<br />\n"
"I\'m working on a better solution. In a future version the \"Exit\" button will get replaced by a \"Hide\" button.", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
