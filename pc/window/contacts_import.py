# -*- coding: utf-8 -*-

# Copyright (c) 2010 Pierre-Yves Chibon <py@chibon.fr>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

import base64
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_contacts_import
import widget.ImageButton
import lib.vobjectconverter
from lib.classes import *

class ContactsImport(QDialog,  ui.ui_contacts_import.Ui_ContactsImport):
    """
    This class handle the import of contacts from a file into the phone.
    Contacts come from a vCard file or a ldif file.
    """
    def __init__(self, parent, main,  format="vcard"):
        super(ContactsImport,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.format = format

        self.setupUi(self)
        main.setupButtonBox(self.buttonBox)

        # Make the connections between the functions and the buttons
        self.connect(self.contactsAddButton,SIGNAL("clicked()"), self.addAllContact)
        self.connect(self.selectFileButton, SIGNAL('clicked()'), self.showDialog)
        self.connect(self.contactsList,SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),self.showContact)

        if self.createConverter():
            self.show()
    
    def containsContact(self, contact, contactlist):
        """ 
        For a given contact check if a similar contact exists
        in the given contactlist
        """
        for c in contactlist:
            if c.value('last_name') == contact.value('last_name') \
                and c.value('first_name') == contact.value('first_name'):
                return True
        return False
        

    def addAllContact(self):
        """ Add all the contact contained in the list """
        
        contactknown = self.database.contacts()
        
        cnt = 0
        flagask = True
        flagupdate = False
        flagadd = False
        while self.contactsList.count () >= 1:
            item = self.contactsList.takeItem(0)
            if item.checkState() != Qt.Checked:
                continue
            contact = item.data(Roles.ContactRole).toPyObject()

            if self.containsContact(contact, contactknown) and flagask is True:
                flagupdate = False
                flagadd = False
                dialog = QMessageBox()
                dialog.setWindowTitle("User already exists!")
                dialog.setText("""A user with the name '%s' is already present in your phone,
    What do you want to do ?""" %contact.name())
                updateButton = dialog.addButton("Update", QMessageBox.YesRole)
                updateAllButton = dialog.addButton("Update all", QMessageBox.YesRole)
                addButton = dialog.addButton("Add", QMessageBox.YesRole)
                addAllButton = dialog.addButton("Add all", QMessageBox.YesRole)
                dialog.exec_()
                if dialog.clickedButton() == updateButton:
                    self.log.debug("update button clicked")
                    flagupdate = True
                elif dialog.clickedButton() == updateAllButton:
                    self.log.debug("update all button clicked")
                    flagupdate = True
                    flagask = False
                elif dialog.clickedButton() == addButton:
                    self.log.debug("add button clicked")
                    flagadd = True
                elif dialog.clickedButton() == addAllButton:
                    self.log.debug("add all button clicked")
                    flagadd = True
                    flagask = False

            if flagupdate is True:
                self.log.debug("update to phone")
                remove,  add = self.database.contactChange(contact)
                self.connection.contactChange(contact,  remove,  add)
            elif flagadd is True:
                self.log.debug("added to phone")
                self.connection.contactAdd(contact)
            else:
                self.log.debug("adding ned contact to phone")
                self.connection.contactAdd(contact)

            self.log.debug(QString("%1 %2").arg(cnt).arg(contact.name()))
            cnt += 1
        self.log.info(QString("%1 contacts added").arg(cnt))
        self.close()

    def showDialog(self):
        """ Show a file select dialog"""
        if self.format == "vcard":
            filenames = QFileDialog.getOpenFileNames(self, self.tr('Open vcard file'), QDir.homePath(),  self.tr("Vcards (*.vcf);;All files (*)"))
        elif self.format == "ldif":
            filenames = QFileDialog.getOpenFileNames(self, self.tr('Open ldif file'), QDir.homePath(),  self.tr("LDIF (*.ldif);;All files (*)"))
        for filename in filenames:
            self.fileToContact(filename)

    def createConverter(self):
        """ Create the needed converter to convert Contact objects """
        if self.format == "vcard":
            self.converter = lib.vobjectconverter.VObjectConverter()
        elif self.format == "ldif":
            self.converter = lib.ldifconverter.LdifConverter()

        missingModules = self.converter.missingModules()
        if missingModules:
            message = QMessageBox.critical(self.parent,
            self.tr("%1 not found!").arg(missingModules),
            self.tr("""Exporting %1 objects is not possible:
Please install the %2 module.""").arg(self.format,  missingModules))
            return False
        return True

    def fileToContact(self, filename):
        """
        Use the VObject converter to read the file and set the contacts
        in the GUI.
        """
        if self.converter is False:
            return

        if self.format == "vcard":
            try:
                v = self.converter.importVCardToContact(filename)
            except vobject.base.ParseError, ex:
                self.log.error(QString("Exception: %1").arg(ex))
                message = QMessageBox.critical(self,
                            self.tr("Error import"),
                            self.tr("An error occured while parsing the file: \n%1").arg(ex)
                        )
                return False

            cnt = 0
            for c in v:
                cnt += 1
                con = self.converter.convertToContact(c)
                self.addContact(con)
            self.log.info(QString("%1 contacts read").arg(cnt))
            item = QTextBrowser(self.contactBrowser)
            item.setText("%s contacts read" %cnt)
            return True

        elif self.format == "ldif":
            try:
                v = self.converter.importLdifToContact(filename)
                v.parse()
            except Exception, ex:
                self.log.error(QString("Exception: %1").arg(ex))
                message = QMessageBox.critical(self,
                            self.tr("Error import"),
                            self.tr("An error occured while parsing the file: \n%1").arg(ex)
                        )
                return False

            cnt = 0
            for item in v.conversion:
                self.addContact(item)
                cnt = cnt +1
            self.log.info(QString("%1 contacts read").arg(cnt))
            item = QTextBrowser(self.contactBrowser)
            item.setText("%s contacts read" %cnt)
            return True


    def addContact(self, contact):
        """ Add contact to the QListWidget """
        item = QListWidgetItem(self.contactsList)
        item.setText(contact.name())
        item.setData(Roles.ContactRole, QVariant(contact))
        item.setCheckState(Qt.Checked)

    def showContact(self,  contact,  previousContact):
        """ Displays the contact's information on the Browser part """
        try:
            contact = contact.data(Roles.ContactRole).toPyObject()
        except:
            return
        self.contactBrowser.clear()

        for field,  value in contact.values():
            if field.isPicture():
                continue
            if field.isDate():
                value = QDate.fromString(value,  "yyyyMMdd").toString(Qt.DefaultLocaleLongDate)
            self.contactBrowser.insertHtml("<b>" + field.toString(printLocation=True) + " </b> " + value + "<br />")


