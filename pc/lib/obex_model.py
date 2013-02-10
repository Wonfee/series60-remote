# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtXml import *
from lib.obex_items import *
from lib.obex_scheduler import *
from lib.obex_iconprovider import *

class ObexModel(QAbstractItemModel):
    #pendingRequest = pyqtSignal()
    #noMoreRequests = pyqtSignal()
    
    def __init__(self,  parent,  handler=None,  scheduler=None,  rootItem=None):
        QAbstractItemModel.__init__(self,  parent)

        # HACK: We need Main()
        main = qApp.property("main").toPyObject()

        self._parent = parent
        self.helper = main.helper

        self.setFilter(QDir.Filter(QDir.Dirs | QDir.Files))

        self.__errorMessage = ""

        if rootItem == None:
            rootItem = DirectoryItem()
        
        self.__rootItem = rootItem
        
        if scheduler == None and handler != None:
            scheduler = ObexScheduler(handler)
        
        if scheduler != None:
            self.setScheduler(scheduler)
        
        self.setIconProvider(self.defaultIconProvider())
    
    def setHandler(self,  handler):
        scheduler = ObexScheduler(handler)
        self.setScheduler(scheduler)
    
    def setScheduler(self,  scheduler):
        try:
            self.__scheduler.stop()
        except:
            pass
        
        self.clear()
        
        self.__scheduler = scheduler
        #self.__scheduler.directoryListed.connect(self.refresh)
        self.connect(self.__scheduler,  SIGNAL("directoryListed"),  self.refresh)
        self.__scheduler.start()
    
    def setErrorMessage(self,  message):
        self.__errorMessage = message
        self.emit(SIGNAL("layoutChanged()"))
    
    def errorMessage(self):
        return self.__errorMessage
    
    def hasError(self):
        return bool(self.__errorMessage)
    
    def clear(self):
        self.__rootItem.clearChildren()
        self.__scheduler = None
        self.__errorMessage = ""
        self.reset()
    
    def hasScheduler(self):
        try:
            return self.__scheduler.handler.address() != None
        except AttributeError:
            return False

    def defaultIconProvider(self):
        return ObexIconProvider()

    def setIconProvider(self,  provider):
        self.__iconProvider = provider

    def iconProvider(self):
        return self.__iconProvider

    def rootItem(self):
        return self.__rootItem

    def setFilter(self,  filter):
        self.__filter = filter
    
    def filter(self):
        return self.__filter

    def pathToIndex(self,  path):
        root = QModelIndex()
        for dir in path.split("\\")[1:]:
            i = 0
            tmp = root
            while tmp:
                if i > self.rowCount(root):
                    return root
                
                tmp = self.index(i,  0,  root)
                if tmp.internalPointer() and tmp.internalPointer().name() == dir:
                    root = tmp
                    break
                else:
                    i += 1
    
        return root
    
    def request_refresh(self, item):
        self.__scheduler.addAction(ObexAction.ListDir,  item)
        item.setWaiting(True)
        #self.pendingRequest.emit()
        self.emit(SIGNAL("pendingRequest"))
    
    def refresh(self, item, xml):        
        if not xml:
            return
        
        reader = QXmlStreamReader(xml)
        
        item.clearChildren()
        
        while not reader.atEnd():
        
            token = reader.readNext()
            if token == reader.StartElement:
            
                if reader.name() == "file":
                    child = FileItem()
                elif reader.name() == "folder":
                    child = DirectoryItem()
                else:
                    continue
                
                label = reader.attributes().value("label").toString()
                name = unicode(reader.attributes().value("name").toString())
                if label:
                    displayName = QString("%1 (%2)").arg(label,  name)
                else:
                    displayName = name
            
                child.setPath(item.path() + u"\\" + name)
                child.setDisplayName(displayName)
                child.setParent(item)
                child.setMemType(unicode(reader.attributes().value("mem-type").toString()))
                child.setSize(str(reader.attributes().value("size").toString()) or 0)
                child.setTime(QDateTime().fromString(str(reader.attributes().value("modified").toString()),  "yyyyMMdd'T'HHmmss'Z'"))
                child.setPermission(str(reader.attributes().value("user-perm").toString()))
                
                item.appendChild(child)
        
        #self.layoutChanged.emit()
        self.emit(SIGNAL("layoutChanged()"))
        self.emit(SIGNAL("directoryListed"),  item)

        item.setRefreshed(True)
        item.setWaiting(False)

        if self.__scheduler.count() == 0:
            #self.noMoreRequests.emit()
            self.emit(SIGNAL("noMoreRequests"))

    def download(self,  source,  destination):
        # source hast to be a fileitem, destination a string
        self.__scheduler.addAction(ObexAction.Download,  [source,  destination])

    def rowCount(self,  parent=QModelIndex()):
        # We don't know the bluetooth address when the view is created,
        # and so no ObexScheduler is set. the best thing is to return a error.
        # -> 1 row (You are not connected...)
        if not self.hasScheduler():
            return 1
        
        if self.__errorMessage:
            return 1
        
        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.__rootItem
        
        if isinstance(parentItem,  FileItem):
            return 0
        
        if not parentItem.refreshed():
            self.request_refresh(parentItem)
        
        return self.__countRows(parentItem.children())

    def hasChildren(self,  index=QModelIndex()):
        if index.isValid():
            parent = index.internalPointer()
        else:
            parent = self.__rootItem

        if not self.hasScheduler() or self.__errorMessage:
            if index == QModelIndex():
                return True
            return False

        # File items have no children.
        # Directory items are assumed to have children until they have actually
        # been refreshed.

        if isinstance(parent, FileItem):
            return False
        elif parent.refreshed():
            return bool(self.__countRows(parent.children()))
        else:
            return True

    def __countRows(self,  dirlist):
        if self.__filter & QDir.Files == QDir.Files:
            # List files
            return len(dirlist)
        else:
            # List only directorys
            cnt = 0
            for item in dirlist:
                if isinstance(item,  DirectoryItem):
                    cnt += 1
            return cnt

    def columnCount(self,  parent=QModelIndex()):
        if not self.hasScheduler() or self.__errorMessage:
            return 1
        
        return 4

    def indexAt(self, point):
        if self.model().rowCount(self.__rootItem) == 0:
            return QModelIndex()

        wx = point.x() + self.horizontalScrollBar().value()
        wy = point.y() + self.verticalScrollBar().value()

        items = self.model().rowCount(self.__rootItem)
        jtems = self.model().columnCount(self.__rootItem)
        for ind in xrange(items):
            for jnd in xrange(jtems):
                i = self.model().index(ind, jnd)
                r = self.visualRect(i)
                if r.contains(QPoint(wx, wy)):
                    return i

        return QModelIndex()

    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if parent.isValid():
            parentItem = parent.internalPointer()
        else:
            parentItem = self.__rootItem

        if self.hasScheduler() and not self.__errorMessage:
            child = parentItem.children()[row]
        else:
            child = None
        index = self.createIndex(row, column, child)
        return index

    def parent(self, index):
        # root item -> QModelIndex()
        # item -> parent (root item) -> QModelIndex()
        # item -> parent
        
        if not index.isValid():
            return QModelIndex()
        
        if not self.hasScheduler() or self.__errorMessage:
            return QModelIndex()
        
        item = index.internalPointer()
        if item == self.__rootItem or item == None:
            return QModelIndex()
        
        # Only items beneath the root item are examined from here.
        parent = item.parent()
        
        if parent == self.__rootItem:
            return QModelIndex()
        else:
            return self.createIndex(parent.row(), 0, parent)

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return QVariant(self.tr("Name"))
            elif section == 1:
                return QVariant(self.tr("Size"))
            elif section == 2:
                return QVariant(self.tr("Date Modified"))
            elif section == 3:
                return QVariant(self.tr("Permissions"))
        return QVariant() 

    def data(self,  index,  role = Qt.DisplayRole):
        if not index.isValid():
            return QVariant()
        
        if self.__errorMessage:
            if role == Qt.DisplayRole and index.column() == 0:
                return QVariant(self.__errorMessage)
            if role == Qt.DecorationRole and index.column() == 0:
                return QVariant(QIcon(":/dialog-close"))
            if role == Qt.ToolTipRole:
                return QVariant(self.__errorMessage)
            return QVariant()
        
        if not self.hasScheduler():
            if role == Qt.DisplayRole and index.column() == 0:
                return QVariant(self.tr("No active connection"))
            if role == Qt.DecorationRole and index.column() == 0:
                return QVariant(QIcon(":/dialog-close"))
            return QVariant()
        
        item = index.internalPointer()
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return QVariant(item.displayName())
            elif index.column() == 1:
                if isinstance(item,  FileItem):
                    return QVariant(self.helper.pretty_filesize(item.size()))
            elif index.column() == 2:
                return QVariant(item.time())
            elif index.column() == 3:
                return QVariant(item.permission())
        
        # TODO: Edit (Rename) items
        # Don't comment these lines, because the EditRole is
        # needed by QCompleter
        elif role == Qt.EditRole:
            if index.column() == 0 and self.hasScheduler():
                return QVariant(item.name())
        
        elif role == Qt.UserRole and self.hasScheduler():
            return QVariant(item.waiting())
    
        elif role == Qt.DecorationRole and index.column() == 0:
            return QVariant(self.iconProvider().icon(item))
        
        return QVariant()

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def flags(self, index):
        flags = Qt.ItemIsEnabled
        if not index.isValid():
            return flags
        elif not self.hasScheduler() or self.__errorMessage:
            return flags | Qt.ItemIsSelectable
        else:
            item = index.internalPointer()
            
            flags |= Qt.ItemIsSelectable
            flags |= Qt.ItemIsDragEnabled
            
            if not "W" in item.permission():
                return flags
            
            # TODO: Edit (Rename) items
            #flags |= Qt.ItemIsEditable
            
            if not isinstance(item,  DirectoryItem):
                return flags
            
            # TODO: Upload items
            #flags |= Qt.ItemIsDropEnabled
            
            return flags
