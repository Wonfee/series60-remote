# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from lib.classes import *

DeviceRoles = Enum("TypeRole DeviceRole ErrorMessageRole",  beginning=Qt.UserRole+10)
DeviceTypes = Enum("Scanning Error NotScanned NoDevicesFound NoDevicesSelected Device")

class _DeviceModel(QAbstractListModel,  QObject):
    def __init__(self,  scanModel):
        super(_DeviceModel, self).__init__()
        
        # HACK: We need Main()
        main = qApp.property("main").toPyObject()
        
        self.__devices = []
        self.__scanModel = scanModel
        
        self.__scanning = False
        self.__scanError = False
        self.__scanErrorMessage = ""
        self.__scanFinished = False
        
        if self.__scanModel:
            self.connection = main.connection
            
            self.connect(self.connection,  SIGNAL("scanStarted"), self.__scanStarted)
            self.connect(self.connection,  SIGNAL("foundDevice"), self.__scanFoundDevice)
            self.connect(self.connection,  SIGNAL("scanFailed"), self.__scanFailed)
            self.connect(self.connection,  SIGNAL("scanCompleted"), self.__scanCompleted)
    
    @pyqtSignature("")
    def scanStart(self):
        if self.__scanModel:
            self.reset()
            self.connection.scan()
        else:
            raise NotImplementedError()

    @pyqtSignature("")
    def scanStop(self):
        if self.__scanModel:
            self.connection.scanStop()
        else:
            raise NotImplementedError()

    def __scanStarted(self):
        self.__devices = []
        self.__scanning = True
        self.__scanError = False
        self.__scanErrorMessage = ""
        
        self.emit(SIGNAL("scanStarted"))
        self.emit(SIGNAL("layoutChanged()"))

    def __scanFoundDevice(self,  addr,  name,  deviceClass = None):
        device = Device(name = name,  bluetoothAddress = addr,  deviceClass = deviceClass)
        self.addDevice(device)
        self.emit(SIGNAL("scanFoundDevice"),  device)
            
    def __scanFailed(self,  message):
        self.__devices = []
        self.__scanning = False
        self.__scanError = True
        self.__scanErrorMessage = message
        self.__scanFinished = True
        
        self.emit(SIGNAL("scanFailed"))
        self.emit(SIGNAL("layoutChanged()"))

    def __scanCompleted(self):
        self.__scanning = False
        self.__scanError = False
        self.__scanErrorMessage = ""
        self.__scanFinished = True
        
        self.emit(SIGNAL("scanCompleted"))
        self.emit(SIGNAL("layoutChanged()"))
    
    def devices(self):
        return self.__devices
    
    def addDevice(self,  device):
        if device in self.__devices:
            return
        self.__devices.append(device)
        self.emit(SIGNAL("layoutChanged()"))
        
    def addDevices(self,  devicelist):
        for device in devicelist:
            self.addDevice(device)
    
    def removeDevice(self,  device):
        self.__devices.remove(device)
        self.emit(SIGNAL("layoutChanged()"))
    
    def removeDevices(self,  devicelist):
        for device in devicelist:
            self.removeDevice(device)
    
    def reset(self):
        self.__devices = []
        self.__scanning = False
        self.__scanError = False
        self.emit(SIGNAL("layoutChanged()"))
    
    def majorClass(self,  deviceClass):
        # Return the major class grouping of the bluetooth device
        # Bits 7 ... 2
        return deviceClass >> 8 & 0x1f
    
    def minorClass(self,  deviceClass):
        # Return the major class grouping of the bluetooth device
        # Bits 12 ... 8
        return deviceClass >> 2 & 0x2f
    
    def classToTuple(self,  deviceClass):
        major = self.majorClass(deviceClass)
        minor = self.minorClass(deviceClass)
        
        majorString = QCoreApplication.translate("DeviceModel",  "unknown")
        minorString = QCoreApplication.translate("DeviceModel",  "unknown")
        image = QIcon(":/device-class-unknown")
        
        if major == 0x00:
            # Miscellaneous
            majorString = QCoreApplication.translate("DeviceModel",  "Miscellaneous")
        
        elif major == 0x01:
            # Computer
            majorString = QCoreApplication.translate("DeviceModel",  "Computer")
            image = QIcon(":/device-class-computer")
            
            if minor == 0x01:
                minorString = QCoreApplication.translate("DeviceModel",  "Desktop workstation")
            elif minor == 0x02:
                minorString = QCoreApplication.translate("DeviceModel",  "Server-class computer")
            elif minor == 0x03:
                minorString = QCoreApplication.translate("DeviceModel",  "Laptop")
                image = QIcon(":/device-class-laptop")
            elif minor == 0x04:
                minorString = QCoreApplication.translate("DeviceModel",  "Handheld PC/PDA")
                image = QIcon(":/device-class-pda")
            elif minor == 0x05:
                minorString = QCoreApplication.translate("DeviceModel",  "Palm sized PC/PDA")
                image = QIcon(":/device-class-pda")
            elif minor == 0x06:
                minorString = QCoreApplication.translate("DeviceModel",  "Wearable computer")
                image = QIcon(":/device-class-openmoko")
            
        elif major == 0x02:
            # Phone
            majorString = QCoreApplication.translate("DeviceModel",  "Phone")
            image = QIcon(":/phone")
            
            if minor == 0x01:
                minorString = QCoreApplication.translate("DeviceModel",  "Cellular")
            elif minor == 0x02:
                minorString = QCoreApplication.translate("DeviceModel",  "Cordless")
            elif minor == 0x03:
                minorString = QCoreApplication.translate("DeviceModel",  "Smart phone")
            elif minor == 0x04:
                minorString = QCoreApplication.translate("DeviceModel",  "Wired modem or voice gateway")
                image = QIcon(":/device-class-modem")
            elif minor == 0x05:
                minorString = QCoreApplication.translate("DeviceModel",  "Common ISDN Access")
                image = QIcon(":/device-class-modem")
        
        elif major == 0x03:
            # LAN
            majorString = QCoreApplication.translate("DeviceModel",  "LAN")
            image = QIcon(":/device-class-network")
            
            minor = minor >> 3
            if minor == 0x00:
                minorString = QCoreApplication.translate("DeviceModel",  "Fully available")
                image = QIcon(":/device-class-network-100")
            elif minor == 0x01:
                minorString = QCoreApplication.translate("DeviceModel",  "1 - 17% utilized")
                image = QIcon(":/device-class-network-75")
            elif minor == 0x02:
                minorString = QCoreApplication.translate("DeviceModel",  "17 - 33% utilized")
                image = QIcon(":/device-class-network-50")
            elif minor == 0x03:
                minorString = QCoreApplication.translate("DeviceModel",  "33 - 50% utilized")
            elif minor == 0x04:
                minorString = QCoreApplication.translate("DeviceModel",  "50 - 67% utilized")
            elif minor == 0x05:
                minorString = QCoreApplication.translate("DeviceModel",  "67 - 83% utilized")
            elif minor == 0x06:
                minorString = QCoreApplication.translate("DeviceModel",  "83 - 99% utilized")
            elif minor == 0x07:
                minorString = QCoreApplication.translate("DeviceModel",  "No service available")
            
        elif major == 0x04:
            # Audio/Video
            majorString = QCoreApplication.translate("DeviceModel",  "Audio/Video")
            image = QIcon(":/device-class-audio-video")
            
            if minor == 0x01:
                minorString = QCoreApplication.translate("DeviceModel",  "Wearable Headset Device")
                image = QIcon(":/device-class-audio-headset")
            elif minor == 0x02:
                minorString = QCoreApplication.translate("DeviceModel",  "Hands-free Device")
                image = QIcon(":/device-class-audio-input")
            elif minor == 0x03:
                minorString = QCoreApplication.translate("DeviceModel",  "(Reserved)")
            elif minor == 0x04:
                minorString = QCoreApplication.translate("DeviceModel",  "Microphone")
                image = QIcon(":/device-class-audio-microphone")
            elif minor == 0x05:
                minorString = QCoreApplication.translate("DeviceModel",  "Loudspeakers")
                image = QIcon(":/device-class-audio-input")
            elif minor == 0x06:
                minorString = QCoreApplication.translate("DeviceModel",  "Headphone")
                image = QIcon(":/device-class-audio-headset")
            elif minor == 0x07:
                minorString = QCoreApplication.translate("DeviceModel",  "Portable audio")
                image = QIcon(":/device-class-audio-card")
            elif minor == 0x08:
                minorString = QCoreApplication.translate("DeviceModel",  "Car audio")
                image = QIcon(":/device-class-audio-card")
            elif minor == 0x09:
                minorString = QCoreApplication.translate("DeviceModel",  "Set-top box")
                image = QIcon(":/device-class-audio-card")
            elif minor == 0x0A:
                minorString = QCoreApplication.translate("DeviceModel",  "HiFi Audio Device")
                image = QIcon(":/device-class-audio-card")
            elif minor == 0x0B:
                minorString = QCoreApplication.translate("DeviceModel",  "VCR")
                image = QIcon(":/device-class-audio-card")
            elif minor == 0x0C:
                minorString = QCoreApplication.translate("DeviceModel",  "Video Camera")
            elif minor == 0x0D:
                minorString = QCoreApplication.translate("DeviceModel",  "Camcorder")
            elif minor == 0x0E:
                minorString = QCoreApplication.translate("DeviceModel",  "Video Monitor")
                image = QIcon(":/device-class-video-television")
            elif minor == 0x0F:
                minorString = QCoreApplication.translate("DeviceModel",  "Video Display and Loudspeaker")
                image = QIcon(":/device-class-video-television")
            elif minor == 0x10:
                minorString = QCoreApplication.translate("DeviceModel",  "Video Conferencing")
                image = QIcon(":/device-class-camera-web")
            elif minor == 0x11:
                minorString = QCoreApplication.translate("DeviceModel",  "(Reserved)")
            elif minor == 0x12:
                minorString = QCoreApplication.translate("DeviceModel",  "Gaming/Toy")
                image = QIcon(":/device-class-gaming")
    
        elif major == 0x05:
            # Peripheral
            majorString = QCoreApplication.translate("DeviceModel",  "Peripheral")
            
            h = minor >> 4
            l = minor & 0xf
            
            if h == 0x01:
                hString = QCoreApplication.translate("DeviceModel",  "Keyboard")
                image = QIcon(":/device-class-input-keyboard")
            elif h == 0x02:
                hString = QCoreApplication.translate("DeviceModel",  "Pointing device")
                image = QIcon(":/device-class-input-mouse")
            elif h == 0x03:
                hString = QCoreApplication.translate("DeviceModel",  "Combo keyboard/pointing device")
                image = QIcon(":/device-class-input-keyboard")
            
            if l == 0x01:
                lString = QCoreApplication.translate("DeviceModel",  "Joystick")
            elif l == 0x02:
                lString = QCoreApplication.translate("DeviceModel",  "Gamepad")
                image = QIcon(":/device-class-gaming")
            elif l == 0x03:
                lString = QCoreApplication.translate("DeviceModel",  "Remote control")
            elif l == 0x04:
                lString = QCoreApplication.translate("DeviceModel",  "Sensing device")
            elif l == 0x05:
                lString = QCoreApplication.translate("DeviceModel",  "Digitizer tablet")
                image = QIcon(":/device-class-input-tablet")
            elif l == 0x06:
                lString = QCoreApplication.translate("DeviceModel",  "Card Reader")
                image = QIcon(":/media-flash-sd-mmc")
            
            if hString and lString:
                minorString = hString + " + " + lString
            elif hString:
                minorString = hString
            elif lString:
                minorString = lString
            
        elif major == 0x06:
            # Imaging
            majorString = QCoreApplication.translate("DeviceModel",  "Imaging")
            minor = minor >> 2
            device = []
            if minor & 0x01:
                device.append(unicode(QCoreApplication.translate("DeviceModel",  "Display")))
                image = QIcon(":/device-class-video-display")
            if minor & 0x02:
                device.append(unicode(QCoreApplication.translate("DeviceModel",  "Camera")))
                image = QIcon(":/device-class-camera")
            if minor & 0x04:
                device.append(unicode(QCoreApplication.translate("DeviceModel",  "Scanner")))
                image = QIcon(":/device-class-scanner")
            if minor & 0x08:
                device.append(unicode(QCoreApplication.translate("DeviceModel",  "Printer")))
                image = QIcon(":/device-class-printer")
            
            minorString = ", ".join(device)
            
        elif major == 0x07:
            # Wearable
            majorString = QCoreApplication.translate("DeviceModel",  "Wearable")
            if minor == 0x01:
                minorString = QCoreApplication.translate("DeviceModel",  "Wrist Watch")
            elif minor == 0x02:
                minorString = QCoreApplication.translate("DeviceModel",  "Pager")
            elif minor == 0x03:
                minorString = QCoreApplication.translate("DeviceModel",  "Jacket")
            elif minor == 0x04:
                minorString = QCoreApplication.translate("DeviceModel",  "Helmet")
            elif minor == 0x05:
                minorString = QCoreApplication.translate("DeviceModel",  "Glasses")
        
        elif major == 0x08:
            # Toy
            majorString = QCoreApplication.translate("DeviceModel",  "Toy")
            if minor == 0x01:
                minorString = QCoreApplication.translate("DeviceModel",  "Robot")
            elif minor == 0x02:
                minorString = QCoreApplication.translate("DeviceModel",  "Vehicle")
            elif minor == 0x03:
                minorString = QCoreApplication.translate("DeviceModel",  "Doll / Action Figure")
            elif minor == 0x04:
                minorString = QCoreApplication.translate("DeviceModel",  "Controller")
                image = QIcon(":/device-class-gaming")
            elif minor == 0x05:
                minorString = QCoreApplication.translate("DeviceModel",  "Game")    
                image = QIcon(":/device-class-gaming")
    
        elif major == 0x1f:
            # Uncategorized
            majorString = QCoreApplication.translate("DeviceModel",  "Uncategorized")
    
        return majorString,  minorString,  image
    
    def data (self,  index,  role = Qt.DisplayRole):
        # Show at least one item...
        if not index.isValid() or \
           not max(0 <= index.row() < len(self.__devices)+int(self.__scanning),  1):
            return QVariant()            
        
        if role == Qt.DisplayRole:
            if index.row() == 0:
                if self.__scanning:
                    return QVariant(QCoreApplication.translate("DeviceModel",  "Scan in progress..."))
                elif self.__scanError:
                    return QVariant(QCoreApplication.translate("DeviceModel",  "Scanning failed"))
                elif not self.__scanFinished and self.__scanModel:
                    return QVariant(QCoreApplication.translate("DeviceModel",  "Please start a scan..."))
                elif len(self.__devices) == 0 and self.__scanModel:
                    return QVariant(QCoreApplication.translate("DeviceModel",  "No devices found"))
                elif len(self.__devices) == 0 and not self.__scanModel:
                    return QVariant(QCoreApplication.translate("DeviceModel",  "No devices selected"))
                else:
                    device = index.data(DeviceRoles.DeviceRole).toPyObject()
                    return QVariant(device.name())
            else:
                device = index.data(DeviceRoles.DeviceRole).toPyObject()
                return QVariant(device.name())

        elif role == Qt.DecorationRole:
            if index.row() == 0:
                if self.__scanning:
                    return QVariant(QIcon(":/wait"))
                elif self.__scanError:
                    return QVariant(QIcon(":/dialog-close"))
                elif not self.__scanFinished and self.__scanModel:
                    return QVariant(QIcon(":/wait"))
                elif len(self.__devices) == 0:
                    return QVariant(QIcon(":/dialog-information"))
                else:
                    device = index.data(DeviceRoles.DeviceRole).toPyObject()
                    return QVariant(self.classToTuple(device.deviceClass())[2])
            else:
                device = index.data(DeviceRoles.DeviceRole).toPyObject()
                return QVariant(self.classToTuple(device.deviceClass())[2])
        
        elif role == DeviceRoles.TypeRole:
            if index.row() == 0:
                if self.__scanning:
                    return QVariant(DeviceTypes.Scanning)
                elif self.__scanError:
                    return QVariant(DeviceTypes.Error)
                elif not self.__scanFinished and self.__scanModel:
                    return QVariant(DeviceTypes.NotScanned)
                elif len(self.__devices) == 0 and self.__scanModel:
                    return QVariant(DeviceTypes.NoDevicesFound)
                elif len(self.__devices) == 0 and not self.__scanModel:
                    return QVariant(DeviceTypes.NoDevicesSelected)
                else:
                    return QVariant(DeviceTypes.Device)
            else:
                return QVariant(DeviceTypes.Device)
            
        elif role == DeviceRoles.DeviceRole:
            if ((index.row() == 0 and 
                 not self.__scanning and 
                 not self.__scanError and 
                 (self.__scanFinished or not self.__scanModel)
                 and len(self.__devices) > 0) or
                (1 <= index.row() < len(self.__devices)+int(self.__scanning))):
                    return QVariant(self.__devices[index.row()-int(self.__scanning)])
            else:
                return QVariant()
            
        elif role == DeviceRoles.ErrorMessageRole:
            if self.__scanError:
                return QVariant(self.__scanErrorMessage)
            else:
                return QVariant()
            
        return QVariant()
    
    def rowCount(self,  index = QModelIndex()):
        return max(len(self.__devices)+int(self.__scanning),  1)

class DeviceScanModel(_DeviceModel):
    def __init__(self):
        super(DeviceScanModel, self).__init__(True)

class DeviceViewModel(_DeviceModel):
    def __init__(self):
        super(DeviceViewModel, self).__init__(False)
