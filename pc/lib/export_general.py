# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtSql import *
from lib.classes import *

class GeneralFormatter(QObject):
    def __init__(self,  parent,  main, exportProgressDialog,
                 contacts=ExportContacts.All,
                 period=ExportPeriod.Daily,
                 graph=ExportGraph.Yes,
                 legend=ExportLegend.Yes,
                 thumbnails=ExportThumbnails.Yes,
                 directory='./export/',
                 order=ExportOrder.ASC,
                 graphFormat=ExportGraphFormat.PNG,
                 exportContacts=None):
        QObject.__init__(self,  parent)

        self.main = main
        self.database = main.database

        self.contacts = contacts
        self.period = period
        self.graph = graph
        self.legend = legend
        self.thumbnails = thumbnails
        self.directory = directory
        self.order = order
        self.graphFormat = graphFormat
        self.exportContacts = exportContacts

        self.messageFiles = 0

        self.lastPeriod = QDate()
        self.files = list()

        if self.contacts == ExportContacts.ContactsWithMessages:
            self.contactList = list()
        elif self.contacts == ExportContacts.All:
            self.contactList = [contact for contact in self.database.contacts(True)] # Convert generator to list
        elif self.contacts == ExportContacts.Filter:
            self.contactList = self.exportContacts
        elif self.contacts == ExportContacts.None_:
            self.contactList = list()

    def orderString(self):
        if self.order == ExportOrder.ASC:
            return "ASC"
        return "DESC"

    def formatMessage(self,  message):
        c = message.contact()
        # Add this contact to list of messages with contacts if this filter is set
        if self.contacts == ExportContacts.ContactsWithMessages and c.idOnPhone() and c not in self.contactList:
            self.contactList.append(c)
            self.emit(SIGNAL("contactCountChanged"),  len(self.contactList))

        # Check if the content should be in a new file...
        date = message.dateTime().date()
        if not self.lastPeriod \
            or self.period == ExportPeriod.Yearly and self.lastPeriod.year() != date.year() \
            or self.period == ExportPeriod.Monthly and (self.lastPeriod.year() != date.year() or self.lastPeriod.month() != date.month()) \
            or self.period == ExportPeriod.Daily and (self.lastPeriod.year() != date.year() or self.lastPeriod.month() != date.month()
                                       or self.lastPeriod.day() != date.day()):

            if self.files:
                self.finalizeMessageFile(self.files[-1])

            self.lastPeriod = date

            if self.period == ExportPeriod.All:
                new = "Messages"
            elif self.period == ExportPeriod.Yearly:
               new =  "Messages_" + date.toString("yyyy")
            elif self.period == ExportPeriod.Monthly:
                new =  "Messages_" + date.toString("yyyy_MM")
            else:
                new =  "Messages_" + date.toString("yyyy_MM_dd")

            self.emit(SIGNAL("fileChanged"),  new)
            self.messageFiles += 1
            self.emit(SIGNAL("calendarFileCountChanged"),  self.messageFiles)
            if not self.openMessageFile(new):
                return False
            self.files.append(str(new))

        return self.subFormatMessage(message)

    def formatContactName(self,  contact):
        name = contact.name()
        # Only allow ascii chars in filename and filter special symbols
        name = name.encode('ascii', 'replace')

        replace = " !\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"
        for char in replace:
            name = name.replace(char,  '_')

        return str(contact.id()) + "_" + name

    def formatContactFile(self,  contact):
        return "Contact_" + self.formatContactName(contact)

    def formatContact(self,  contact):
        self.subFormatContact(contact)

    def periodString(self):
        if self.period == ExportPeriod.All:
            return unicode(self.tr("All messages"))

        if self.period == ExportPeriod.Yearly:
           return unicode(self.tr("Messages for %1").arg(self.lastPeriod.toString("yyyy")))

        if self.period == ExportPeriod.Monthly:
            return unicode(self.tr("Messages for %1").arg(self.lastPeriod.toString("MMMM, yyyy")))

        return unicode(self.tr("Messages for %1").arg(self.lastPeriod.toString("dddd, dd. MMMM yyyy")))

    # Function needed to be implement in the children
    def initialize(self):
        return True
    def openMessageFile(self,  filename):
        return True
    def subFormatMessage(self,  message):
        return True
    def finalizeMessageFiles(self):
        return True
    def writeCalender(self,  filename):
        return True
    def openContactFile(self,  filename):
        return True
    def subFormatContact(self,  contact):
        return True
    def finalizeContactFile(self,  file):
        return True
    def finalizeContactFiles(self):
        return True
    def finalizeFiles(self):
        return True

