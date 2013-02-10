# -*- coding: utf-8 -*-

# File imagewidget.cpp originally taken from the KDE libraries.
# Copyright (c) 2004 Antonio Larrosa <larrosa@kde.org>
# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.classes import Enum

CursorState = Enum("None_ Resizing Moving")
RotateDirection = Enum("Rotate90 Rotate180 Rotate270")

class PixmapRegionSelectorWidget(QWidget):
    def __init__(self,  parent=None):
        super(PixmapRegionSelectorWidget,  self).__init__(parent)

        self.__state = CursorState.None_

        self.__unzoomedPixmap = QPixmap()
        self.__originalPixmap = QPixmap()
        self.__linedPixmap = QPixmap()
        self.__selectedRegion = QRect()
        self.__label = QLabel(self)


        self.__tempFirstClick = QPoint()
        self.__normalAspectRatio = 1.0
        self.__forcedAspectRatio = 1.0

        self.__maxWidth = int()
        self.__maxHeight = int()
        self.__zoomFactor = 1.0

        self.__rubberBand = QRubberBand(QRubberBand.Rectangle, self.__label)
        self.__rubberBand.hide()

        hboxLayout = QHBoxLayout(self)
        hboxLayout.addStretch()

        vboxLayout = QVBoxLayout()
        hboxLayout.addItem(vboxLayout)

        vboxLayout.addStretch()
        self.__label.setAttribute(Qt.WA_NoSystemBackground, True) #setBackgroundMode( Qt.NoBackground )
        self.__label.installEventFilter(self)

        vboxLayout.addWidget(self.__label)
        vboxLayout.addStretch()

        hboxLayout.addStretch()

    def pixmap(self):
        return self.__unzoomedPixmap

    def setPixmap(self,  pixmap):
        assert not pixmap.isNull()   # This class isn't designed to deal with null pixmaps.
        self.__originalPixmap = QPixmap(pixmap)
        self.__unzoomedPixmap = QPixmap(pixmap)
        self.__label.setPixmap(pixmap)
        self.resetSelection()

    def resetSelection(self):
        self.__selectedRegion = QRect(self.__originalPixmap.rect())
        self.__rubberBand.hide()
        self.__updatePixmap()

    def selectedRegion(self):
        return self.__selectedRegion

    def setSelectedRegion(self,  rect):
        if not rect.isValid():
            self.resetSelection()
        else:
            self.__selectedRegion = rect
            self.__updatePixmap()

    def __updatePixmap(self):
        assert not self.__originalPixmap.isNull()
        if self.__selectedRegion.width() > self.__originalPixmap.width():
            self.__selectedRegion.setWidth( self.__originalPixmap.width() )
        if self.__selectedRegion.height() > self.__originalPixmap.height():
            self.__selectedRegion.setHeight( self.__originalPixmap.height() )

        painter = QPainter()
        if self.__linedPixmap.isNull():
            self.__linedPixmap = QPixmap(self.__originalPixmap)
            p = QPainter(self.__linedPixmap)
            p.setCompositionMode(QPainter.CompositionMode_SourceAtop)
            p.fillRect(self.__linedPixmap.rect(), QColor(0, 0, 0, 100))

        pixmap = QPixmap(self.__linedPixmap)
        painter.begin(pixmap)
        painter.drawPixmap(self.__selectedRegion.topLeft(), self.__originalPixmap,  self.__selectedRegion)
        painter.end()

        self.__label.setPixmap(pixmap)

        qApp.sendPostedEvents(None, QEvent.LayoutRequest)

        if self.__selectedRegion == self.__originalPixmap.rect():
            self.__rubberBand.hide()
        else:
            self.__rubberBand.setGeometry(QRect(self.__selectedRegion.topLeft(),  self.__selectedRegion.size()))

            if self.__state != CursorState.None_:
                self.__rubberBand.show()

    def createPopupMenu(self):
        popup = QMenu(self)
        popup.addAction(QIcon(":/object-rotate-right"),  self.tr("&Rotate Clockwise"),  self,  SLOT("rotateClockwise()"))
        popup.addAction(QIcon(":/object-rotate-left"),  self.tr("Rotate &Counterclockwise"),  self,  SLOT("rotateCounterClockwise()"))
        return popup

    def rotate(self,  direction):
        w = self.__originalPixmap.width()
        h = self.__originalPixmap.height()

        img = self.__unzoomedPixmap.toImage()

        if direction == RotateDirection.Rotate90:
            img = img.transformed(QTransform().rotate(90.0))
        elif direction == RotateDirection.Rotate180:
            img = img.transformed(QTransform().rotate(180.0))
        else:
            img = img.transformed(QTransform().rotate(270.0))

        self.__unzoomedPixmap = QPixmap.fromImage(img)

        img = self.__originalPixmap.toImage()
        if direction == RotateDirection.Rotate90:
            img = img.transformed(QTransform().rotate(90.0))
        elif direction == RotateDirection.Rotate180:
            img = img.transformed(QTransform().rotate(180.0))
        else:
            img = img.transformed(QTransform().rotate(270.0))

        self.__originalPixmap = QPixmap(QPixmap.fromImage(img))
        self.__linedPixmap = QPixmap()

        if self.__forcedAspectRatio > 0 and self.__forcedAspectRatio != 1:
            self.resetSelection()
        else:
            if direction == RotateDirection.Rotate90:
                x = h - self.__selectedRegion.y() - self.__selectedRegion.height()
                y = self.__selectedRegion.x()
                self.__selectedRegion.setRect(x, y, self.__selectedRegion.height(), self.__selectedRegion.width() )
                self.__updatePixmap()
            elif direction == RotateDirection.Rotate270:
                x = self.__selectedRegion.y()
                y = self.__selectedRegion.x() - self.__selectedRegion.width()
                self.__selectedRegion.setRect(x, y, self.__selectedRegion.height(), self.__selectedRegion.width() )
                self.__updatePixmap()
            else:
                self.resetSelection()

    @pyqtSignature("")
    def rotateClockwise(self):
        self.rotate(RotateDirection.Rotate90)

    @pyqtSignature("")
    def rotateCounterClockwise(self):
        self.rotate(RotateDirection.Rotate270)

    def eventFilter(self,  obj,  ev):
        if ev.type() == QEvent.MouseButtonPress:
            mev = QMouseEvent(ev)
            if mev.button() == Qt.RightButton:
                popup = self.createPopupMenu()
                popup.exec_(mev.globalPos())
                return True

            cursor = QCursor()

            if self.__selectedRegion.contains(mev.pos()) and self.__selectedRegion != self.__originalPixmap.rect():
                self.__state = CursorState.Moving
                cursor.setShape( Qt.SizeAllCursor )
                self.__rubberBand.show()
            else:
                self.__state = CursorState.Resizing
                cursor.setShape( Qt.CrossCursor )

            QApplication.setOverrideCursor(cursor)
            self.__tempFirstClick = QPoint(mev.pos())

            return True

        if ev.type() == QEvent.MouseMove:
            mev = QMouseEvent(ev)

            if self.__state == CursorState.Resizing:
                self.setSelectedRegion(self.__calcSelectionRectangle(self.__tempFirstClick,  QPoint(mev.pos())))
            elif self.__state == CursorState.Moving:
                mevx = mev.x()
                mevy = mev.y()

                mouseOutside = False

                if mevx < 0:
                    self.__selectedRegion.translate(-self.__selectedRegion.x(),  0)
                    mouseOutside = True
                elif mevx > self.__originalPixmap.width():
                    self.__selectedRegion.translate(self.__originalPixmap.width() - self.__selectedRegion, width() - self.__selectedRegion.x(),  0)
                    mouseOutside = True
                if mevy < 0:
                    self.__selectedRegion.translate(0,  -self.__selectedRegion.y())
                    mouseOutside = True
                elif mevy > self.__originalPixmap.height():
                    self.__selectedRegion.translate(0,  self.__originalPixmap.height() - self.__selectedRegion.height() - self.__selectedRegion.y())
                    mouseOutside = True

                if mouseOutside:
                    self.__updatePixmap()
                    return True

                self.__selectedRegion.translate( mev.x() - self.__tempFirstClick.x(), mev.y() - self.__tempFirstClick.y() )

                # Check that the region has not fallen outside the image
                if self.__selectedRegion.x() < 0:
                    self.__selectedRegion.translate(-self.__selectedRegion.x(),  0)
                elif self.__selectedRegion.right() > self.__originalPixmap.width():
                    self.__selectedRegion.translate(-(self.__selectedRegion.right() - self.__originalPixmap.width()),  0)

                if (self.__selectedRegion.y() < 0):
                    self.__selectedRegion.translate(0,  -self.__selectedRegion.y())
                elif self.__selectedRegion.bottom() > self.__originalPixmap.height():
                    self.__selectedRegion.translate(0,  -(self.__selectedRegion.bottom() - self.__originalPixmap.height()))

                self.__tempFirstClick = QPoint(mev.pos())
                self.__updatePixmap()

            return True

        if ev.type() == QEvent.MouseButtonRelease:
            mev = QMouseEvent(ev)

            if self.__state == CursorState.Resizing and mev.pos() == self.__tempFirstClick:
                self.resetSelection()

            self.__state = CursorState.None_
            QApplication.restoreOverrideCursor()
            self.__rubberBand.hide()
            return True

        QWidget.eventFilter(self,  obj,  ev)
        return False

    def __calcSelectionRectangle(self,  startPoint,  _endPoint):
        endPoint = QPoint(_endPoint)

        if endPoint.x() < 0:
            endPoint.setX(0)
        elif endPoint.x() > self.__originalPixmap.width():
            endPoint.setX(self.__originalPixmap.width())

        if endPoint.y() < 0:
            endPoint.setY(0)
        elif endPoint.y() > self.__originalPixmap.height():
            endPoint.setY(self.__originalPixmap.height())

        w = abs(startPoint.x() - endPoint.x())
        h = abs(startPoint.y() - endPoint.y())

        if w == 0 or h == 0:
            return QRect(0,  0,  0,  0)

        if self.__forcedAspectRatio > 0:
            aspectRatio = w / float(h)

            if aspectRatio > self.__forcedAspectRatio:
                h = int(w / self.__forcedAspectRatio)
            else:
                w = int(h * self.__forcedAspectRatio)

        if startPoint.x() < endPoint.x():
            x = startPoint.x()
        else:
            x = startPoint.x() - w
        if startPoint.y() < endPoint.y():
            y = startPoint.y()
        else:
            y = startPoint.y()-h

        if x < 0:
            w += x
            x = 0
            h = int(w / self.__forcedAspectRatio)

            if startPoint.y() > endPoint.y():
                y = startPoint.y() - h

        elif x + w > self.__originalPixmap.width():
            w = self.__originalPixmap.width() - x
            h = int(w / self.__forcedAspectRatio)

            if startPoint.y() > endPoint.y():
                y = startPoint.y() - h

        if y < 0:
            h += y
            y = 0
            w = int(h * self.__forcedAspectRatio)

            if startPoint.x() > endPoint.x():
                x = startPoint.x() - w

        elif (y + h > self.__originalPixmap.height()):
            h = self.__originalPixmap.height() - y
            w = int(h * self.__forcedAspectRatio)

            if startPoint.x() > endPoint.x():
                x = startPoint.x() - w

        return QRect(x,  y,  w,  h)

    def unzoomedSelectedRegion(self):
            return QRect( int(self.__selectedRegion.x() / self.__zoomFactor),
                                    int(self.__selectedRegion.y() / self.__zoomFactor),
                                    int(self.__selectedRegion.width() / self.__zoomFactor),
                                    int(self.__selectedRegion.height() / self.__zoomFactor))

    def selectedImage(self):
        origImage = self.__unzoomedPixmap.toImage()
        return origImage.copy(self.unzoomedSelectedRegion())

    @pyqtSignature("int, int")
    def setSelectionAspectRatio(self,  width,  height):
        self.__forcedAspectRatio = width / float(height)
        self.__normalAspectRatio = self.__forcedAspectRatio

    @pyqtSignature("")
    def setLandscapeFormatSelectionAspectRatio(self):
        if self.__forcedAspectRatio < 1:
            self.__forcedAspectRatio = 1/self.__normalAspectRatio
        self.resetSelection()

    @pyqtSignature("")
    def setPortraitFormatSelectionAspectRatio(self):
        if self.__forcedAspectRatio > 1:
            self.__forcedAspectRatio = self.__normalAspectRatio
        self.resetSelection()

    @pyqtSignature("")
    def setFreeSelectionAspectRatio(self):
        self.__forcedAspectRatio = 0
        self.resetSelection()

    def setMaximumWidgetSize(self,  width,  height):
        self.__maxWidth = width
        self.__maxHeight = height

        self.__originalPixmap = QPixmap(self.__unzoomedPixmap)

        if self.__selectedRegion == self.__originalPixmap.rect():
            self.__selectedRegion = QRect()

        if not self.__originalPixmap.isNull() and (self.__originalPixmap.width() > self.__maxWidth or self.__originalPixmap.height() > self.__maxHeight):
            # We have to resize the pixmap to get it complete on the screen
            image = self.__originalPixmap.toImage()
            self.__originalPixmap = QPixmap.fromImage( image.scaled( width, height, Qt.KeepAspectRatio,Qt.SmoothTransformation ) )
            oldZoomFactor = self.__zoomFactor
            self.__zoomFactor = self.__originalPixmap.width() / float(self.__unzoomedPixmap.width())

            if self.__selectedRegion.isValid():
                self.__selectedRegion = QRect(int(self.__selectedRegion.x() * self.__zoomFactor / oldZoomFactor),
                                                                int(self.__selectedRegion.y() * self.__zoomFactor / oldZoomFactor),
                                                                int(self.__selectedRegion.width() * self.__zoomFactor / oldZoomFactor),
                                                                int(self.__selectedRegion.height() * self.__zoomFactor / oldZoomFactor) )

        if not self.__selectedRegion.isValid():
            self.__selectedRegion = self.__originalPixmap.rect()

        self.__linedPixmap = QPixmap()
        self.__updatePixmap()
        self.resize(self.__label.width(),  self.__label.height())
