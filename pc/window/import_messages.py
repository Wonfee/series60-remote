# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.import_messages
import ui.ui_import_applicationPage
import ui.ui_import_versionPage
import ui.ui_import_settingsPage
import ui.ui_import_messagesPage
from lib.classes import *

class ImportMessages(QWizard):
    def __init__(self,  parent,  main):
        super(ImportMessages,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings

        self.application = None
        self.version = None

        self.applicationPage = applicationPage(self,  main)
        self.versionPage = versionPage(self,  main)
        self.settingsPage = settingsPage(self,  main)
        self.messagesPage = messagesPage(self,  main)

        self.addPage(self.applicationPage)
        self.addPage(self.versionPage)
        self.addPage(self.settingsPage)
        self.addPage(self.messagesPage)

        self.connect(self,  SIGNAL("finished(int)"),  self.finished)

        self.setWindowTitle(self.tr("Import Messages"))
        self.setWindowIcon(QIcon(":/document-import"))

        self.log.info(QString("Show import wizard"))

        self.show()

    def finished(self):
        pass

    def __str__(self):
        return "\"Import\""

class applicationPage(ui.ui_import_applicationPage.Ui_applicationPage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(applicationPage,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.setupUi(self)

        self.connect(self.applicationList, SIGNAL("itemSelectionChanged()"), SIGNAL("completeChanged()"))

        applications = lib.import_messages.Import(self,  main).applications()
        for app in applications:
            item = QListWidgetItem(app.applicationName(),  self.applicationList)
            item.setData(Roles.ApplicationRole,  QVariant(app))

    def isComplete(self):
        return bool(self.applicationList.selectedItems())

    def validatePage(self):
        self.parent.application = self.applicationList.selectedItems()[0].data(Roles.ApplicationRole).toPyObject()
        return True

    def cleanupPage(self):
        self.applicationList.clear()

class versionPage(ui.ui_import_versionPage.Ui_versionPage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(versionPage,  self).__init__(parent)

        self.tmpList = list()

        self.parent = parent
        self.main = main

        self.setupUi(self)

        self.connect(self.versionList, SIGNAL("itemSelectionChanged()"), SIGNAL("completeChanged()"))
        self.connect(self.versionList, SIGNAL("itemClicked(QListWidgetItem *)"), self.versionChanged)

    def versionChanged(self,  item=None):
        if not item:
            if self.versionList.selectedItems():
                item = self.versionList.selectedItems()[0]
            else:
                self.notesLabel.setText(QString())
                self.notesLabel.resize(QSize(0,  0))
                return

        version = item.data(Roles.VersionRole).toPyObject()
        if version.help().isEmpty():
                self.notesLabel.setText(QString())
                self.notesLabel.resize(QSize(0,  0))
        else:
            self.notesLabel.setText("<br />" + version.help())

    def initializePage(self):
        application = self.parent.application

        for version in application.versions():
            self.tmpList.append(version)
            
            item = QListWidgetItem(version.version(),  self.versionList)
            item.setData(Roles.VersionRole,  QVariant(version))

        self.versionChanged()

    def isComplete(self):
        return bool(self.versionList.selectedItems())

    def validatePage(self):
        self.parent.version = self.versionList.selectedItems()[0].data(Roles.VersionRole).toPyObject()
        return True

    def cleanupPage(self):
        self.versionList.clear()

class settingsPage(ui.ui_import_settingsPage.Ui_settingsPage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(settingsPage,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.setupUi(self)

        self.types = lib.import_messages.Types()
        self.type = None

        self.connect(self.openFileButton,  SIGNAL("clicked()"),  self.openFileDialog)
        self.connect(self.sqlite_fileLine, SIGNAL("textChanged(const QString &)"), SIGNAL("completeChanged()"))
        self.connect(self.mysql_hostLine, SIGNAL("textChanged(const QString &)"), SIGNAL("completeChanged()"))
        self.connect(self.mysql_userLine, SIGNAL("textChanged(const QString &)"), SIGNAL("completeChanged()"))
        self.connect(self.mysql_passLine, SIGNAL("textChanged(const QString &)"), SIGNAL("completeChanged()"))
        self.connect(self.mysql_databaseLine, SIGNAL("textChanged(const QString &)"), SIGNAL("completeChanged()"))
        self.connect(self.databaseBox,  SIGNAL("currentIndexChanged(int)"),  SIGNAL("completeChanged()"))
        self.connect(self.databaseBox,  SIGNAL("currentIndexChanged(int)"),  self.databaseChanged)

    def initializePage(self):
        self.version = self.parent.version

        self.databaseBox.clear()
        for db in self.version.databases():
            self.databaseBox.addItem(self.types.name(db),  QVariant(db))

        self.databaseChanged(0)

    def openFileDialog(self):
        url = QUrl(QFileDialog.getOpenFileName(self,  self.tr("Open Database file"),  QString(),  self.tr("SQLite database (*.db)")))
        if url.isValid():
            self.sqlite_fileLine.setText(url.toLocalFile())

    def databaseChanged(self,  index):
        self.type = self.databaseBox.itemData(index).toInt()[0]
        if self.type == self.types.SQLite:
            self.databaseStack.setCurrentWidget(self.sqlitePage)
        elif self.type == self.types.MySQL:
            self.databaseStack.setCurrentWidget(self.mysqlPage)

    def isComplete(self):
        if self.type == self.types.SQLite:
            return not self.sqlite_fileLine.text().isEmpty()
        elif self.type == self.types.MySQL:
            return not (self.mysql_hostLine.text().isEmpty() or self.mysql_userLine.text().isEmpty() or self.mysql_passLine.text().isEmpty()
            or self.mysql_databaseLine.text().isEmpty())

        return True

    def validatePage(self):
        data = dict()
        if self.type == self.types.SQLite:
            data["filename"] = self.sqlite_fileLine.text()
        elif self.type == self.types.MySQL:
            data["host"] = self.mysql_hostLine.text()
            data["port"] = self.mysql_portBox.value()
            data["user"] = self.mysql_userLine.text()
            data["pass"] = self.mysql_passLine.text()
            data["database"] = self.mysql_databaseLine.text()

        if self.version.use(self.type,  data):
            return True
        else:
            message = QMessageBox.critical(self,
            self.tr("Can't connect to database!"),
            self.tr("Error when trying to connect to database: %1").arg(self.version.error()),
            QMessageBox.StandardButtons(\
                    QMessageBox.Ok),
            QMessageBox.Ok)
            return False

class messagesPage(ui.ui_import_messagesPage.Ui_messagesPage,  QWizardPage):
    def __init__(self,  parent,  main):
        super(messagesPage,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.setupUi(self)

    def initializePage(self):
        self.version = self.parent.version
        self.complete_ = False

        self.messageNumberBar.setValue(0)
        self.messageNumberLabel.setText(self.tr("%1 of %2").arg(0).arg(0))

        self.count = self.version.count()
        self.connect(self.version,  SIGNAL("messageImported"),  self.imported)
        self.connect(self.version, SIGNAL("importComplete"), self.complete)

        self.emit(SIGNAL("completeChanged()"))

        self.version.import_()

    def imported(self,  anzahl):
        self.messageNumberLabel.setText(self.tr("%1 of %2").arg(anzahl).arg(self.count))
        self.messageNumberBar.setValue(int(anzahl / float(self.count) * 100))

    def complete(self):
        self.complete_ = True

        self.messageNumberLabel.setText(self.tr("%1 of %2").arg(self.count).arg(self.count))
        self.messageNumberBar.setValue(100)
        self.emit(SIGNAL("completeChanged()"))

    def isComplete(self):
        return self.complete_

    def validatePage(self):
        self.version.stop()
        return True

    def closeEvent(self):
        if not self.complete_:
            self.version.stop()

    def cleanupPage(self):
        if not self.complete_:
            self.version.stop()
