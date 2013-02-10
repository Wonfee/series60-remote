# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import time
import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import window.favorites
import lib.favorites
from lib.classes import *

class TrayIcon(QSystemTrayIcon):
    def __init__(self,  parent,  main):
        super(TrayIcon,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.menu = QMenu(self.parent)
        self.favMenu = lib.favorites.FavoriteMenu(self.menu,  main)
        self.dblClickTimer = QTimer()
        self.dblClickTimer.setSingleShot(True)
        self.ignoreNextRelease = False

        self.addMenu()
        self.setContextMenu(self.menu)

        self.connect(self,  SIGNAL("activated(QSystemTrayIcon::ActivationReason)"),  self.clicked)

        # Update favorite list
        self.connect(main,  SIGNAL("favoriteListChanged"),  self.addMenu)

        # Update unread message list
        self.connect(main,  SIGNAL("messageNew"),  self.newMessage)
        self.connect(main,  SIGNAL("ignoreListChanged"),  self.addMenu)
        self.connect(main,  SIGNAL("messageUnread"),  self.newMessage)
        self.connect(main,  SIGNAL("chatOpened"),  self.addMenu)
        self.connect(self.connection,  SIGNAL("messageRead"),  self.addMenu)

        self.connect(self.dblClickTimer,  SIGNAL("timeout()"),  self.emitClicked)
        self.connect(self.menu,  SIGNAL("triggered(QAction *)"),  self.contextMenuTriggered)

        self.setIcon(QIcon(":/phone"))
        self.setToolTip(self.tr("Series 60 - Remote"))

        self.show()

    def newMessage(self,  message):
        #print message.contact(),  "has open chat",  self.main.chatManager.hasOpenChat(message.contact())
        if self.main.chatManager.hasOpenChat(message.contact()):
            return

        #print "adding menu"
        self.addMenu()

    def clicked(self,  reason):
        if sys.platform == 'darwin':
            # A (left-mouse) click on Mac OS X opens the context menu, so only show the menu
            return

        if reason == QSystemTrayIcon.Trigger:
            if not self.ignoreNextRelease:
                self.dblClickTimer.start(QApplication.doubleClickInterval())
            self.ignoreNextRelease = False
        elif reason == QSystemTrayIcon.DoubleClick:
            self.ignoreNextRelease = True
            self.dblClickTimer.stop()
            try:
                message = self.main.unreadMessages[0]
                contact = message.contact()
            except IndexError:
                pass
            else:
                self.log.info(QString("DoubleClick on Trayicon... starting chat with %1").arg(contact.name()))
                self.openChat(contact)

    def emitClicked(self):
        self.parent.setVisible(not self.parent.isVisible())
        self.addMenu()

    def addMenu(self):
        self.menu.clear()
        self.favMenu.menu(self.menu)

        if self.main.unreadMessages and not self.settings.setting("contacts/ignoreAll"):
            messagesMenu = QMenu(self.tr("&Unread messages"),  self.parent)
            messagesMenu.setIcon(QIcon(":/message-new"))

            if sys.platform == 'darwin':
                self.connect(messagesMenu,  SIGNAL("triggered(QAction *)"),  self.contextMenuTriggered)

            # Show only unique contacts
            contacts = list()
            for message in self.main.unreadMessages:
                if message.contact() not in contacts and \
                    not message.contact().isIgnored() and \
                    not self.main.chatManager.hasOpenChat(message.contact()):

                    contacts.append(message.contact())
            if contacts:
                self.helper.addContactsToMenu(contacts,  messagesMenu)
                self.setIcon(QIcon(":/message-new"))
            else:
                self.setIcon(QIcon(":/phone"))
        else:
            self.setIcon(QIcon(":/phone"))

        mainWindowAction = QAction(self)
        mainWindowAction.setProperty("type",  QVariant("mainWindow"))
        if self.parent.isVisible():
            mainWindowAction.setText(self.tr("&Minimize"))
        else:
            mainWindowAction.setText(self.tr("&Restore"))

        closeAction = QAction(self)
        closeAction.setProperty("type",  QVariant("close"))
        closeAction.setText(self.tr("&Quit"))
        closeAction.setIcon(QIcon(":/application-exit"))

        if self.main.unreadMessages and not self.settings.setting("contacts/ignoreAll") and contacts:
            self.menu.addMenu(messagesMenu)
            self.menu.addSeparator()

        self.menu.addAction(mainWindowAction)
        self.menu.addAction(closeAction)

    def openChat(self,  contact):
        if contact:
            # Close all popup windows of the contact
            for popup in self.main.popups:
                if popup.popupType() == PopupTypes.Message and popup.property("contact").toPyObject() == contact:
                    popup.forceClose()
                    break

            self.main.chatManager.openChat(contact)

    def contextMenuTriggered(self,  action):
        type = action.property("type").toString()

        if type == "contact":
            contact = action.data().toPyObject()
            self.openChat(contact)
        elif type == "close":
            self.main.app.closeAllWindows()
            self.main.app.quit()
        elif type == "mainWindow":
            self.parent.setVisible(not self.parent.isVisible())
            self.addMenu()
        elif type == "configureFavorites":
            self.showFavoriteDialog()

    def showFavoriteDialog(self):
        dlg = window.favorites.Favorites(self.main.mainWindow,  self.main)
