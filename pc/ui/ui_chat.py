# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/src/chat.ui'
#
# Created: Wed Nov 17 12:05:55 2010
#      by: PyQt4 UI code generator 4.7.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_Chat(object):
    def setupUi(self, Chat):
        Chat.setObjectName("Chat")
        Chat.resize(683, 508)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/phone"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Chat.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(Chat)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtGui.QSplitter(Chat)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.frame = QtGui.QFrame(self.splitter)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Sunken)
        self.frame.setObjectName("frame")
        self.verticalLayout_19 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_19.setSpacing(0)
        self.verticalLayout_19.setMargin(0)
        self.verticalLayout_19.setObjectName("verticalLayout_19")
        self.messagesView = ChatMessageView(self.frame)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.messagesView.sizePolicy().hasHeightForWidth())
        self.messagesView.setSizePolicy(sizePolicy)
        self.messagesView.setFocusPolicy(QtCore.Qt.NoFocus)
        self.messagesView.setRenderHints(QtGui.QPainter.Antialiasing|QtGui.QPainter.HighQualityAntialiasing|QtGui.QPainter.SmoothPixmapTransform|QtGui.QPainter.TextAntialiasing)
        self.messagesView.setObjectName("messagesView")
        self.verticalLayout_19.addWidget(self.messagesView)
        self.messageText = MessageTextEdit(self.splitter)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.messageText.sizePolicy().hasHeightForWidth())
        self.messageText.setSizePolicy(sizePolicy)
        self.messageText.setObjectName("messageText")
        self.verticalLayout.addWidget(self.splitter)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.sendButton = QtGui.QPushButton(Chat)
        self.sendButton.setObjectName("sendButton")
        self.horizontalLayout.addWidget(self.sendButton)
        spacerItem = QtGui.QSpacerItem(258, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.charLabel = QtGui.QLabel(Chat)
        self.charLabel.setObjectName("charLabel")
        self.horizontalLayout.addWidget(self.charLabel)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.statusBar = QtGui.QStatusBar(Chat)
        self.statusBar.setObjectName("statusBar")
        self.verticalLayout.addWidget(self.statusBar)

        self.retranslateUi(Chat)
        QtCore.QMetaObject.connectSlotsByName(Chat)

    def retranslateUi(self, Chat):
        Chat.setWindowTitle(QtGui.QApplication.translate("Chat", "Chat", None, QtGui.QApplication.UnicodeUTF8))
        self.sendButton.setText(QtGui.QApplication.translate("Chat", "Send", None, QtGui.QApplication.UnicodeUTF8))
        self.sendButton.setShortcut(QtGui.QApplication.translate("Chat", "Ctrl+S", None, QtGui.QApplication.UnicodeUTF8))
        self.charLabel.setText(QtGui.QApplication.translate("Chat", "160 chars left; 1 message", None, QtGui.QApplication.UnicodeUTF8))

from widget.MessageTextEdit import MessageTextEdit
from widget.ChatMessageView import ChatMessageView
import resource_rc
