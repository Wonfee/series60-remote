# -*- coding: utf-8 -*-

# File imagewidget.cpp originally taken from the KAddressBook KDE project.
# Copyright (c) 2003 Tobias Koenig <tokoe@kde.org>
# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import base64
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import window.pixmap_region_selector_dialog

class ImageLoader(QObject):
    def __init__(self,  parent=None):
        super(ImageLoader,  self).__init__(parent)

        self.__parent = parent

    def loadPicture(self,  url):
        pixmap = QPixmap()

        if url.isEmpty():
            return pixmap

        image = QImage()
        
        #if not image.load(url.toLocalFile()): # this seems to be broken on windows
        if not image.load(url.toString()):
            QMessageBox.information(None,
                self.trUtf8("Image not found"),
                self.trUtf8("""This contact's image cannot be found."""))
            return pixmap

        pixmap = pixmap.fromImage(image)
        region = window.pixmap_region_selector_dialog.PixmapRegionSelectorDialog(self.__parent).getSelectedImage(pixmap,  (72,  96),  self.__parent)

        if region.isNull():
            return pixmap

        if region.height() != 96 or region.width() != 72:
            if region.height() > region.width():
                region = region.scaledToHeight(96)
            else:
               region = region.scaledToWidth(72)

        return pixmap.fromImage(region)

class ImageButton(QPushButton):
    def __init__(self,  parent):
        super(ImageButton,  self).__init__(parent)

        self.__parent = parent

        self.__readOnly = False
        self.__imageLoader = ImageLoader(self)
        self.__picture = QPixmap()
        self.__data = str()
        self.__dragStartPos = QPoint()

        self.setAcceptDrops(True)
        self.setIconSize( QSize( 72*1.2, 96*1.2 ) )

        self.updateGui()

        self.connect(self, SIGNAL("clicked()"), self.load)

    def parent(self):
        return self.__parent

    def setReadOnly(self,  readOnly):
        self.__readOnly = readOnly

    def setPicture(self,  picture,  data=None):
        self.__picture = picture
        if not data:
            bytes = QByteArray()
            buffer = QBuffer(bytes)
            buffer.open(QIODevice.WriteOnly)
            picture.save(buffer,  "JPEG")

            data = str(bytes.data())
            data = base64.encodestring(data).replace('\n',  '')

        self.__data = data

    def picture(self):
        return self.__picture

    def data(self):
        return self.__data

    def setImageLoader(self,  loader):
        self.__imageLoader = loader

    def startDrag(self):
        if not self.__picture.isNull():
            drag = QDrag(self)
            drag.setMimeData(QMimeData())
            drag.mimeData().setImageData(QVariant(self.__picture.toImage()))
            drag.start()

    def updateGui(self):
        if self.__picture.isNull():
            self.setIcon(QIcon(":/user-identity"))
        else:
            self.setIcon(QIcon(self.__picture))

    def dragEnterEvent(self,  event):
        md = event.mimeData()
        event.setAccepted(md.hasImage() or md.hasUrls())

    def dropEvent(self,  event):
        if self.__readOnly:
            return

        md = event.mimeData()
        if md.hasImage():
            image = QImage(md.imageData())
            self.__picture.fromImage(image)

            self.updateGui()
            self.emit(SIGNAL("changed()"))

        urls = md.urls()
        if not urls:
            # oops, no data
            event.setAccepted(False)
        else:
            if self.__imageLoader:
                pic = self.__imageLoader.loadPicture(urls[0])
                if not pic.isNull():
                    self.setPicture(pic)
                    self.updateGui()
                    self.emit(SIGNAL("changed()"))

    def mousePressEvent(self,  event):
        self.__dragStartPos = QPoint(event.pos())
        QPushButton.mousePressEvent(self,  event)

    def mouseMoveEvent(self,  event):
        if (event.buttons() & Qt.LeftButton) and (event.pos() - self.__dragStartPos).manhattanLength() > QApplication.startDragDistance():
            self.startDrag()

    def contextMenuEvent(self,  event):
        menu = QMenu()
        menu.addAction(self.tr("Reset"),  self,  SLOT("clear()"))
        menu.exec_(event.globalPos())

    def load(self):
        if self.__readOnly:
            return

        url = QUrl(QFileDialog.getOpenFileName(self,  self.tr("Open Image"),  QString(),  self.tr("Images (*.png *.xpm *.jpg)")))
        if url.isValid():
            if self.__imageLoader:
                pic = self.__imageLoader.loadPicture(url)
                if not pic.isNull():
                    self.setPicture(pic)
                    self.updateGui()
                    self.emit(SIGNAL("changed()"))

    @pyqtSignature("")
    def clear(self):
        self.setPicture(QPixmap())
        self.updateGui()
        self.emit(SIGNAL("changed()"))
