# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import time
import random
from PyQt4.QtCore import *
from lib.classes import *

class Connection(QObject):
    def __init__(self,  parent):
        """This plugin should ONLY be used for testing! It actually doesn't do anything!"""
        super(Connection,  self).__init__(parent)

        self.PLUGIN_NAME = "null"
        self.PLUGIN_VERSION = 0.1
        self.PLUGIN_DEVICES = self.tr("None (Just for testing)")

    def useThisPlugin(self,  database,  saveAllMessages=False,  logger=None):
        """Use the plugin"""
        # Logger erzeugen
        if logger == None:
            import logging
            import sys
            handler = logging.StreamHandler(sys.stdout)
            format = logging.Formatter("%(levelname)-8s - %(message)s",
                            "%d.%m.%Y %H:%M:%S")
            handler.setFormatter(format)
            self.__log = logging.getLogger()
            self.__log.addHandler(handler)
            self.__log.setLevel(logging.ERROR)
        else:
            self.__log = logger

        self.__database = database

        self.__connected = False
        self.__connectionEstablishment = False
        self.__sysinfo = dict()
        self.__device = Device()
        self.__connection_states = 1

    def __str__(self):
        return "\"Connection with null\""

    def connected(self):
        """Return connection state as Boolean"""
        return self.__connected

    def connectToDevice(self,  device):
        """Fake a connection to device"""
        self.__connected = True
        self.__device = device

        self.__sysinfo = dict()
        self.__sysinfo["model"] =  "Fake"
        self.__sysinfo["battery"] =  "50"
        self.__sysinfo["signal_dbm"] = "50"
        self.__sysinfo["signal_bars"] =  "3"
        self.__sysinfo["active_profile"] = "None"
        self.__sysinfo["display"] = "100x200"
        self.__sysinfo["free_drivespace"] = "C:500"
        self.__sysinfo["imei"] = "123456789"
        self.__sysinfo["free_ram"] = "999999999"
        self.__sysinfo["total_ram"] = "999999999"
        self.__sysinfo["total_rom"] = "999999999"
        self.__sysinfo["program_version"] = "0.0.0"
        self.__sysinfo["pys60_version"] = "0.0.0"
        self.__sysinfo["s60_version"] = "0.0.0"
        self.emit(SIGNAL("sysinfoCompleted"))

        self.__contacts = dict()
        self.__contacts["Fake 1"] = "06641234567"
        self.__contacts["Fake 2"] = "06761234567"
        self.__contacts["Fake 3"] = "06501234567"
        self.emit(SIGNAL("contactsCompleted"))

        self.emit(SIGNAL("connectionCompleted"),  device.name())

    def device(self):
        """Return a fake device"""
        dev = Device(10,  "Fake",  "00:11:22:33:44:55")
        for key,  value in self.__sysinfo.iteritems():
            dev.addValue(key,  value)
        return dev

    def sendMessage(self,  message):
        """Send a fake text message to the contact message.contact()"""
        message.setId(random.randint(1, 1000))

        myTime = time.time()
        myTime = QDateTime.fromTime_t(int(myTime))

        self.emit(SIGNAL("messageQueued"),  message)

        # Show immediatly the same message, but in the other direction
        message.setType(MessageType.Incoming)
        self.emit(SIGNAL("messageNew"),  message)

    def setRead(self,  message,  state=True,  send=True):
        """Doesn't have any effect"""
        if state:
            self.emit(SIGNAL("messageRead"),  message)

    def refreshSysinfo(self):
        """Refresh system informations"""
        if not self.__connected:
            raise NotConnectedError,  "No active connection!"

        self.__sysinfo = dict()
        self.__sysinfo["sw version"] =  0.0
        self.__sysinfo["battery"] =  "0"
        self.__sysinfo["signal dbm"] = "0"
        self.__sysinfo["signal bars"] =  "0"
        self.__sysinfo["active profile"] = "None"
        self.__sysinfo["display"] = "0x0"
        self.__sysinfo["free drivespace"] = dict()
        self.__sysinfo["imei"] = "00000000"
        self.__sysinfo["free ram"] = "0"
        self.__sysinfo["total ram"] = "0"
        self.__sysinfo["total rom"] = "0"
        self.__sysinfo["program version"] = "0"
        self.__sysinfo["pys60 version"] = "0"
        self.__sysinfo["s60 version"] = "0"
        self.emit(SIGNAL("sysinfoCompleted"))

    def scan(self):
        """Scan for devices"""
        self.emit(SIGNAL("scanFinished"),  { "00:11:22:33:44:55": "Test 1",  "00:00:00:00:00:00": "Test 2" } )

    def messageStates(self):
        """Return a dictionary with states of all sent messages"""
        return list()

    def pendingMessages(self):
        """Return a list with all pending messages"""
        return list()

    def closeConnection(self):
        """Close connection"""
        self.__connected = False
        self.emit(SIGNAL("connectionClosed"),  self.__device.name())
