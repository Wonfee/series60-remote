# -*- coding: utf-8 -*-

# File kdepim/calendarviews/eventviews/month/monthgraphicsitems.cpp originally taken from the KDE project.
# Copyright (c) 2008 Bruno Virlet <bruno.virlet@gmail.com>
# Copyright (c) 2008 Thomas Thrainer <tom_t@gmx.at>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class CalendarGraphicsItem(QGraphicsItem):
    def __init__(self,  manager):
        super(CalendarGraphicsItem,  self).__init__(None,  manager.calendarScene)

        self.__calendarItem = manager
        self.__startDate = QDate()
        self.__daySpan = 0

        self.hide()
        #self.__calendarItem.calendarScene.addItem(self)

        transform = QTransform()
        transform = transform.translate(0.5,  0.5)
        self.setTransform(transform)

    def calendarItem(self):
        return self.__calendarItem

    def boundingRect(self):
        # width - 2 because of the cell-dividing line with width == 1 at beginning and end
        return QRectF(0,  0,  (self.daySpan() + 1) * self.__calendarItem.calendarScene.columnWidth() - 2,
                                self.__calendarItem.calendarScene.itemHeight())

    def widgetPath(self,  border):
        # If border is set we won't draw all the path. Items spanning on multiple
        # rows won't have borders on their boundaries.
        # If this is the mask, we draw it one pixel bigger

        x0 = 0
        y0 = 0
        x1 = int(self.boundingRect().width())
        y1 = int(self.boundingRect().height())

        height = y1 - y0
        beginRound = height / 3

        path = QPainterPath(QPointF(x0 + beginRound, y0))
        if True: #self.isBeginItem():
            path.arcTo(QRectF(x0, y0, beginRound * 2, height), +90, +180)
        else:
            path.lineTo(x0, y0)
            if not border :
                path.lineTo(x0, y1)
            else:
                path.moveTo( x0, y1 );
            path.lineTo(x0 + beginRound, y1)

        if True: #self.isEndItem():
            path.lineTo(x1 - beginRound, y1)
            path.arcTo(QRectF(x1 - 2 * beginRound, y0, beginRound * 2, height), -90, +180 )
        else:
            path.lineTo(x1, y1)
            if not border:
                path.lineTo(x1, y0)
            else:
                path.moveTo(x1, y0)

        # close path
        path.lineTo(x0 + beginRound, y0)

        return path

    def paint(self,  painter,  option,  widget):
        #if not self.__calendarItem.calendarScene.initialized():
        #    print "not initialized"
        #    return

        painter.setRenderHint(QPainter.Antialiasing)

        textMargin = 10

        bgColor = self.__calendarItem.bgColor()
        frameColor = QColor(Qt.black)
        textColor = QColor(Qt.black)

        gradient = QLinearGradient(0, 0, 0, self.boundingRect().height())
        gradient.setColorAt(0,  bgColor)
        gradient.setColorAt(0.7, bgColor.dark(110))
        gradient.setColorAt(1, bgColor.dark(150))
        brush = QBrush(gradient)
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        # Rounded rect without border
        painter.drawPath(self.widgetPath(False))

        # Draw the border without fill
        pen = QPen(frameColor)
        pen.setWidth(2)
        painter.setPen(Qt.NoPen)
        painter.drawPath(self.widgetPath(True))

        painter.setPen(textColor)

        alignFlag = Qt.AlignVCenter
        if self.isBeginItem():
            alignFlag |= Qt.AlignLeft
        elif self.isEndItem():
            alignFlag |= Qt.AlignRight
        else:
            alignFlag |= Qt.AlignHCenter

        text = self.__calendarItem.calendarEntry.content()
        painter.setFont(QFont("Sans serif",  8))

        # Every item should set its own LayoutDirection, or eliding fails miserably
        painter.setLayoutDirection(Qt.LeftToRight) # TODO...

        textRect = QRect(textMargin,  0,
                         int(self.boundingRect().width() - 2*textMargin),
                         self.__calendarItem.calendarScene.itemHeight())

        if True: # enableMonthItemIcons
            icons = self.__calendarItem.icons()
            iconWidths = 0

            for icon in icons:
                iconWidths += icon.width()

            if icons:
                iconWidths += textMargin / 2

            textWidth = painter.fontMetrics().size(0,  text).width()
            if textWidth + iconWidths > textRect.width():
                textWidth = textRect.width() - iconWidths
                text = painter.fontMetrics().elidedText(text,  Qt.ElideRight,  textWidth)

            curXPos = textRect.left()
            if alignFlag & Qt.AlignRight:
                curXPos += textRect.width() - textWidth - iconWidths
            elif alignFlag & Qt.AlignHCenter:
                curXPos += (textRect.width() - textWidth - iconWidths) / 2

            alignFlag &= ~(Qt.AlignRight | Qt.AlignCenter)
            alignFlag |= Qt.AlignLeft

            # update the rect, where the text will be displayed
            textRect.setLeft(curXPos + iconWidths)

            # assume that all pixmaps have the same height
            pixYPos = ( textRect.height() - icons[0].height() ) / 2 if icons else 0
            for icon in icons:
                painter.drawPixmap(curXPos, pixYPos, icon)
                curXPos += icon.width()

            painter.drawText(textRect, alignFlag, text)

        else:
            text = painter.fontMetrics().elidedText(text,  Qt.ElideRight,  textRect.width())
            painter.drawText(textRect, alignFlag, text)

    def setStartDate(self,  date):
        self.__startDate = date

    def setDaySpan(self,  span):
        self.__daySpan = span

    def startDate(self):
        #return self.scene().calendarView.startDateTime().date()
        return self.__startDate

    def endDate(self):
        return self.__startDate.addDays(self.daySpan())

    def daySpan(self):
        return self.__daySpan

    def isBeginItem(self):
        return self.startDate() == self.__calendarItem.startDate()

    def isEndItem(self):
        return self.endDate() == self.__calendarItem.endDate()

    def updateGeometry(self):
        cell = self.__calendarItem.calendarScene.cellMap[self.startDate()]

        beginX = 1 + self.__calendarItem.calendarScene.cellHorizontalPos(cell)
        beginY = 1 + cell.topMargin() + self.__calendarItem.calendarScene.cellVerticalPos(cell)

        beginY += self.__calendarItem.position() * \
                         self.__calendarItem.calendarScene.itemHeightIncludingSpacing() - \
                         self.__calendarItem.calendarScene.startHeight() * \
                         self.__calendarItem.calendarScene.itemHeightIncludingSpacing() # scrolling

        self.setPos(beginX, beginY)

        if self.__calendarItem.position() < self.__calendarItem.calendarScene.startHeight() \
            or self.__calendarItem.position() - self.__calendarItem.calendarScene.startHeight() >= \
                 self.__calendarItem.calendarScene.maxRowCount():
            self.hide()
        else:
            self.show()
            self.update()
