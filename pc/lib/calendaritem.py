# -*- coding: utf-8 -*-

# File kdepim/calendarviews/eventviews/month/monthitem.cpp originally taken from the KDE project.
# Copyright (c) 2008 Bruno Virlet <bruno.virlet@gmail.com>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import widget.CalendarGraphicsItem

class CalendarItem(QObject):
    # A CalendarItem is one item in the calendar.
    # It consists of more CalendarGraphicsItems if the events spans over more rows

    def __init__(self,  calendarScene,  calendarEntry):
        super(CalendarItem,  self).__init__(calendarScene)

        # HACK: We need Main()
        #main = qApp.property("main").toPyObject()

        #self.main = main
        #self.connection = main.connection

        self.calendarScene = calendarScene
        self.calendarEntry = calendarEntry

        self.__position = 0
        self.__selected = False
        self.__moving = False
        self.__resizing = False

        self.__overrideStartDate = None
        self.__overrideDaySpan = None

        self.__calendarGraphicsItems = list()

    def __gt__(self,  other):
        if not self.startDate().isValid() or not other.startDate().isValid():
            return False

        if self.startDate() == other.startDate():
            if self.daySpan() == other.daySpan():
                if self.allDay() and not other.allDay():
                    return True
                if not self.allDay() and other.allDay():
                    return False

                # Fallback..
                return id(self) > id(other)

            else:
                return self.daySpan() > other.daySpan()
        else:
            return self.startDate() < other.startDate()

    def resetAll(self):
        for item in self.__calendarGraphicsItems:
            self.calendarScene.removeItem(item)
        del self.__calendarGraphicsItems[:]

    def parentWidget(self):
        if self.__scene:
            return self.calendarScene.calendarView()
        return None

    def toolTipText(self):
        toolTip = "<b>%s</b>" % self.calendarEntry.content()
        toolTip += "<hr>"
        if self.calendarEntry.location():
            toolTip += "<i>" + self.tr("Location:") + "</i> " + self.calendarEntry.location()
            toolTip += "<br>"

        if self.calendarEntry.startTime().date() == self.calendarEntry.endTime().date():
            date = "<i>" + self.tr("Date:") + "</i> " + self.calendarEntry.startTime().date().toString(Qt.DefaultLocaleLongDate)
        else:
            days = self.calendarEntry.startTime().daysTo(self.calendarEntry.endTime())+1
            
            date = "<i>" + self.tr("From:") + "</i> " + self.calendarEntry.startTime().date().toString(Qt.DefaultLocaleLongDate)
            date += "<br>"
            date += "<i>" + self.tr("To:") + "</i> " + self.calendarEntry.endTime().date().toString(Qt.DefaultLocaleLongDate)
            date += "<br>"
            date += "<i>" + self.tr("Duration:") + "</i> " + self.tr("%n day(s)",  "",  days)
        toolTip += date

        if self.calendarEntry.repeatType():
            recurrence = self.calendarScene.main.helper.calendarEntryRecurrenceToString(self.calendarEntry.repeatType(),  self.calendarEntry.repeatDays(),
                                        self.calendarEntry.repeatExceptions(),  self.calendarEntry.repeatStart(),  self.calendarEntry.repeatEnd(),  self.calendarEntry.repeatInterval())
            toolTip += "<br><br><i>" + self.tr("Recurrence:") + "</i> " + recurrence

        toolTip = toolTip.replace(" ",  "&nbsp;")

        return toolTip

    def icons(self):
        ret = list()

        #if not self.connection.connected():
        #    ret.append(self.calendarScene.readonlyPixmap())

        if self.calendarEntry.type() == "anniversary":
            ret.append(self.calendarScene.anniversaryPixmap())
        elif self.calendarEntry.type() == "event":
            ret.append(self.calendarScene.eventPixmap())
        elif self.calendarEntry.type() == "todo":
            if self.calendarEntry.crossedOut():
                ret.append(self.calendarScene.todoCompletedPixmap())
            else:
                ret.append(self.calendarScene.todoPixmap())

        if self.calendarEntry.recurs() and self.calendarEntry.type() != "anniversary":
            ret.append(self.calendarScene.recurPixmap())

        return ret

    def bgColor(self):
        if self.calendarEntry.type() == "anniversary":
            return self.calendarScene.anniversaryBackgroundColor()
        if self.calendarEntry.type() == "event":
            return self.calendarScene.eventBackgroundColor()
        if self.calendarEntry.type() == "todo":
            if not self.calendarEntry.crossedOut() and QDateTime.currentDateTime() > self.calendarEntry.endTime():
                return self.calendarScene.todoDelayedBackgroundColor()
        return self.calendarScene.itemBackgroundColor()

    def updateMonthGraphicsItems(self):
        del self.__calendarGraphicsItems[:]

        # For each row of the month view, create an item to build the whole
        # CalendarItem's CalendarGraphicsItems.

        day = self.calendarScene.calendarView.actualStartDateTime().date()
        while day < self.calendarScene.calendarView.actualEndDateTime().date():
            end = day.addDays(6)

            if self.startDate() <= day and self.endDate() >= end:
                # CalendarItem takes the whole line
                span = 6
                start = day
            elif self.startDate() >= day and self.endDate() <= end:
                # starts and ends on this line
                span = self.daySpan()
                start = self.startDate()
            elif day <= self.endDate() and self.endDate() <= end:
                # ends on this line
                span = self.calendarScene.getLeftSpan(self.endDate())
                start = day
            elif day <= self.startDate() and self.startDate() <= end:
                # begins on this line
                span = self.calendarScene.getRightSpan(self.startDate())
                start = self.startDate()
            else:
                # CalendarItem is not on the line
                day = end.addDays(1)
                continue

            # A new item needs to be created
            item = widget.CalendarGraphicsItem.CalendarGraphicsItem(self)
            item.setStartDate(start)
            item.setDaySpan(span)
            item.setToolTip(self.toolTipText())

            self.__calendarGraphicsItems.append(item)

            if self.isMoving() or self.isResizing():
                self.setZValue(100)
            else:
                self.setZValue(0)

            day = end.addDays(1)

    def beginResize(self):
        self.__overrideStartDate = self.startDate()
        self.__overrideDaySpan = self.daySpan()
        self.__resizing = True
        self.setZValue(100)

    def endResize(self):
        self.setZValue(0)
        self.__resizing = False # self.startDate() and self.daySpan() return real values again
        if self.__overrideStartDate != self.startDate() or self.__overrideDaySpan != self.daySpan():
            self.finalizeResize(self.__overrideStartDate, self.__overrideStartDate.addDays(self.__overrideDaySpan))

    def beginMove(self):
        self.__overrideStartDate = self.startDate()
        self.__overrideDaySpan = self.daySpan()
        self.__moving = True
        self.setZValue(100)

    def endMove(self):
        self.setZValue(0)
        self.__moving = False # self.startDate() and self.daySpan() return real values again
        if self.__overrideStartDate != self.startDate():
            self.finalizeMove(self.__overrideStartDate)

    #def resizeBy
    #def moveBy

    def updateGeometry(self):
        for item in self.__calendarGraphicsItems:
            item.updateGeometry()

    def setZValue(self,  z):
        for item in self.__calendarGraphicsItems:
            item.setZValue(z)

    def startDate(self):
        if self.isMoving() or self.isResizing():
            return self.__overrideStartDate
        return self.realStartDate()

    def endDate(self):
        if self.isMoving() or self.isResizing():
            return self.__overrideStartDate.addDays(self.__overrideDaySpan)
        return self.realEndDate()

    def realStartDate(self):
        return self.calendarEntry.startTime().date()

    def realEndDate(self):
        return self.calendarEntry.endTime().date()

    def daySpan(self):
        if self.isMoving() or self.isResizing():
            return self.__overrideDaySpan

        start = self.startDate()
        end = self.endDate()

        if start.isValid() and end.isValid():
            return start.daysTo(end)
        return 0

    def allDay(self):
        # TODO...
        return True

    # def greaterThan
    # def greaterThanFallback

    def isMoving(self):
        return self.__moving

    def isResizing(self):
        return self.__resizing

    def position(self):
        return self.__position

    def updatePosition(self):
        if not self.startDate() or not self.endDate().isValid():
            return

        firstFreeSpace = 0
        for day in [self.startDate().addDays(i) for i in range(self.startDate().daysTo(self.endDate())+1)]:
            try:
                cell = self.calendarScene.cellMap[day]
            except KeyError:
                continue

            if cell.firstFreeSpace() > firstFreeSpace:
                firstFreeSpace = cell.firstFreeSpace()

        for day in [self.startDate().addDays(i) for i in range(self.startDate().daysTo(self.endDate())+1)]:
            try:
                cell = self.calendarScene.cellMap[day]
            except KeyError:
                continue

            cell.addMonthItem(self,  firstFreeSpace)

        self.__position = firstFreeSpace
