# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/export_progress.ui'
#
# Created: Wed Nov 17 12:05:56 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_ExportProgress(object):
    def setupUi(self, ExportProgress):
        ExportProgress.setObjectName("ExportProgress")
        ExportProgress.resize(414, 460)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/document-export"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ExportProgress.setWindowIcon(icon)
        self.verticalLayout_5 = QtGui.QVBoxLayout(ExportProgress)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label = QtGui.QLabel(ExportProgress)
        font = QtGui.QFont()
        font.setPointSize(11)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout_5.addWidget(self.label)
        self.messagesWidget = QtGui.QWidget(ExportProgress)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.messagesWidget.sizePolicy().hasHeightForWidth())
        self.messagesWidget.setSizePolicy(sizePolicy)
        self.messagesWidget.setObjectName("messagesWidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.messagesWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtGui.QLabel(self.messagesWidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.messageProgress = QtGui.QProgressBar(self.messagesWidget)
        self.messageProgress.setProperty("value", 0)
        self.messageProgress.setObjectName("messageProgress")
        self.horizontalLayout_2.addWidget(self.messageProgress)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.messageCount = QtGui.QLabel(self.messagesWidget)
        self.messageCount.setText("0 / 0")
        self.messageCount.setObjectName("messageCount")
        self.horizontalLayout.addWidget(self.messageCount)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_5.addWidget(self.messagesWidget)
        self.createCalendarWidget = QtGui.QWidget(ExportProgress)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.createCalendarWidget.sizePolicy().hasHeightForWidth())
        self.createCalendarWidget.setSizePolicy(sizePolicy)
        self.createCalendarWidget.setObjectName("createCalendarWidget")
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.createCalendarWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.createCalendarLabel = QtGui.QLabel(self.createCalendarWidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.createCalendarLabel.setFont(font)
        self.createCalendarLabel.setObjectName("createCalendarLabel")
        self.verticalLayout_2.addWidget(self.createCalendarLabel)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.calendarProgress = QtGui.QProgressBar(self.createCalendarWidget)
        self.calendarProgress.setProperty("value", 0)
        self.calendarProgress.setObjectName("calendarProgress")
        self.horizontalLayout_3.addWidget(self.calendarProgress)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        spacerItem3 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem3)
        self.calendarCount = QtGui.QLabel(self.createCalendarWidget)
        self.calendarCount.setText("0 / 0")
        self.calendarCount.setObjectName("calendarCount")
        self.horizontalLayout_4.addWidget(self.calendarCount)
        self.verticalLayout_2.addLayout(self.horizontalLayout_4)
        self.verticalLayout_5.addWidget(self.createCalendarWidget)
        self.contactWidget = QtGui.QWidget(ExportProgress)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.contactWidget.sizePolicy().hasHeightForWidth())
        self.contactWidget.setSizePolicy(sizePolicy)
        self.contactWidget.setObjectName("contactWidget")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.contactWidget)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.contactLabel = QtGui.QLabel(self.contactWidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.contactLabel.setFont(font)
        self.contactLabel.setObjectName("contactLabel")
        self.verticalLayout_3.addWidget(self.contactLabel)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        spacerItem4 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem4)
        self.contactProgress = QtGui.QProgressBar(self.contactWidget)
        self.contactProgress.setProperty("value", 0)
        self.contactProgress.setObjectName("contactProgress")
        self.horizontalLayout_5.addWidget(self.contactProgress)
        self.verticalLayout_3.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        spacerItem5 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem5)
        self.contactCount = QtGui.QLabel(self.contactWidget)
        self.contactCount.setText("0 / 0")
        self.contactCount.setObjectName("contactCount")
        self.horizontalLayout_6.addWidget(self.contactCount)
        self.verticalLayout_3.addLayout(self.horizontalLayout_6)
        self.verticalLayout_5.addWidget(self.contactWidget)
        self.calendarWidget = QtGui.QWidget(ExportProgress)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendarWidget.sizePolicy().hasHeightForWidth())
        self.calendarWidget.setSizePolicy(sizePolicy)
        self.calendarWidget.setObjectName("calendarWidget")
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.calendarWidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.calendarLabel = QtGui.QLabel(self.calendarWidget)
        font = QtGui.QFont()
        font.setWeight(75)
        font.setBold(True)
        self.calendarLabel.setFont(font)
        self.calendarLabel.setObjectName("calendarLabel")
        self.verticalLayout_4.addWidget(self.calendarLabel)
        self.horizontalLayout_7 = QtGui.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        spacerItem6 = QtGui.QSpacerItem(20, 20, QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem6)
        self.calemdarProgress = QtGui.QProgressBar(self.calendarWidget)
        self.calemdarProgress.setProperty("value", 0)
        self.calemdarProgress.setObjectName("calemdarProgress")
        self.horizontalLayout_7.addWidget(self.calemdarProgress)
        self.verticalLayout_4.addLayout(self.horizontalLayout_7)
        self.horizontalLayout_8 = QtGui.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        spacerItem7 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem7)
        self.calendarCount_2 = QtGui.QLabel(self.calendarWidget)
        self.calendarCount_2.setText("0 / 0")
        self.calendarCount_2.setObjectName("calendarCount_2")
        self.horizontalLayout_8.addWidget(self.calendarCount_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_8)
        self.verticalLayout_5.addWidget(self.calendarWidget)
        spacerItem8 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem8)
        self.horizontalLayout_9 = QtGui.QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.label_5 = QtGui.QLabel(ExportProgress)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout_9.addWidget(self.label_5)
        self.fileLabel = QtGui.QLabel(ExportProgress)
        font = QtGui.QFont()
        font.setItalic(True)
        self.fileLabel.setFont(font)
        self.fileLabel.setObjectName("fileLabel")
        self.horizontalLayout_9.addWidget(self.fileLabel)
        self.fileExtensionLabel = QtGui.QLabel(ExportProgress)
        self.fileExtensionLabel.setText("")
        self.fileExtensionLabel.setObjectName("fileExtensionLabel")
        self.horizontalLayout_9.addWidget(self.fileExtensionLabel)
        spacerItem9 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_9.addItem(spacerItem9)
        self.verticalLayout_5.addLayout(self.horizontalLayout_9)
        self.buttonBox = QtGui.QDialogButtonBox(ExportProgress)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Abort|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_5.addWidget(self.buttonBox)

        self.retranslateUi(ExportProgress)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ExportProgress.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ExportProgress.reject)
        QtCore.QMetaObject.connectSlotsByName(ExportProgress)

    def retranslateUi(self, ExportProgress):
        ExportProgress.setWindowTitle(QtGui.QApplication.translate("ExportProgress", "Export progress", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ExportProgress", "Progress of messages and contact export", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ExportProgress", "Exporting messages...", None, QtGui.QApplication.UnicodeUTF8))
        self.createCalendarLabel.setText(QtGui.QApplication.translate("ExportProgress", "Create calendar...", None, QtGui.QApplication.UnicodeUTF8))
        self.contactLabel.setText(QtGui.QApplication.translate("ExportProgress", "Exporting contacts...", None, QtGui.QApplication.UnicodeUTF8))
        self.calendarLabel.setText(QtGui.QApplication.translate("ExportProgress", "Exporting calendar...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("ExportProgress", "Writing to:", None, QtGui.QApplication.UnicodeUTF8))
        self.fileLabel.setText(QtGui.QApplication.translate("ExportProgress", "unknown", None, QtGui.QApplication.UnicodeUTF8))

import resource_rc
