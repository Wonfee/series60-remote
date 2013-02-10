# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import pickle
import logging
from PyQt4.QtCore import *

class Settings(QSettings):
    def __init__(self,  parent,  main):
        super(Settings,  self).__init__(QSettings.IniFormat,  QSettings.UserScope,  main.app.organizationName(),  main.app.applicationName(),  parent)

        self.parent = parent
        self.main = main

        self.__settings = {}
        self.loadSettings()

    def __str__(self):
        return "\"Settings\""

    def loadSettings(self):
        self.__settings = dict()

        # Application settings
        self.beginGroup("general")
        self.__settings["general/firstStart"] = self.value("firstStart",  QVariant(True)).toBool()
        self.__settings["general/sendMessageOnReturn"] = self.value("sendMessageOnReturn",  QVariant(False)).toBool()
        self.__settings["general/connectionPlugin"] = self.value("connectionPlugin",  QVariant("series60")).toString()
        self.__settings["general/automaticConnectionEnabled"]  = self.value("automaticConnectionEnabled",  QVariant(False)).toBool()
        self.__settings["general/automaticConnectionInterval"]  = int(self.value("automaticConnectionInterval",  QVariant(60)).toInt()[0])
        self.__settings["general/autoStartMinimized"]  = self.value("autoStartMinimized",  QVariant(True)).toBool()
        self.endGroup()

        # Log settings
        self.beginGroup("log")
        self.__settings["log/level"] = int(self.value("level",  QVariant(logging.WARNING)).toInt()[0])
        self.__settings["log/long"]  = self.value("long",  QVariant(False)).toBool()
        self.endGroup()

        # Message settings
        self.beginGroup("messages")
        self.__settings["messages/markAsRead"]  = self.value("markAsRead",  QVariant(True)).toBool()
        self.__settings["messages/saveAllMessages"]  = self.value("saveAllMessages",  QVariant(True)).toBool()
        self.__settings["messages/displayLast"]  = int(self.value("displayLast",  QVariant(5)).toInt()[0])
        self.endGroup()

        # Contact settings
        self.beginGroup("contacts")
        self.__settings["contacts/displayIcon"]  = self.value("displayIcon",  QVariant(True)).toBool()
        self.__settings["contacts/ignoreAll"] = self.value("ignoreAll",  QVariant(False)).toBool()
        self.__settings["contacts/hideCellnumber"]  = self.value("hideCellnumber",  QVariant(True)).toBool()
        self.__settings["contacts/displayFavoritesDays"]  = int(self.value("displayFavoritesDays",  QVariant(15)).toInt()[0])
        self.__settings["contacts/displayFavoritesCount"]  = int(self.value("displayFavoritesCount",  QVariant(5)).toInt()[0])
        self.__settings["contacts/displayFavoritesNum"]  = int(self.value("displayFavoritesNum",  QVariant(3)).toInt()[0])
        self.__settings["contacts/displayFavoritesInSubmenu"]  = self.value("displayFavoritesInSubmenu",  QVariant(True)).toBool()
        self.endGroup()

        # Popup settings
        self.beginGroup("popups")
        self.__settings["popups/show"] = self.value("show",  QVariant(True)).toBool()
        self.__settings["popups/timeout"] = int(self.value("timeout",  QVariant(15)).toInt()[0])
        self.__settings["popups/animate"] = self.value("animate",  QVariant(True)).toBool()
        self.endGroup()

        # Window settings
        messages_splitter = '\x00\x00\x00\xff\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x01\x9b\x00\x00\x01\x17\x01\x00\x00\x00\x0c\x01\x00\x00\x00\x01'

        self.beginGroup("windows")
        self.beginGroup("main")
        self.__settings["windows/main/size"]  = self.value("size",  QVariant(QSize())).toSize()
        self.__settings["windows/main/position"]  = self.value("position",  QVariant(QPoint())).toPoint()
        self.__settings["windows/main/messagesSplitter"]  = self.value("messagesSplitter",  QVariant(QByteArray(messages_splitter))).toByteArray()
        self.__settings["windows/main/contactsSplitter"]  = self.value("contactsSplitter",  QVariant(QByteArray())).toByteArray()
        self.__settings["windows/main/minimizeOnClose"]  = int(self.value("minimizeOnClose",  QVariant(0)).toInt()[0])
        self.endGroup()

        self.beginGroup("favorites")
        self.__settings["windows/favorites/size"]  = self.value("size",  QVariant(QSize())).toSize()
        self.endGroup()

        self.beginGroup("chat")
        self.__settings["windows/chat/tabbedChat"]  = self.value("tabbedChat",  QVariant(False)).toBool()
        self.__settings["windows/chat/size"]  = self.value("size",  QVariant(QSize())).toSize()
        self.__settings["windows/chat/splitter"]  = self.value("splitter",  QVariant(QByteArray())).toByteArray()

        self.beginGroup("theme")
        self.__settings["windows/chat/theme/name"] = unicode(self.value("name",  QVariant("Stock")).toString())
        self.__settings["windows/chat/theme/variant"] = unicode(self.value("variant",  QVariant("")).toString())
        self.__settings["windows/chat/theme/groupMessages"]  = self.value("groupMessages",  QVariant(True)).toBool()
        self.__settings["windows/chat/theme/compact"]  = self.value("compact",  QVariant(False)).toBool()
        self.endGroup()

        self.endGroup()

        self.endGroup()

        # Bluetooth settings
        self.beginGroup("bluetooth")
        self.__settings["bluetooth/lastName"] = unicode(self.value("lastName",  QVariant("")).toString())
        self.__settings["bluetooth/port"]  = int(self.value("port",  QVariant("18")).toString())
        self.endGroup()

        # Database settings
        self.beginGroup("database")
        file = str(QFileInfo(self.fileName()).absoluteDir().absolutePath()) + "/messages.db"
        self.__settings["database/type"] = str(self.value("type",  QVariant("sqlite")).toString())

        self.beginGroup("sqlite")
        self.__settings["database/sqlite/filename"] = str(self.value("filename",  QVariant(file)).toString())
        self.endGroup()

        self.beginGroup("mysql")
        self.__settings["database/mysql/host"] = str(self.value("host",  QVariant("localhost")).toString())
        self.__settings["database/mysql/port"] = int(self.value("port",  QVariant(3306)).toInt()[0])
        self.__settings["database/mysql/user"] = str(self.value("user",  QVariant("")).toString())
        self.__settings["database/mysql/pass"] = str(self.value("pass",  QVariant("")).toString())
        self.__settings["database/mysql/database"] = str(self.value("database",  QVariant("")).toString())
        self.endGroup()

        self.endGroup()

        # Update checker
        self.beginGroup("updateCheck")
        self.__settings["updateCheck/enabled"]  = self.value("enabled",  QVariant(True)).toBool()
        self.__settings["updateCheck/url"] = self.value("url",  QVariant("http://series60-remote.sourceforge.net/update_checker.php")).toUrl()
        self.__settings["updateCheck/website"] = self.value("website",  QVariant("http://series60-remote.sourceforge.net")).toUrl()
        self.__settings["updateCheck/interval"]  = int(self.value("interval",  QVariant(3)).toInt()[0])
        self.__settings["updateCheck/showUnstable"]  = self.value("showUnstable",  QVariant(not self.main.versionIsStable)).toBool()
        self.__settings["updateCheck/lastCheck"]  = self.value("lastCheck",  QVariant(QDate())).toDate()
        self.__settings["updateCheck/lastVersion"] = str(self.value("lastVersion",  QVariant("")).toString())
        self.__settings["updateCheck/lastMessage"] = unicode(self.value("lastMessage",  QVariant("")).toString())
        self.endGroup()

        # Look and Feel
        self.beginGroup("lookAndFeel")
        self.__settings["lookAndFeel/widgetStyle"] = str(self.value("widgetStyle",  QVariant("")).toString())
        self.__settings["lookAndFeel/language"] = str(self.value("language",  QVariant("")).toString())
        self.endGroup()

    def reloadSettings(self):
        self.loadSettings()
        self.emit(SIGNAL("reloadSettings"))
        self.main.emit(SIGNAL("ignoreListChanged"))

    def chatThemeChanged(self):
        self.emit(SIGNAL("chatThemeChanged"))

    def setSetting(self,  key,  value,  usePickle=False):
        self.setValue(key, QVariant(value))

        if self.group():
            key = str(self.group()) + "/" + key

        if usePickle:
            self.__settings[key] = pickle.loads(value)
        else:
            self.__settings[key] = value

    def setting(self,  key):
        return self.__settings[key]
