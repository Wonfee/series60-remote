# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import sys
from PyQt4.QtCore import *
import devices.series60
import devices.null

class Device(QObject):
    def __init__(self,  parent,  main):
        """Import plugin for connectiong to a device"""
        super(Device,  self).__init__(parent)

        self.__parent = parent
        self.__main = main

        self.__settings= main.settings
        self.__database = main.database
        self.__log = main.log

        self.__connection = None
        self.__plugin =  str(self.__settings.setting("general/connectionPlugin"))

    def connection(self):
        """return connection to mobile phone"""
        return self.__connection

    def plugins(self):
        devlist = dict()
        devlist["series60"] = devices.series60
        devlist["null"] = devices.null
        return devlist

    def plugin(self):
        return self.__plugin

    def loadPlugin(self):
        """Load selected plugin"""

        self.__plugin =  str(self.__settings.setting("general/connectionPlugin"))
        if not self.__plugin in self.plugins():
            self.__plugin = "series60"

        # Import the selected plugin
        save = str(self.__settings.setting("messages/saveAllMessages"))

        self.__connection = self.plugins()[self.__plugin].Connection(self.__parent)
        self.__connection.useThisPlugin(self.__database,  save,  self.__log)
