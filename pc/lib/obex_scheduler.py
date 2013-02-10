# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.classes import *

USE_PYBLUEZ = False
USE_LIGHTBLUE = False

try:
   # PyBluez module for Linux and Windows
   import bluetooth
   USE_PYBLUEZ = True
except ImportError:
   # Lightblue for Mac OS X
   import lightblue
   # Mac OS X is currently not supported
   # Please look at the following mailing lists for more informations:
   # http://lists.apple.com/archives/Bluetooth-dev/2010/Feb/msg00003.html
   # https://sourceforge.net/mailarchive/message.php?msg_name=201001301133.59073.LuHe@gmx.at
   # https://sourceforge.net/mailarchive/message.php?msg_name=201002090855.02919.LuHe@gmx.at
   # https://sourceforge.net/projects/lightblue/forums/forum/596727/topic/3602492
   USE_LIGHTBLUE = False

ObexAction = Enum("ListDir Download Disconnect",  beginning=1)

class ObexScheduler(QThread):

    #directoryListed = pyqtSignal(object, str)
    #downloaded = pyqtSignal(object, bool)
    
    def __init__(self, handler):
        QThread.__init__(self)
        self.handler = handler
        self.actions = []
        self.currentAction = None
        self.mutex = QMutex()
    
    def findObexPort(self,  address):
        if USE_PYBLUEZ:
            services = bluetooth.find_service(address=address, name="OBEX File Transfer")
            
            # Windows (Widcomm) seems to ignore the name argument...
            for service in services:
                if service["name"] == "OBEX File Transfer":
                    return service["port"]
            return None
        elif USE_LIGHTBLUE:
            services = lightblue.findservices(addr=address, name="OBEX File Transfer")
            if service:
                return services[0][1]
            else:
                return None
        else:
            return None
    
    def addAction(self, action,  argument = None):
        self.mutex.lock()
        if [action,  argument] not in self.actions and [action,  argument] != self.currentAction:
            # There could be two model which want to fetch the root directory,
            # so check if the request is really unique - otherwise we get a UnknownResponse
            # in listdir
            self.actions.append([action,  argument])
        self.mutex.unlock()
    
    def count(self):
        self.mutex.lock()
        number = len(self.actions)
        self.mutex.unlock()
        
        return number
    
    def run(self):
        self.running = True
        while self.running:
            self.mutex.lock()
            try:
                action,  argument = self.actions.pop()
            except IndexError:
                action = None
            self.mutex.unlock()
            
            if action != None:
                self.mutex.lock()
                self.currentAction = [action,  argument]
                self.mutex.unlock()
                
                # Check if the obex port is already set...
                if not self.handler.port():
                    try:
                        self.handler.setPort(self.findObexPort(self.handler.address()))
                    except Exception, msg:
                        if os.name == "nt":
                            errno,  errmsg = msg.errno, msg.message
                        else:
                            try:
                                errno, errmsg = eval(msg[0]) # msg.message has been deprecated as of Python 2.6
                            except:
                                errno,  errmsg = 0,  str(msg) # for obexftp
                        
                        errmsg = unicode(errmsg,  "utf8")
                        self.handler.setPort(None) # to reconnect the next time
                        self.emit(SIGNAL("connectionFailed"),  errno,  errmsg)
                        
                        # Remove current action, otherwise it cannot be added again
                        self.mutex.lock()
                        self.currentAction = None
                        self.mutex.unlock()

                        continue
                
                if action == ObexAction.ListDir:
                    #if self.handler.setpath(argument.path()):
                    result = self.handler.listdir(argument.path())
                    if result:
                        self.emit(SIGNAL("directoryListed"), argument, result)
                        #self.directoryListed.emit(argument, result)
                    else:
                        self.emit(SIGNAL("directoryListed"), argument, "")
                        self.directoryListed.emit(argument, "")
                
                elif action == ObexAction.Download:
                    # action is a list, containing the source file as FileItem Object
                    # and the destination file as string
                    source,  destination = argument
                    if self.handler.setpath(source.parent().path()):
                        result = self.handler.download(source.name(),  destination)
                        if result != False:
                            self.emit(SIGNAL("dowloaded"), source, result)
                            #self.downloaded.emit(source, result)
                        else:
                            self.emit(SIGNAL("downloaded"), source, "")
                            #self.downloaded.emit(source, "")
                elif action == ObexAction.Disconnect:
                    self.handler.disconnect()

                self.mutex.lock()
                self.currentAction = None
                self.mutex.unlock()
            
            qApp.processEvents()
            self.usleep(600)

    def stop(self):
        self.handler.disconnect()
        self.running = False
        self.wait(5)
