# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widget.ChatWidget import ChatWidget
from window.chat_mainwindow import ChatMainWindow
from window.chat_tabwindow import ChatTabWindow
from lib.classes import *

class ChatManager(QObject):
    def __init__(self,  parent,  main):
        super(ChatManager,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.connection = main.connection
        self.log = main.log
        self.settings = main.settings
        self.helper = main.helper

        self.activeChatWidgets = dict()
        self.chatTabWindow = None
        self.statusBar = None

        self.__tabbedChat = self.settings.setting("windows/chat/tabbedChat")

        self.connect(main, SIGNAL("messageNew"),  self.newMessage)

    def newMessage(self,  msg):
        msg.setPriority(MessagePriority.Medium)

        if msg.contact().id() not in self.activeChatWidgets:
            return

        widget = self.activeChatWidgets[msg.contact().id()]
        widget.showMessage(msg)
        self.highlightWidget(widget)

        if self.hasOpenChat(msg.contact()):
            self.main.unreadMessages.remove(msg)
            self.connection.setRead(msg)

    def openChat(self,  contact):
        # Only one chat window for each contact
        if contact.id() in self.activeChatWidgets:
            self.showContact(contact)
            return

        if self.__tabbedChat:
            self.checkTabWindow()
            widget = ChatWidget(self.chatTabWindow,  self.main,  contact)
            self.activeChatWidgets[contact.id()] = widget
            widget.statusBar.setSizeGripEnabled(False)
            index = self.chatTabWindow.tabWidget.addTab(widget,  contact.name())
            self.chatTabWindow.tabWidget.setCurrentIndex(index)
            self.chatTabWindow.raise_()
            self.chatTabWindow.activateWindow()
        else:
            chatMain = ChatMainWindow(self)
            chatMain.setWindowTitle(contact.name() + " - Series60-Remote")
            widget = ChatWidget(chatMain,  self.main,  contact)
            chatMain.setStatusBar(widget.statusBar)
            chatMain.setCentralWidget(widget)

        # Create an entry in the list of open chats with the current windget
        self.activeChatWidgets[contact.id()] = widget

    def hasOpenChat(self,  contact):
        if self.__tabbedChat:
            return self.chatTabWindow is not None and self.chatTabWindow.tabWidget.currentWidget().contact == contact
        else:
            return contact.id() in self.activeChatWidgets

    def checkTabWindow(self):
        # This function is only called if the chats are displayed in a QTabWidget

        if self.chatTabWindow is not None:
            # We already have a chat window
            return

        self.chatTabWindow = ChatTabWindow(self)
        self.connect(self.chatTabWindow.tabWidget,  SIGNAL("tabCloseRequested(int)"),  self.closeTab)
        self.connect(self.chatTabWindow.tabWidget,  SIGNAL("currentChanged(int)"),  self.updateTab)

    def updateTab(self,  index):
        # This function is only called if the chats are displayed in a QTabWidget
        widget = self.chatTabWindow.tabWidget.widget(index)
        if widget is None:
            return
        contact = widget.contact

        self.chatTabWindow.setWindowTitle(contact.name() + " - Series60-Remote")
        self.chatTabWindow.tabWidget.tabBar().setTabTextColor(index,  QColor())

        widget.messageText.setFocus()

        for msg in self.main.unreadMessages:
            if msg.contact() == contact:
                self.main.unreadMessages.remove(msg)
                self.connection.setRead(msg)

    def showContact(self,  contact):
        widget = self.activeChatWidgets[contact.id()]
        self.showWidget(widget)

    def showWidget(self,  widget):
        if self.__tabbedChat:
            self.chatTabWindow.tabWidget.setCurrentWidget(widget)
            self.chatTabWindow.raise_()
            self.chatTabWindow.activateWindow()
        else:
            widget.parent.raise_()
            widget.parent.activateWindow()

    def highlightContact(self,  contact):
        widget = self.activeChatWidgets[contact.id()]
        self.highlightWidget(widget)

    def highlightWidget(self,  widget):
        if self.__tabbedChat:
            self.main.app.alert(self.chatTabWindow)
            if widget == self.chatTabWindow.tabWidget.currentWidget():
                return
            index = self.chatTabWindow.tabWidget.indexOf(widget)
            self.chatTabWindow.tabWidget.tabBar().setTabTextColor(index,  QColor(Qt.darkRed))
        else:
            self.main.app.alert(widget.parent)

    def closeChat(self,  contact):
        widget = self.activeChatWidgets[contact.id()]
        del self.activeChatWidgets[contact.id()]

        if self.__tabbedChat:
            index = self.chatTabWindow.tabWidget.indexOf(widget)
            self.chatTabWindow.tabWidget.removeTab(index)
        else:
            widget.parent.close()

    def closeAllChats(self):
        # This function is only called if the chats are displayed in a QTabWidget
        for num in xrange(self.chatTabWindow.tabWidget.count()):
            widget = self.chatTabWindow.tabWidget.widget(num)
            if widget is not None:
                self.closeChat(widget.contact)

        self.chatTabWindow = None

    def closeTab(self,  index):
        # This function is only called if the chats are displayed in a QTabWidget
        widget = self.chatTabWindow.tabWidget.widget(index)
        contact = widget.contact

        self.settings.setSetting("windows/chat/splitter", widget.splitter.saveState())
        self.closeChat(contact)

        if self.chatTabWindow.tabWidget.count() == 0:
            self.chatTabWindow.close()
