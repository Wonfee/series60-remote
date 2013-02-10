# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import window.calendar_edit_recurrence
import ui.ui_calendar_edit
from lib.classes import *

CalendarReminderUnit = Enum("Minute Hour Day")

class CalendarEntryEdit(QDialog,  ui.ui_calendar_edit.Ui_CalendarEntryEdit):
    def __init__(self, parent, main, calendarEntry=None,  date=QDate.currentDate(),  type=None):
        super(CalendarEntryEdit,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.database = main.database
        self.connection = main.connection

        self.calendarEntry = calendarEntry
        self.date = date
        self.recurrenceChanged = False

        self.setupUi(self)

        if type is None:
            type = calendarEntry.type()

        self.type = type

        self.recurrenceDialog = window.calendar_edit_recurrence.CalendarEntryRecurrenceEdit(self, self.main)

        # Use longer format for date pickers
        self.startDate.setDisplayFormat(main.locale.dateFormat(QLocale.ShortFormat).replace("yy",  "yyyy"))
        self.endDate.setDisplayFormat(main.locale.dateFormat(QLocale.ShortFormat).replace("yy",  "yyyy"))

        # Add items to the comboboxes
        self.reminderUnitBox.addItem(self.tr("minute(s)"),  QVariant(CalendarReminderUnit.Minute))
        self.reminderUnitBox.addItem(self.tr("hour(s)"),  QVariant(CalendarReminderUnit.Hour))
        self.reminderUnitBox.addItem(self.tr("day(s)"),  QVariant(CalendarReminderUnit.Day))

        self.priorityBox.addItem(self.tr("High"),  QVariant(1))
        self.priorityBox.addItem(self.tr("Normal"),  QVariant(2))
        self.priorityBox.addItem(self.tr("Low"),  QVariant(3))

        self.accessBox.addItem(self.tr("Open"),  QVariant("open"))
        self.accessBox.addItem(self.tr("Private"),  QVariant("private"))
        self.accessBox.addItem(self.tr("Restricted"),  QVariant("restricted"))

        self.connect(self.recurrenceButton,  SIGNAL("clicked()"),  self.openRecurrenceDialog)
        self.connect(self.buttonBox.button(QDialogButtonBox.Reset),  SIGNAL("clicked()"), self,  SLOT("reset()"))
        self.connect(self.buttonBox.button(QDialogButtonBox.Discard),  SIGNAL("clicked()"),  self,  SLOT("close()"))
        self.connect(self.recurrenceDialog,  SIGNAL("accepted()"),  self.recurrenceAccepted)

        if calendarEntry is None:
            self.setWindowTitle(self.tr("Add %1",  "Add [type of event]").arg(CalendarEntry.typeString(type)))
        else:
            self.setWindowTitle(self.tr("Edit %1",  "Edit [type of event]").arg(CalendarEntry.typeString(type)))


        if type == "todo":
            self.recurrenceLabel.hide()
            self.recurrenceButton.hide()

        self.reset()
        self.show()

    def updateRecurrence(self,  type,  days,  exceptions,  start,  end,  interval):
        recurrence = self.main.helper.calendarEntryRecurrenceToString(type,  days,  exceptions,  start,  end,  interval)
        self.recurrenceLabel.setText(recurrence)

        self.recurrenceDialog.loadEntry(type,  days,  exceptions,  start,  end,  interval)

    def resetRecurrence(self):
        self.recurrenceDialog.loadDate(self.startDate.date())
        self.recurrenceChanged = False

        if self.calendarEntry is None:
            if self.type == "anniversary":
                dt = QDateTime(self.date,  QTime(0,  0))
                self.updateRecurrence("yearly_by_date",  "",  "",  dt,  None,  1)
                self.recurrenceChanged = True
            else:
                self.updateRecurrence("",  None,  None,  None,  None, None)
        else:
            self.updateRecurrence(self.calendarEntry.repeatType(),  self.calendarEntry.repeatDays(),  self.calendarEntry.repeatExceptions(),
                                  self.calendarEntry.repeatStart(),  self.calendarEntry.repeatEnd(),  self.calendarEntry.repeatInterval())

    @pyqtSignature("bool")
    def setAdvancedReminder(self,  advancedEnabled):
        if advancedEnabled:
            self.reminderStack.setCurrentWidget(self.advancedReminderWidget)
        else:
            self.reminderStack.setCurrentWidget(self.basicReminderWidget)
    
    @pyqtSignature("")
    def entryChanged(self):
        self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(True)

    @pyqtSignature("")
    def reset(self):
        if self.calendarEntry is None:
            self.titleLine.setText("")
            self.locationLine.setText("")
            self.startDate.setDate(self.date)
            self.endDate.setDate(self.date)
            self.startTime.setTime(QTime(0,  0))
            self.endTime.setTime(QTime(0,  0))

            self.priorityBox.setCurrentIndex(self.priorityBox.findData(QVariant(2)))
            self.accessBox.setCurrentIndex(self.accessBox.findData(QVariant("open")))

        else:
            self.titleLine.setText(self.calendarEntry.content())
            self.locationLine.setText(self.calendarEntry.location())
            self.startDate.setDateTime(self.calendarEntry.realStartTime())
            self.startTime.setDateTime(self.calendarEntry.realStartTime())
            self.endDate.setDateTime(self.calendarEntry.realEndTime())
            self.endTime.setDateTime(self.calendarEntry.realEndTime())
            self.priorityBox.setCurrentIndex(self.priorityBox.findData(QVariant(self.calendarEntry.priority())))
            self.accessBox.setCurrentIndex(self.accessBox.findData(QVariant(self.calendarEntry.replication())))
            
            if self.calendarEntry.alarm().isValid():
                self.reminderCheckBox.setChecked(True)
                
                self.reminderDateTime.setDateTime(self.calendarEntry.alarm())
                sec = self.calendarEntry.alarm().secsTo(self.calendarEntry.realStartTime())
                if sec % 60 == 0 and sec / 60 <= 60:
                    self.reminderUnitBox.setCurrentIndex(self.reminderUnitBox.findData(QVariant(CalendarReminderUnit.Minute)))
                    self.reminderTimeBox.setValue(sec / 60)
                elif sec % 3600 == 0 and sec / 3600 <= 24:
                    self.reminderUnitBox.setCurrentIndex(self.reminderUnitBox.findData(QVariant(CalendarReminderUnit.Hour)))
                    self.reminderTimeBox.setValue(sec / 3600)
                elif sec % 86400 == 0 and sec / 86400 <= 30:
                    self.reminderUnitBox.setCurrentIndex(self.reminderUnitBox.findData(QVariant(CalendarReminderUnit.Day)))
                    self.reminderTimeBox.setValue(sec / 86400)
                else:
                    self.reminderAdvancedButton.setChecked(True)
                    self.reminderUnitBox.setCurrentIndex(self.reminderUnitBox.findData(QVariant(CalendarReminderUnit.Minute)))
                    self.reminderTimeBox.setValue(max(sec / 60,  300))

        self.resetRecurrence()
        self.buttonBox.button(QDialogButtonBox.Reset).setEnabled(False)

    def openRecurrenceDialog(self):
        self.recurrenceDialog.show()

    def recurrenceAccepted(self):
        self.entryChanged()

        recurrence = self.main.helper.calendarEntryRecurrenceToString(self.recurrenceDialog.type(),  self.recurrenceDialog.days(),  self.recurrenceDialog.exceptions(),
                               self.recurrenceDialog.start(), self.recurrenceDialog.end(),  self.recurrenceDialog.interval())
        self.recurrenceLabel.setText(recurrence)
        self.recurrenceChanged = True

    def accept(self):
        if not self.buttonBox.button(QDialogButtonBox.Reset).isEnabled():
            self.close()
            return

        if not self.titleLine.text():
            QMessageBox.warning(self, self.tr("No title found!"), self.tr("Please specify a title."))
            self.titleLine.setFocus()
            return

        if not self.connection.connected():
            QMessageBox.critical(None,
                self.tr("No active connection."),
                self.tr("""You aren't connected to a mobile phone.
All changes will get lost."""),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ok))
            self.close()

        start = QDateTime(self.startDate.date(),  self.startTime.time())
        end = QDateTime(self.endDate.date(),  self.endTime.time())

        if end < start:
            QMessageBox.warning(self, self.tr("Event Entry Validation"), self.tr("The event ends before it starts. Please correct dates and times."))
            self.startDate.setFocus()
            return

        if self.calendarEntry is not None:
            entry = self.calendarEntry
        else:
            entry = CalendarEntry()
            entry.setType(self.type)

        entry.setContent(unicode(self.titleLine.text()))
        entry.setLocation(unicode(self.locationLine.text()))
        entry.setStartTime(start)
        entry.setEndTime(end)
        entry.setLastModified(QDateTime.currentDateTime())
        entry.setReplication(unicode(self.accessBox.itemData(self.accessBox.currentIndex()).toString()))
        entry.setPriority(self.priorityBox.itemData(self.priorityBox.currentIndex()).toInt()[0])

        if self.reminderCheckBox.isChecked():
            if self.reminderAdvancedButton.isChecked():
                entry.setAlarm(self.reminderDateTime.dateTime())
            else:
                type = self.reminderUnitBox.itemData(self.reminderUnitBox.currentIndex()).toInt()[0]
                if type == CalendarReminderUnit.Minute:
                    entry.setAlarm(start.addSecs(-self.reminderTimeBox.value() * 60))
                elif type == CalendarReminderUnit.Hour:
                    entry.setAlarm(start.addSecs(-self.reminderTimeBox.value() * 3600))
                elif type == CalendarReminderUnit.Day:
                    entry.setAlarm(start.addSecs(-self.reminderTimeBox.value() * 86400))
        else:
            entry.setAlarm(0)

        if self.recurrenceChanged:
            entry.setRepeatType(self.recurrenceDialog.type())
            entry.setRepeatDays(self.recurrenceDialog.days())
            entry.setRepeatExceptions(self.recurrenceDialog.exceptions())
            entry.setRepeatStart(self.recurrenceDialog.start())
            entry.setRepeatEnd(self.recurrenceDialog.end())
            entry.setRepeatInterval(self.recurrenceDialog.interval())

        if self.calendarEntry:
            self.connection.calendarEntryChange(entry)
        else:
            self.connection.calendarEntryAdd(entry)

        self.main.mainWindow.calendarWidget.reloadIncidences()
        self.close()
