# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_export_progress
from lib.classes import *

class ExportProgress(QDialog,  ui.ui_export_progress.Ui_ExportProgress):
    def __init__(self, parent, main,  export):
        super(ExportProgress,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.export = export

        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        main.setupButtonBox(self.buttonBox)

        self.messages= 0
        self.contacts = 0
        self.currentMessage = 0
        self.currentContact = 0

        self.calendarFileCount = 0
        self.calendarFile = 0

        self.connect(export,  SIGNAL("messageExport"),  self.updateMessageNumber)
        self.connect(export,  SIGNAL("messageCountChanged"),  self.updateMessageCount)
        self.connect(export,  SIGNAL("calendarFile"),  self.updateCalendarNumber)
        self.connect(export,  SIGNAL("calendarFileCountChanged"),  self.updateCalendarCount)
        self.connect(export,  SIGNAL("contactExport"),  self.updateContactNumber)
        self.connect(export,  SIGNAL("contactCountChanged"),  self.updateContactCount)
        self.connect(export,  SIGNAL("fileChanged"),  self.updateFile)
        self.connect(export,  SIGNAL("exportFinished"),  self.exportFinished)
        self.connect(self,  SIGNAL("rejected()"),  self.abort)

    def updateMessageNumber(self,  num):
        self.currentMessage = num
        self.updateMessages()

    def updateMessageCount(self,  num):
        self.messages = num
        self.updateMessages()

    def updateCalendarNumber(self,  num):
        self.calendarFile = num
        self.updateCalendar()

    def updateCalendarCount(self,  num):
        self.calendarFileCount = num
        self.updateCalendar()

    def updateContactNumber(self,  num):
        self.currentContact = num
        self.updateContacts()

    def updateContactCount(self,  num):
        self.contacts = num
        self.updateContacts()

    def updateMessages(self):
        self.messageCount.setText(QString("%1 / %2").arg(self.currentMessage).arg(self.messages))
        if self.messages != 0:
            self.messageProgress.setValue(int(self.currentMessage / float(self.messages) * 100))

    def updateCalendar(self):
        self.calendarCount.setText(QString("%1 / %2").arg(self.calendarFile).arg(self.calendarFileCount))
        if self.calendarFileCount != 0:
            self.calendarProgress.setValue(int(self.calendarFile / float(self.calendarFileCount) * 100))

    def updateContacts(self):
        self.contactCount.setText(QString("%1 / %2").arg(self.currentContact).arg(self.contacts))
        if self.contactCount != 0:
            self.contactProgress.setValue(int(self.currentContact / float(self.contacts) * 100))

    def updateFile(self,  file):
        self.fileLabel.setText(file)

    def exportFinished(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Abort).setEnabled(False)

    def abort(self):
        self.export.stopExport = True

    def forceClose(self):
        self.export.stopExport = True
        self.export.running = False
        self.close()

    def closeEvent(self,  e):
        if not self.export.running:
            e.accept()
            return

        ret = QMessageBox.warning(self,  self.tr("Abort export process"),  self.tr("Do you really want to cancel this operation?"),
                                  QMessageBox.Yes,  QMessageBox.No)

        if ret == QMessageBox.Yes:
            e.accept()
        else:
            e.ignore()
