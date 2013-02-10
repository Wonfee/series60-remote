# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_messageQueue
from lib.classes import *
from devices.series60 import NotConnectedError

class MessageQueue(QDialog,  ui.ui_messageQueue.Ui_MessageQueue):
    def __init__(self, parent, main):
        super(MessageQueue,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)
        main.setupButtonBox(self.buttonBox)

        self.empty = True

        self.connect(self.main.connection,  SIGNAL("messageQueued"),  self.addMessage)
        self.connect(self.refreshBox,  SIGNAL("toogled(bool)"),  self.refreshBoxChanged)
        self.connect(self.refreshButton,  SIGNAL("clicked()"),  self.refresh)

        self.show()
        self.refresh()

    def refreshBoxChanged(self,  state):
        if state:
            self.connect(self.main.connection,  SIGNAL("messageQueued"),  self.addMessage)
            for i in range(self.messageTree.topLevelItemCount()):
                item = self.messageTree.topLevelItem(i)
                msg = item.data(0).toPyObject()
                self.connect(msg,  SIGNAL("messageStateAdded"),  self.addedState)
        else:
            self.disconnect(self.main.connection,  SIGNAL("messageQueued"),  self.addMessage)
            for i in range(self.messageTree.topLevelItemCount()):
                item = self.messageTree.topLevelItem(i)
                msg = item.data(0).toPyObject()
                self.disconnect(msg,  SIGNAL("messageStateAdded"),  self.addedState)

    def refresh(self):
        self.messageTree.clear()

        try:
            queue = self.main.connection.sentMessages() + self.main.connection.pendingMessages()
        except NotConnectedError:
            item = QTreeWidgetItem(self.messageTree)
            item.setText(0, self.tr("No active connection"))
            item.setIcon(0,  QIcon(":/dialog-close"))
            item.setFirstColumnSpanned(True)
            return

        if not queue:
            item = QTreeWidgetItem(self.messageTree)
            item.setText(0, self.tr("No messages in queue"))
            item.setIcon(0,  QIcon(":/dialog-close"))
            item.setFirstColumnSpanned(True)
            self.messageTree.addTopLevelItem(item)
            return

        for message in queue:
            self.addMessage(message)

    def addMessage(self,  message):
        if self.empty:
            self.messageTree.clear()
        
        name = message.contact().name()
        phone = message.contact().internalValue("phone")
        msg = message.message().replace("\n",  " ")
        if len(msg) > 60:
            msg = msg[:57] + "..."

        messageItem = QTreeWidgetItem(self.messageTree)
        messageItem.setData(0,  Roles.MessageRole, QVariant(message))
        messageItem.setText(0,  QString("%1 (%2): %3").arg(name,  phone,  msg))
        messageItem.setFirstColumnSpanned(True)
        
        if self.refreshBox.checkState() == Qt.Checked:
            self.connect(message,  SIGNAL("messageStateAdded"),  self.addedState)

        for stateList in message.states():
            self.addState(messageItem,  stateList)
            
        if self.empty:
            item = self.messageTree.topLevelItem(0)
            if item:
                self.messageTree.setAnimated(False)
                self.messageTree.expandItem(item)
            self.messageTree.resizeColumnToContents(0)
            self.messageTree.resizeColumnToContents(1)
            if item:
                self.messageTree.collapseItem(item)
                self.messageTree.setAnimated(True)
            self.empty = False

    def addedState(self,  message,  stateList):
        for i in range(self.messageTree.topLevelItemCount()):
            item = self.messageTree.topLevelItem(i)
            msg = item.data(0,  Roles.MessageRole).toPyObject()
            if msg == message:
                self.addState(item,  stateList)
                break

    def addState(self,  messageItem,  stateList):
        datetime = stateList[0]
        state = stateList[1]
        stateMessage = stateList[2]

        message = messageItem.data(0,  Roles.MessageRole).toPyObject()
        stateItem = QTreeWidgetItem(messageItem)
        stateItem.setText(1,  str(datetime.time().toString()))
        stateItem.setText(2,  stateMessage)
        if state == MessageState.Pending or state == MessageState.Created:
            stateItem.setIcon(0,  QIcon(":/wait")) 
        elif state == MessageState.Sending:
            stateItem.setIcon(0,  QIcon(":/go-next"))
        elif state == MessageState.SendOk:
            stateItem.setIcon(0,  QIcon(":/dialog-apply"))  # Okay/Accept icon
        elif state == MessageState.SendFailed:
            stateItem.setIcon(0,  QIcon(":/dialog-close")) # FIXME: Find a better icon...
        # Don't show an icon otherwise.. Should look better ;)
        #else:
        #    stateItem.setIcon(0,  QIcon(":/dialog-information")) # FIXME: Find a better icon...
        
        if message.states().pending() or message.states().created():
            messageItem.setIcon(0,  QIcon(":/wait")) 
        elif message.states().sending(): 
            messageItem.setIcon(0,  QIcon(":/go-next"))
        elif message.states().sendOk():
            messageItem.setIcon(0,  QIcon(":/dialog-apply"))  # Okay/Accept icon
        elif message.states().sendFailed():
            messageItem.setIcon(0,  QIcon(":/dialog-close")) # FIXME: Find a better icon...
        else:
            messageItem.setIcon(0,  QIcon(":/dialog-information")) # FIXME: Find a better icon...
