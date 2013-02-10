# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *

try:
    import PyOBEX.client
    from PyOBEX.responses import *
except ImportError:
    FOUND_PYOBEX = False
else:
    FOUND_PYOBEX = True

try:
    import obexftp
except ImportError:
    FOUND_OPENOBEX = False
else:
    FOUND_OPENOBEX = True

try:
    import lightblue
except ImportError:
    FOUND_LIGHTBLUE = False
else:
    FOUND_LIGHTBLUE = True

FOUND_OBEX = FOUND_OPENOBEX or FOUND_PYOBEX or FOUND_LIGHTBLUE

USE_PYOBEX = False
USE_OPENOBEX = False
USE_LIGHTBLUE = False
if FOUND_PYOBEX:
    USE_PYOBEX = True
elif FOUND_OPENOBEX:
    USE_OPENOBEX = True
elif FOUND_LIGHTBLUE:
    USE_LIGHTBLUE = True

if USE_OPENOBEX or USE_LIGHTBLUE:
    class BluetoothError(): pass
    class ConnectSuccess(): pass
    class FailureResponse(): pass
    class UnknownResponse(): pass

if FOUND_OBEX:
    if USE_PYOBEX:
        base = PyOBEX.client.BrowserClient
    else:
        base = object
    class ObexClient(base):        
        if USE_PYOBEX:
            path = []
            
            def listdir(self, path=""):
                if path:
                    self.setpath(path)
                return PyOBEX.client.BrowserClient.listdir(self)
            
            def put_file(self,  filename):
                return self.put(unicode(QFileInfo(filename).fileName()),  file(filename,  "rb").read())
            
            def setpath(self,  name = "", create_dir = False, to_parent = False, header_list = ()):
                # Normalise the path.
                pieces = filter(lambda x: x, name.split("\\"))
                
                if pieces == self.path:
                    return True
                
                # Find a common path.
                common = []
                common_length = min(len(pieces), len(self.path))
                
                for i in range(common_length):
                
                    if pieces[0] == self.path[0]:
                        pieces.pop(0)
                        common.append(self.path.pop(0))
                    else:
                        break
                
                # Leave any subdirectories of the common path.
                for subdir in self.path:
                    response = PyOBEX.client.BrowserClient.setpath(self,  to_parent=True)
                    
                    if isinstance(response, FailureResponse):
                        # We couldn't leave a subdirectory. Put the remaining path
                        # back together and return False to indicate an error.
                        self.path = common + self.path
                        return False
                
                # Construct a new path from the common path.
                self.path = common
                
                # Descend into the new path.
                for subdir in pieces:
                    response = PyOBEX.client.BrowserClient.setpath(self,  subdir)
                    if isinstance(response, FailureResponse):
                        # We couldn't enter a subdirectory, so just return False to
                        # indicate an error.
                        return False
                    
                    self.path.append(subdir)
                
                return True
        
        if USE_OPENOBEX:            
            def __check(self,  value):
                if value == 1:
                    return ConnectSuccess()
                else:
                    return FailureResponse()
            
            def __init__(self,  address,  port):
                self.client = obexftp.client(obexftp.BLUETOOTH)
                self.address = address
                self.port = port
            
            def connect(self):
                return self.__check(self.client.connect(self.address,  self.port))
            
            def setpath(self,  path="",  to_parent = False):
                if to_parent:
                    return self.__check(self.client.cdup())
                else:
                    path = str(path).replace("\\",  "/")
                    return self.__check(self.client.chpath(path))
            
            def listdir(self,  subdir):
                if subdir:
                    self.setpath(subdir)
                return [ConnectSuccess(),  self.client.list()]
            
            def get(self,  source):
                source = unicode(source).encode("utf8")
                return [ConnectSuccess(),  self.client.get(source)]
            
            def put_file(self,  file):
                return self.__check(self.client.put_file(str(file)))
            
            def disconnect(self):
                self.__check(self.client.disconnect())
        
        if USE_LIGHTBLUE:
            def __init__(self,  address,  port):
                self.client = lightblue.obex.OBEXClient(address, port)
                self.address = address
                self.port = port
            
            def connect(self):
                try:
                    self.client.connect()
                    return ConnectSuccess()
                except:
                    return FailureResponse()
                
            def put_file(self,  filename):
                try:
                    self.client.put({"name": unicode(QFileInfo(filename).fileName())}, file(filename, 'rb'))
                    return ConnectSuccess()
                except:
                    return FailureResponse()
                    
            def disconnect(self):
                try:
                    self.client.disconnect()
                    return ConnectSuccess()
                except:
                    return FailureResponse()
