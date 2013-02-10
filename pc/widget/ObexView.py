# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.helper
from lib.delegate_movie import *
from lib.obex_items import *
from lib.obex_model import *

class ObexView(QTreeView):
    def __init__(self,  parent,  handler=None,  scheduler=None,  rootItem=None):
        super(ObexView,  self).__init__()

        # TODO: Implement Drag&Drop (Download and Upload)
        #self.setDragEnabled(True)
        #self.viewport().setAcceptDrops(True)
        #self.setDropIndicatorShown(True)
        
        if scheduler == None and handler != None:
            scheduler = ObexScheduler(handler)
            self.connect(scheduler,  SIGNAL("connectionFailed"),  self.connectionFailed)
        
        if rootItem == None:
            rootItem = DirectoryItem()

        self.savePath = QDir.homePath()
        
        self.handler = handler
        self.model = ObexModel(parent,  handler,  scheduler,  rootItem)
        self.setModel(self.model)

        if sys.platform == "darwin":
            # File browser isn't supported on Mac OS X
            self.model.setErrorMessage(self.tr("File browsing is not yet supported on Mac OS X"))

        # Draw a delegate (loading movie) when  there is an ongoing process (e.g. directory listing)
        movie = QMovie(":/loading-2")
        movie.setScaledSize(QSize(16, 16))
        self.delegate = MovieDelegate(movie)
        self.setItemDelegate(self.delegate)
        
        #self.delegate.needsRedraw.connect(self.viewport().update)
        #self.model.pendingRequest.connect(self.delegate.startMovie)
        #self.model.noMoreRequests.connect(self.delegate.stopMovie)

        self.connect(self.delegate, SIGNAL("needsRedraw()"), self.viewport(), SLOT("update()"))
        self.connect(self.model, SIGNAL("pendingRequest"), self.delegate, SLOT("startMovie()"))
        self.connect(self.model, SIGNAL("noMoreRequests"), self.delegate, SLOT("stopMovie()"))

        # The first section (file name) should be stretched
        self.header().setStretchLastSection(False)
        self.header().setResizeMode(0, QHeaderView.Stretch)

    def setScheduler(self,  scheduler):
        self.model.setScheduler(scheduler)
        self.connect(scheduler,  SIGNAL("connectionFailed"),  self.connectionFailed)

    def connectionFailed(self,  errno,  errmsg):
        if isinstance(errno,  type(None)):
            errno = 0
        if isinstance(errmsg,  type(None)):
            errmsg = self.tr("Unknown error")

        self.model.setErrorMessage(self.tr("Connection failed (%1): %2").arg(errno).arg(errmsg))

    def setPath(self,  path):
        self.setRootIndex(self.model.pathToIndex(path))

    def selectPath(self,  path):
        index = self.model.pathToIndex(path)
        self.setCurrentIndex(index)
        self.expand(index)

    def setColumnCount(self,  number):
        for column in range(self.model.columnCount()+1)[number:]:
            self.hideColumn(column)

    def contextMenuEvent(self,  event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return
        
        item = index.internalPointer()
        
        menu = QMenu(self)
        saveAs = QAction(self)
        saveAs.setText(self.tr("Save as..."))
        saveAs.setEnabled(isinstance(item,  FileItem))  # "Save as..." is currently only supported for File Items
        saveAs.setProperty("type",  QVariant("save"))
        saveAs.setProperty("item",  QVariant(item))

        menu.addAction(saveAs)
        menu.popup(QCursor.pos())
        
        self.connect(menu,  SIGNAL("triggered(QAction *)"),  self.customContextMenuTriggered)
    
    def customContextMenuTriggered(self,  action):
        type = str(action.property("type").toString())
        item = action.property("item").toPyObject()
        if type == "save":
            destination = QFileDialog.getSaveFileName(self,  self.tr("Choose a filename to save under..."),  
                                    self.savePath + "/" + item.name())
            if destination:
                self.savePath = QFileInfo(destination).absolutePath()
                exists = QFile(destination).exists()
                if exists:
                    ret = QMessageBox.question(None,
                        self.tr("Overwrite file?"),
                        self.tr("Do you really want to overwrite the file \"%1\"?").arg(destination),
                        QMessageBox.StandardButtons(\
                            QMessageBox.No | \
                            QMessageBox.Yes))
                    overwrite = (ret == QMessageBox.Yes)
                if not exists or (exists and overwrite):
                    self.model.download(item,  destination)
