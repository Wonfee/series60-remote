# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

from obex_wrapper import *

if USE_PYOBEX:
    from PyOBEX.responses import *

class ObexError(Exception): pass

class ObexHandler(object):
    def __init__(self, address,  port=None):        
        self.client = None
        
        self.setAddress(address)
        self.setPort(port)
        
        self.path = []
    
    def setAddress(self,  address):
        self.__address = address
        try:
            if self.port():
                self.client = ObexClient(self.address(), port)
                if not isinstance(self.client.connect(), ConnectSuccess):
                    raise ObexError, "Failed to connect"
        except AttributeError:
            pass
    
    def setPort(self,  port):
        self.__port = port
        if port != None and self.address():
            self.client = ObexClient(self.address(), port)
            if not isinstance(self.client.connect(), ConnectSuccess):
                raise ObexError, "Failed to connect"
    
    def address(self):
        return self.__address
    
    def port(self):
        return self.__port
    
    def setpath(self, path):
        return self.client.setpath(path)
    
    def listdir(self, subdir = ""):
        response = self.client.listdir(subdir)
        #if isinstance(response, FailureResponse) or isinstance(response, UnknownResponse):
        #    return False
        
        headers, listing = response
        return listing
    
    def download(self,  source,  destination):
        response = self.client.get(source)
        if isinstance(response, FailureResponse) or isinstance(response, UnknownResponse):
            return False
        
        headers, listing = response
        file(destination, 'wb').write(listing)
        return True

    def disconnect(self):
        self.client.disconnect()
