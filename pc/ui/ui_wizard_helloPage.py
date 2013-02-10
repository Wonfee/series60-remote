# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/wizard_helloPage.ui'
#
# Created: Wed Nov 17 12:06:01 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_helloPage(object):
    def setupUi(self, helloPage):
        helloPage.setObjectName("helloPage")
        helloPage.resize(590, 380)
        helloPage.setMinimumSize(QtCore.QSize(590, 380))
        self.verticalLayout = QtGui.QVBoxLayout(helloPage)
        self.verticalLayout.setContentsMargins(25, 25, 25, -1)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(helloPage)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.previewWidget = QtGui.QWidget(helloPage)
        self.previewWidget.setObjectName("previewWidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.previewWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.line = QtGui.QFrame(self.previewWidget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.previewLabel = QtGui.QLabel(self.previewWidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(146, 145, 144))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        self.previewLabel.setPalette(palette)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.previewLabel.setFont(font)
        self.previewLabel.setWordWrap(True)
        self.previewLabel.setObjectName("previewLabel")
        self.verticalLayout_2.addWidget(self.previewLabel)
        self.verticalLayout.addWidget(self.previewWidget)

        self.retranslateUi(helloPage)
        QtCore.QMetaObject.connectSlotsByName(helloPage)

    def retranslateUi(self, helloPage):
        self.label.setText(QtGui.QApplication.translate("helloPage", "Hello,<br />\n"
"<br />\n"
"Welcome to your first run of Series60-Remote<br />\n"
"<br />\n"
"You can manage the following things with your mobile phone:<br />\n"
" - Send text messages<br />\n"
" - Store and read text messages<br />\n"
" - Add, edit and delete contacts<br />\n"
" - Browse the folders of your mobile phone<br />\n"
" - and much more<br />\n"
"<br />\n"
"<br />\n"
"On the following pages you go along your settings.<br />\n"
"Keep in mind that everything can be changed afterwards in <i>File - Settings</i>.", None, QtGui.QApplication.UnicodeUTF8))
        self.previewLabel.setText(QtGui.QApplication.translate("helloPage", "This is a preview release! Do not use it in production enviroments! Please report all bugs you can find!", None, QtGui.QApplication.UnicodeUTF8))

