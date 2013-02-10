# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtSql import *
import lib.export_html
import lib.export_vcard
import lib.export_csv
import lib.export_ldif
from lib.classes import *

class Export(QObject):
    def __init__(self, parent, main):
        super(Export,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.running = False
        self.stopExport = False

        self.__formats = list()
        self.__formats.append( lib.export_html.HTMLFormatter )
        self.__formats.append( lib.export_csv.CSVFormatter )
        self.__formats.append( lib.export_vcard.VCardFormatter )
        self.__formats.append( lib.export_ldif.LdifFormatter )

    def formats(self):
        return self.__formats

    def start(self,  exportProgressDialog,  plugin,  items,  *args,  **kwargs):
        plugin = plugin(self,  self.main,  exportProgressDialog,  *args,  **kwargs)

        if not items & ExportItems.Contacts == ExportItems.Contacts:
            exportProgressDialog.contactWidget.setHidden(True)

        if not items & ExportItems.Messages == ExportItems.Messages:
            exportProgressDialog.messagesWidget.setHidden(True)

        if not items & ExportItems.Calendar == ExportItems.Calendar:
            exportProgressDialog.calendarWidget.setHidden(True)

        if not plugin.extraExportOptions() & ExportExtraOptions.WriteCalendar == ExportExtraOptions.WriteCalendar:
            exportProgressDialog.createCalendarWidget.setHidden(True)

        font = exportProgressDialog.fileLabel.font()
        font.setItalic(False)
        exportProgressDialog.fileLabel.setFont(font)

        exportProgressDialog.fileExtensionLabel.setText("." + plugin.fileExtension())

        exportProgressDialog.resize(exportProgressDialog.width(),  exportProgressDialog.minimumHeight())
        exportProgressDialog.show()

        self.running = True

        currentMessage = 0
        currentCalendarFile = 0
        currentContact = 0

        self.connect(plugin,  SIGNAL("fileChanged"),  lambda f: self.emit(SIGNAL("fileChanged"),  f))
        self.connect(plugin,  SIGNAL("contactCountChanged"),  lambda f: self.emit(SIGNAL("contactCountChanged"),  f))
        self.connect(plugin,  SIGNAL("calendarFileCountChanged"),  lambda f: self.emit(SIGNAL("calendarFileCountChanged"),  f))

        self.emit(SIGNAL("messageCountChanged"),  self.database.messageCount(contactFilter=plugin.exportContacts))
        self.emit(SIGNAL("contactCountChanged"),  len(plugin.contactList))

        if not plugin.initialize():
            exportProgressDialog.forceClose()
            return

        if items & ExportItems.Messages == ExportItems.Messages:
            for message in self.database.messages(order=plugin.orderString(),  contactFilter=plugin.exportContacts):
                # Process all pending events until there are no more events to process.
                self.main.app.processEvents()
                if self.stopExport:
                    self.running = False
                    return
                currentMessage += 1
                self.emit(SIGNAL("messageExport"),  currentMessage)
                plugin.formatMessage(message)

            if plugin.files:
                plugin.finalizeMessageFile(plugin.files[-1])

            plugin.finalizeMessageFiles()

            if plugin.extraExportOptions() & ExportExtraOptions.WriteCalendar == ExportExtraOptions.WriteCalendar:
                for file in plugin.files:
                    self.main.app.processEvents()
                    if self.stopExport:
                        self.running = False
                        return

                    if file.startswith("Messages"):
                        currentCalendarFile += 1
                        self.emit(SIGNAL("calendarFile"),  currentCalendarFile)
                        self.emit(SIGNAL("fileChanged"),  file)
                        plugin.writeCalender(file)

        if items & ExportItems.Contacts == ExportItems.Contacts:
            seperateContactFile = plugin.extraExportOptions() & ExportExtraOptions.ContactsInSeperateFiles == ExportExtraOptions.ContactsInSeperateFiles
            if not seperateContactFile:
                plugin.emit(SIGNAL("fileChanged"),  "Contacts")
                plugin.openContactFile("Contacts")

            for contact in plugin.contactList:
                self.main.app.processEvents()
                if self.stopExport:
                    self.running = False
                    return

                # Only handle active contacts
                if contact.idOnPhone():
                    currentContact += 1
                    self.emit(SIGNAL("contactExport"),  currentContact)

                    if seperateContactFile:
                        plugin.emit(SIGNAL("fileChanged"),  plugin.formatContactFile(contact))
                        plugin.openContactFile(plugin.formatContactFile(contact))

                    plugin.formatContact(contact)

                    if seperateContactFile:
                        plugin.finalizeContactFile(plugin.formatContactFile(contact))

            if not seperateContactFile:
                plugin.finalizeContactFile("Contacts")

            plugin.finalizeContactFiles()

        plugin.finalizeFiles()

        self.running = False
        self.emit(SIGNAL("exportFinished"))
