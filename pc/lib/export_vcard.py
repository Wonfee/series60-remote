# -*- coding: utf-8 -*-

# Copyright (c) 2010 Pierre-Yves Chibon <py@chibon.fr>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

# Export the contacts into a vCard format using python-vobject

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.classes import *
import lib.export_general
import lib.vobjectconverter

class VCardFormatter(lib.export_general.GeneralFormatter):
    def __init__(self,  parent,  main,  exportProgressDialog,  *args,  **kwargs):
        lib.export_general.GeneralFormatter.__init__(self,  parent,  main,  exportProgressDialog,  *args,  **kwargs)

        self.main = main
        self.database = main.database
        self.helper = main.helper

        self.exportProgressDialog = exportProgressDialog

    @staticmethod
    def format():
        return "vCard"

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
        return "vcf"

    def initialize(self):
        """ Create the directory in which the vCard file will be exported """

        # Check if the needed vobject module is installed
        self.converter = lib.vobjectconverter.VObjectConverter()
        missingModules = self.converter.missingModules()
        if missingModules:
            message = QMessageBox.critical(self.exportProgressDialog,
            self.tr("%1 not found!").arg(missingModules),
            self.tr("""Exporting %1 objects is not possible:
Please install the %2 module.""").arg("vcard",  missingModules))
            return False

        # Create needed directorys
        if not QDir(self.directory).exists():
            QDir().mkdir(self.directory)

        if QDir(self.directory).exists('Contacts.vcf'):
            message = QMessageBox.question(self.exportProgressDialog,
            self.tr("File already exists!"),
            self.tr("""The file Contacts.vcf already exists in this directory.
Would you like to overwrite it?"""),  QMessageBox.Yes | QMessageBox.No,  QMessageBox.No)
            if message == QMessageBox.No:
                return False

        return True

    def openContactFile(self,  file):
        self.file = open(self.directory + file + '.vcf', 'w')

    def subFormatContact(self,  contact):
        """ Happends each contact into the vCard list """
        c = self.converter.convertToVObject(contact)

        # Add the contact to the vcard file
        self.file.write(c.serialize())

    def finalizeContactFile(self,  file):
        self.file.close()
