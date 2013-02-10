# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import os
import sys
import tarfile
import zipfile
import shutil
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.obex_wrapper
from lib.ordinal_number_formatter import OrdinalNumberFormatter
from lib.classes import *

if sys.platform == "win32":
    try:
        import winshell
        USE_WINSHELL = True
    except ImportError:
        USE_WINSHELL = False

USE_PYBLUEZ = False
USE_LIGHTBLUE = False

try:
   # PyBluez module for Linux and Windows
   import bluetooth
   from bluetooth import BluetoothError
   USE_PYBLUEZ = True
except ImportError:
   # Lightblue for Mac OS X
   import lightblue
   from lib.obex_wrapper import BluetoothError
   USE_LIGHTBLUE = True

class Helper(QObject):
    def __init__(self,  parent,  main):
        """Often used functions"""
        super(Helper,  self).__init__(parent)

        self.parent = parent
        self.main = main

        if main != None:
            self.log = main.log

    def addContactsToMenu(self,  contacts,  menu,  start=0):
        i = 0
        for contact in contacts:
            if i + 1 + start < 10:
                action = QAction("&%d: %s" % (i + 1 + start,  contact.name()),  menu)
            else:
                action = QAction("%d: %s" % (i + 1 + start,  contact.name()),  menu)
            action.setData(QVariant(contact))
            action.setProperty("type",  QVariant("contact"))
            menu.addAction(action)
            i += 1
        return i+1

    def pretty_filesize(self,  bytes):
        """Function to convert bytes to KB/MB/GB/TB"""
        bytes = float(bytes)
        if bytes >= 1099511627776:
            terabytes = bytes / 1099511627776
            size = '%.1f TB' % terabytes
        elif bytes >= 1073741824:
            gigabytes = bytes / 1073741824
            size = '%.1f GB' % gigabytes
        elif bytes >= 1048576:
            megabytes = bytes / 1048576
            size = '%.1f MB' % megabytes
        elif bytes >= 1024:
            kilobytes = bytes / 1024
            size = '%.1f KB' % kilobytes
        else:
            size = '%.0f B' % bytes
        return size

    def countMessages(self,  chars):
        """Return number of messages and remaining chars of an text message
        A tuple of the format (number_of_messages, remeining_chars)
        is returned"""
        # The first part of a text message can be up tp 160 chars
        if chars <= 160:
            return 160-chars,  1

        # The second part up to 145 chars
        elif chars <= 160+145:
            return (160+146)-chars,  2

        # All the others can have 152 chars
        else:
            rest = chars-(160+146)
            sms = rest/152+1
            ch = (sms)*152-rest
            return ch,  sms+2

    def chatThemes(self):
        folders = self.findFolders("",  "data",  ["chat-themes"])
        for folder in folders:
            folder = QDir(folder)
            for theme in folder.entryList(QDir.Dirs | QDir.NoDotAndDotDot):
                themeFolder = QDir(folder.absolutePath() + os.sep + theme)
                if themeFolder.exists("Contents" + os.sep + "Resources" + os.sep + "Status.html"):
                    # This file must exist, otherwise it isn't a valid theme
                    yield unicode(theme),  unicode(themeFolder.absolutePath())

    def chatThemeFolder(self,  theme):
        return self.findFolder("",  "data",  ["chat-themes",  theme])

    def __directorys(self,  root):
        directorys = list()

        # Path of executable file (could be the python executable or the application if it was compiled)
        directorys.append(QDir(self.main.app.applicationDirPath()))

        # Path of current script file
        directorys.append(QDir(sys.path[0]))

        # Path of helper script
        directorys.append(QDir(sys.path[0]+ os.sep + 'pc'))

        if root == "mobile":
            dir = QDir.current()
            if dir.cdUp():
                directorys.append(dir)
        else:
            directorys.append(QDir.current())
            # User-specific files (e.g. themes)
            if self.main != None:
                directorys.append(QFileInfo(QSettings().fileName()).absoluteDir())

        if os.name == 'posix':
            # Linux and Mac OS X
            directorys.append(QDir("/usr/share/series60-remote"))
            directorys.append(QDir("/usr/local/share/series60-remote"))
        #if sys.platform == 'darwin':
            # Mac OS X
            # for bundled application
            # QDir() is current working directory (Series60-Remote.app/Contents/Resources)
            #directorys.append(QDir().absolutePath())

        return directorys

    def __find(self,  directory,  regexp):
        files = directory.entryList(QStringList(regexp))
        if not files.isEmpty():
            last = files.takeLast()
            return unicode(directory.absoluteFilePath(last))
        return None

    def findFolder(self,  regexp,  root="data",  folders=list()):
        # root can be data or mobile
        directorys = self.__directorys(root)

        for directory in directorys:
            directory = QDir(directory.absolutePath() + os.sep + root + os.sep + os.sep.join(folders))
            if not regexp and directory.exists():
                # Return the base directory when we're not looking for a subfolder
                return unicode(directory.absolutePath())
            path = self.__find(directory,  regexp)
            if path != None:
                return path

    def findFolders(self,  regexp,  root="data",  folders=list()):
        # root can be data or mobile
        retFolders = list()

        directorys = self.__directorys(root)

        for directory in directorys:
            directory = QDir(directory.absolutePath() + os.sep + root + os.sep + os.sep.join(folders))
            if not regexp and directory.exists():
                # Return the base directory when we're not looking for a subfolder
                retFolders.append(unicode(directory.absolutePath()))
            path = self.__find(directory,  regexp)
            if path != None:
                retFolders.append(path)

        return retFolders

    def openFolder(self):
        folder = self.findFolder(self.main.applicationSis_Py14,  "mobile") or self.findFolder(self.main.pythonSis_Py14,  "mobile") \
                    or self.findFolder(self.main.applicationSis_Py20,  "mobile") or self.findFolder(self.main.pythonSis_Py20,  "mobile")
        if folder == None:
            message = QMessageBox.critical(self,
            self.tr("Can't find file!"),
            self.tr("""The file %1 couldn't be found!\n
If you're using the SVN version of the application you have to create the file yourself\n
If you downloaded a pre-built package please report the error to series60-remote-devel@lists.sourceforge.net !""").arg(file),
            QMessageBox.StandardButtons(\
                QMessageBox.Ok),
            QMessageBox.Ok)
        else:
            dir = QFileInfo(folder).absoluteDir().absolutePath()
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir))

    def sendFile(self,  parent,  device,  file):
        if self.main == None:
            return

        try:
            assert device.bluetoothAddress()
        except:
            message = QMessageBox.critical(parent,
            self.tr("File transfer failed!"),
            self.tr("""File transer failed!\n
No device was specified!\n
You have to send the file %1 in the folder mobile manuelly to your mobile phone!""").arg(file),
            QMessageBox.StandardButtons(\
                    QMessageBox.Ok),
            QMessageBox.Ok)

            return

        found = False

        path = self.findFolder(file,  "mobile")
        if path == None:
            message = QMessageBox.critical(parent,
            self.tr("Can't find file!"),
            self.tr("""The file %1 couldn't be found!\n
If you're using the SVN version of the application you have to create the file yourself\n
If you downloaded a pre-built package please report the error to series60-remote-devel@lists.sourceforge.net !""").arg(file),
            QMessageBox.StandardButtons(\
                QMessageBox.Ok),
            QMessageBox.Ok)
            return

        port = 11
        try:
            if USE_PYBLUEZ:
                services = bluetooth.find_service(address=address, name="OBEX File Transfer")

                # Windows (Widcomm) seems to ignore the name argument...
                for service in services:
                    if service["name"] == "OBEX File Transfer":
                        port = service["port"]
            elif USE_LIGHTBLUE:
                services = lightblue.findservices(addr=address, name="OBEX File Transfer")
                if service:
                    port = services[0][1]
        except:
            pass

        self.log.info(QString("Sending file %1 to host %2 on port %3").arg(path).arg(device.bluetoothAddress()).arg(port))

        errormsg = None
        client = lib.obex_wrapper.ObexClient(device.bluetoothAddress(),  port)
        try:
            ret = client.connect()
        except BluetoothError,  msg:
            try:
                error = eval(str(msg)) # Doesn't work on Windows, why?
                errormsg = error[1]
                errormsg = unicode(errormsg,  "utf8")
            except:
                errormsg = "None"
        except IOError,  msg:
            errormsg = msg.message

        if errormsg:
            message = QMessageBox.critical(parent,
            self.tr("File transfer failed!"),
            self.tr("""File transer failed!\n
I could not connect to the file transfer service of your mobile phone!\n
The error message was: %1\n
You have to send the file %2 in the folder mobile manuelly to your mobile phone!\n
The absolute filepath is: %3""").arg(errormsg,  file,  path),
            QMessageBox.StandardButtons(\
                    QMessageBox.Ok),
            QMessageBox.Ok)
            return

        if not isinstance(ret, lib.obex_wrapper.ConnectSuccess):
            message = QMessageBox.critical(parent,
            self.tr("File transfer failed!"),
            self.tr("""File transer failed!\n
I could not connect to the file transfer service of your mobile phone!\n
You have to send the file %1 in the folder mobile manuelly to your mobile phone!\n
The absolute filepath is: %2""").arg(file,  path),
            QMessageBox.StandardButtons(\
                    QMessageBox.Ok),
            QMessageBox.Ok)
            return

        self.log.info(QString("Connection returned %1").arg(repr(ret)))

        ret = client.put_file(path)
        self.log.info(QString("Sending file returned %1").arg(repr(ret)))

        client.disconnect()

        message = QMessageBox.information(parent,
        self.trUtf8("File succesfully transfered to mobile phone!"),
        self.trUtf8("""The file was transfered successfully to your mobile phone!\n
Please open your messages and continue with the installation!"""),
        QMessageBox.StandardButtons(\
                QMessageBox.Ok),
        QMessageBox.Ok)

    def calendarEntryRecurrenceToString(self,  type,  days,  exceptions,  start,  end,  interval):
        days = CalendarEntry.recurrenceParsedDays(type,  days)

        recurrence = self.tr("No recurrence")
        if type == "daily":
            if interval == 1:
                recurrence = self.tr("Recurs daily")
            else:
                recurrence = self.tr("Recurs every %n day(s)",  "",  interval)
        elif type == "weekly":
            weekdays = unicode(self.tr(", ",  "join string for weekdays")).join(
                                            [unicode(self.main.locale.standaloneDayName(int(day)+1,  QLocale.ShortFormat)) for day in days]
                                )
            if interval == 1:
                recurrence = self.tr("Recurs weekly on %1").arg(weekdays)
            else:
                recurrence = self.tr("Recurs every %n week(s) on %1",  "",  interval).arg(weekdays)
        elif type == "monthly_by_dates":
            datesinmonth = unicode(self.tr(", ",  "join string for dates in month")).join(
                                                [unicode(OrdinalNumberFormatter.toString(int(day)+1)) for day in days]
                                    )
            if interval == 1:
                recurrence = self.tr("Recurs monthly on the %1 day").arg(datesinmonth)
            else:
                recurrence = self.tr("Recurs every %n month(s) on the %1 day",  "",  interval).arg(datesinmonth)
        elif type == "monthly_by_days":
            locstring = list()
            for day in days:
                locstring.append(unicode(OrdinalNumberFormatter.toString(int(day['week'])+1) + ' ' + self.main.locale.standaloneDayName(int(day['day'])+1)) )
            daysinmonth = unicode(self.tr(" and ",  "join string for days in month")).join(locstring)

            if interval == 1:
                recurrence = self.tr("Recurs every month on the %1").arg(daysinmonth)
            else:
                recurrence = self.tr("Recurs every %n month(s) on the %1",  "",  interval).arg(daysinmonth)
        elif type == "yearly_by_date":
            arg = self.tr("%1 %2",  "month day{ordinal number}").arg(self.main.locale.monthName(start.date().month()), OrdinalNumberFormatter.toString(start.date().day()))
            if interval == 1:
                recurrence = self.tr("Recurs yearly on %1").arg(arg)
            else:
                recurrence = self.tr("Recurs every %n years(s) on %1",  "",  interval).arg(arg)
        elif type == "yearly_by_day":
            arg = self.tr("the %1 %2 of %3",  "the day{ordinal number} {weekday} of month").arg(OrdinalNumberFormatter.toString(days['week']+1),
                                                                                                                              self.main.locale.dayName(days['day']+1),
                                                                                                                              self.main.locale.monthName(days['month']+1))
            if interval == 1:
                recurrence = self.tr("Recurs every year on %1").arg(arg)
            else:
                recurrence = self.tr("Recurs every %n years(s) on %1",  "",  interval).arg(arg)

        if recurrence and end and end.isValid():
            recurrence = self.tr("%1 until %2",  "Recurs ... until").arg(recurrence,  self.main.locale.toString(end.date(),  QLocale.ShortFormat))

        return recurrence

    def installTheme(self,  archive,  destination):
        self.log.info(QString("Installing theme %1 to %2").arg(archive,  destination))

        if archive.endswith(".zip") and zipfile.is_zipfile(archive):
            fileobj = zipfile.ZipFile(archive)
            names = fileobj.namelist()
        elif (archive.endswith(".tar") or archive.endswith(".tar.gz") or archive.endswith(".tar.bz2")) and tarfile.is_tarfile(archive):
            fileobj = tarfile.open(archive)
            names = fileobj.getnames()
        else:
            self.log.error(QString("Theme file does not have an supported filetype!"))
            return False,  None,  None

        themeName = names[0]

        if not (themeName + "/Contents/Resources/Outgoing/Content.html" in names
                and themeName + "/Contents/Resources/Incoming/Content.html"):
                    self.log.error(QString("Invalid file content!"))
                    return False,  None,  None

        # Create destionation directory if it doesn't exist yet
        if not QDir(destination).mkpath("data/chat-themes"):
            self.log.error(QString("Could not create destination directory!"))
            return False,  None,  None

        extractdir = unicode(QDir(destination).absoluteFilePath("data/chat-themes"))
        self.log.debug(QString("Theme name is: %1").arg(themeName))
        self.log.debug(QString("Extract directory is: %1").arg(extractdir))
        fileobj.extractall(extractdir)

        return True,  themeName,  extractdir + os.sep + themeName

    def removeTheme(self,  directory):
        if os.path.isdir(directory):
            shutil.rmtree(directory)

    def getExecutable(self):
        if sys.platform == "linux2":
            if sys.argv[0].endswith("series60-remote"):
                return sys.argv[0]
            if os.path.realpath(self.main.file).endswith("series60_remote.py"):
                if QFileInfo(os.path.realpath(self.main.file)).isExecutable():
                    return os.path.realpath(self.main.file)
                else:
                    return "python " + os.path.realpath(self.main.file)
            if sys.argv[0].endswith("series60_remote.py"):
                file = unicode(QDir.cleanPath(QDir(os.getcwd()).absoluteFilePath(sys.argv[0])))
                if QFileInfo(os.path.realpath(self.main.file)).exists():
                    if QFileInfo(os.path.realpath(self.main.file)).isExecutable():
                        return file
                    else:
                        return "python " + file
        elif sys.platform == "win32":
            if sys.argv[0].endswith("series60-remote.exe"):
                return sys.argv[0]
        return None


    def getAutostart(self):
        if sys.platform == "linux2":
            return QFileInfo(QDir.home(), ".config/autostart/series60-remote.desktop").exists()
        elif sys.platform == "win32":
            if USE_WINSHELL:
                autostart = winshell.startup()
                return QFileInfo(QDir(autostart), "series60-remote.exe.lnk").exists()
        return False

    def autostartSupported(self):
        if sys.platform == "linux2" or (sys.platform == "win32" and USE_WINSHELL):
            return bool(self.getExecutable())
        return False

    def createAutostart(self, minimized):
        application = self.getExecutable()
        if not application or self.getAutostart() or not self.getExecutable():
            return

        if minimized:
            args = "-m"
        else:
            args=""

        if sys.platform == "linux2":
            if not QDir.home().mkpath(".config/autostart"):
                return
            if self.getExecutable().startswith("python "):
               tryexec = "python"
            else:
               tryexec = self.getExecutable()
            desktopfile = open(unicode(QDir.home().filePath(".config/autostart/series60-remote.desktop")), 'w')
            print >> desktopfile, "[Desktop Entry]"
            print >> desktopfile, "Encoding=UTF-8"
            print >> desktopfile, "Name=Series60-Remote S60 Software Suite"
            print >> desktopfile, "TryExec=%s" % tryexec
            print >> desktopfile, "Exec=%s %s" % (self.getExecutable(), args)
            print >> desktopfile, "StartupNotify=false"
            print >> desktopfile, "Type=Application"
            desktopfile.close()
        elif sys.platform == "win32":
            if USE_WINSHELL:
                exe = self.getExecutable()
                dir = unicode(QFileInfo(exe).dir().absolutePath())
                winshell.CreateShortcut(
                    Path=os.path.join(winshell.startup(), "series60-remote.exe.lnk"),
                    Target=exe,
                    Arguments=args,
                    Icon=(exe, 0),
                    Description="Series60-Remote S60 Software Suite",
                    StartIn=dir
                )

    def removeAutostart(self):
        if sys.platform == "linux2":
            return QFile(QDir.home().filePath(".config/autostart/series60-remote.desktop")).remove()
        elif sys.platform == "win32":
            if USE_WINSHELL:
                return QFile(QDir(winshell.startup()).filePath("series60-remote.exe.lnk")).remove()

    def getModel(self,  firmware):
        """Translates the firmware version to the model"""
        #
        # Firmware.py for S60 Nokia Phones
        #
        # source code by Cyke64 (Forum Nokia Champion http://www.forum.nokia.com/main/forum_nokia_champion/who_is_a_forum_nokia_champion.html)
        # original idea from Korakotc
        # Apache license 2.0
        # version 07 http://homepage.mac.com/alvinmok/nokia/firmware.html
        #            http://www.nokiaport.de/index.php?mid=3&pid=processor
        # modified by Lukas Hetzenecker

        mapping_firmware={
        'RM-51': '3230',
        'RM-52': '3230b',
        'RM-38': '3250',
        'RM-40': '3250b',
        'NHM-10': '3600',
        'NAM-1': '3610',
        'NHM-10X': '3620',
        'NHL-8': '3650',
        'NHL-8X': '3660',
        'RM-86': '5500d',
        'RM-87': '5500',
        'RM-230': '5700',
        'RM-302': '5700b',
        'NSE-3':'6110',
        'RM-122':'6110n-1',
        'RM-186':'6110n-5',
        'NSC-3': '6120',
        'RM-243': '6120c-1',
        'RM-310': '6120c-5',
        'RM-308': '6121c',
        'RM-25': '6260',
        'RM-29': '6260b',
        'RM-176': '6290',
        'RM-175': '6290b',
        'NHL-10': '6600',
        'NHL-12': '6620',
        'NHL-12X': '6620',
        'RM-1': '6630',
        'RM-109': '6631',
        'RH-67': '6670',
        'RH-68': '6670b',
        'RM-36': '6680',
        'RM-57': '6681',
        'RM-58': '6682',
        'RH-51': '7610',
        'RH-52': '7610b',
        'NHL-2NA': '7650',
        'RM-170': 'E50-1',
        'RM-171': 'E50-2',
        'RM-244': 'E51-1',
        'RM-49': 'E60-1',
        'RM-89': 'E61-1',
        'RM-227':'E61i-1',
        'RM-294':'E61i-2',
        'RM-88': 'E62-1',
        'RM-88A': 'E62-1',
        'RM-208': 'E65-1',
        'RM-10': 'E70-1',
        'RM-24': 'E70-2',
        'NEM-4': 'N-Gage',
        'RH-29': 'N-Gage QD (asia/europe)',
        'RH-47': 'N-Gage QD (americas)',
        'RM-84': 'N70-1',
        'RM-99': 'N70-5',
        'RM-67': 'N71-1',
        'RM-112': 'N71-5',
        'RM-180': 'N72-5',
        'RM-133': 'N73-1',
        'RM-132': 'N73-5',
        'RM-128': 'N75-3',
        'RM-135': 'N76-1',
        'RM-149': 'N76-5',
        'RM-194': 'N77-1',
        'RM-195': 'N77-2 or N77-5',
        'RM-92': 'N80-1',
        'RM-93': 'N80-2',
        'RM-91': 'N80-3',
        'RM-179': 'N81-1',
        'RM-223': 'N81-3',
        'RM-256': 'N81-5',
        'RM-42': 'N90-1',
        'RM-43': 'N91-1 or N91-2',
        'RM-158': 'N91-5 or N91-6',
        'RM-100': 'N92-1',
        'RM-101': 'N92-2',
        'RM-55': 'N93-1',
        'RM-153': 'N93-5',
        'RM-156': 'N93i-1',
        'RM-157': 'N93i-5',
        'RM-159': 'N95-1',
        'RM-160': 'N95-3',
        'RM-245': 'N95-5',
        'RM-320': 'N95-2 8GB',
        'RA-6': 'E90-1',
        'RA-7': 'E90',
        'RM-346': 'E71-1',
        'RM-357': 'E71-2',
        'RM-407': 'E71-3',
        'RM-462': 'E71x'
        }

        code = firmware.split(' ')
        if code[3] in mapping_firmware:
            return "Nokia " + mapping_firmware[code[3]]
        elif code[2] in mapping_firmware:
            return "Nokia " + mapping_firmware[code[2]]
        else:
            return "unknown (" + firmware + ")"
