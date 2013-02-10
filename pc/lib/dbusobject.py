# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import dbus
import dbus.service
import dbus.mainloop.qt
from PyQt4.QtCore import *

class DBusObject(dbus.service.Object):
    def __init__(self,  session_bus,  main):
        dbus.service.Object.__init__(self,  session_bus, '/Series60Remote')

        self.main = main

        self.log = main.log
        #self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.log.info(QString("D-BUS Object created, name 'net.sourceforge.series60remote' on Session Bus"))

    @dbus.service.method("net.sourceforge.series60remote", in_signature='s', out_signature='as')
    def HelloWorld(self, hello_message):
        print (str(hello_message))
        return ["Hello", "from Series60Remote"]

    @dbus.service.method("net.sourceforge.series60remote", out_signature='ai')
    def Contacts(self):
        return [contact.id() for contact in self.database.contacts(True)]
    
    @dbus.service.method("net.sourceforge.series60remote", in_signature='i', out_signature='s')
    def ContactName(self,  id):
        return self.database.contacts(contactId=id).next().name()
