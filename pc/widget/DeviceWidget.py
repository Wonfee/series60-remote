# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.obex_wrapper
import lib.devicemodel
import lib.delegate_device
from lib.devicemodel import DeviceRoles,  DeviceTypes

class _DeviceWidget(QWidget):
    def __init__(self,  parent):
        super(_DeviceWidget,  self).__init__(parent)
        
        self.delegate = lib.delegate_device.DeviceDelegate(self)
        
        self.topLayout = QVBoxLayout(self)
        
        self.deviceView = QListView(self)
        self.deviceView.setItemDelegate(self.delegate)
        
        self.topLayout.addWidget(self.deviceView)
        
        self.connect(self.delegate, SIGNAL("needsRedraw()"), self.deviceView.viewport(), SLOT("update()"))
        self.connect(self.deviceView,  SIGNAL("doubleClicked(const QModelIndex &)"),  self.__handleDoubleclick)
    
    def __handleDoubleclick(self,  index):
        elementType = index.data(DeviceRoles.TypeRole)
        elementType = elementType.toInt()[0]
        if elementType == DeviceTypes.Device:
            device = index.data(DeviceRoles.DeviceRole).toPyObject()
            self.emit(SIGNAL("deviceDoubleClicked"),  device)
    
    def selectedDevices(self):
        devices = list()
        indexes = self.deviceView.selectedIndexes()
        for index in indexes:
            elementType = index.data(DeviceRoles.TypeRole)
            elementType = elementType.toInt()[0]
            if elementType == DeviceTypes.Device:
                device = index.data(DeviceRoles.DeviceRole).toPyObject()
                devices.append(device)
        
        return devices
    
class DeviceScanWidget(_DeviceWidget):
    def __init__(self,  parent):
        super(DeviceScanWidget,  self).__init__(parent)
        
        # HACK: We need Main()
        main = qApp.property("main").toPyObject()

        self.main = main
        self.helper = main.helper
        
        self.model = lib.devicemodel.DeviceScanModel()
        self.deviceView.setModel(self.model)
        
        self.deviceView.setContextMenuPolicy(Qt.CustomContextMenu)
        
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addStretch(1)
        
        self.rescanButton = QPushButton(self.tr("Rescan"),  self)
        self.buttonLayout.addWidget(self.rescanButton)
        
        self.topLayout.addLayout(self.buttonLayout)
        
        self.connect(self.rescanButton, SIGNAL("pressed()"), self.model, SLOT("scanStart()"))
        self.connect(self.deviceView,  SIGNAL("customContextMenuRequested(QPoint)"),  self.showContextMenu)
        self.connect(self.model, SIGNAL("scanStarted"), self.delegate, SLOT("startAnimation()"))
        self.connect(self.model, SIGNAL("scanCompleted"), self.delegate, SLOT("stopAnimation()"))
        self.connect(self.model, SIGNAL("scanFailed"), self.delegate, SLOT("stopAnimation()"))
        self.connect(self.model, SIGNAL("scanStarted"), lambda : self.rescanButton.setEnabled(False))
        self.connect(self.model, SIGNAL("scanCompleted"), lambda : self.rescanButton.setEnabled(True))
        self.connect(self.model, SIGNAL("scanFailed"), lambda : self.rescanButton.setEnabled(True))
        
        self.model.scanStart()

    def showContextMenu(self,  pos):
        index =  self.deviceView.indexAt(pos)
        if not index.isValid():
            return
        
        item = self.deviceView.model().data(index,  DeviceRoles.DeviceRole)
        if not item.isValid():
            return
            
        device = item.toPyObject()
        
        menu = QMenu(self)

        sendPythonAction_Py14 = QAction(self.tr("Send Python SIS file to device (PyS60 1.4)"),  menu)
        sendApplicationAction_Py14 = QAction(self.tr("Send Application SIS file to device (PyS60 1.4)"),  menu)
        sendPythonAction_Py20 = QAction(self.tr("Send Python SIS file to device (PyS60 2.0)"),  menu)
        sendApplicationAction_Py20 = QAction(self.tr("Send Application SIS file to device (PyS60 2.0)"),  menu)

        sendPythonAction_Py14.setEnabled(lib.obex_wrapper.FOUND_OBEX)
        sendApplicationAction_Py14.setEnabled(lib.obex_wrapper.FOUND_OBEX)
        sendPythonAction_Py20.setEnabled(lib.obex_wrapper.FOUND_OBEX)
        sendApplicationAction_Py20.setEnabled(lib.obex_wrapper.FOUND_OBEX)

        menu.addAction(sendPythonAction_Py14)
        menu.addAction(sendApplicationAction_Py14)
        menu.addAction(sendPythonAction_Py20)
        menu.addAction(sendApplicationAction_Py20)

        self.connect(sendPythonAction_Py14,  SIGNAL("triggered()"),
                                lambda : self.sendFile(device, self.main.pythonSis_Py14))
        self.connect(sendApplicationAction_Py14,  SIGNAL("triggered()"),
                                lambda : self.sendFile(device, self.main.applicationSis_Py14))
        self.connect(sendPythonAction_Py20,  SIGNAL("triggered()"),
                                lambda : self.sendFile(device, self.main.pythonSis_Py20))
        self.connect(sendApplicationAction_Py20,  SIGNAL("triggered()"),
                                lambda : self.sendFile(device, self.main.applicationSis_Py20))

        menu.popup(QCursor.pos())
    
    def sendFile(self,  device,  sis):
        self.scanStop()
        self.helper.sendFile(self,  device,  sis)

    def scanStop(self):
        self.model.scanStop()

class DeviceViewWidget(_DeviceWidget):
    def __init__(self,  parent):
        super(DeviceViewWidget,  self).__init__(parent)
        
        self.model = lib.devicemodel.DeviceViewModel()
        self.deviceView.setModel(self.model)
    
    def reset(self):
        self.model.reset()
    
    def devices(self):
        return self.model.devices()
    
    def addDevice(self,  device):
        self.model.addDevice(device)

    def removeDevice(self,  device):
        self.model.removeDevice(device)

    def addDevices(self,  devicelist):
        self.model.addDevices(devicelist)

    def removeDevices(self,  devicelist):
        self.model.removeDevices(devicelist)

class DeviceDatabaseViewCombobox(QComboBox):
    def __init__(self,  parent):
        super(DeviceDatabaseViewCombobox,  self).__init__(parent)
        
        # HACK: We need Main()
        main = qApp.property("main").toPyObject()
        
        self.main = main
        self.settings = main.settings
        self.database = main.database
        
        self.connect(self.settings,  SIGNAL("reloadSettings"),  self.addDevices)
        
        self.delegate = lib.delegate_device.DeviceDelegate(self)
        self.model = lib.devicemodel.DeviceViewModel()
        
        self.setItemDelegate(self.delegate)
        self.setModel(self.model)
        
        self.addDevices()
    
    def addDevices(self):
        self.model.reset()
        for device in self.database.devices():
            self.model.addDevice(device)
        
        last = self.settings.setting("bluetooth/lastName")
        row = self.findText(last)
        if not row == -1:
            self.setCurrentIndex(row)

    def selectDevice(self, device):
        for i in range(self.count()):
           data = self.itemData(i, DeviceRoles.DeviceRole)
           if data.isValid() and data.toPyObject() == device:
              self.setCurrentIndex(i)

    def currentDevice(self):
        elementType = self.itemData(self.currentIndex(),  DeviceRoles.TypeRole).toPyObject()
        if elementType != lib.devicemodel.DeviceTypes.Device:
            return None
        
        device = self.itemData(self.currentIndex(),  DeviceRoles.DeviceRole).toPyObject()
        return device
