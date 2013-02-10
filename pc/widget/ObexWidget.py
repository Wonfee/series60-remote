# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.obex_items import *
from lib.obex_completer import *
from lib.obex_scheduler import *
from widget.ObexView import *

class ObexWidget(QWidget):
    def __init__(self,  parent,  handler=None,  scheduler=None,  rootItem=None):
        super(ObexWidget,  self).__init__()

        # Recently opened folders, for navigating back and forward
        self.future = list()
        self.history = list()
        
        if scheduler == None and handler != None:
            self.setScheduler(ObexScheduler(handler))
        
        if rootItem == None:
            rootItem = DirectoryItem()
        
        self.directoryTree = ObexView(parent,  handler,  scheduler,  rootItem)
        sizePolicy = QSizePolicy()
        sizePolicy.setHorizontalStretch(1)
        self.directoryTree.setSizePolicy(sizePolicy)
        self.directoryTree.model.setFilter(QDir.Dirs)
        
        self.fileList = ObexView(parent,  handler,  scheduler,  rootItem)
        sizePolicy = QSizePolicy()
        sizePolicy.setHorizontalStretch(3)
        self.fileList.setSizePolicy(sizePolicy)
        self.fileList.setRootIsDecorated(False)
        self.fileList.setItemsExpandable(False)
        self.fileList.setExpandsOnDoubleClick(False)
        
        # TODO: Implement Drag&Drop (Download and Upload)
        #self.fileList.setDragEnabled(True)
        #self.fileList.setAcceptDrops(True)
        
        # When the user doubleclicks on a directory in file view, the loading movie should also be shown
        # in directory view
        #self.fileList.model.pendingRequest.connect(self.directoryTree.delegate.startMovie)
        #self.fileList.model.noMoreRequests.connect(self.directoryTree.delegate.stopMovie)
        self.connect(self.fileList.model, SIGNAL("pendingRequest"), self.directoryTree.delegate, SLOT("startMovie()"))
        self.connect(self.fileList.model, SIGNAL("noMoreRequests"), self.directoryTree.delegate, SLOT("stopMovie()"))
        
        self.splitter = QSplitter()
        self.splitter.addWidget(self.directoryTree)
        self.splitter.addWidget(self.fileList)
    
        self.connect(self.directoryTree.model, SIGNAL("layoutChanged()"),  self,  SLOT("updateLayout()"))
        self.connect(self.directoryTree, SIGNAL("clicked(QModelIndex)"),  self,  SLOT("setRootIndex(QModelIndex)"))
        self.connect(self.fileList, SIGNAL("doubleClicked(QModelIndex)"),  self,  SLOT("setRootIndex(QModelIndex)"))

        self.locationLine = QLineEdit(parent)
        self.completer = ObexCompleter(self.locationLine)
        self.locationLine.setCompleter(self.completer)
        self.completer.setModel(self.directoryTree.model)
        
        self.connect(self.locationLine,  SIGNAL("returnPressed()"),  self.setPath)
        self.connect(self.directoryTree.model,  SIGNAL("directoryListed"),  self.showCompletionPopup)
        
        # Draw navigating actions as Toolbuttons
        self.backButton = QToolButton(parent)
        self.forwardButton = QToolButton(parent)
        self.upButton = QToolButton(parent)
        self.homeButton = QToolButton(parent)
        self.refreshButton = QToolButton(parent)
        
        self.backAction = QAction(QIcon(":/go-previous"), self.tr("Back"),  parent)
        self.forwardAction = QAction(QIcon(":/go-next"), self.tr("Forward"),  parent)
        self.upAction = QAction(QIcon(":/go-up"), self.tr("Up"),  parent)
        self.homeAction = QAction(QIcon(":/go-home"), self.tr("Home"),  parent)
        self.refreshAction = QAction(QIcon(":/view-refresh"), self.tr("Refresh"),  parent)
        
        self.connect(self.backAction,  SIGNAL("triggered()"),  self,  SLOT("goBack()"))
        self.connect(self.forwardAction,  SIGNAL("triggered()"),  self,  SLOT("goForward()"))
        self.connect(self.upAction,  SIGNAL("triggered()"),  self,  SLOT("goUp()"))
        self.connect(self.homeAction,  SIGNAL("triggered()"),  self,  SLOT("goHome()"))
        self.connect(self.refreshAction,  SIGNAL("triggered()"),  self,  SLOT("refresh()"))
    
        self.backButton.setDefaultAction(self.backAction)
        self.forwardButton.setDefaultAction(self.forwardAction)
        self.upButton.setDefaultAction(self.upAction)
        self.homeButton.setDefaultAction(self.homeAction)
        self.refreshButton.setDefaultAction(self.refreshAction)
        
        self.topLayout = QHBoxLayout()
        self.topLayout.addWidget(self.locationLine)
        self.topLayout.addWidget(self.backButton)
        self.topLayout.addWidget(self.forwardButton)
        self.topLayout.addWidget(self.upButton)
        self.topLayout.addWidget(self.homeButton)
        self.topLayout.addWidget(self.refreshButton)
        
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addLayout(self.topLayout)
        self.mainLayout.addWidget(self.splitter)
        
        # The line edit should't have focus initially
        self.setTabOrder(self.fileList,  self.directoryTree)
        self.setTabOrder(self.directoryTree,  self.locationLine)
        self.setTabOrder(self.locationLine,  self.backButton)
        self.setTabOrder(self.backButton,  self.forwardButton)
        self.setTabOrder(self.forwardButton,  self.upButton)
        self.setTabOrder(self.upButton,  self.homeButton)
        self.setTabOrder(self.homeButton,  self.refreshButton)
        
        self.updateActions()
        self.updateLayout()
    
    def connected(self):
        return self.directoryTree.model.hasScheduler()
    
    def setScheduler(self,  scheduler):
        if sys.platform == "darwin":
            return
        
        self.scheduler = scheduler
        
        self.directoryTree.setScheduler(scheduler)
        self.fileList.setScheduler(scheduler)
        
        self.updateLayout()
        self.updateActions()
        self.refresh()
    
    def closeConnection(self):
        self.directoryTree.model.clear()
        self.fileList.model.clear()
        self.locationLine.setText("")
        self.future = list()
        self.history = list()
        self.updateActions()
        self.updateLayout()
        if hasattr(self,  "scheduler") and self.scheduler != None:
            self.scheduler.running = False
    
    @pyqtSignature("")
    def updateLayout(self):
        self.directoryTree.setColumnCount(1)
    
    def setPath(self):
        # A path has to begin with a backslash (\)
        path = "\\" + self.locationLine.text()
        self.setRootIndex(self.directoryTree.model.pathToIndex(path))

    @pyqtSignature("QModelIndex")
    def setRootIndex(self,  index,  remember=True):
        if isinstance(index.internalPointer(),  FileItem):
            return
        if index.isValid() and index.internalPointer():
            self.setRootPath(index.internalPointer().path(),  remember)
    
    def setRootPath(self,  path,  remember = True):
        if remember:
            del self.future[:] # Clear list
            item = self.fileList.rootIndex().internalPointer()
            if item:
                self.history.append(item.path())
            else:
                self.history.append("")
        
        self.fileList.setPath(path)
        self.directoryTree.selectPath(path)
        self.locationLine.setText(path.replace("\\",  "",  1))
        
        self.updateActions()
    
    @pyqtSignature("")
    def goUp(self):
        index = self.directoryTree.currentIndex()
        if (index.isValid() and index.parent() and index.parent().internalPointer()):
            self.setRootIndex(index.parent())
        else:
            self.setRootPath("")

    @pyqtSignature("")
    def goHome(self):
        self.setRootPath("")

    @pyqtSignature("")
    def goBack(self):
        item = self.fileList.rootIndex().internalPointer()
        if item:
            self.future.append(item.path())
        else:
            self.future.append("")
        self.setRootPath(self.history.pop(),  False)

    @pyqtSignature("")
    def goForward(self):
        item = self.fileList.rootIndex().internalPointer()
        if item:
            self.history.append(item.path())
        else:
            self.history.append("")
        self.setRootPath(self.future.pop(),  False)

    @pyqtSignature("")
    def refresh(self):
        if self.fileList.model.hasError():
            self.fileList.model.setErrorMessage("")
            self.directoryTree.model.setErrorMessage("")
            self.updateLayout()
        
        if self.fileList.rootIndex().internalPointer():
            ref = self.fileList.rootIndex().internalPointer()
        else:
            ref = self.fileList.model.rootItem()
        self.fileList.model.request_refresh(ref)

    def showCompletionPopup(self,  item):
        if self.locationLine.hasFocus():
            self.completer.complete()
    
    def updateActions(self):
        self.backAction.setEnabled(len(self.history) > 0)
        self.forwardAction.setEnabled(len(self.future) > 0)
        self.upAction.setEnabled(self.fileList.rootIndex().internalPointer() != None)
        self.homeAction.setEnabled(self.fileList.rootIndex().internalPointer() != None)
        self.refreshAction.setEnabled(self.connected() and sys.platform != "darwin")
