# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import pickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import widget.Popup
from lib.classes import *

class Popups(QWidget):
    def __init__(self,  parent,  main):
        super(Popups,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.trayicon = main.trayicon

        self.connect(main,  SIGNAL("messageNew"),  self.newMessage)
        self.connect(self.connection,  SIGNAL("connectionCompleted"),  self.connected)
        self.connect(self.connection,  SIGNAL("connectionClosed"),  self.disconnected)

    def connected(self):
        if not self.settings.setting("popups/show"):
            return

        myPopup = widget.Popup.Popup(self,  self.main)
        myPopup.setCaption(self.tr("Connection established!"))
        myPopup.setText(self.tr("Succesfully connected with <b>%1</b>!").arg(self.connection.device().name()))
        myPopup.setIcon(QPixmap(":/phone"))
        myPopup.setTarget(QRect(self.trayicon.geometry()))
        myPopup.setTimeout(self.settings.setting("popups/timeout"))
        myPopup.setMaximumWidth(qApp.desktop().availableGeometry().width()/3)
        myPopup.setPopupType(PopupTypes.ConnectionCompleted)
        myPopup.showPopup()

    def disconnected(self,  name):
        if not self.settings.setting("popups/show"):
            return

        myPopup = widget.Popup.Popup(self,  self.main)
        myPopup.setCaption(self.tr("Connection closed"))
        myPopup.setText(self.tr("Connection with <b>%1</b> closed!").arg(name))
        myPopup.setIcon(QPixmap(":/phone"))
        myPopup.setTarget(QRect(self.trayicon.geometry()))
        myPopup.setTimeout(self.settings.setting("popups/timeout"))
        myPopup.setMaximumWidth(qApp.desktop().availableGeometry().width()/3)
        myPopup.setPopupType(PopupTypes.ConnectionClosed)
        myPopup.showPopup()

    def newMessage(self,  message):
        if not self.settings.setting("popups/show"):
            return

        if self.settings.setting("contacts/ignoreAll") or message.contact().isIgnored():
            return

        # Send an highlight event if there is already an open window
        contact = message.contact()
        if contact.id() in self.main.chatManager.activeChatWidgets:
            self.main.chatManager.highlightContact(contact)
            return
        
        for popup in self.main.popups:
            if popup.popupType() == PopupTypes.Message and popup.property("contact").toPyObject() == contact:
                
                # There is already a popup window of this contact...
                message =  popup.property("firstMessage").toString()
                
                messageCount = popup.property("messages").toInt()[0]
                if messageCount == 1:
                    messageCountText = self.tr("+ 1 more message...")
                else:
                    messageCountText = self.tr("+ %1 more messages...").arg(messageCount)
                
                message += "<br /><div align='right'><i>" + messageCountText + "</i></div>"
                
                popup.setText(self.tr("<b>%1</b> writes: <br />%2").arg(contact.name(),  message))
                popup.setProperty("messages",  QVariant(messageCount+1))
                popup.resetTimer()
                
                return

        # Check if there is any unread message of this contact...
        firstUnread = None
        messageCount = 0
        for unreadMessage in self.main.unreadMessages:
            if unreadMessage.contact() == contact:
                if isinstance(firstUnread,  type(None)):
                    firstUnread = unreadMessage
                messageCount += 1
        
        message = message.message().replace("\n",  "<br />")
        
        myPopup = widget.Popup.Popup(self,  self.main)
        myPopup.setCaption(self.tr("New message"))
        
        if messageCount > 1:
            # There is already an unread message of this contact...
            if messageCount == 2:
                messageCountText = self.tr("+ 1 more message...")
            else:
                messageCountText = self.tr("+ %1 more messages...").arg(messageCount-1)
                
            message = firstUnread.message().replace("\n",  "<br />")
            message += "<br /><div align='right'><i>" + messageCountText + "</i></div>"
                
            myPopup.setProperty("firstMessage",  QVariant(firstUnread.message()))
            myPopup.setProperty("messages",  QVariant(messageCount+1))
        else:
            myPopup.setProperty("firstMessage",  QVariant(message))
            myPopup.setProperty("messages",  QVariant(1))
        
        myPopup.setText(self.tr("<b>%1</b> writes: <br />%2").arg(contact.name(),  message))
        myPopup.setIcon(QPixmap(":/message-new"))

        chat = myPopup.addButton(self.tr("Start chat"))
        chat.setProperty("message",  QVariant(message))
        chat.setProperty("contact",  QVariant(contact))

        ignore = myPopup.addButton(self.tr("Block"))
        menu = QMenu(ignore)

        # Block contact
        cont = menu.addAction(self.tr("Block %1").arg(contact.name()))
        cont.setProperty("type",  QVariant("contact"))
        cont.setProperty("contact",  QVariant(contact))

        # Block all
        all = menu.addAction(self.tr("Block all"))
        all.setProperty("type",  QVariant("all"))
        all.setProperty("contact",  QVariant(contact))

        ignore.setMenu(menu)

        myPopup.setTarget(QRect(self.trayicon.geometry()))
        myPopup.setTimeout(self.settings.setting("popups/timeout"))
        myPopup.setMaximumWidth(qApp.desktop().availableGeometry().width()/3)
        myPopup.setPopupType(PopupTypes.Message)
        myPopup.setProperty("contact",  QVariant(contact))
        myPopup.showPopup()

        self.connect(myPopup.buttons,  SIGNAL("clicked(QAbstractButton *)"),  self.buttonClicked)
        self.connect(menu,  SIGNAL("triggered(QAction *)"), lambda act : myPopup.close())
        self.connect(menu,  SIGNAL("triggered(QAction *)"),  self.ignore)

    def ignore(self,  action):
        type = str(action.property("type").toString())
        contact = action.property("contact").toPyObject()

        if type == "contact":
            contact.ignore()
            self.database.contactIgnoreUpdate(contact)
        elif type == "all":
            self.settings.setSetting("contacts/ignoreAll",  True)

        self.main.emit(SIGNAL("ignoreListChanged"))

    def buttonClicked(self,  button):
        if button.text() == self.tr("Start chat"):
            contact = button.property("contact").toPyObject()
            self.main.chatManager.openChat(contact)
