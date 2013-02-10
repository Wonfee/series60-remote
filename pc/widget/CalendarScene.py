# -*- coding: utf-8 -*-

# File kdepim/calendarviews/eventviews/month/monthscene.cpp originally taken from the KDE project.
# Copyright (c) 2008 Bruno Virlet <bruno.virlet@gmail.com>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import window.calendar_edit
import widget.CalendarCell
import widget.CalendarGraphicsItem
import widget.ScrollIndicator
from lib.classes import *

class CalendarScene(QGraphicsScene):
    def __init__(self,  parent):
        super(CalendarScene,  self).__init__(parent)

        # HACK: We need Main()
        main = qApp.property("main").toPyObject()

        self.main = main
        self.connection = main.connection
        self.database = main.database

        self.calendarView = parent

        self.setSceneRect(0,  0,  parent.width(),  parent.height())

        self.cellMap = dict()
        self.managerList = list()
        self.__selectedCellDate = None
        self.__initialized = False
        self.__startHeight = 0

    def anniversaryPixmap(self):
        return QIcon(":/emblem-birthday").pixmap(16,  16)
        #return QIcon(":/emblem-anniversary").pixmap(16,  16)

    def eventPixmap(self):
        return QIcon(":/emblem-event").pixmap(16,  16)

    def readonlyPixmap(self):
        return QIcon(":/emblem-readonly").pixmap(16,  16)

    def recurPixmap(self):
        return QIcon(":/emblem-recurring").pixmap(16,  16)

    def todoPixmap(self):
        return QIcon(":/emblem-todo").pixmap(16,  16)

    def todoCompletedPixmap(self):
        return QIcon(":/emblem-todo-completed").pixmap(16,  16)

    def anniversaryBackgroundColor(self):
        return QColor("#EB8B4B")

    def eventBackgroundColor(self):
        return QColor("#83D8FF")

    def todoDelayedBackgroundColor(self):
        return QColor("#FF3F3F")

    def itemBackgroundColor(self):
        return QColor("#97EB79")

    def setStartHeight(self,  height):
        self.__startHeight = height

    def startHeight(self):
        return self.__startHeight

    def calendarView(self):
        return self.calendarView

    def headerHeight(self):
        return 50

    def availableHeight(self):
        return int ( self.sceneRect().height() - self.headerHeight() )

    def rowHeight(self):
        return int ( ( self.availableHeight() - 1 ) / 6. )

    def availableWidth(self):
        return int ( self.sceneRect().width() )

    def columnWidth(self):
        return int ( ( self.availableWidth() - 1 ) / 7. )

    def cellVerticalPos(self,  cell):
        return self.headerHeight() + cell.y() * self.rowHeight()

    def cellHorizontalPos(self,  cell):
        return cell.x() * self.columnWidth()

    def sceneYToMonthGridY(self,  yScene):
        return yScene - self.headerHeight()

    def sceneXToMonthGridX(self,  xScene):
        return xScene

    def maxRowCount(self):
        return (self.rowHeight() - widget.CalendarCell.CalendarCell.topMargin()) / self.itemHeightIncludingSpacing()

    def isInMonthGrid(self,  x,  y):
        return x >= 0 and y >= 0 and x <= self.availableWidth() and y <= self.availableHeight()

    def itemHeightIncludingSpacing(self):
        return widget.CalendarCell.CalendarCell.topMargin() + 2

    def itemHeight(self):
        return widget.CalendarCell.CalendarCell.topMargin()

    def setInitialized(self,  initialized):
        self.__initialized = initialized

    def initialized(self):
        return self.__initialized

    def getCellFromPos(self,  pos):
        y = self.sceneYToMonthGridY(pos.y())
        x = self.sceneXToMonthGridX(pos.x())
        if not self.isInMonthGrid(x,  y):
            return 0

        id = int(y / self.rowHeight()) * 7 + int(x / self.columnWidth())
        return self.cellMap[self.calendarView.actualStartDateTime().date().addDays(id)]

    def selectedCell(self):
        try:
            return self.cellMap[self.__selectedCellDate]
        except KeyError:
            return None

    def getRightSpan(self,  date):
        try:
            cell = self.cellMap[date]
        except KeyError:
            return 0

        return 7 - cell.x() - 1

    def getLeftSpan(self,  date):
        try:
            cell = self.cellMap[date]
        except KeyError:
            return 0

        return cell.x()

    def updateGeometry(self):
        for manager in self.managerList:
            manager.updateGeometry()

    def resetAll(self):
        for manager in self.managerList:
            manager.resetAll()
        del self.managerList[:]
        self.cellMap.clear()

    def lastItemFit(self,  cell):
        if cell.firstFreeSpace() > self.maxRowCount() + self.startHeight():
            return False
        return True

    def changeHeight(self,  newHeight):
        self.setStartHeight(newHeight)

        for manager in self.managerList:
            manager.updateGeometry()

        self.invalidate(QRectF(),  QGraphicsScene.BackgroundLayer)

    def scrollCellsUp(self):
        self.changeHeight(self.startHeight() - 1)

    def scrollCellsDown(self):
        self.changeHeight(self.startHeight() + 1)

    def entryAdd(self,  date,  type=type):
        dlg = window.calendar_edit.CalendarEntryEdit(self.calendarView,  self.main,  date=date,  type=type)

    def entryEdit(self,  entry):
        dlg = window.calendar_edit.CalendarEntryEdit(self.calendarView,  self.main,  entry)

    def entryRemove(self,  entry):
        ret = QMessageBox.question(None,
            self.tr("Delete calendar entry"),
            self.tr("Do you really want permanently remove the calendar entry \"%1\"?").arg(entry.content()),
            QMessageBox.StandardButtons(\
                QMessageBox.No | \
                QMessageBox.Yes))
        if ret == QMessageBox.Yes:
            self.connection.calendarEntryRemove(entry)
            self.calendarView.reloadIncidences()

    def entryRemoveRecurrence(self,  entry,  date):
        exceptionDates = entry.repeatExceptions()
        exceptionDates = exceptionDates.split(",") if exceptionDates else []
        exceptionDates = [str(int(exception)) for exception in exceptionDates]
        exceptionDates.append(str(date.toTime_t()))
        exceptionDates.sort()
        exceptionDates = ",".join(exceptionDates)
        
        entry.setRepeatExceptions(exceptionDates)
        
        self.connection.calendarEntryChange(entry)
        self.main.mainWindow.calendarWidget.reloadIncidences()

    def mouseDoubleClickEvent(self,  mouseEvent):
        pos = mouseEvent.scenePos()
        item = self.itemAt(pos)
        if item:
            if isinstance(item,  widget.CalendarGraphicsItem.CalendarGraphicsItem):
                if self.connection.connected():
                    self.entryEdit(item.calendarItem().calendarEntry)
        else:
            if self.connection.connected():
                self.entryAdd(self.__selectedCellDate,  "appointment")

    def mousePressEvent(self,  mouseEvent):
        pos = mouseEvent.scenePos()
        item =  self.itemAt(pos)
        if item:
            if isinstance(item,  widget.CalendarGraphicsItem.CalendarGraphicsItem):
                if mouseEvent.button() == Qt.RightButton:
                    menu = QMenu()
                    menu.addAction(QIcon(":/document-edit"),  self.tr("&Edit..."),  lambda : self.entryEdit(item.calendarItem().calendarEntry)).setEnabled(self.connection.connected())
                    menu.addAction(QIcon(":/edit-delete"),  self.tr("&Remove..."),  lambda : self.entryRemove(item.calendarItem().calendarEntry)).setEnabled(self.connection.connected())
                    if item.calendarItem().calendarEntry.recurs():
                        menu.addAction(QIcon(":/edit-delete"),  self.tr("&Remove this recurrence..."),  
                                lambda : self.entryRemoveRecurrence(item.calendarItem().calendarEntry,  
                                                                                    item.calendarItem().calendarEntry.startTime())).setEnabled(self.connection.connected())
                    menu.exec_(mouseEvent.screenPos())
            elif isinstance(item,  widget.ScrollIndicator.ScrollIndicator):
                if item.direction == widget.ScrollIndicator.ArrowDirection.Up:
                    self.scrollCellsUp()
                elif item.direction == widget.ScrollIndicator.ArrowDirection.Down:
                    self.scrollCellsDown()
        else:
            cell = self.getCellFromPos(pos)
            if cell:
                self.__selectedCellDate = cell.date()
                self.update()
            if mouseEvent.button() == Qt.RightButton:
                    menu = QMenu()
                    menu.addAction(QIcon(":/appointment-new"),  self.tr("New Appointment..."),
                                              lambda : self.entryAdd(self.__selectedCellDate,  "appointment")).setEnabled(self.connection.connected())
                    menu.addAction(QIcon(":/journal-new"),  self.tr("New Memo..."),
                                              lambda : self.entryAdd(self.__selectedCellDate,  "event")).setEnabled(self.connection.connected())
                    menu.addAction(QIcon(":/anniversary-new"),  self.tr("New Anniversary/Birthday..."),
                                              lambda : self.entryAdd(self.__selectedCellDate,  "anniversary")).setEnabled(self.connection.connected())
                    menu.addAction(QIcon(":/task-new"),  self.tr("New To-do..."),
                                              lambda : self.entryAdd(self.__selectedCellDate,  "todo")).setEnabled(self.connection.connected())
                    menu.exec_(mouseEvent.screenPos())
        mouseEvent.accept()

    #def selectedCell(self):
    #    return self.cellMap[self.selectedDate]

    #def mousePressEvent(self,  mouseEvent):
    #    pos = mouseEvent.scenePos()
