# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *

class GeneralItem(object):
    def __init__(self,  path = str(),  displayName = str(),  parent = None,  refreshed = False,  waiting = False,  
                 memtype = "",  size = int(),  time = QDateTime(),  permission = str()):

        self.setPath(path)
        self.setDisplayName(displayName)
        
        if parent == None or parent.name() == str():
            parent = None
            
        self.setParent(parent)
        self.setRefreshed(refreshed)
        self.setWaiting(waiting)
        self.setMemType(memtype)
        self.setSize(size)
        self.setTime(time)
        self.setPermission(permission)
    
    def __eq__(self,  b):
        try:
            return self.path() == b.path()
        except:
            return False
    
    def __nonzero__(self):
        return self.name() != str()
    
    def setPath(self,  path):
        self.__path = path
    
    def setDisplayName(self,  displayName):
        self.__displayName = displayName
    
    def setParent(self,  parent):
        self.__parent = parent
    
    def setRefreshed(self,  refreshed):
        self.__refreshed = refreshed
    
    def setWaiting(self,  waiting):
        self.__waiting = waiting
    
    def setMemType(self,  memtype):
        self.__memtype = memtype
    
    def setSize(self,  size):
        self.__size = size
    
    def setTime(self,  time):
        self.__time = time
    
    def setPermission(self,  permission):
        self.__permission = permission
    
    def name(self):
        return self.__path.split(u"\\")[-1]
    
    def path(self):
        return self.__path
    
    def displayName(self):
        return self.__displayName
    
    def parent(self):
        try:
            return self.__parent
        except NameError:
            return None
    
    def refreshed(self):
        return self.__refreshed

    def waiting(self):
        return self.__waiting
    
    def memType(self):
        return self.__memtype
    
    def row(self):
        if self.parent() != None:
            return self.parent().children().index(self)
        return 0
    
    def size(self):
        return self.__size
    
    def time(self):
        return self.__time
    
    def permission(self):
        return self.__permission

class DirectoryItem(GeneralItem):
    def __init__(self,  path = str(),  displayName = str(),  parent = None,  refreshed = False,  waiting = False,  
                 memtype = "",  size = int(),  time = QDateTime(),  permission = str()):
        GeneralItem.__init__(self,  path,  displayName,  parent,  refreshed,  waiting,  memtype,  size,  time,  permission)
        
        self.__populatedChildren = False
        self.__children = list()
    
    def __del__(self):
        for child in self.__children:
            del child
        del self
    
    def setPopulatedChildren(self,  state):
        self.__populatedChildren = state

    def children(self):
        return self.__children

    def populatedChildren(self):
        return self.__populatedChildren

    def hasChildren(self):
        return bool(self.children())

    def appendChild(self,  child):
        child.setParent(self)
        self.__children.append(child)

    def clearChildren(self):
        for child in self.__children:
            del child
        self.__children = list()

    def __len__(self):
        return len(self.children())

class FileItem(GeneralItem):
    def __init__(self,  path = str(),  displayName = str(),  parent = None,  refreshed = False,  waiting = False,  
                 memtype = "",  size = int(),  time = QDateTime(),  permission = str()):
        GeneralItem.__init__(self,  path,  displayName,  parent,  refreshed,  waiting,  memtype,  size,  time,  permission)

    def hasChildren(self):
        return False

    def populatedChildren(self):
        return True
