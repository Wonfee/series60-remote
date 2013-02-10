# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSvg import *

from lib.devicemodel import DeviceRoles,  DeviceTypes

class DeviceDelegate(QStyledItemDelegate):
    def __init__(self,  parent=None):
        super(DeviceDelegate,  self).__init__(parent)
    
        self.parent = parent
        
        # Display a clock with animated hands during device scan
        # This icon is based on status/user-away.svgz from the KDE Artwork team
        self.scanningAnimation = QSvgRenderer(":/load-1-svg")
        self.frames = self.scanningAnimation.framesPerSecond()
        self.stopAnimation()
    
    @pyqtSignature("")
    def startAnimation(self):
        self.connect(self.scanningAnimation, SIGNAL("repaintNeeded()"),  self.__repaintNeeed)
        self.scanningAnimation.setFramesPerSecond(self.frames)
    
    @pyqtSignature("")
    def stopAnimation(self):
        self.disconnect(self.scanningAnimation, SIGNAL("repaintNeeded()"),  self.__repaintNeeed)
        self.scanningAnimation.setFramesPerSecond(0)
    
    def __repaintNeeed(self):
        self.emit(SIGNAL("needsRedraw()"))
    
    def paint(self,  painter,  option,  index):
        if not index.isValid():
            return
        
        elementType =  index.data(DeviceRoles.TypeRole)
        if not elementType.isValid():
            return
        elementType = elementType.toInt()[0]
        display = index.data(Qt.DisplayRole).toString()
        
        painter.save()
        
        # Draw the background of our item
        QApplication.style().drawPrimitive(QStyle.PE_PanelItemViewItem, QStyleOptionViewItemV4(option), painter,  self.parent)
        
        painter.translate(option.rect.topLeft())
        
        if elementType == DeviceTypes.Scanning:
            # Draw our own animated icon if there is an active scan
            self.scanningAnimation.render(painter,  QRectF(5, 5,  20,  20))
        elif elementType == DeviceTypes.Device:
            # The image should be placed in the middle..
            image = QImage(index.data(Qt.DecorationRole).toPyObject().pixmap(32,  32))
            x = 5
            y = self.sizeHint(option,  index).height()/2.0  - image.height() / 2.0
            painter.drawImage(QRectF(x, y,  32,  32),  image)
        else:
            image = QImage(index.data(Qt.DecorationRole).toPyObject().pixmap(20,  20))
            x = 5
            y = self.sizeHint(option,  index).height()/2.0  - image.height() / 2.0
            painter.drawImage(QRectF(x, y,  20,  20),  image)
        
        if QApplication.style().inherits("QWindowsStyle") and option.state & QStyle.State_Selected \
            and not option.state & QStyle.State_HasFocus:
            painter.setPen(option.palette.color(QPalette.Normal, QPalette.Text))
        elif option.state & QStyle.State_Selected:
            painter.setPen(option.palette.color(QPalette.Normal, QPalette.HighlightedText))
            painter.setBrush(option.palette.highlight())
        else:
            painter.setPen(option.palette.color(QPalette.Normal, QPalette.Text))

        f = painter.font()
        
        if elementType == DeviceTypes.Error:
            error = index.data(DeviceRoles.ErrorMessageRole).toString()
            
            painter.drawText(5 + 20 + 10,  5 + 1 * QFontMetrics(f).height() - QFontMetrics(f).descent(),  display)
            
            f.setItalic(True)
            painter.setFont(f)
            
            pen = painter.pen()
            pen.setColor(pen.color().lighter(300))
            painter.setPen(pen)
            
            painter.drawText(5 + 20 + 10,  5 + 2 * QFontMetrics(f).height() - QFontMetrics(f).descent(),  error)
            
        elif elementType == DeviceTypes.Device:
            device = index.data(DeviceRoles.DeviceRole).toPyObject()
            major, minor,  image = index.model(). classToTuple(device.deviceClass())
            
            # We need to subtract the descent of the font, otherwise the text would be lower
            painter.drawText(5 + 32 + 10,  5 + 1 * QFontMetrics(f).height() - QFontMetrics(f).descent(),  device.name())
            
            if f.pixelSize() != -1:
                f.setPixelSize(f.pixelSize() - 1)
            elif f.pointSize() != -1:
                f.setPointSize(f.pointSize() - 1)
            
            f.setItalic(True)
            painter.setFont(f)
            
            pen = painter.pen()
            pen.setColor(pen.color().lighter(300))
            painter.setPen(pen)
            
            painter.drawText(5 + 32 + 10,  5 + 2 * QFontMetrics(f).height() - QFontMetrics(f).descent() + 1,  major + " / " + minor)
            
            painter.setFont(f)
            
            painter.drawText(5 + 32 + 10,  5 + 3 * QFontMetrics(f).height() - QFontMetrics(f).descent() + 1,  device.bluetoothAddress())
        
        else:
            x = 5 + 20 + 10
            y = (self.sizeHint(option,  index).height()/2)  + QFontMetrics(f).height() / 2 - QFontMetrics(f).descent() 
            painter.drawText(x,  y,  display)
        
        painter.restore()
    
    def sizeHint(self,  option,  index):
        elementType = index.data(DeviceRoles.TypeRole)
        if not elementType.isValid():
            return QSize(0, 0)
        
        elementType = elementType.toInt()[0]
        display = index.data(Qt.DisplayRole).toString()
        
        if elementType == DeviceTypes.Device:
            device = index.data(DeviceRoles.DeviceRole).toPyObject()
            major, minor,  image = index.model(). classToTuple(device.deviceClass())
            
            f1 = option.font
            f2 = QFont(f1)
            if f2.pixelSize() != -1:
                f2.setPixelSize(f2.pixelSize() - 1)
            elif f2.pointSize() != -1:
                f2.setPointSize(f2.pointSize() - 1)
            
            f2.setItalic(True)
            
            f3 = QFont(f2)
            f3.setItalic(False)
            
            fm1 = option.fontMetrics
            fm2 = QFontMetrics(f2)
            fm3 = QFontMetrics(f3)
            
            x = 5 + 32 + 10
            y = 5
            
            x += max(
                     fm1.width(device.name()), 
                     fm2.width(device.bluetoothAddress()), 
                     fm3.width(major + " / " + minor)
                    )
            
            x += 10
            
            y += max(
                     fm1.height() + fm2.height() + fm3.height(), 
                     32
                    )
            
            y += 5
            
            return QSize(x,  y)
            
        elif elementType == DeviceTypes.Error:
            error = index.data(DeviceRoles.ErrorMessageRole).toString()
            fontMetrics = option.fontMetrics
            
            font = option.font
            font.setItalic(True)
            fontMetricsItalic = QFontMetrics(font)
            
            x = 5 + 20 + 10
            y = 5
            
            x += max(
                     fontMetrics.width(display), 
                     fontMetricsItalic.width(error)
                    )
            
            x += 10
            
            y += max(
                     fontMetrics.height() + fontMetricsItalic.height(), 
                     20
                    )
            
            y += 5
            
            return QSize(x,  y)
            
        else:
            x = 5 + 20 + 10
            y = 5 + 20 + 5
            
            x += option.fontMetrics.width(display)
            
            x += 10
            
            return QSize(x,  y)
