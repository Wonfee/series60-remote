# -*- coding: utf-8 -*-

# Copyright (c) 2010 Pierre-Yves Chibon <py@chibon.fr>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

# Export the contacts into a vCard format using python-vobject
# Export the messages into a CSV (comma separated value) file

## TODO: Export the agenda into a csv file

import os
from types import *
from PyQt4.QtCore import *
from lib.classes import *
import lib.export_general

class CSVFormatter(lib.export_general.GeneralFormatter):
    def __init__(self,  parent,  main,  *args,  **kwargs):
        lib.export_general.GeneralFormatter.__init__(self,  parent,  main,  *args,  **kwargs)

        self.main = main
        self.database = main.database
        self.helper = main.helper
        self.log = main.log

        self.contacts = list()

        self.fields = ["last_name",  "first_name",  "job_title",  "company_name",  "phone_number",  "mobile_number",
                           "pager_number",  "fax_number",  "email_address",  "url",  "postal_address", "po_box",
                           "extended_address",  "street_address",  "postal_code",  "city",  "state",  "country",
                           "dtmf_string",  "date",  "note",  "prefix",  "suffix","second_name"]

        if self.thumbnails == ExportThumbnails.Yes:
            self.fields.append("thumbnail_image")

    @staticmethod
    def format():
        return "CSV"

    @staticmethod
    def supportedExportItems():
        return ExportItems.Contacts | ExportItems.Messages

    @staticmethod
    def supportedExportOptions():
        return ExportOptions.Period | ExportOptions.Order | ExportOptions.Thumbnails

    @staticmethod
    def extraExportOptions():
        return 0

    @staticmethod
    def fileExtension():
        return "csv"

    def initialize(self):
        """ Create the directory in which the CSV file will be exported """
        # Create needed directorys
        if not QDir(self.directory).exists():
            QDir().mkdir(self.directory)

        if not QDir(self.directory + "messages").exists():
            QDir(self.directory).mkdir("messages")

        return True

    def openMessageFile(self,  filename):
        self.file = open(self.directory + "messages" + os.sep + filename + '.csv',  'w')
        self.file.write(self.formatCsvLine(['Date',  'Time', 'Name',  'Message']))

    def subFormatMessage(self,  message):
        """
        Stores all the messages into a list in the order:
        'date', 'From', 'message'
        """
        name = unicode(message.contact().name()).encode('utf-8')
        msg = unicode(message.message()).encode('utf-8')
        date = unicode(message.dateTime().date().toString(Qt.ISODate))
        time = unicode(message.dateTime().time().toString(Qt.ISODate))

        #self.list_messages.append( [date, name, msg] )
        self.file.write(self.formatCsvLine([date,  time,  name,  msg]))

    def finalizeMessageFile(self,  file):
        """ Write messages to a file """
        self.file.close()

    def openContactFile(self,  file):
        self.file = open(self.directory + file + '.csv', 'w')

    def subFormatContact(self,  contact):
        """ Happens for each contact into the dictionary """
        c = ["" for i in range(0,len(self.fields))]
        for field,  value in contact:
            fieldname = field.type()

            if self.thumbnails != ExportThumbnails.Yes and field.isPicture():
                continue

            if field.location() != 'none':
                fieldname = fieldname + '_' + field.location()

            if fieldname not in self.fields:
                self.fields.append(fieldname)
                c.append("")

            # position of the field
            pos = self.fields.index(fieldname)
            # check is the field is alreay filled (reason: date is present twice)
            if len(str(c[pos])) != 0 :
                cnt = 1;
                fieldname_tmp = fieldname
                while ( fieldname_tmp in self.fields and len(str( c[ self.fields.index(fieldname_tmp) ] )) != 0 ):
                    cnt = cnt + 1
                    fieldname_tmp = '%s_%s' %(fieldname, cnt)
                fieldname = fieldname_tmp
                if fieldname not in self.fields:
                    self.fields.append(fieldname)
                    c.append("")

            # Append the value in the right column
            c[self.fields.index(fieldname)] = unicode(value).encode('utf-8')

        # Add the contact to the list of contacts
        self.contacts.append(c)

    def finalizeContactFile(self,  file):
        """ Write contacts to a file """
        self.contacts.insert(0, self.fields)
        for contact in self.contacts:
            self.file.write(self.formatCsvLine(contact))

        self.file.close()

    def formatCsvLine(self, list, delimiter = ','):
        '''
            This method writes a CSV file with the name filename, the delimiter
            'delimiter' (',' by default) and with the content given as parameter.
            The content is the list of rows. It checks if all element of
            the list are list as well if it is then it writes it to the
            file with the delimiter given else it happens the string directly.
        '''
        line = ''
        pos = 0
        for el in list:
            #print "el is",  el
            pos = pos + 1
            line += '"%s"' % str(el)
            if pos != len(list):
                line += delimiter
        line += '\n'
        return line
