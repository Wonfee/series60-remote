# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import copy
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_chat
import ui.ui_mobileNumberSelect
from lib.classes import *

class ChatWidget(QWidget,  ui.ui_chat.Ui_Chat):
    def __init__(self, parent, main, contact):
        super(ChatWidget,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)

        self.connect(self.sendButton, SIGNAL("clicked()"),  self.sendButtonClicked)
        self.connect(self.messageText, SIGNAL("sendMessage"),  self.sendButton,  SLOT("animateClick()"))
        self.connect(self.messageText,  SIGNAL("textChanged()"),  self.textChanged)
        self.connect(self.connection, SIGNAL("messageSent"),  self.messageStateChanged)
        self.connect(self.connection, SIGNAL("messageQueued"),  self.messageStateChanged)
        self.connect(self.connection, SIGNAL("messageQueued"),  self.sendSignal)
        self.connect(self.connection, SIGNAL("connectionCompleted"),  self.checkSendButton)
        self.connect(self.connection, SIGNAL("connectionClosed"),  self.checkSendButton)
        self.connect(self.settings,  SIGNAL("reloadSettings"),  self.loadSettings)
        self.connect(self.settings,  SIGNAL("chatThemeChanged"),  self.reloadTheme)

        # Destroy the window when it is closed
        # Otherwise all signals would be still connected - this causes wired problems
        self.setAttribute(Qt.WA_DeleteOnClose)

        chatSplitter = self.settings.setting("windows/chat/splitter")
        if not chatSplitter.isNull():
            self.splitter.restoreState(chatSplitter)

        self.contact = copy.deepcopy(contact)

        if "phone" in contact.internalValues():
            phone = contact.internalValue("phone")
        elif len(contact.value("mobile_number")) > 1:
            self.log.info(QString("Contact %1 has more then one mobile number.").arg(contact.name()))
            phone = self.askMobileNumber(contact)
            if phone == None:
                self.main.chatManager.closeChat(contact)
                return
        elif len(contact.value("mobile_number")) == 1:
            phone = contact.value("mobile_number")[0]
        elif re.match(r"^[+]{0,1}\d*$", contact.name()) != None:
            # name is a phone number
            phone = contact.name()
        else:
            self.log.info(QString("Contact %1 has no valid mobile number.").arg(contact.name()))

            dialog = QDialog(self)
            ml = QVBoxLayout(dialog)
            label = QLabel(self.tr("Please enter a valid mobile phone number:"),  dialog)
            lineedit = QLineEdit(dialog)
            validator = QRegExpValidator(QRegExp("\+?\d*"),  dialog)
            buttonbox = QDialogButtonBox(QDialogButtonBox.Ok,  Qt.Horizontal,  dialog)

            lineedit.setValidator(validator)
            ml.addWidget(label)
            ml.addWidget(lineedit)
            ml.addWidget(buttonbox)

            dialog.connect(buttonbox, SIGNAL("accepted()"), dialog.accept)

            dialog.exec_()

            phone = lineedit.text()

        self.contact.addInternalValue("phone",  phone)

        self.queueMessages = 0
        self.maxMessagePriority = MessagePriority.History

        if self.connection.connected():
            self.messagesView.init(contact,  self.connection.device())
        else:
            self.messagesView.init(contact,  self.database.devices().next())
        self.reloadTheme()

        self.messageText.setFocus()

        self.lastMessages()
        self.checkSendButton()
        self.loadSettings()

        self.main.emit(SIGNAL("chatOpened"),  contact)

    def loadSettings(self):
        self.messageText.setSendMessageOnReturn(self.settings.setting("general/sendMessageOnReturn"))

    def reloadTheme(self):
        theme = self.settings.setting("windows/chat/theme/name")
        variant = self.settings.setting("windows/chat/theme/variant")
        groupMessages = self.settings.setting("windows/chat/theme/groupMessages")
        compact = self.settings.setting("windows/chat/theme/compact")
        self.messagesView.setStyleName(theme,  variant,  groupMessages,  compact)

    def lastMessages(self):
        messageList = self.database.messagesLast(self.contact,  self.settings.setting("messages/displayLast"))

        for msg in self.main.unreadMessages:
            if msg.contact() == self.contact and msg not in messageList:
                messageList.append(msg)

        for msg in messageList:
            if msg in self.main.unreadMessages:
                msg.setPriority(MessagePriority.Medium)
                self.main.unreadMessages.remove(msg)
                self.connection.setRead(msg,  send=self.settings.setting("messages/markAsRead"))
            else:
                msg.setPriority(MessagePriority.History)
            self.showMessage(msg)

    def askMobileNumber(self,  contact):
        dlg = QDialog(self)
        dialog = ui.ui_mobileNumberSelect.Ui_MobileNumberSelectDialog()
        dialog.setupUi(dlg)
        self.main.setupButtonBox(dialog.buttonBox)
        dialog.contactLabel.setText(self.trUtf8("Please choose the telephone number for contact <i>%1</i>:").arg(contact.name()))
        for number in contact.value("mobile_number"):
            dialog.mobileBox.addItem(number)

        if not dlg.exec_():
            return None

        return str(dialog.mobileBox.currentText())

    def sendButtonClicked(self):
        message = unicode(self.messageText.toPlainText())
        msg = Message()
        msg.setType(MessageType.Outgoing)
        msg.setDevice(self.connection.device())
        msg.setContact(self.contact)
        msg.setDateTime(QDateTime.currentDateTime())
        msg.setMessage(message)

        self.connection.sendMessage(msg)
        self.messageText.clear()
        self.messageText.setFocus()

    def textChanged(self):
        len = int(self.messageText.toPlainText().length())
        chars,  messages = self.helper.countMessages(len)
        self.charLabel.setText(self.tr("%1 chars left; %n message(s)",  "",  messages).arg(chars))

        self.checkSendButton()

    def sendSignal(self,  msg):
        if msg.contact() != self.contact:
            return

        msg.setPriority(MessagePriority.Medium)
        name = msg.device().name()
        self.showMessage(msg)

    def showMessage(self,  msg, history = False):
        # Append the message to the view, everything else is handled there...
        self.messagesView.appendMessage(msg)

    def messageStateChanged(self,  message):
        queue = self.connection.pendingMessages()

        num = 0
        for message in queue:
            if message.contact() == self.contact:
                num += 1

        time = QTime().currentTime().toString()
        if num >= 1:
            self.statusBar.showMessage(self.tr("[%1] %n message(s) in queue",  "",  num).arg(time))
        elif num == 0 and self.queueMessages > 0:
            self.statusBar.showMessage(self.tr("[%1] All messages were sent").arg(time),  5000)

        self.queueMessages = num

    def checkSendButton(self,  dummy=None):
        if self.messageText.toPlainText() and self.connection.connected():
            self.sendButton.setEnabled(True)
        else:
            self.sendButton.setEnabled(False)
