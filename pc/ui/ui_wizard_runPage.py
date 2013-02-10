# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/wizard_runPage.ui'
#
# Created: Wed Nov 17 12:05:50 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_runPage(object):
    def setupUi(self, runPage):
        runPage.setObjectName("runPage")
        runPage.resize(590, 380)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(runPage.sizePolicy().hasHeightForWidth())
        runPage.setSizePolicy(sizePolicy)
        runPage.setMinimumSize(QtCore.QSize(590, 380))
        self.horizontalLayout = QtGui.QHBoxLayout(runPage)
        self.horizontalLayout.setSpacing(20)
        self.horizontalLayout.setContentsMargins(15, 10, 20, 10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtGui.QLabel(runPage)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(201, 360))
        self.label.setMaximumSize(QtCore.QSize(201, 360))
        self.label.setPixmap(QtGui.QPixmap(":/mobile-1"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.label_2 = QtGui.QLabel(runPage)
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

        self.retranslateUi(runPage)
        QtCore.QMetaObject.connectSlotsByName(runPage)

    def retranslateUi(self, runPage):
        self.label_2.setText(QtGui.QApplication.translate("runPage", "<p align=\"justify\">At first complete the installation of the application on your mobile phone.<br />\n"
"<br />\n"
"Afterwards start the application. It should be located in the \"Applications\" menu and named \"S60-Remote\".</p>", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
