# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import pickle
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import ui.ui_wizard_helloPage
import ui.ui_wizard_phonePage
import ui.ui_wizard_installPage
import ui.ui_wizard_runPage
import ui.ui_wizard_minimizePage
import ui.ui_wizard_databasePage
import ui.resource_rc
import lib.obex_wrapper
from lib.classes import *

try:
   # PyBluez module for Linux and Windows
   import bluetooth
except ImportError:
   # Lightblue for Mac OS X
   import lightblue

LINUX= "qt_x11_wait_for_window_manager" in dir()

class Wizard(QWizard):
    def __init__(self,  parent,  main):
        super(Wizard,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.helloPage = helloPage(self,  main)
        self.phonePage = phonePage(self,  main)
        self.installPage = installPage(self,  main)
        self.runPage = runPage(self,  main)
        self.minimizePage = minimizePage(self,  main)
        self.databasePage = databasePage(self,  main)

        self.addPage(self.helloPage)
        self.addPage(self.phonePage)
        self.addPage(self.installPage)
        self.addPage(self.runPage)
        self.addPage(self.minimizePage)
        self.addPage(self.databasePage)

        self.connect(self,  SIGNAL("finished(int)"),  self.finished)

        self.setWindowTitle(self.tr("Series 60 Remote - Settings"))
        self.setWindowIcon(QIcon(":/phone"))

        self.log.info(QString("Show wizard"))

        self.show()

    def __str__(self):
        return "\"Wizard\""

    def finished(self,  id):
        if id == 1:
            self.settings.setSetting("general/firstStart",  False)
        else:
            self.main.app.quit()

    def closeEvent(self,  event):
        self.main.app.quit()
        event.accept()

class helloPage(ui.ui_wizard_helloPage.Ui_helloPage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(helloPage,  self).__init__(parent)
        
        self.parent = parent
        self.main = main
        
        self.setupUi(self)

        self.previewWidget.setHidden(self.main.versionIsStable)

    def validatePage(self):
        return True

class phonePage(ui.ui_wizard_phonePage.Ui_phonePage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(phonePage,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        
        self.setupUi(self)
    
    def validatePage(self):
        devices = self.devicesView.selectedDevices()

        if len(devices) == 0:
            self.log.warning(QString("No device selected"))
            ret = QMessageBox.question(self, self.tr("No devices found"),
            self.trUtf8("""You didn't select a mobile phone.
If you continue, you have to select it afterwards in the settings."""),
                QMessageBox.StandardButtons(\
                    QMessageBox.Ignore | \
                    QMessageBox.Retry),
                QMessageBox.Retry)

            if ret == QMessageBox.Retry:
                return False
            else:
                self.devicesView.scanStop()
                return True

        self.log.info(QString("Selected device %1 with mac %2").arg(devices[0].name(),  devices[0].bluetoothAddress()))
        self.settings.setSetting("bluetooth/lastName",  devices[0].name())
        self.devicesView.scanStop()
        
        return True

class installPage(ui.ui_wizard_installPage.Ui_installPage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(installPage,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)

    def initializePage(self):
        self.devices = self.parent.phonePage.devicesView.selectedDevices()
        if len(self.devices) == 0:
            self.sendPythonButton.setEnabled(False)
            self.sendApplicationButton.setEnabled(False)
        else:
            self.sendPythonButton.setEnabled(True)
            self.sendApplicationButton.setEnabled(True)

            self.connect(self.sendApplicationButton,  SIGNAL("clicked()"),  self.sendApplicationFile)
            self.connect(self.sendPythonButton,  SIGNAL("clicked()"),  self.sendPythonFile)

        if lib.obex_wrapper.FOUND_OBEX:
            self.obexStack.setCurrentWidget(self.obexFoundWidget)
            self.log.info(QString("OBEX support was found, trying to send installation file to device"))
        else:
            self.obexStack.setCurrentWidget(self.obexNotFoundWidget)
            self.log.info(QString("OBEX support was not found"))
            if LINUX:
                self.operatingSystemStack.setCurrentWidget(self.linuxWidget)
            else:
                self.operatingSystemStack.setCurrentWidget(self.windowsWidget)

        self.connect(self.openFolderButton,  SIGNAL("clicked()"),  self.helper.openFolder)
    
    def sendApplicationFile(self):
        if self.py20Box.isChecked():
            self.helper.sendFile(self,  self.devices[0], self.main.applicationSis_Py20)
        else:
            self.helper.sendFile(self,  self.devices[0], self.main.applicationSis_Py14)
    
    def sendPythonFile(self):
        if self.py20Box.isChecked():
            self.helper.sendFile(self, self.devices[0], self.main.pythonSis_Py20)
        else:
            self.helper.sendFile(self,  self.devices[0], self.main.pythonSis_Py14)

    def validatePage(self):
        return True

class runPage(ui.ui_wizard_runPage.Ui_runPage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(runPage,  self).__init__(parent)
        self.setupUi(self)

    def validatePage(self):
        return True

class minimizePage(ui.ui_wizard_minimizePage.Ui_minimizePage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(minimizePage,  self).__init__(parent)
        self.setupUi(self)

    def validatePage(self):
        return True

class databasePage(ui.ui_wizard_databasePage.Ui_databasePage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(databasePage,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings

        self.setupUi(self)

        self.sqliteDriverNotFoundLabel.setHidden(QSqlDatabase.drivers().contains("QSQLITE"))
        self.mysqlDriverNotFoundLabel.setHidden(QSqlDatabase.drivers().contains("QMYSQL"))

    def validatePage(self):
        type = str(self.typeBox.currentText()).lower()
        data = dict()

        if type == "sqlite":
           file = str(QFileInfo(self.settings.fileName()).absoluteDir().absolutePath()) + "/messages.db"
           data["filename"] = file
        elif type == "mysql":
            host = str(self.hostLine.text())
            port = int(self.portBox.value())
            user = str(self.userLine.text())
            pw = str(self.passLine.text())
            db = str(self.databaseLine.text())

            if not (host and port and user and pw and db):
                QMessageBox.critical(self,  self.trUtf8("Mysql connection fields incomplete!"), self.trUtf8("You didn't fill in all required fields. If you are ubsure please use SQLite."))
                return False

            data["host"] = host
            data["port"] = port
            data["user"] = user
            data["pass"] = pw
            data["database"] = db

        self.log.info(QString("Trying to connect to database"))
        ret = self.database.openDatabase(type,  data)

        if ret == False:
            # Connection wasn't succesful
            # Show error message
            err = self.database.error()

            message = QMessageBox.critical(self,
            self.tr("Connection failed!"),
            self.trUtf8("Connection failed with error:\n%1\n").arg(err),
            QMessageBox.StandardButtons(\
                    QMessageBox.Ignore | \
                    QMessageBox.Retry),
            QMessageBox.Retry)

            if message == QMessageBox.Retry:
                return False

        else:
            # Connection was successful
            # Write connection data to settings
            self.settings.beginGroup("database")
            self.settings.setSetting("type",  type)
            if type == "sqlite":
                self.settings.beginGroup("sqlite")
                self.settings.setSetting("filename",  file)
                self.settings.endGroup()
            elif type == "mysql":
                self.settings.beginGroup("mysql")
                self.settings.setSetting("host", host)
                self.settings.setSetting("port", port)
                self.settings.setSetting("user", user)
                self.settings.setSetting("pass", pw)
                self.settings.setSetting("database", db)
                self.settings.endGroup()
            self.settings.endGroup()

            devices = self.parent.phonePage.devicesView.selectedDevices()
            for device in devices:
                self.database.deviceAdd(device)

        return True
