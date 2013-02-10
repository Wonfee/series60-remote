#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import sys
import os
sys.path.append(os.path.dirname( os.path.realpath( __file__ ) ))

import getopt
import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.chatmanager
import lib.device
import lib.database
import lib.settings
import lib.helper
#import lib.dbusobject
import lib.log
import window.systemtrayicon
import window.popups
import window.mainwindow
import window.settings
import window.wizard
import window.log
import ui.resource_rc

#DBUS = True
#try:
#    import dbus
#    import dbus.service
#    import dbus.mainloop.qt
#except:
#    DBUS = False

appVersion = (0, 4, 80)
settingsVersion = (0, 3)
databaseVersion = (0, 5)
versionIsStable = bool(0)

def get_version():
    appVersionStr = str()
    for i in appVersion[:-1]:
        appVersionStr += str(i) + "."
    appVersionStr += str(appVersion[-1:][0])
    return appVersionStr

class Main(QObject):
    def __init__(self,  parent=None):
        """Create a wizard or the mainwindow"""
        super(Main,  self).__init__(parent)

        # Application version
        self.appVersion = appVersion
        self.settingsVersion = settingsVersion
        self.databaseVersion = databaseVersion
        self.versionIsStable = versionIsStable

        # Application data files
        self.applicationSis_Py14 = "series60-remote-py14.sis"
        self.pythonSis_Py14 = "PythonForS60_1_4_5_3rdEd.sis"
        self.applicationSis_Py20 = "series60-remote-py20.sis"
        self.pythonSis_Py20 = "Python_2.0.0.sis"
        self.file = __file__

        # Application version strings

#        self.appVersionStr = str()
#        for i in self.appVersion[:-1]:
#            self.appVersionStr += str(i) + "."
#        self.appVersionStr += str(self.appVersion[-1:][0])
        self.appVersionStr = "0.5.0 - Alpha 1"

        self.settingsVersionStr = str()
        for i in self.settingsVersion[:-1]:
            self.settingsVersionStr += str(i) + "."
        self.settingsVersionStr += str(self.settingsVersion[-1:][0])

        self.databaseVersionStr = str()
        for i in self.databaseVersion[:-1]:
            self.databaseVersionStr += str(i) + "."
        self.databaseVersionStr += str(self.databaseVersion[-1:][0])

        # The QApplication initialisation will override the Qt arguments,
        # so check for some things we need later...
        customStyle = "-style" in sys.argv

        # Initialisize Qt application
        self.app = QApplication(sys.argv)

        # PyQt4 and Qt4 version 4.6 required
        self.checkVersion()

        # We need this class everywhere ;)
        self.app.setProperty("main",  QVariant(self))

        # Application name
        self.app.setOrganizationName("Series 60 - Remote")
        self.app.setApplicationName("Series 60 - Remote " + self.settingsVersionStr)
        self.app.setQuitOnLastWindowClosed(False)

        # Initialize settings
        self.settings = lib.settings.Settings(self,  self)

        # Widget style
        style = self.settings.setting("lookAndFeel/widgetStyle")
        if style and not customStyle:
            self.app.setStyle(style)

        # Languages
        localename = self.settings.setting("lookAndFeel/language")
        if localename:
            self.locale = QLocale(localename)
            QLocale.setDefault(self.locale) # for QDate.toString(x, Qt.DefaultLocaleLongDate)
        else:
            self.locale = QLocale.system()

        locale = self.locale.name()

        tmpTranslator = QTranslator()
        qtTranslator = QTranslator()
        appTranslator = QTranslator()

        if tmpTranslator.load("qt_" + locale, ":/lang"):
            qtTranslator.load("qt_" + locale, ":/lang")
            self.app.installTranslator(qtTranslator)

        if tmpTranslator.load("app_" + locale,  ":/lang"):
            appTranslator.load("app_" + locale,  ":/lang")
            self.app.installTranslator(appTranslator)

        # Variables
        self.popups = list()
        self.unreadMessages = list()
        self.verbose = False
        self.debug = False
        self.sqlDebug = False
        self.long = False
        self.minimized = False

        # Check command-line arguments
        self.arguments()

        # Initialize the logger
        self.logWindow = window.log.Log(None,  self)
        self.logger()

        # Initialize S60 modules
        self.database = lib.database.Database(self,  self)
        self.connectionBase = lib.device.Device(self,  self)
        self.helper = lib.helper.Helper(self,  self)

        self.connectionBase.loadPlugin()
        self.connection = self.connectionBase.connection()

        # Initialize D-Bus
#        if DBUS:
#            self.log.info(QString("D-Bus support enabled"))
#            dbus.mainloop.qt.DBusQtMainLoop(set_as_default=True)
#
#            session_bus = dbus.SessionBus()
#            name = dbus.service.BusName("net.sourceforge.series60remote", session_bus)
#            object = lib.dbusobject.DBusObject(session_bus,  self)
#        else:
#            self.log.info(QString("D-Bus support disabled"))

        # Signals
        self.connect(self.settings,  SIGNAL("reloadSettings"),  self.reloadPlugin)
        self.connect(self.connection,  SIGNAL("messageUnread"),  self.messageUnread)
        self.connect(self.connection,  SIGNAL("messageNew"),  self.messageNew)

        # Show a wizard screen on first startup
        if self.settings.setting("general/firstStart"):
            self.log.info(QString("Show wizard-dialog"))

            myWizard = window.wizard.Wizard(None,  self)
            self.connect(myWizard,  SIGNAL("finished(int)"),  self.showMainWindow)
        else:
            self.showMainWindow()

        self.app.exec_()

    def __str__(self):
        return "\"Main\""

    def showMainWindow(self, id=None):
        # Refresh settings after the wizard finished
        if (id == 1):
            self.settings.loadSettings()

        # Continue only if the wizard exited successfully
        if (id == 1 or id == None):
            self.log.info(QString("Show Mainwindow"))

            # Connect to database
            self.databaseConnect()

            # Show mainwindow, a trayicon and popups
            self.mainWindow = window.mainwindow.MainWindow(None,  self)
            self.chatManager = lib.chatmanager.ChatManager(self.mainWindow,  self)
            self.trayicon = window.systemtrayicon.TrayIcon(self.mainWindow,  self)
            self.popup = window.popups.Popups(None,  self)

    def reloadPlugin(self):
        plugin =  str(self.settings.setting("general/connectionPlugin"))
        if not plugin in self.connectionBase.plugins():
            plugin = "series60"

        if self.connectionBase.plugin() != plugin:
            if self.connection.connected():
                self.connection.closeConnection()
            del self.connection
            self.connectionBase.loadPlugin()
            self.connection = self.connectionBase.connection()

    def checkVersion(self):
        if QT_VERSION < 0x040600:
            print self.tr("Qt4 version 4.6 required!")
            print self.tr("Found version: %1").arg(QT_VERSION_STR)
            QMessageBox.critical(None, self.tr("Qt4 version 4.6 required!"), self.tr("Qt4 version 4.6 required!") + '\n' + self.tr("Found version: %1").arg(QT_VERSION_STR))
            sys.exit(2)
        if PYQT_VERSION < 0x040600:
            print self.tr("PyQt4 version 4.6 required!")
            print self.tr("Found version: %1").arg(PYQT_VERSION_STR)
            QMessageBox.critical(None, self.tr("PyQt4 version 4.6 required!"), self.tr("PyQt4 version 4.6 required!") + '\n' + self.tr("Found version: %1").arg(PYQT_VERSION_STR))
            sys.exit(2)

    def usage(self):
        print unicode(self.tr("""
usage: series60-remote [Qt-options] [options]

series60-remote, manage your Series60 mobile phone

Optionen:
  -v, --verbose             Print verbose information - normally routine progress messages will be displayed
  -d, --debug               Print lots of ugly debugging information
  -s, --sqldebug            Print all executed SQL queries
  -l, --long                Use a long format
  -m, --minimized           Start with minimized mainwindow
  -h, --help                Show help about options
  -a, --author              Show author information
  -V, --version             Show version information
  -L, --license             Show license information

Qt-Optionen:
  -display <displayname>    Use the X-server display 'displayname'
  -session <sessionId>      Restore the application for the given 'sessionId'
  -cmap                     Causes the application to install a private color
                            map on an 8-bit display
  -ncols <count>            Limits the number of colors allocated in the color
                            cube on an 8-bit display, if the application is
                            using the QApplication::ManyColor color
                            specification
  -nograb                   tells Qt to never grab the mouse or the keyboard
  -dograb                   running under a debugger can cause an implicit
                            -nograb, use -dograb to override
  -sync                     switches to synchronous mode for debugging
  -fn, -font <fontname>     defines the application font
  -bg, -background <color>  sets the default background color and an
                            application palette (light and dark shades are
                            calculated)
  -fg, -foreground <color>  sets the default foreground color
  -btn, -button <color>     sets the default button color
  -name <name>              sets the application name
  -title <title>            sets the application title (caption)
  -visual TrueColor         forces the application to use a TrueColor visual on
                            an 8-bit display
  -inputstyle <inputstyle>  sets XIM (X Input Method) input style. Possible
                            values are onthespot, overthespot, offthespot and
                            root
  -im <XIM server>          set XIM server
  -noxim                    disable XIM
  -reverse                  mirrors the whole layout of widgets
  -stylesheet <file.qss>    applies the Qt stylesheet to the application widgets
"""))

    def arguments(self):
        # Remove all Qt arguments
        qtArguments = ["display=",  "session=",  "cmap", "ncols=",  "nograb",  "dograb",
                       "sync",  "fn=",  "font=",  "bg=",  "background",  "fg=",  "foreground=",
                       "btn=",  "button=",  "name=",  "title=",  "visual=",  "inputstyle=",  "im=",
                       "noxim",  "reverse",  "stylesheet=",  "style="]

        myArgs = []
        ignore = False
        for arg in sys.argv:
            argMod = arg.replace("-",  "",  1)

            if argMod in qtArguments:
                pass
            elif argMod + "=" in qtArguments:
                ignore = True
            else:
                if ignore:
                    # shouldn't be a new argument
                    if arg.startswith("-"):
                        myArgs.append(arg)
                    ignore = False
                else:
                    myArgs.append(arg)

        # Filter own arguments
        try:
            self.opts,  self.args = getopt.getopt(myArgs[1:], "vdslhaVLm", ["verbose", "debug", "sqldebug",  "long",  "help",  "author",  "version",  "license", "minimized"])
        except getopt.GetoptError, err:
            # Show help on unknown arguments
            print str(err)
            self.usage()
            sys.exit(2)

        for opt,  value in self.opts:
            # Help
            if "-h" in opt or "--help" in opt:
                self.usage()
                sys.exit(2)

            # Author
            elif "-a" in opt or "--author" in opt:
                print unicode(self.tr("""
Series60-Remote was written by
""")) + """
        Lukas Hetzenecker <LuHe@gmx.at>
"""
                sys.exit(2)

            # License
            elif "-L" in opt or "--license" in opt:
                print """
(c) 2008-2009, Lukas Hetzenecker
""" + unicode(self.tr( """"
This program is distributed under the terms of the GPL v2.
"""))
                sys.exit(2)

            # Verbose
            elif "-v" in opt or "--verbose" in opt:
                self.verbose = True

            # Debug
            elif "-d" in opt or "--debug" in opt:
                self.debug = True

            # SQL-Debug
            elif "-s" in opt or "--sqldebug" in opt:
                self.sqlDebug = True

            # Long format
            elif "-l" in opt or "--long" in opt:
                self.long = True

            # Start with minimized mainwindow
            elif "-m" in opt or "--minimized" in opt:
                self.minimized = True

    def logger(self):
        # Output forwarding
        sys.stdout = lib.log.QtOutput(self.logWindow.outputEdit,  sys.__stdout__,  self.logWindow.outputEdit.textColor())
        sys.stderr = lib.log.QtOutput(self.logWindow.outputEdit,  sys.__stderr__,  QColor(Qt.red))

        # Create logger
        logger = logging.getLogger("series60-remote")
        logger.setLevel(9)

        # Create standart output handler
        self.stdout = logging.StreamHandler(sys.__stderr__)
        if self.sqlDebug:
            self.stdout.setLevel(9)
        elif self.debug:
            self.stdout.setLevel(logging.DEBUG)
        elif self.verbose:
            self.stdout.setLevel(logging.INFO)
        else:
            self.stdout.setLevel(logging.WARNING)

        if self.long:
            format = logging.Formatter("[%(asctime)s] - %(levelname)-8s - %(message)s (%(module)s: %(funcName)s - line %(lineno)s, process %(process)s)", "%d.%m.%Y %H:%M:%S")
            self.stdout.setFormatter(format)

        # Create log window handler
        self.dialogHandler = lib.log.QtStreamHandler(self.logWindow.logEdit,  self)
        self.dialogHandler.setLevel(self.settings.setting("log/level"))

        long = self.settings.setting("log/level")
        if long:
            format = logging.Formatter("[%(asctime)s] - %(levelname)-8s - %(message)s (%(module)s: %(funcName)s - line %(lineno)s, process %(process)s)", "%d.%m.%Y %H:%M:%S")
            self.dialogHandler.setFormatter(format)

        # Add handlers to logger
        logger.addHandler(self.stdout)
        logger.addHandler(self.dialogHandler)

        self.log = logger

    def databaseConnect(self):
        type = self.settings.setting("database/type")
        data = dict()

        if type == "mysql":
            data["host"] = self.settings.setting("database/mysql/host")
            data["port"] = self.settings.setting("database/mysql/port")
            data["user"] = self.settings.setting("database/mysql/user")
            data["pass"] = self.settings.setting("database/mysql/pass")
            data["database"] = self.settings.setting("database/mysql/database")
        elif type=="sqlite":
            data["filename"] = self.settings.setting("database/sqlite/filename")

        if not self.database.openDatabase(type,  data):
            QMessageBox.critical(None, self.tr("Connection failed"), self.tr("Database error: %1\n").arg(self.database.error()))
            self.log.critical(QString("Database error: %1").arg(self.database.error()))
            self.settingsDialog = window.settings.Settings(None,  self)
            self.settingsDialog.show()
            self.settingsDialog.exec_()

    def messageNew(self,  message):
        self.unreadMessages.append(message)
        self.emit(SIGNAL("messageNew"),  message)

    def messageUnread(self,  message):
        self.unreadMessages.append(message)
        self.emit(SIGNAL("messageUnread"),  message)

    def setupButtonBox(self,  buttonBox):
        for standardButton in buttonBox.buttons():
            if buttonBox.buttonRole(standardButton) == QDialogButtonBox.AcceptRole:
                standardButton.setIcon(QIcon(":/dialog-ok"))
            elif buttonBox.buttonRole(standardButton) == QDialogButtonBox.RejectRole:
                standardButton.setIcon(QIcon(":/dialog-close"))
            elif buttonBox.buttonRole(standardButton) == QDialogButtonBox.YesRole:
                standardButton.setIcon(QIcon(":/dialog-ok"))
            elif buttonBox.buttonRole(standardButton) == QDialogButtonBox.NoRole:
                standardButton.setIcon(QIcon(":/dialog-close"))
            elif buttonBox.buttonRole(standardButton) == QDialogButtonBox.ApplyRole:
                standardButton.setIcon(QIcon(":/dialog-apply"))
            elif buttonBox.buttonRole(standardButton) == QDialogButtonBox.ResetRole:
                standardButton.setIcon(QIcon(":/edit-undo"))

if __name__ == "__main__":
      main = Main()
