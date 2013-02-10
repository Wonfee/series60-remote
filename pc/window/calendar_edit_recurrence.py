# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_calendar_edit_recurrence
from lib.ordinal_number_formatter import OrdinalNumberFormatter
from widget.DateSortedListWidgetItem import DateSortedListWidgetItem
from lib.classes import *

class CalendarEntryRecurrenceEdit(QDialog,  ui.ui_calendar_edit_recurrence.Ui_CalendarEntryRecurrenceEdit):
    def __init__(self, parent, main, calendarEntry=None):
        super(CalendarEntryRecurrenceEdit,  self).__init__(parent)

        self.parent = parent

        self.setupUi(self)

        locale = main.locale
        shortDay = lambda day : locale.standaloneDayName(day,  QLocale.ShortFormat)
        longDay = lambda day : locale.standaloneDayName(day)
        longMonth = lambda day : locale.standaloneMonthName(day)

        # Use longer format for date pickers
        self.startDate.setDisplayFormat(main.locale.dateFormat(QLocale.ShortFormat).replace("yy",  "yyyy"))
        self.endDate.setDisplayFormat(main.locale.dateFormat(QLocale.ShortFormat).replace("yy",  "yyyy"))

        # Translate Ui
        self.mondayBox.setText(shortDay(1))
        self.tuesdayBox.setText(shortDay(2))
        self.wednesdayBox.setText(shortDay(3))
        self.thursdayBox.setText(shortDay(4))
        self.fridayBox.setText(shortDay(5))
        self.saturdayBox.setText(shortDay(6))
        self.sundayBox.setText(shortDay(7))

        for day in xrange(1,  32):
            self.monthlyDayInMonthBox.addItem(unicode(OrdinalNumberFormatter.toString(day)),  QVariant(day))

        for week in xrange(1,  6):
            self.monthlyWeekInMonthBox.addItem(unicode(OrdinalNumberFormatter.toString(week)),  QVariant(week))
            self.yearlyWeekInMonthBox.addItem(unicode(OrdinalNumberFormatter.toString(week)),  QVariant(week))

        for day in xrange(1,  8):
            self.monthlyDayInWeekBox.addItem(longDay(day),  QVariant(day))
            self.yearlyDayInWeekBox.addItem(longDay(day),  QVariant(day))

        for month in xrange(1,  13):
            self.yearlyMonthInYearBox_ByDate.addItem(longMonth(month),  QVariant(month))
            self.yearlyMonthInYearBox_ByDay.addItem(longMonth(month),  QVariant(month))

        if not parent.calendarEntry:
            self.endDate.setDateTime(QDateTime(parent.date.addYears(3),  QTime(0,  0)))

        self.lastType = ""
        self.lastDays = ""
        self.lastExceptions = ""
        self.lastStart = QDateTime()
        self.lastEnd = QDateTime()
        self.lastInterval = 1

        self.connect(self,  SIGNAL("accepted()"),  self.recurrenceAccepted)
        self.connect(self,  SIGNAL("rejected()"),  self.resetRecurrence)
        self.connect(self.dailyButton,  SIGNAL("clicked()"),  lambda : self.ruleWidget.setCurrentWidget(self.dailyWidget))
        self.connect(self.weeklyButton,  SIGNAL("clicked()"),  lambda : self.ruleWidget.setCurrentWidget(self.weeklyWidget))
        self.connect(self.monthlyButton,  SIGNAL("clicked()"),  lambda : self.ruleWidget.setCurrentWidget(self.monthlyWidget))
        self.connect(self.yearlyButton,  SIGNAL("clicked()"),  lambda : self.ruleWidget.setCurrentWidget(self.yearlyWidget))
        self.connect(self.exceptionAddButton,  SIGNAL("clicked()"),  self.addException)
        self.connect(self.exceptionDeleteButton,  SIGNAL("clicked()"),  self.deleteException)        

    def loadDate(self,  date):
        def weekInMonth(date):
            firstDayInMonth = date.addDays(-date.day()+1)
            firstDayOfWeek = firstDayInMonth.dayOfWeek()
            week = (date.day() - date.dayOfWeek() + firstDayOfWeek - 1) / 7
            if date.dayOfWeek() >= firstDayOfWeek:
                week += 1
            return week

        dow = date.dayOfWeek()
        # Weekly repeat
        self.mondayBox.setChecked(1 == dow)
        self.tuesdayBox.setChecked(2 == dow)
        self.wednesdayBox.setChecked(3 == dow)
        self.thursdayBox.setChecked(4 == dow)
        self.fridayBox.setChecked(5 == dow)
        self.saturdayBox.setChecked(6 == dow)
        self.sundayBox.setChecked(7 == dow)

        # Monthly repeat
        self.monthlyDayInMonthBox.setCurrentIndex(self.monthlyDayInMonthBox.findData(QVariant(date.day())))

        self.monthlyWeekInMonthBox.setCurrentIndex(self.monthlyWeekInMonthBox.findData(QVariant(weekInMonth(date))))
        self.monthlyDayInWeekBox.setCurrentIndex(self.monthlyDayInWeekBox.findData(QVariant(dow)))

        # Yearly repeat
        self.yearlyDayInMonthBox.setValue(date.day())
        self.yearlyMonthInYearBox_ByDate.setCurrentIndex(self.yearlyMonthInYearBox_ByDate.findData(QVariant(date.month())))

        self.yearlyWeekInMonthBox.setCurrentIndex(self.yearlyWeekInMonthBox.findData(QVariant(weekInMonth(date))))
        self.yearlyDayInWeekBox.setCurrentIndex(self.yearlyDayInWeekBox.findData(QVariant(dow)))
        self.yearlyMonthInYearBox_ByDay.setCurrentIndex(self.yearlyMonthInYearBox_ByDay.findData(QVariant(date.month())))
        
        # Exception Date
        self.exceptionDateEdit.setDate(date)

    def loadEntry(self,  type,  days,  exceptions,  start,  end,  interval):
        self.lastType = type
        self.lastDays = days
        self.lastExceptions = exceptions
        self.lastStart = start
        self.lastEnd = end
        self.lastInterval = interval

        self.recurrenceBox.setChecked(bool(type))

        if type:
            self.endingDateBox.setChecked(not bool(end and end.isValid()))
            if end and end.isValid():
                self.endDate.setDateTime(end)
            else:
                self.endDate.setDateTime(start.addYears(1))

            parsedDays = CalendarEntry.recurrenceParsedDays(type,  days)

            if type == "daily":
                self.dailyButton.click()
                self.recurDayBox.setValue(interval)
            elif type == "weekly":
                self.weeklyButton.click()
                self.recurWeekBox.setValue(interval)

                self.mondayBox.setChecked(0 in parsedDays)
                self.tuesdayBox.setChecked(1 in parsedDays)
                self.wednesdayBox.setChecked(2 in parsedDays)
                self.thursdayBox.setChecked(3 in parsedDays)
                self.fridayBox.setChecked(4 in parsedDays)
                self.saturdayBox.setChecked(5 in parsedDays)
                self.sundayBox.setChecked(6 in parsedDays)
            elif type == "monthly_by_dates":
                self.monthlyButton.click()
                self.monthlyByDatesButton.click()
                self.recurMonthBox.setValue(interval)

                self.monthlyDayInMonthBox.setCurrentIndex(self.monthlyDayInMonthBox.findData(QVariant(parsedDays[0]+1)))
            elif type == "monthly_by_days":
                week = parsedDays[0]['week'] + 1
                day = parsedDays[0]['day'] + 1

                self.monthlyButton.click()
                self.monthlyByDaysButton.click()
                self.recurMonthBox.setValue(interval)

                self.monthlyWeekInMonthBox.setCurrentIndex(self.monthlyWeekInMonthBox.findData(QVariant(week)))
                self.monthlyDayInWeekBox.setCurrentIndex(self.monthlyDayInWeekBox.findData(QVariant(day)))
            elif type == "yearly_by_date":
                self.yearlyButton.click()
                self.yearlyByDateButton.click()
                self.recurYearBox.setValue(interval)

                self.yearlyDayInMonthBox.setValue(start.date().day())
                self.yearlyMonthInYearBox_ByDate.setCurrentIndex(self.yearlyMonthInYearBox_ByDate.findData(QVariant(start.date().month())))
            elif type == "yearly_by_day":
                week = parsedDays['week'] + 1
                day = parsedDays['day'] + 1
                month = parsedDays['month'] + 1

                self.yearlyButton.click()
                self.yearlyByDaysButton.click()
                self.recurYearBox.setValue(interval)

                self.yearlyWeekInMonthBox.setCurrentIndex(self.yearlyWeekInMonthBox.findData(QVariant(week)))
                self.yearlyDayInWeekBox.setCurrentIndex(self.yearlyDayInWeekBox.findData(QVariant(day)))
                self.yearlyMonthInYearBox_ByDay.setCurrentIndex(self.yearlyMonthInYearBox_ByDay.findData(QVariant(month)))
            
            self.exceptionList.clear()
            if exceptions:
                for date in exceptions.split(","):
                    date = QDateTime.fromTime_t(int(float(date))).date()
                    item = DateSortedListWidgetItem(date.toString(Qt.DefaultLocaleLongDate))
                    item.setData(Roles.DateRole,  QVariant(date))
                    self.exceptionList.addItem(item)

    def addException(self):
        date = self.exceptionDateEdit.date()
        dateVar = QVariant(date)
        for num in xrange(self.exceptionList.count()):
            item = self.exceptionList.item(num)
            if item.data(Roles.DateRole) == dateVar:
                return
        
        item = DateSortedListWidgetItem(date.toString(Qt.DefaultLocaleLongDate))
        item.setData(Roles.DateRole,  dateVar)
        # Do not use self.exceptionList as parent, because this widget is sorted
        self.exceptionList.addItem(item)
        self.exceptionList.setCurrentItem(item)
    
    def deleteException(self):
        self.exceptionList.takeItem(self.exceptionList.currentRow())

    def type(self):
        if not self.recurrenceBox.isChecked():
            return ""
        if self.dailyButton.isChecked():
            return "daily"
        if self.weeklyButton.isChecked():
            return "weekly"
        if self.monthlyButton.isChecked():
            if self.monthlyByDatesButton.isChecked():
                return "monthly_by_dates"
            if self.monthlyByDaysButton.isChecked():
                return "monthly_by_days"
        if self.yearlyButton.isChecked():
            if self.yearlyByDateButton.isChecked():
                return "yearly_by_date"
            if self.yearlyByDaysButton.isChecked():
                return "yearly_by_day"
        return ""

    def days(self):
        type = self.type()

        if type == "weekly":
            days = []
            boxes = (self.mondayBox,  self.tuesdayBox,  self.wednesdayBox,  self.thursdayBox,  self.fridayBox,  self.saturdayBox,  self.sundayBox)
            for day in xrange(len(boxes)):
                if boxes[day].isChecked():
                    days.append(str(day))
            return ",".join(days)
        if type == "monthly_by_dates":
            return str(self.monthlyDayInMonthBox.itemData(self.monthlyDayInMonthBox.currentIndex()).toInt()[0] - 1)
        if type == "monthly_by_days":
            day = str(self.monthlyDayInWeekBox.itemData(self.monthlyDayInWeekBox.currentIndex()).toInt()[0] - 1)
            week = str(self.monthlyWeekInMonthBox.itemData(self.monthlyWeekInMonthBox.currentIndex()).toInt()[0] - 1)
            return "week:" + week + ",day:" + day
        if type == "yearly_by_day":
            day = str(self.yearlyDayInWeekBox.itemData(self.yearlyDayInWeekBox.currentIndex()).toInt()[0] - 1)
            week = str(self.yearlyWeekInMonthBox.itemData(self.yearlyWeekInMonthBox.currentIndex()).toInt()[0] - 1)
            month = str(self.yearlyMonthInYearBox_ByDay.itemData(self.yearlyMonthInYearBox_ByDay.currentIndex()).toInt()[0] - 1)
            return "week:" + week + ",day:" + day + ",month:" + month
        return ""

    def interval(self):
        type = self.type()

        if type == "daily":
            return self.recurDayBox.value()
        if type == "weekly":
            return self.recurWeekBox.value()
        if type in ("monthly_by_dates",  "monthly_by_days"):
            return self.recurMonthBox.value()
        if type in ("yearly_by_date",  "yearly_by_day"):
            return self.recurYearBox.value()
        return ""

    def start(self):
        if not self.type():
            return 0
        #return self.startDate.dateTime()
        return self.parent.startDate.dateTime()

    def end(self):
        if not self.type():
            return 0
        if self.endDate.isEnabled():
            return self.endDate.dateTime()
        return 0

    def exceptions(self):
        return ",".join([str(self.exceptionList.item(i).data(Roles.DateRole).toDateTime().toTime_t())
                                  for i in xrange(self.exceptionList.count())])

    def recurrenceAccepted(self):
        self.lastType = self.type()
        self.lastDays = self.days()
        self.lastExceptions = self.exceptions()
        self.lastStart = self.start()
        self.lastEnd = self.end()
        self.lastInterval = self.interval()

    def resetRecurrence(self):
        self.loadEntry(self.lastType,  self.lastDays,  self.lastExceptions,  self.lastStart,  self.lastEnd,  self.lastInterval)

    def showEvent(self,  event):
        self.startDate.setDateTime(self.parent.startDate.dateTime())

        QDialog.showEvent(self,  event)
