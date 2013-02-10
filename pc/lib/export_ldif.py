# -*- coding: utf-8 -*-

# Copyright (c) 2010 Pierre-Yves Chibon <py@chibon.fr>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

# Export the contacts into a ldif format using python-ldap

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.classes import *
import lib.export_general
import lib.ldifconverter

class LdifFormatter(lib.export_general.GeneralFormatter):
    def __init__(self,  parent,  main,  exportProgressDialog,  *args,  **kwargs):
        lib.export_general.GeneralFormatter.__init__(self,  parent,  main,  exportProgressDialog,  *args,  **kwargs)

        self.main = main
        self.database = main.database
        self.helper = main.helper

        self.exportProgressDialog = exportProgressDialog

    @staticmethod
    def format():
        return "ldif"

    @staticmethod
    def supportedExportItems():
        return ExportItems.Contacts

    @staticmethod
    def supportedExportOptions():
        return 0

    @staticmethod
    def extraExportOptions():
        return 0

    @staticmethod
    def fileExtension():
        return "ldif"

    def initialize(self):
        """ Create the directory in which the ldif file will be exported """

        # Check if the needed vobject module is installed
        self.converter = lib.ldifconverter.LdifConverter()
        missingModules = self.converter.missingModules()
        if missingModules:
            message = QMessageBox.critical(self.exportProgressDialog,
            self.tr("%1 not found!").arg(missingModules),
            self.tr("""Exporting %1 objects is not possible:
Please install the %2 module.""").arg("ldif",  missingModules))
            return False

        # Create needed directorys
        if not QDir(self.directory).exists():
            QDir().mkdir(self.directory)

        if QDir(self.directory).exists('Contacts.ldif'):
            message = QMessageBox.question(self.exportProgressDialog,
            self.tr("File already exists!"),
            self.tr("""The file Contacts.ldif already exists in this directory.
Would you like to overwrite it?"""),  QMessageBox.Yes | QMessageBox.No,  QMessageBox.No)
            if message == QMessageBox.No:
                return False

        return True

    def openContactFile(self,  file):
        self.file = open(self.directory + file + '.ldif', 'w')

    def subFormatContact(self,  contact):
        """ Happends each contact into the ldif list """
        c = self.converter.convertToLdif(contact)

        # Add the contact to the ldif file
        self.file.write(c)

    def finalizeContactFile(self,  file):
        self.file.close()
