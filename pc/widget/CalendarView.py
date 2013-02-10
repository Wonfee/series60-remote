# -*- coding: utf-8 -*-

# File kdepim/calendarviews/eventviews/month/monthview.cpp originally taken from the KDE project.
# Copyright (c) 2008 Bruno Virlet <bruno.virlet@gmail.com>
# Copyright (C) 2010 Klarälvdalens Datakonsult AB, a KDAB Group company, info@kdab.net
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.calendaritem

# representation of two objects with the same date will have the same hash
# this is needed to be able to use QDate as a key for python dictionaries
def hdate(self):
    return hash(str(self))
QDate.__hash__ = hdate

import widget.CalendarGraphicsView
import widget.CalendarScene
import widget, CalendarCell

class CalendarView(QWidget):
    def __init__(self,  parent=None):
        super(CalendarView,  self).__init__(parent)

        # HACK: We need Main()
        main = qApp.property("main").toPyObject()
        self.connection = main.connection

        self.main = main
        self.database = main.database

        self.__actualStartDateTime = QDateTime()
        self.__actualEndDateTime = QDateTime()
        self.__startDateTime = QDateTime()
        self.__endDateTime = QDateTime()

        self.topLayout = QHBoxLayout(self)
        self.view = widget.CalendarGraphicsView.CalendarGraphicsView(self)

        self.scene = widget.CalendarScene.CalendarScene(self)
        self.view.setScene(self.scene)
        self.topLayout.addWidget(self.view)

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setSpacing(0)
        self.rightLayout.setMargin(0)

        # push buttons to the bottom
        self.rightLayout.addStretch(1)

        self.minusMonth = QToolButton(self)
        self.minusMonth.setIcon(QIcon(":/arrow-up-double"))
        self.minusMonth.setToolTip(self.tr("Go back one month"))
        self.minusMonth.setAutoRaise(True)
        self.connect(self.minusMonth,  SIGNAL("clicked()"),  self,  SLOT("moveBackMonth()"))

        self.minusWeek = QToolButton(self)
        self.minusWeek.setIcon(QIcon(":/arrow-up"))
        self.minusWeek.setToolTip(self.tr("Go back one week"))
        self.minusWeek.setAutoRaise(True)
        self.connect(self.minusWeek,  SIGNAL("clicked()"),  self,  SLOT("moveBackWeek()"))

        self.today = QToolButton(self)
        self.today.setIcon(QIcon(":/go-jump-today"))
        self.today.setToolTip(self.tr("Go to today"))
        self.today.setAutoRaise(True)
        self.connect(self.today,  SIGNAL("clicked()"),  self,  SLOT("jumpToToday()"))

        self.plusWeek = QToolButton(self)
        self.plusWeek.setIcon(QIcon(":/arrow-down"))
        self.plusWeek.setToolTip(self.tr("Go forward one week"))
        self.plusWeek.setAutoRaise(True)
        self.connect(self.plusWeek,  SIGNAL("clicked()"),  self,  SLOT("moveFwdWeek()"))

        self.plusMonth = QToolButton(self)
        self.plusMonth.setIcon(QIcon(":/arrow-down-double"))
        self.plusMonth.setToolTip(self.tr("Go forward one month"))
        self.plusMonth.setAutoRaise(True)
        self.connect(self.plusMonth,  SIGNAL("clicked()"),  self,  SLOT("moveFwdMonth()"))

        self.rightLayout.addWidget(self.minusMonth)
        self.rightLayout.addWidget(self.minusWeek)
        self.rightLayout.addWidget(self.today)
        self.rightLayout.addWidget(self.plusWeek)
        self.rightLayout.addWidget(self.plusMonth)

        self.topLayout.addLayout(self.rightLayout)

        self.connect(self.connection, SIGNAL("calendarCompleted"),  self.updateView)
        self.connect(self.connection, SIGNAL("calendarUpdated"),  self.updateView)

        self.view.update()

        #self.reloadIncidences()

    def startDateTime(self):
        return self.__startDateTime

    def endDateTime(self):
        return self.__endDateTime

    def actualStartDateTime(self):
        return self.__actualStartDateTime

    def actualEndDateTime(self):
        return self.__actualEndDateTime

    def reloadIncidences(self):
        self.scene.resetAll()

        num = 0
        for day in [self.actualStartDateTime().date().addDays(i) for i in range(self.actualStartDateTime().daysTo(self.actualEndDateTime())+1) ]:
            self.scene.cellMap[day] = widget.CalendarCell.CalendarCell(num,  day,  self.scene)
            num += 1

        for entry in self.database.calendarEntries(self.actualStartDateTime(),  self.actualEndDateTime(),  True):
            item = lib.calendaritem.CalendarItem(self.scene,  entry)
            self.scene.managerList.append(item)

        self.scene.managerList.sort(reverse=True)

        for manager in self.scene.managerList:
            manager.updateMonthGraphicsItems()
            manager.updatePosition()

        for manager in self.scene.managerList:
            manager.updateGeometry()

        self.scene.setInitialized(True)
        self.view.update()
        self.scene.update()

    def averageDate(self):
        return self.actualStartDateTime().date().addDays( self.actualStartDateTime().date().daysTo( self.actualEndDateTime().date() ) / 2 )

    def currentMonth(self):
        return self.averageDate().month()

    def actualDateRange(self,  start,  end):
        dayOne = start
        #dayOne = QDateTime(start)
        #dayOne.setDate(QDate(start.date().year(), start.date().month(), 1))

        weekdayCol = (dayOne.date().dayOfWeek() + 7 - 1) % 7

        actualStart = dayOne.addDays(-weekdayCol)
        actualStart.setTime( QTime( 0, 0, 0, 0 ) )

        actualEnd = actualStart.addDays(6 * 7 - 1)
        actualEnd.setTime(QTime( 23, 59, 59, 99 ))

        return actualStart,  actualEnd

    def setDateRange(self,  start,  end):
        self.__startDateTime,  self.__endDateTime = start,  end
        self.__actualStartDateTime,  self.__actualEndDateTime = self.actualDateRange(start,  end)
        self.reloadIncidences()

    @pyqtSignature("")
    def jumpToToday(self):
        current = QDate.currentDate()
        start = QDateTime(current.year(),  current.month(),  1,  0,  0)
        end = QDateTime(current.year(),  current.month(),  current.daysInMonth(),  0,  0)
        self.setDateRange(start,  end)

    @pyqtSignature("")
    def moveBackMonth(self):
        self.moveStartDate(0,  -1)

    @pyqtSignature("")
    def moveBackWeek(self):
        self.moveStartDate(-1,  0)

    @pyqtSignature("")
    def moveFwdWeek(self):
        self.moveStartDate(1,  0)

    @pyqtSignature("")
    def moveFwdMonth(self):
        self.moveStartDate(0,  1)

    def moveStartDate(self,  weeks,  months):
        start = self.startDateTime()
        end = self.endDateTime()

        start = start.addDays(weeks * 7)
        end = end.addDays(weeks * 7)

        start = start.addMonths(months)
        end = end.addMonths(months)

        self.setDateRange(start,  end)

    def updateView(self):
        if self.scene.initialized():
            self.reloadIncidences()

    def showEvent(self,  event):
        if not self.scene.initialized():
            self.jumpToToday()

    def wheelEvent(self,  event):
        # invert direction to get scroll-like behaviour
        if event.delta() > 0:
            self.moveStartDate(-1,  0)
        elif event.delta() < 0 :
            self.moveStartDate(1,  0)

        # call accept in every case, we do not want anybody else to react
        event.accept()

    def keyPressEvent(self,  event):
        if event.key() == Qt.Key_PageUp:
            self.moveStartDate(0,  -1)
            event.accept()
        elif event.key() == Qt.Key_PageDown:
            self.moveStartDate(0,  1)
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
   app = QApplication([])
   v = CalendarView()
   v.show()
   app.exec_()
