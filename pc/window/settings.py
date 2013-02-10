# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import os
import pickle
import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtSql import *
import ui.ui_settings
import ui.resource_rc
import widget.SortedListWidgetItem
import lib.device
import lib.chatwindowstyle
from lib.classes import *

ANIMATION_SUPPORT = "QPropertyAnimation" in dir()

class Settings(QDialog,  ui.ui_settings.Ui_Settings):
    def __init__(self, parent, main):
        super(Settings,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)
        main.setupButtonBox(self.buttonBox)

        # Show some messages as preview
        dummyPreviewContact = Contact(1,  1, unicode(self.tr("John Doe")))
        dummyPreviewDevice = Device(1,  unicode(self.tr("Myself")))

        dummyMessage1 = Message(1,  1,  MessageType.Outgoing,  MessagePriority.Medium,  dummyPreviewDevice,  dummyPreviewContact,
                                                       MessageStates(),  QDateTime.currentDateTime().addDays(-1).addSecs(-50),  unicode(self.tr("Hello!")))

        dummyMessage2 = Message(2,  2,  MessageType.Outgoing,  MessagePriority.Medium,  dummyPreviewDevice,  dummyPreviewContact,
                                                       MessageStates(),  QDateTime.currentDateTime().addDays(-1),  unicode(self.tr("Are you available?")))

        dummyMessage3 = Message(3,  3,  MessageType.Incoming,  MessagePriority.Medium,  dummyPreviewDevice,  dummyPreviewContact,
                                                       MessageStates(),  QDateTime.currentDateTime().addSecs(-60),
                                                       unicode(self.tr("Sorry, I have only just read your message. ")))

        dummyMessage4 = Message(4,  4,  MessageType.Outgoing,  MessagePriority.Medium,  dummyPreviewDevice,  dummyPreviewContact,
                                                       MessageStates(),  QDateTime.currentDateTime(),
                                                       unicode(self.tr("Never mind, I wanted to get in touch with you because...")))


        self.messagesView.init(dummyPreviewContact,  dummyPreviewDevice)
        self.messagesView.appendMessage(dummyMessage1)
        self.messagesView.appendMessage(dummyMessage2)
        self.messagesView.appendMessage(dummyMessage3)
        self.messagesView.appendMessage(dummyMessage4)

        self.connect(self.addContactButton,  SIGNAL("clicked()"),  self.addContact)
        self.connect(self.removeContactButton,  SIGNAL("clicked()"),  self.removeContact)
        self.connect(self.buttonBox,  SIGNAL("clicked(QAbstractButton *)"),  self.apply)

        self.connect(self.allDevicesList,  SIGNAL("deviceDoubleClicked"),  self.selectedDevicesList.addDevice)
        self.connect(self.selectedDevicesList,  SIGNAL("deviceDoubleClicked"),  self.selectedDevicesList.removeDevice)

        self.connect(self.allDevicesList,  SIGNAL("deviceDoubleClicked"),  self.addDeviceButton,  SLOT("animateClick()"))
        self.connect(self.selectedDevicesList,  SIGNAL("deviceDoubleClicked"),  self.removeDeviceButton,  SLOT("animateClick()"))

        self.connect(self.addDeviceButton,  SIGNAL("clicked()"),
                                                            lambda : self.selectedDevicesList.addDevices(self.allDevicesList.selectedDevices()))
        self.connect(self.removeDeviceButton,  SIGNAL("clicked()"),
                                                            lambda : self.selectedDevicesList.removeDevices(self.selectedDevicesList.selectedDevices()))

        self.connect(self.themeList,  SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),  self.showThemePreview)
        self.connect(self.themeVariantsList,  SIGNAL("currentIndexChanged(const QString &)"),  self.showThemeVariantPreview)
        self.connect(self.groupMessagesBox,  SIGNAL("stateChanged(int)"),  self.showThemeGroupMessagesPreview)
        self.connect(self.compactBox,  SIGNAL("stateChanged(int)"),  self.showThemeCompactPreview)
        self.connect(self.installThemeButton,  SIGNAL("clicked()"),  self.installTheme)
        self.connect(self.deleteThemeButton,  SIGNAL("clicked()"),  self.deleteTheme)

        self.sqliteDriverNotFoundLabel.setHidden(QSqlDatabase.drivers().contains("QSQLITE"))
        self.mysqlDriverNotFoundLabel.setHidden(QSqlDatabase.drivers().contains("QMYSQL"))

        self.show()

    def show(self):
        self.loadSettings()
        #self.scanStart()
        QDialog.show(self)

    def loadSettings(self):
        # Read values
        plugin =  self.settings.setting("general/connectionPlugin")
        pluginList = lib.device.Device(self, self.main).plugins()
        port = self.settings.setting("bluetooth/port")
        lastName = self.settings.setting("bluetooth/lastName")
        showCellnumber = not self.settings.setting("contacts/hideCellnumber")
        sendMessageOnReturn = self.settings.setting("general/sendMessageOnReturn")
        markAsRead = self.settings.setting("messages/markAsRead")
        saveMessages = self.settings.setting("messages/saveAllMessages")
        lastMessages = self.settings.setting("messages/displayLast")
        showPopup = self.settings.setting("popups/show")
        timeoutPopup = self.settings.setting("popups/timeout")
        animatePopup = self.settings.setting("popups/animate")
        autoConnect = self.settings.setting("general/automaticConnectionEnabled")
        autoConnectInterval = self.settings.setting("general/automaticConnectionInterval")
        autoStart = self.helper.getAutostart()
        autoStartMinimized = self.settings.setting("general/autoStartMinimized")

        minimizeOnClose = self.settings.setting("windows/main/minimizeOnClose")
        if minimizeOnClose == 2:
            quitOnClose = True
        else:
            quitOnClose = False

        ignoreAllContacts = self.settings.setting("contacts/ignoreAll")
        displayIcon = self.settings.setting("contacts/displayIcon")

        db_type = self.settings.setting("database/type")
        if db_type == "sqlite":
            db_type = 0
        else:
            db_type = 1

        chatTheme = self.settings.setting("windows/chat/theme/name")
        chatThemeVariant = self.settings.setting("windows/chat/theme/variant")
        chatThemeGroupMessages = self.settings.setting("windows/chat/theme/groupMessages")
        chatThemeCompact = self.settings.setting("windows/chat/theme/compact")

        mysql_host = self.settings.setting("database/mysql/host")
        mysql_port = self.settings.setting("database/mysql/port")
        mysql_user = self.settings.setting("database/mysql/user")
        mysql_pass = self.settings.setting("database/mysql/pass")
        mysql_database = self.settings.setting("database/mysql/database")

        updateInterval = self.settings.setting("updateCheck/interval")
        updateUnstable = self.settings.setting("updateCheck/showUnstable")
        updateEnabled = self.settings.setting("updateCheck/enabled")

        tabbedChat = self.settings.setting("windows/chat/tabbedChat")
        widgetStyle = self.settings.setting("lookAndFeel/widgetStyle")
        country = self.settings.setting("lookAndFeel/language")
        if country:
            language = QLocale(country).language()
        else:
            language = 0

        # Write values
        self.pluginBox.clear()

        for item in pluginList:
            self.pluginBox.addItem(item)

        self.pluginBox.setCurrentIndex(self.pluginBox.findText(plugin))
        self.portBox.setValue(port)

        self.selectedDevicesList.reset()
        for device in self.database.devices():
            self.selectedDevicesList.addDevice(device)

        self.allContactsList.clear()
        self.blockedContactsList.clear()
        if not self.database.contactCount():
            item = QListWidgetItem(self.allContactsList)
            item.setText(self.tr("No contacts available"))
        else:
            for contact in self.database.contacts(True):
                if contact.isIgnored():
                    item = QListWidgetItem(self.blockedContactsList)
                else:
                    item = QListWidgetItem(self.allContactsList)

                item.setData(Roles.ContactRole,  QVariant(contact))
                item.setText(contact.name())

        self.allContactsList.sortItems(Qt.AscendingOrder)

        self.showCellnumberBox.setCheckState(self.checkBoxValue(showCellnumber))
        self.sendMessageOnReturnBox.setCheckState(self.checkBoxValue(sendMessageOnReturn))
        self.markAsReadBox.setCheckState(self.checkBoxValue(markAsRead))
        self.saveMessagesBox.setCheckState(self.checkBoxValue(saveMessages))
        self.lastMessagesBox.setValue(lastMessages)
        self.showPopupBox.setCheckState(self.checkBoxValue(showPopup))
        self.timeoutPopupBox.setValue(timeoutPopup)
        self.animatePopupBox.setCheckState(self.checkBoxValue(animatePopup))
        self.quitOnCloseBox.setCheckState(self.checkBoxValue(quitOnClose))
        self.ignoreAllContactsBox.setCheckState(self.checkBoxValue(ignoreAllContacts))
        self.displayIconBox.setCheckState(self.checkBoxValue(displayIcon))
        self.typeBox.setCurrentIndex(db_type)
        self.mysql_hostLine.setText(mysql_host)
        self.mysql_portBox.setValue(mysql_port)
        self.mysql_userLine.setText(mysql_user)
        self.mysql_passLine.setText(mysql_pass)
        self.mysql_databaseLine.setText(mysql_database)

        # Only enable "Animate popups" when there is animation support in PyQt4
        # This is true for Qt versions >= 4.6
        self.animatePopupBox.setEnabled(ANIMATION_SUPPORT)

        # Only enable these options when autostart is supported
        # (e.g. false on Mac OS X or when running the source files on Windows)
        self.autoStartBox.setEnabled(self.helper.autostartSupported())
        self.autoStartMinimizedBox.setEnabled(self.helper.autostartSupported() and autoStart)

        self.autoConnectBox.setCheckState(self.checkBoxValue(autoConnect))
        self.autoConnectIntervalBox.setValue(autoConnectInterval)
        self.autoStartBox.setCheckState(self.checkBoxValue(autoStart))
        self.autoStartMinimizedBox.setCheckState(self.checkBoxValue(autoStartMinimized))

        # Save the old values, so that the autostart isn't always recreated
        self.oldAutoStart = autoStart
        self.oldAutoStartMinimized = autoStartMinimized

        self.groupMessagesBox.setCheckState(self.checkBoxValue(chatThemeGroupMessages))
        self.compactBox.setCheckState(self.checkBoxValue(chatThemeCompact))

        # Build list of chat themes
        for theme,  directory in self.helper.chatThemes():
            # Show only unique themes
            if self.themeList.findItems(theme,  Qt.MatchExactly):
                continue
            item = widget.SortedListWidgetItem.SortedListWidgetItem(self.themeList)
            item.setText(theme)
            item.setData(Roles.DirectoryRole,  QVariant(directory))

        items = self.themeList.findItems(chatTheme,  Qt.MatchExactly)
        if len(items) > 0:
            self.themeList.setCurrentItem(items[0])
        else:
            self.themeList.setCurrentRow(0)

        if chatThemeVariant == "":
            chatThemeVariant = self.tr("(No variant)")
        self.themeVariantsList.setCurrentIndex(self.themeVariantsList.findText(chatThemeVariant))

        # Save the old value, otherwise a redraw of all chat windows would be needed...
        self.oldChatTheme = chatTheme
        self.oldChatThemeVariant = chatThemeVariant
        self.oldChatThemeGroupMessages = chatThemeGroupMessages
        self.oldChatThemeCompact = chatThemeCompact

        # Build list of update intervals
        self.updateIntervalBox.addItem(self.tr("Daily"),  QVariant(1))
        self.updateIntervalBox.addItem(self.tr("Every third day"),  QVariant(3))
        self.updateIntervalBox.addItem(self.tr("Weekly"),  QVariant(7))
        self.updateIntervalBox.addItem(self.tr("Never"),  QVariant(0))
        self.updateIntervalBox.setCurrentIndex(self.updateIntervalBox.findData(QVariant(updateInterval)))
        self.updateUnstableBox.setCheckState(self.checkBoxValue(updateUnstable))

        # Save the old value, otherwise there wouldn't be a recheck at the next startup...
        self.oldUpdateUnstable = updateUnstable

        # Disable groupBox when the website says that the update checker should get displayed
        # this only happens when anything is seriously fucked up ;)
        self.updateIntervalLabel.setEnabled(updateEnabled)
        self.updateIntervalBox.setEnabled(updateEnabled)
        self.updateUnstableBox.setEnabled(updateEnabled)

        self.chatGroupBox.addItem(self.tr("Open all contacts in a seperate chat window"),  QVariant(False))
        self.chatGroupBox.addItem(self.tr("Show contacts in different tabs"),  QVariant(True))
        self.widgetStyleBox.setCurrentIndex(self.widgetStyleBox.findData(QVariant(tabbedChat)))

        # Build list of widget styles
        self.widgetStyleBox.addItem(self.tr("Default style"),  QVariant(""))
        for style in QStyleFactory.keys():
            self.widgetStyleBox.addItem(style,  QVariant(style))
        self.widgetStyleBox.setCurrentIndex(self.widgetStyleBox.findData(QVariant(widgetStyle)))

        # Build list of languages
        self.languageBox.addItem(self.tr("Default language"),  QVariant(0))
        languages = list()
        for file in QDir(":/lang").entryList():
            match = re.match("app_(.*).qm", unicode(file))
            if match:
                locale = QLocale(match.group(1))
                languages.append([QLocale.languageToString(locale.language()),  locale.language()])

        languages.sort() # Sort languages by name
        for name,  languagecode in languages:
            self.languageBox.addItem(name,  QVariant(languagecode))
        if language != 0:
            self.languageBox.setCurrentIndex(self.languageBox.findData(QVariant(language)))
        else:
            self.languageBox.setCurrentIndex(0)

        self.updateCountryBox(self.languageBox.currentIndex(),  country)
        # Refill the country box when the language is changed
        self.connect(self.languageBox,  SIGNAL("currentIndexChanged(int)"),  self.updateCountryBox)

        # Show the restart hint label only when the settings were changed
        self.restartHintLabel.hide()

    def updateCountryBox(self,  index,  name=""):
        language = self.languageBox.itemData(index).toInt()[0]

        self.countryBox.clear()
        countries = list()
        for countrycode in QLocale.countriesForLanguage(language):
            countries.append([QLocale.countryToString(countrycode),  QLocale(language,  countrycode).name()])

        if not countries:
            countries.append([self.tr("Default country"),  ""])

        countries.sort() # Sort countries by name
        for country,  isoname in countries:
            self.countryBox.addItem(country,  QVariant(isoname))

        if language != 0:
            if not name:
                name = QLocale(language).name()
            index = self.countryBox.findData(QVariant(name))
            self.countryBox.setCurrentIndex(index)
        else:
            self.countryBox.setCurrentIndex(0)

    def showThemePreview(self,  currentItem,  previousItem):
        if not currentItem:
            return

        name = unicode(currentItem.text())
        variant = ""
        directory = unicode(currentItem.data(Roles.DirectoryRole).toString())
        groupMessages = bool(self.groupMessagesBox.checkState())
        compact = bool(self.compactBox.checkState())

        theme = lib.chatwindowstyle.ChatWindowStyle(name, directory)
        self.messagesView.setStyle(theme,  variant,  groupMessages,  compact)

        self.themeVariantsList.clear()
        self.themeVariantsList.addItem(self.tr("(No variant)"))
        for variant in theme.variants():
            self.themeVariantsList.addItem(variant)

        # Update compact checkbox
        self.compactBox.setEnabled(self.messagesView.currentChatStyle.hasCompact(""))

        # Only allow the deletion of user-installed themes
        # Remove the latest 6 dirs from the directory path (data/chat-themes/themename/Contents/Resources)
        base = os.sep.join(theme.stylePath.split(os.sep)[:-6])
        self.deleteThemeButton.setEnabled(QFileInfo(QSettings().fileName()).absoluteDir() == QDir(base))

    def showThemeVariantPreview(self,  variant):
        if variant == self.tr("(No variant)"):
            variant = ""

        self.messagesView.setStyleVariant(variant)
        self.compactBox.setEnabled(self.messagesView.currentChatStyle and self.messagesView.currentChatStyle.hasCompact(variant))

    def showThemeGroupMessagesPreview(self,  checkstate):
        self.messagesView.setGroupConsecutiveMessages(bool(checkstate))

    def showThemeCompactPreview(self,  checkstate):
        self.messagesView.setCompact(bool(checkstate))

    def installTheme(self):
        url = QUrl(QFileDialog.getOpenFileName(self,  self.tr("Open theme archive"),  QDir.homePath(),
                                               self.tr("Zip archive") + ", " +
                                               self.tr("Tar archive") + ", "+
                                               self.tr("Tar archive (gzip-compressed)") + ", "+
                                               self.tr("Tar archive (bzip-compressed)") + " (*.zip *.tar *.tar.gz *.tar.bz2)" + ";;" +
                                               self.tr("Zip archive") + " (*.zip)" + ";;" +
                                               self.tr("Tar archive") + "(*.tar)"+ ";;" +
                                               self.tr("Tar archive (gzip-compressed)") + "(*.tar.gz)" + ";;" +
                                               self.tr("Tar archive (bzip-compressed)") + " (*.tar.bz2)"))
        if url.isValid():
            returncode,  theme,  directory = self.helper.installTheme(unicode(url.toLocalFile()),  unicode(QFileInfo(self.settings.fileName()).absolutePath()))
            if returncode:
                if not self.themeList.findItems(theme,  Qt.MatchExactly):
                    item = widget.SortedListWidgetItem.SortedListWidgetItem(self.themeList)
                    item.setText(theme)
                    item.setData(Roles.DirectoryRole,  QVariant(directory))
                self.themeList.setCurrentItem(self.themeList.findItems(theme,  Qt.MatchExactly)[0])
            else:
                message = QMessageBox.critical(self,
                self.tr("Theme installation failed"),
                self.tr("""The theme could not be installed!\n
Please check that it is a valid archive file!"""),
                QMessageBox.StandardButtons(\
                        QMessageBox.Ok),
                QMessageBox.Ok)

    def deleteTheme(self):
        currentItem = self.themeList.currentItem()
        theme = unicode(currentItem.text())
        directory = unicode(currentItem.data(Roles.DirectoryRole).toPyObject())
        message = QMessageBox.question(self,
        self.tr("Delete theme?"),
        self.tr("""Do you really want to delete the theme "%1"!\n
This will remove the following directory:\n
%2!""").arg(theme,  directory),
        QMessageBox.StandardButtons(\
                QMessageBox.Yes | QMessageBox.No),
        QMessageBox.No)

        if message == QMessageBox.Yes:
            self.helper.removeTheme(directory)
            self.themeList.takeItem(self.themeList.currentRow())

    def addContact(self):
        try:
            item = self.allContactsList.currentItem()
            contact = item.data(Roles.ContactRole).toPyObject()
            name = contact.name()
        except:
            return

        # Don't add contacts twice
        if self.blockedContactsList.findItems(name,  Qt.MatchExactly):
            return

        contact.ignore()
        tmp = QListWidgetItem(item)
        self.blockedContactsList.addItem(tmp)

    def removeContact(self):
        try:
            contact = self.blockedContactsList.currentRow()
            self.blockedContactsList.takeItem(contact)
        except:
            return

    def apply(self,  button):
        if self.buttonBox.buttonRole(button) == QDialogButtonBox.ApplyRole:
            self.saveSettings()

    def accept(self):
        if self.saveSettings():
            self.close()

    def saveSettings(self):
        # Read values
        plugin = str(self.pluginBox.currentText())
        port = int(self.portBox.value())

        self.database.deviceHideAll()
        for device in self.selectedDevicesList.devices():
            self.database.deviceAdd(device)

        self.database.contactUnignoreAll()
        for row in range(self.blockedContactsList.count()):
            item = self.blockedContactsList.item(row)
            contact = item.data(Roles.ContactRole).toPyObject()
            self.database.contactIgnoreUpdate(contact)

        showCellnumber = bool(self.showCellnumberBox.checkState())
        sendMessageOnReturn = bool(self.sendMessageOnReturnBox.checkState())
        markAsRead = bool(self.markAsReadBox.checkState())
        saveMessages = bool(self.saveMessagesBox.checkState())
        lastMessages = int(self.lastMessagesBox.value())
        showPopup = bool(self.showPopupBox.checkState())
        timeoutPopup = int(self.timeoutPopupBox.value())
        animatePopup = bool(self.animatePopupBox.checkState())
        quitOnClose = bool(self.quitOnCloseBox.checkState())
        autoConnect = bool(self.autoConnectBox.checkState())
        autoConnectInterval = int(self.autoConnectIntervalBox.value())
        autoStart = bool(self.autoStartBox.checkState())
        autoStartMinimized = bool(self.autoStartMinimizedBox.checkState())
        ignoreAllContacts = bool(self.ignoreAllContactsBox.checkState())
        displayIcon = bool(self.displayIconBox.checkState())
        type = str(self.typeBox.currentText()).lower()
        #sqlite_file = str(QFileInfo(self.settings.fileName()).absoluteDir().absolutePath()) + "/messages.db"
        mysql_host = str(self.mysql_hostLine.text())
        mysql_port = int(self.mysql_portBox.value())
        mysql_user = str(self.mysql_userLine.text())
        mysql_pass = str(self.mysql_passLine.text())
        mysql_database = str(self.mysql_databaseLine.text())

        if quitOnClose:
            minimizeOnClose = 2
        else:
            minimizeOnClose = 1

        chatTheme = unicode(self.themeList.currentItem().text())
        chatThemeVariant = unicode(self.themeVariantsList.currentText())
        if chatThemeVariant == self.tr("(No variant)"):
            chatThemeVariant = ""
        chatThemeGroupMessages = bool(self.groupMessagesBox.checkState())
        chatThemeCompact = bool(self.compactBox.checkState())

        updateInterval = self.updateIntervalBox.itemData(self.updateIntervalBox.currentIndex()).toInt()[0]
        updateUnstable = bool(self.updateUnstableBox.checkState())
        tabbedChat = self.chatGroupBox.itemData(self.chatGroupBox.currentIndex()).toBool()
        widgetStyle = unicode(self.widgetStyleBox.itemData(self.widgetStyleBox.currentIndex()).toString())
        language = unicode(self.countryBox.itemData(self.countryBox.currentIndex()).toString())

        # Check database connection
        self.database.close()

        data = dict()
        if type == "sqlite":
           # Use filename from the settings
           #data["filename"] = sqlite_file
           data["filename"] = self.settings.setting("database/sqlite/filename")
        elif type == "mysql":
            if not (mysql_host and mysql_port and mysql_user and mysql_pass and mysql_database):
                QMessageBox.critical(self,  self.tr("MySQL data is incomplete!"), self.tr("You didn't enter all connection informations. If you are unsure please use SQlite."))
                return False

            data["host"] = mysql_host
            data["port"] = mysql_port
            data["user"] = mysql_user
            data["pass"] = mysql_pass
            data["database"] = mysql_database

        self.log.info(QString("Trying to connect to database"))
        ret = self.database.openDatabase(type,  data)

        if ret == False:
            # Connection failed
            # Show error message
            err = self.database.error()

            message = QMessageBox.critical(self,
            self.tr("Error by creating the database!"),
            self.tr("""The creation of the database failed with the following error:\n%1\n
Please mind that the application doesn't work without an database connection.""").arg(err),
            QMessageBox.StandardButtons(\
                    QMessageBox.Ignore | \
                    QMessageBox.Retry),
            QMessageBox.Retry)

            if message == QMessageBox.Retry:
                return False

        # Write values
        self.settings.setSetting("general/connectionPlugin",  plugin)
        self.settings.setSetting("bluetooth/port",  port)
        self.settings.setSetting("contacts/hideCellnumber",  not showCellnumber)
        self.settings.setSetting("general/sendMessageOnReturn",  sendMessageOnReturn)
        self.settings.setSetting("messages/markAsRead",  markAsRead)
        self.settings.setSetting("messages/saveAllMessages",  saveMessages)
        self.settings.setSetting("messages/displayLast",  lastMessages)
        self.settings.setSetting("popups/show",  showPopup)
        self.settings.setSetting("popups/timeout",  timeoutPopup)
        self.settings.setSetting("popups/animate",  animatePopup)
        self.settings.setSetting("windows/chat/theme/name",  chatTheme)
        self.settings.setSetting("windows/chat/theme/variant",  chatThemeVariant)
        self.settings.setSetting("windows/chat/theme/groupMessages",  chatThemeGroupMessages)
        self.settings.setSetting("windows/chat/theme/compact",  chatThemeCompact)
        self.settings.setSetting("windows/main/minimizeOnClose",  minimizeOnClose)
        self.settings.setSetting("general/automaticConnectionEnabled",  autoConnect)
        self.settings.setSetting("general/automaticConnectionInterval",  autoConnectInterval)
        self.settings.setSetting("general/autoStartMinimized",  autoStartMinimized)
        self.settings.setSetting("contacts/ignoreAll",  ignoreAllContacts)
        self.settings.setSetting("contacts/displayIcon",  displayIcon)
        self.settings.setSetting("database/type",  type)

        # Do not replace current filename, the default should be okay
        #self.settings.setSetting("database/sqlite/filename",  sqlite_file)
        self.settings.setSetting("database/mysql/host",  mysql_host)
        self.settings.setSetting("database/mysql/port",  mysql_port)
        self.settings.setSetting("database/mysql/user",  mysql_user)
        self.settings.setSetting("database/mysql/pass",  mysql_pass)
        self.settings.setSetting("database/mysql/database",  mysql_database)
        self.settings.setSetting("updateCheck/interval",  updateInterval)
        self.settings.setSetting("updateCheck/showUnstable",  updateUnstable)
        self.settings.setSetting("windows/chat/tabbedChat",  tabbedChat)
        self.settings.setSetting("lookAndFeel/widgetStyle",  widgetStyle)
        self.settings.setSetting("lookAndFeel/language",  language)

        self.settings.reloadSettings()

        # Recreate shortcut / desktop file if there was a change in autostart settings
        if autoStart != self.oldAutoStart or autoStartMinimized != self.oldAutoStartMinimized:
            self.helper.removeAutostart()
            if autoStart:
                self.helper.createAutostart(autoStartMinimized)

        # Emit a signal to reload all themes of the chat windows
        if chatTheme != self.oldChatTheme \
            or chatThemeVariant != self.oldChatThemeVariant \
            or chatThemeGroupMessages != self.oldChatThemeGroupMessages \
            or chatThemeCompact != self.oldChatThemeCompact:
                self.settings.chatThemeChanged()
        self.oldChatTheme = chatTheme
        self.oldChatThemeVariant = chatThemeVariant
        self.oldChatThemeGroupMessages = chatThemeGroupMessages
        self.oldChatThemeCompact = chatThemeCompact

        # Reset these settings
        if updateUnstable != self.oldUpdateUnstable:
            self.settings.setSetting("updateCheck/lastCheck",  QDate())
            self.settings.setSetting("updateCheck/lastVersion",  "")
            self.settings.setSetting("updateCheck/lastMessage",  "")

        return True

    def checkBoxValue(self,  bool):
        if bool:
            return Qt.Checked
        else:
            return Qt.Unchecked
