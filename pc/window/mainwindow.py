# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import sys
import re
import base64
import copy
import distutils.version
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import window.contacts_edit
import window.contacts_import
import window.settings
import window.history
import window.statistics
import window.export
import window.message_queue
import window.import_messages
import window.about
import window.favorites
import widget.SortedTreeWidgetItem
import widget.SortedListWidgetItem
import ui.ui_main
import ui.ui_mobileNumberSelect
import ui.ui_mobileNumberNotFound
import ui.ui_connection_failed
import ui.ui_connection_version_mismatch
import ui.ui_connection_update_version
import ui.resource_rc
import lib.update_checker
import lib.favorites
import lib.obex_handler
import lib.obex_scheduler
import lib.obex_wrapper
from lib.classes import *

LINUX= "qt_x11_wait_for_window_manager" in dir()

class MainWindow(QMainWindow,  ui.ui_main.Ui_MainWindow):
    def __init__(self,  parent,  main):
        super(MainWindow,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        # Refresh all 10 minutes the device information
        self.refreshTimer = QTimer(self)
        self.refreshTimer.setInterval(600000)

        self.setupUi(self)

        # Favorites menu
        self.contactMenu = self.menu_Contacts
        self.favMenu = lib.favorites.FavoriteMenu(self.contactMenu,  main)

        # Change color of the ListWidget to a normal background color and make the highlight color lighter
        pal = QPalette()
        pal.setColor(QPalette.Base,  self.palette().color(QPalette.Window))
        pal.setColor(QPalette.Highlight,  QColor(38,  136,  240))
        self.listWidget.setPalette(pal)

        # Add menu to "Import contacts" button
        self.importMenu = QMenu(self)
        self.importVcardAction = self.importMenu.addAction(QIcon(":/text-x-vcard"),  self.tr("Import &Vcard file..."))
        self.importLdifAction = self.importMenu.addAction(QIcon(":/text-x-ldif"),  self.tr("Import &LDIF file..."))
        self.contactsImportButton.setMenu(self.importMenu)

        # Restore size, position and splitter states from previous saved value
        windowSize = self.settings.setting("windows/main/size")
        windowPosition = self.settings.setting("windows/main/position")
        messagesSplitter = self.settings.setting("windows/main/messagesSplitter")
        contactsSplitter = self.settings.setting("windows/main/contactsSplitter")

        if windowSize.isValid():
            self.resize(windowSize)

        if not windowPosition.isNull():
            self.move(windowPosition)

        if not messagesSplitter.isNull():
            self.messagesSplitter.restoreState(messagesSplitter)

        if not contactsSplitter.isNull():
            self.contactsSplitter.restoreState(contactsSplitter)

        self.newMessagesComplete = False
        self.queueMessages = 0
        self.fillTypeBox = True
        self.connectionAttemptByUser = True
        self.connectionClosedByUser = False
        self.deviceScanner = self.connection.scanner()
        self.automaticConnectionTimer = QTimer()

        self.emptyPixmap = QPixmap(16,  16)
        self.emptyPixmap.fill(Qt.transparent)
        self.emptyIcon = QIcon(self.emptyPixmap)
        self.contactIsRecipientIcon = QIcon(":/dialog-apply")

        self.fileWidget.updateActions()

        # Load the contacts and devices when the event loop is started and all other events are handled
        # This results in a faster startup (saved ~274ms)
        self.loadSettings()
        self.showFavorites()
        QTimer.singleShot(0,  self.loadUpdateChecker)
        QTimer.singleShot(0,  lambda : self.loadAutomaticConnection(True))

        self.adjustSize()

        self.connect(self.main,  SIGNAL("favoriteListChanged"),  self.showFavorites)
        self.connect(self.main,  SIGNAL("updateContact"),  self.updateContact)
        self.connect(self.contactMenu,  SIGNAL("triggered(QAction *)"),  self.favoriteClicked)
        self.connect(self.settingsAction,  SIGNAL("triggered()"),  self.showSettings)
        self.connect(self.exportAction,  SIGNAL("triggered()"),  self.showExportDialog)
        self.connect(self.quitAction,  SIGNAL("triggered()"),  self.quit)
        self.connect(self.aboutApplicationAction,  SIGNAL("triggered()"),  self.showAboutDialog)
        self.connect(self.aboutQtAction,  SIGNAL("triggered()"),  self.main.app.aboutQt)
        self.connect(self.historyAction,  SIGNAL("triggered()"),  self.showHistory)
        self.connect(self.statisticsAction,  SIGNAL("triggered()"),  self.showStatistics)
        self.connect(self.messageQueueAction,  SIGNAL("triggered()"),  self.showMessageQueue)
        self.connect(self.importMessagesAction,  SIGNAL("triggered()"),  self.showImportMessages)
        self.connect(self.logAction,  SIGNAL("triggered()"),  self.showLog)
        self.connect(self.donateAction,  SIGNAL("triggered()"),  self.openDonateWebsite)
        self.connect(self.connectButton, SIGNAL("clicked()"),  self.connectToDevice)
        self.connect(self.messageText, SIGNAL("sendMessage"),  self.sendButton,  SLOT("animateClick()"))
        self.connect(self.sendButton, SIGNAL("clicked()"),  self.sendMessage)
        self.connect(self.refreshButton, SIGNAL("clicked()"),  self.refreshSysinfo)
        self.connect(self.refreshTimer,  SIGNAL("timeout()"),  self.refreshSysinfo)
        self.connect(self.listWidget,  SIGNAL("itemSelectionChanged()"),  self.checkPosition)
        self.connect(self.stackedWidget,  SIGNAL("currentChanged(int)"),
                                                                 lambda: self.searchLine.setSearchText() or self.searchLine_2.setSearchText())
        self.connect(self.stackedWidget,  SIGNAL("currentChanged(int)"), self.checkFiles)
        self.connect(self.disconnectButton, SIGNAL("clicked()"),  self.closeConnection)
        self.connect(self.cancelButton, SIGNAL("clicked()"),  self.closeConnection)
        self.connect(self.messageText,  SIGNAL("textChanged()"),  self.textChanged)
        self.connect(self.toLine,  SIGNAL("textEdited(const QString &)"),  self.recipientChanged)
        self.connect(self.contactsTree,SIGNAL("customContextMenuRequested(QPoint)"),self.showCustomContextMenu)
        self.connect(self.contactsTree,SIGNAL("itemActivated(QTreeWidgetItem *, int)"),self.contactClicked)
        self.connect(self.contactsList,SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),self.showContact)
        self.connect(self.contactsList,SIGNAL("currentItemChanged(QListWidgetItem *, QListWidgetItem *)"),
                                                                  self,  SLOT("checkEditContactButton()"))
        self.connect(self.contactEditButton,SIGNAL("clicked()"), self.editContact)
        self.connect(self.contactAddButton,SIGNAL("clicked()"), self.addContact)
        self.connect(self.importVcardAction,SIGNAL("triggered()"), lambda : self.importContacts("vcard"))
        self.connect(self.importLdifAction,SIGNAL("triggered()"), lambda : self.importContacts("ldif"))
        self.connect(self.contactsList,SIGNAL("customContextMenuRequested(QPoint)"),self.showContactListContextMenu)
        self.connect(self.searchLine,SIGNAL("textChanged(const QString &)"),self.showContacts)
        self.connect(self.searchLine_2,SIGNAL("textChanged(const QString &)"),self.showContacts)
        self.connect(self.typeBox,SIGNAL("currentIndexChanged(int)"),self.showContacts)
        self.connect(self.connection, SIGNAL("connectionStateChanged"),  lambda x: self.connectBar.setValue(x))
        self.connect(self.connection, SIGNAL("sysinfoCompleted"),  self.showSysinfo)
        self.connect(self.connection, SIGNAL("contactsCompleted"),  self.showContacts)
        self.connect(self.connection, SIGNAL("contactsUpdated"),  self.showContacts)
        self.connect(self.connection, SIGNAL("connectionCompleted"),  self.connected)
        self.connect(self.connection, SIGNAL("connectionClosed"),  self.connectionClosed)
        self.connect(self.connection, SIGNAL("connectionAborted"),  self.connectionClosed)
        self.connect(self.connection, SIGNAL("connectionFailed"),  self.connectionFailed)
        self.connect(self.connection, SIGNAL("connectionVersionMismatchError"),  self.connectionVersionMismatch)
        self.connect(self.connection, SIGNAL("messagesRequest"),  self.newMessages)
        self.connect(self.connection, SIGNAL("messagesRequestComplete"),  self.newMessagesFinished)
        self.connect(self.connection, SIGNAL("messageSent"),  self.messageStateChanged)
        self.connect(self.connection, SIGNAL("messageQueued"),  self.messageStateChanged)
        self.connect(self.automaticConnectionTimer,  SIGNAL("timeout()"),  self.automaticConnectionTimerFired)
        self.connect(self.deviceScanner,  SIGNAL("scanStarted"),  self.automaticConnectionScanStarted)
        self.connect(self.deviceScanner,  SIGNAL("foundDevice"),  self.automaticConnectionFoundDevice)
        self.connect(self.deviceScanner,  SIGNAL("scanCompleted"),  self.automaticConnectionScanFinished)
        self.connect(self.deviceScanner,  SIGNAL("scanFailed"),  self.automaticConnectionScanFinished)
        self.connect(self.settings,  SIGNAL("reloadSettings"),  self.loadSettings)
        self.connect(self.settings,  SIGNAL("reloadSettings"),  self.loadAutomaticConnection)

        # Also update the icons in the summary tab when the connection state has changed

        self.okPixmap = QIcon(":/dialog-apply").pixmap(16,  16)
        self.loadingMovie = QMovie(":/loading-2",  parent=self)
        self.loadingMovie.setScaledSize(QSize(20,  20))
        self.loadingMovie.start()

        self.connect(self.connection, SIGNAL("connectionEstablished"),  lambda : self.connectionStateLabel.setPixmap(self.okPixmap))
        self.connect(self.connection, SIGNAL("connectionEstablished"),  lambda : self.sysinfoStateLabel.setMovie(self.loadingMovie))

        self.connect(self.connection, SIGNAL("sysinfoCompleted"),  lambda : self.sysinfoStateLabel.setPixmap(self.okPixmap))
        self.connect(self.connection, SIGNAL("sysinfoCompleted"),  lambda : self.contactStateLabel.setMovie(self.loadingMovie))

        self.connect(self.connection, SIGNAL("contactsCompleted"),  lambda : self.contactStateLabel.setPixmap(self.okPixmap))
        self.connect(self.connection, SIGNAL("contactsCompleted"),  lambda : self.calendarStateLabel.setMovie(self.loadingMovie))

        self.connect(self.connection, SIGNAL("calendarCompleted"),  lambda : self.calendarStateLabel.setPixmap(self.okPixmap))


        if not main.minimized:
            self.show()

    def __str__(self):
        return "\"Main-Window\""

    def loadSettings(self):
        self.updateDevices()
        if self.connection.connected():
            # Show the extended StackedWidget when there is an active connection
            # after reloading the settings
            self.showSysinfo()
        self.showContacts()
        self.connection = self.main.connection

        self.messageText.setSendMessageOnReturn(self.settings.setting("general/sendMessageOnReturn"))

        self.checkSendButton()
        self.checkEditContactButton()

    def loadUpdateChecker(self):
        if self.settings.setting("updateCheck/enabled"):
            lastCheck = self.settings.setting("updateCheck/lastCheck")
            interval = self.settings.setting("updateCheck/interval")
            if interval == 0:
                return
            if not lastCheck.isValid() or lastCheck.daysTo(QDate.currentDate()) >= interval:
                self.updateChecker = lib.update_checker.UpdateChecker(self,  self.main)
                self.connect(self.updateChecker,  SIGNAL("updateCheckFailed"),  self.updateCheckError)
                self.connect(self.updateChecker,  SIGNAL("updateCheckNewVersion"),  self.updateCheckNewVersion)

                self.updateChecker.updateCheck()
            else:
                lastVersion = self.settings.setting("updateCheck/lastVersion")
                if not lastVersion:
                    return
                lastVersion = distutils.version.LooseVersion(lastVersion)

                currentVersion = ".".join([str(i) for i in self.main.appVersion])
                currentVersion = distutils.version.LooseVersion(currentVersion)

                if lastVersion > currentVersion:
                    self.updateCheckNewVersion(self.settings.setting("updateCheck/lastVersion"),  self.settings.setting("updateCheck/lastMessage"))

    def loadAutomaticConnection(self,  firstStart=False):
        enabled = self.settings.setting("general/automaticConnectionEnabled")
        if enabled and not self.connection.connected():
            interval = self.settings.setting("general/automaticConnectionInterval")
            if firstStart:
                self.automaticConnectionTimerFired()
            self.automaticConnectionTimer.setInterval(interval * 1000)
            self.automaticConnectionTimer.start()

    def showFavorites(self):
        self.contactMenu.clear()
        self.favMenu.menu(self.contactMenu)

    def adjustSize(self):
        maxSize = QSize()
        for i in range(self.listWidget.count()):
            itemSize = self.listWidget.sizeHintForIndex( self.listWidget.indexFromItem(self.listWidget.item(i)) )
            if itemSize.width() > maxSize.width():
                maxSize.setWidth(itemSize.width())
            if itemSize.height() > maxSize.height():
                maxSize.setHeight(itemSize.height())

        # Add spacing
        maxSize.setWidth(maxSize.width() + 13)
        maxSize.setHeight(maxSize.height() + 10)

        for i in range(self.listWidget.count()):
            self.listWidget.item(i).setSizeHint(maxSize)

        self.listWidget.setGridSize(maxSize)
        self.listWidget.setMaximumWidth(maxSize.width() + self.listWidget.rect().width() - self.listWidget.contentsRect().width() )
        self.listWidget.setMinimumWidth(maxSize.width() + self.listWidget.rect().width() - self.listWidget.contentsRect().width() )

    def checkPosition(self):
        # If you select the last item, hold the left mouse button move your mouse to a free space select the last item
        if len(self.listWidget.selectedItems()) == 0:
            self.listWidget.setCurrentRow(self.listWidget.currentRow())

    def checkFiles(self,  index):
        if self.stackedWidget.indexOf(self.files) == index:
            if lib.obex_wrapper.FOUND_OBEX and not self.fileWidget.connected() and self.connection.connected():
                handler = lib.obex_handler.ObexHandler(self.connection.device().bluetoothAddress())
                scheduler = lib.obex_scheduler.ObexScheduler(handler)
                self.fileWidget.setScheduler(scheduler)

    def updateDevices(self):
        device = self.devicesBox.currentDevice()
        if not isinstance(device,  type(None)):
            try:
                try:
                    totalRam = self.helper.pretty_filesize(device.value("total_ram"))
                except:
                    totalRam = self.tr("unknown")

                try:
                    totalRom = self.helper.pretty_filesize(device.value("total_rom"))
                except:
                    totalRom = self.tr("unknown")

                self.modelLabel_3.setText(str(device.value("model")))
                self.imeiLabel_3.setText(str(device.value("imei")))
                self.totalRamLabel_3.setText(totalRam)
                self.romLabel_3.setText(totalRom)
                self.displayLabel_3.setText(self.tr("%1 pixels").arg(device.value("display") ))
                self.osLabel_3.setText(device.value("s60_version")) # TODO: append to modelLabel
                self.detailStack.setCurrentWidget(self.simpleWidget)
            except ValueError:
                # This happens when you were never connected to the device
                # (e.g. when you start the application for the first time)
                self.detailStack.setCurrentWidget(self.noDataWidget)
        else:
            self.detailStack.setCurrentWidget(self.noDataWidget)

    def __connectToDevice(self, device):
        if self.connection.connected():
            return

        if isinstance(device,  type(None)):
            return

        self.settings.setSetting("bluetooth/lastName",  device.name())
        port = self.settings.setting("bluetooth/port")

        if self.scanningMovie.movie():
            self.scanningMovie.movie().stop()
        self.scanningMovie.setMovie(QMovie())
        self.scanningMovie.setToolTip("")
        self.automaticConnectionTimer.stop()

        # FIXME: Ugly hack
        device.setPort(port)

        # Reset connection state icons
        self.connectionStateLabel.setMovie(self.loadingMovie)
        self.sysinfoStateLabel.clear()
        self.contactStateLabel.clear()
        self.calendarStateLabel.clear()

        self.log.info(QString("Connect to device %1 ( %2 on port %3 )").arg(device.name()).arg(device.bluetoothAddress()).arg(port))
        self.statusLabel.setText(self.tr("Establish connection!"))
        self.connectLabel.setText(self.tr("Connection establishment to: <b>%1</b>").arg(device.name()))
        self.devicesBox.selectDevice(device)
        self.devicesBox.setEnabled(False)
        self.connectButton.setEnabled(False)
        self.establishConnectionStack.setCurrentWidget(self.establishConnectionWidget)

        self.connection.connectToDevice(device)

    def connectToDevice(self):
        device = self.devicesBox.currentDevice()
        if isinstance(device,  type(None)):
            return

        self.connectionAttemptByUser = True
        self.__connectToDevice(device)


    def showSysinfo(self):
        refreshDate = QDate.currentDate().toString("dd.MM.yyyy")
        refreshTime = QTime().currentTime().toString("hh:mm:ss")

        try:
            freeRam = self.helper.pretty_filesize(self.connection.device().value("free_ram"))
        except:
            freeRam = self.tr("unknown")

        try:
            totalRam = self.helper.pretty_filesize(self.connection.device().value("total_ram"))
        except:
            totalRam = self.tr("unknown")

        try:
            totalRom = self.helper.pretty_filesize(self.connection.device().value("total_rom"))
        except:
            totalRom = self.tr("unknown")

        try:
            signalBars = int(self.connection.device().value("signal_bars"))
        except:
            signalBars = 0

        try:
            battery = int(self.connection.device().value("battery"))
        except:
            battery = 0

        if self.connection.device().value("signal_dbm") == u"-1":
            # Mobile phone is in offline mode
            signalDbm = self.tr("offline mode")
        else:
            signalDbm = self.tr("%1 dbM").arg(self.connection.device().value("signal_dbm"))

        if signalBars == -1:
            # Mobile phone is in offline mode
            self.signalBar_2.setHidden(True)
            self.signalBar.setHidden(True)
        else:
            self.signalBar_2.setHidden(False)
            self.signalBar.setHidden(False)

        self.refreshTimeLabel_2.setText(refreshDate + " " + refreshTime)
        self.modelLabel_2.setText(str(self.connection.device().value("model")))
        self.batteryLabel_2.setText(self.tr("%1% of 100%").arg(self.connection.device().value("battery")))
        self.batteryBar_2.setValue(battery)
        self.signalLabel_2.setText(signalDbm)
        self.signalBar_2.setValue(signalBars)

        self.refreshTimeLabel.setText(refreshDate + " " + refreshTime)
        self.modelLabel.setText(str(self.connection.device().value("model")))
        self.batteryLabel.setText(self.tr("%1% of 100%").arg(self.connection.device().value("battery")))
        self.batteryBar.setValue(battery)
        self.signalLabel.setText(signalDbm)
        self.signalBar.setValue(signalBars)
        self.profileLabel.setText(self.connection.device().value("active_profile"))
        self.btAddressLabel.setText(self.connection.device().bluetoothAddress())
        self.displayLabel.setText(self.tr("%1 pixels").arg(self.connection.device().value("display") ))

        self.drivespaceBox.clear()

        for type,  value in self.connection.device().values():
            if type <> "free_drivespace":
                continue
            drive,  free = value.split(":")
            free = self.helper.pretty_filesize(free)
            self.drivespaceBox.addItem(QString("%1: %2").arg(drive,  free))

        self.imeiLabel.setText(str(self.connection.device().value("imei")))
        self.freeRamLabel.setText(freeRam)
        self.totalRamLabel.setText(totalRam)
        self.romLabel.setText(totalRom)
        self.swLabel.setText(self.connection.device().value("program_version"))
        self.programLabel.setText(self.connection.device().value("pys60_version"))
        self.osLabel.setText(self.connection.device().value("s60_version")) # TODO: append to modelLabel

        self.detailStack.setCurrentWidget(self.extendedWidget)

    def showContacts(self,  search=""):
        if self.fillTypeBox:
            self.typeBox.addItem(self.tr("Name"),  QVariant("s60remote-name"))
            self.typeBox.addItem(self.tr("All fields"),  QVariant("s60remote-all"))
            self.typeBox.insertSeparator(2)

        search = self.searchLine.searchText()
        if not search:
            search = self.searchLine_2.searchText()
        search = unicode(search).lower()
        self.contactsTree.clear()
        self.contactsList.clear()

        searchField = self.typeBox.itemData(self.typeBox.currentIndex()).toString()
        for contact in self.database.contacts(True):
            if self.fillTypeBox:
                for field,  value in contact.values():
                    if field.isPicture():
                        continue
                    if self.typeBox.findData(QVariant(field.type())) == -1:
                        self.typeBox.addItem(field.toString()[:-1],  QVariant(field.type()))

            if search:
                # Search for name
                if searchField == "s60remote-name":
                    if search not in contact.name().lower():
                        continue
                # Search in all field
                elif searchField == "s60remote-all":
                    found = False
                    for type in contact.types():
                        if type == "thumbnail_image":
                            continue
                        for value in contact.value(type):
                            if search in value.lower():
                                found = True
                    if not found:
                        continue
                # Search in one specific field
                else:
                    found = False
                    for value in contact.value(searchField):
                        if search in value.lower():
                            found = True
                    if not found:
                        continue

            item = widget.SortedListWidgetItem.SortedListWidgetItem(self.contactsList)
            item.setData(Roles.ContactRole,  QVariant(contact))
            item.setText(contact.name())
            if "thumbnail_image" in contact and self.settings.setting("contacts/displayIcon"):
                try:
                    data = base64.decodestring(contact.value("thumbnail_image")[0])
                except:
                    pass
                image = QImage().fromData(data)
                icon = QIcon(QPixmap().fromImage(image))
                item.setIcon(icon)
                self.contactsList.setIconSize( QSize(image.size().width()/2,  image.size().height()/2) )
            if "mobile_number" in contact:
                if self.settings.setting("contacts/hideCellnumber"):
                        item = widget.SortedTreeWidgetItem.SortedTreeWidgetItem(self.contactsTree)
                        item.setData(0, Roles.ContactRole,  QVariant(contact))
                        item.setText(0, contact.name())
                        item.setIcon(0,  self.contactIsRecipientIcon) if self.contactIsRecipient(contact) else item.setIcon(0,  self.emptyIcon)
                else:
                    for number in contact.value("mobile_number"):
                        item = widget.SortedTreeWidgetItem.SortedTreeWidgetItem(self.contactsTree)
                        item.setData(0, Roles.ContactRole,  QVariant(contact))
                        item.setText(0, contact.name())
                        item.setText(1,  number)
                        item.setIcon(0,  self.contactIsRecipientIcon) if self.contactIsRecipient(contact) else item.setIcon(0,  self.emptyIcon)

        if self.contactsList.currentRow() == -1 and self.contactsList.count() > 0:
            self.contactsList.setCurrentRow(0)

        self.contactsTree.setColumnHidden(1,  self.settings.setting("contacts/hideCellnumber"))
        self.contactsTree.sortByColumn(0,  Qt.AscendingOrder)
        self.contactsTree.resizeColumnToContents(0)
        self.contactsTree.resizeColumnToContents(1)

        if self.fillTypeBox:
            self.fillTypeBox = False

    def updateContact(self,  contact):
        #TODO: Only update the changed contact...
        self.showContacts()

        item = self.contactsList.item(0)

        for row in range(self.contactsList.count()):
            data = self.contactsList.item(row).data(Roles.ContactRole).toPyObject()
            if data == contact:
                item = self.contactsList.item(row)
                break

        self.contactsList.setCurrentItem(item,  QItemSelectionModel.ClearAndSelect)

    def showContact(self,  contact,  previousContact):
        try:
            contact = contact.data(Roles.ContactRole).toPyObject()
        except:
            return
        self.contactBrowser.clear()
        self.nameLabel.setText("""<span style=" font-size:16pt; font-weight:600;">""" + unicode(contact.name()) + """</span>""")
        if "thumbnail_image" in contact:
            data = base64.decodestring(contact.value("thumbnail_image")[0])
            image = QImage().fromData(data)
            pixmap = QPixmap().fromImage(image)
            self.pictureLabel.setPixmap(pixmap)
        else:
            self.pictureLabel.setPixmap(QPixmap())

        for field,  value in contact.values():
            if field.isPicture():
                continue
            if field.isDate():
                value = QDate.fromString(value,  "yyyyMMdd").toString(Qt.DefaultLocaleLongDate)
            self.contactBrowser.insertHtml("<b>" + field.toString(printLocation=True) + " </b> " + value + "<br />")

    def connected(self):
        self.refreshTimer.start()

        self.connectionClosedByUser = False

        self.connectionDate = QDate.currentDate().toString("dd.MM.yyyy")
        self.connectionTime = QTime().currentTime().toString("hh:mm:ss")
        self.connectionTimeLabel.setText(self.connectionDate + " " + self.connectionTime)
        self.connectionTimeLabel_2.setText(self.connectionDate + " " + self.connectionTime)

        self.disconnectButton.setEnabled(True)
        self.refreshButton.setEnabled(True)

        self.statusLabel.setText(self.tr("Connected to <b>%1</b>").arg(self.connection.device().name()))
        self.connectionStack.setCurrentWidget(self.informationWidget)

        self.checkEditContactButton()
        self.checkSendButton()

    def contactClicked(self,  item,  column):
        contact = item.data(0,  Roles.ContactRole).toPyObject()
        phone = item.text(1) if not self.settings.setting("contacts/hideCellnumber") else None
        if phone:
            contact.addInternalValue("phone",  phone)
        
        if self.contactIsRecipient(contact):
            self.takeContact(contact,  phone)
            item.setIcon(0,  self.emptyIcon)
        else:
            self.insertContact(contact,  phone)
            item.setIcon(0,  self.contactIsRecipientIcon)
        
        self.checkSendButton()
    
    def contactIsRecipient(self,  contact):
        to = self.toLine.text()
        
        if not to:
            return False
        
        hide = self.settings.setting("contacts/hideCellnumber")
        for recipient in unicode(to).split(";"):
            recipient = recipient.strip()
            if hide:
                if recipient == contact.name():
                    return True
            else:
                if recipient == contact.name() + " (" + contact.internalValue("phone") + ")":
                    return True
        return False
    
    def insertContact(self,  contact,  phone):
        name = contact.name()

        if phone:
            name += " (" + phone + ")"

        curName = unicode(self.toLine.text())

        if (len(curName) == 0):
           name = unicode(name)
           self.toLine.setText(name)
        else:
           name = curName + u"; " + unicode(name)
           self.toLine.setText(name)

    def takeContact(self,  contact,  phone):
        to = unicode(self.toLine.text())
        
        name = contact.name()
        if phone:
            name += " (" + phone + ")"
        
        toList = to.split(";")
        toList = [entry.strip() for entry in toList]
        toList.remove(name)
        to = "; ".join(toList)
        
        self.toLine.setText(to)

    def textChanged(self):
        len = int(self.messageText.toPlainText().length())
        chars,  messages = self.helper.countMessages(len)
	if len >= 512:
		bigsms = '***'
	else:	bigsms = ''
	self.charLabel.setText(self.tr("%1 chars left; %n message(s); total chars: %2%3",  "",  messages).arg(chars).arg(len).arg(bigsms))

        self.checkSendButton()

    def recipientChanged(self,  recipients):
        # This is only called if the to line is changed by the user (and NOT programmatically)
        toList = recipients.split(";")
        toList = [unicode(entry).strip() for entry in toList]
        
        hideCell = self.settings.setting("contacts/hideCellnumber")
        
        for itemPos in xrange(self.contactsTree.topLevelItemCount()):
            item = self.contactsTree.topLevelItem(itemPos)
            contact = item.data(0,  Roles.ContactRole).toPyObject()
            if (hideCell and contact.name() in toList) \
                or (not hideCell and contact.name() + " (" + item.text(1) + ")" in toList):
            
                item.setIcon(0,  self.contactIsRecipientIcon)
            else:
                item.setIcon(0,  self.emptyIcon)
        
        self.checkSendButton()

    def sendMessage(self):
        to = unicode(self.toLine.text())
        msg = unicode(self.messageText.toPlainText())

        to = to.split(";")
        for name in to:
            contact = None
            name = name.strip()

            # Only a phone number, sth. like 06641234567 or +436641234567
            if re.match(r"^[+]{0,1}\d*$", name) != None:
                contact = Contact(name=name)
                contact.addInternalValue("phone",  name)

            # Name and phone number, sth. like foo for (06641234567)
            elif re.match(r".*\([+]{0,1}\d{3,15}\)$", name) != None:
                search = re.search(r"(.*)\s\((.*)\)$", name)
                name = search.groups()[0]
                phone = search.groups()[1]

                contact = Contact(name=name)
                contact.addInternalValue("phone",  phone)

            #  Only a name, sth. like foo
            else:
                for recipient in self.database.contacts(True):
                    if unicode(recipient.name()) == name:
                        contact = copy.deepcopy(recipient)
                        if len(recipient.value("mobile_number")) > 1:
                            self.log.info(QString("Contact %1 has more then one mobile number.").arg(name))
                            number = self.askMobileNumber(contact)
                            if number != None:
                                contact.addInternalValue("phone",  number)
                            else:
                                continue
                        else:
                            contact.addInternalValue("phone",  recipient.value("mobile_number")[0])

                if not contact:
                    # foo must be in the contact list
                    dlg = QDialog(self)
                    dialog = ui.ui_mobileNumberNotFound.Ui_MobileNumberNotFoundDialog()
                    dialog.setupUi(dlg)
                    self.main.setupButtonBox(dialog.buttonBox)
                    dlg.exec_()

                    continue

            if not "phone" in contact.internalValues():
                continue

            self.log.info(QString("Sending message to contact %1").arg(unicode(contact)))

            message = Message()
            message.setType(MessageType.Outgoing)
            message.setDevice(self.connection.device())
            message.setContact(contact)
            message.setDateTime(QDateTime.currentDateTime())
            message.setMessage(msg)
            self.connection.sendMessage(message)

            self.toLine.clear()
            self.messageText.clear()
            self.messageText.setFocus()

        for itemPos in xrange(self.contactsTree.topLevelItemCount()):
            item = self.contactsTree.topLevelItem(itemPos)
            item.setIcon(0,  self.emptyIcon)

    def askMobileNumber(self,  contact):
        dlg = QDialog(self)
        dialog = ui.ui_mobileNumberSelect.Ui_MobileNumberSelectDialog()
        dialog.setupUi(dlg)
        self.main.setupButtonBox(dialog.buttonBox)
        dialog.contactLabel.setText(self.tr("Please choose the telephone number for contact <i>%1</i>:").arg(contact.name()))
        for number in contact.value("mobile_number"):
            dialog.mobileBox.addItem(number)

        if not dlg.exec_():
            return None

        return str(dialog.mobileBox.currentText())

    def showCustomContextMenu(self, pos):
        index = self.contactsTree.indexAt(pos)

        if not index.isValid():
            return

        item = self.contactsTree.itemAt(pos)

        menu = QMenu(self)
        # Contact as QVariant: There is no need to convert it to a PyObject,
        # because  it is only used to pass it to the actions
        contact = item.data(0,  Roles.ContactRole)

        startChat = QAction(self)
        startChat.setText(self.tr("Start &chat"))
        startChat.setIcon(QIcon(":/message-chat"))
        startChat.setProperty("type",  QVariant("chat"))
        startChat.setProperty("contact",  contact)

        menu.addAction(startChat)

        if self.settings.setting("messages/saveAllMessages"):
            showHistory = QAction(self)
            showHistory.setText(self.tr("View &history"))
            showHistory.setIcon(QIcon(":/message-history"))
            showHistory.setProperty("type",  QVariant("history"))
            showHistory.setProperty("contact",  contact)

            menu.addAction(showHistory)

        showStatistics = QAction(self)
        showStatistics.setText(self.tr("View &statistics"))
        showStatistics.setIcon(QIcon(":/view-statistics"))
        showStatistics.setProperty("type",  QVariant("statistics"))
        showStatistics.setProperty("contact",  contact)

        menu.addAction(showStatistics)

        menu.popup(QCursor.pos())

        self.connect(menu,  SIGNAL("triggered(QAction *)"),  self.customContextMenuTriggered)

    def customContextMenuTriggered(self,  action):
        type = str(action.property("type").toString())
        contact = action.property("contact").toPyObject()
        if type == "chat":
            self.openChat(contact)
        elif type == "history":
            historyBrowser = window.history.History(self, self.main,  contact)
        elif type == "statistics":
            statisticsDialog = window.statistics.Statistics(self,  self.main,  contact)

    def showContactListContextMenu(self,  pos):
        menu = QMenu(self)

        if self.connection.connected():
            index = self.contactsList.indexAt(pos)

            if not index.isValid():
                return

            item = self.contactsList.itemAt(pos)

            # Contact as QVariant: There is no need to convert it to a PyObject,
            # because  it is only used to pass it to the actions
            contact = item.data(Roles.ContactRole)

            editAction = QAction(self)
            editAction.setText(self.tr("&Edit contact"))
            editAction.setIcon(QIcon(":/user-properties"))
            editAction.setProperty("type",  QVariant("edit"))
            editAction.setProperty("contact",  contact)

            menu.addAction(editAction)

            removeAction = QAction(self)
            removeAction.setText(self.tr("&Remove contact"))
            removeAction.setIcon(QIcon(":/list-remove-user"))
            removeAction.setProperty("type",  QVariant("remove"))
            removeAction.setProperty("contact",  contact)

            menu.addAction(removeAction)

            self.connect(menu,  SIGNAL("triggered(QAction *)"),  self.contactListContextMenuTriggered)

        else:
            notConnectedAction = QAction(self)
            notConnectedAction.setText(self.tr("You aren't connected to the mobile phone."))
            notConnectedAction.setIcon(QIcon(":/dialog-close"))
            notConnectedAction.setEnabled(False)
            menu.addAction(notConnectedAction)

        menu.popup(QCursor.pos())

    def contactListContextMenuTriggered(self,  action):
        type = str(action.property("type").toString())
        contact = action.property("contact").toPyObject()
        if type == "edit":
            dlg = window.contacts_edit.ContactsEdit(self,  self.main,  contact)
        elif type == "remove":
            ret = QMessageBox.question(None,
                self.tr("Delete contact"),
                self.tr("Do you really want to remove contact \"%1\"?").arg(contact.name()),
                QMessageBox.StandardButtons(\
                    QMessageBox.No | \
                    QMessageBox.Yes))
            if ret == QMessageBox.Yes:
                self.connection.contactRemove(contact)
                self.database.contactRemove(contact.idOnPhone())
                self.showContacts()

    def refreshSysinfo(self):
        if not self.connection.connected():
            return

        self.connection.refreshSysinfo()

    def newMessages(self):
        if not self.newMessagesComplete:
            time = QTime().currentTime().toString()
            self.statusBar().showMessage(self.tr("[%1] Fetching new messages...").arg(time))

    def newMessagesFinished(self,  num):
        if not self.newMessagesComplete:
            time = QTime().currentTime().toString()
            if num > 0:
                self.statusBar().showMessage(self.tr("[%1] %n new message(s) got saved.",  "",  num).arg(time),  5000)
            else:
                self.statusBar().showMessage(self.tr("[%1] There are no new messages.").arg(time),  5000)
            self.newMessagesComplete = True

    def messageStateChanged(self,  message):
        queue = self.connection.pendingMessages()

        anz = len(queue)
        time = QTime().currentTime().toString()
        if anz >= 1:
            self.statusBar().showMessage(self.tr("[%1] %n message(s) in queue",  "",  anz).arg(time))
        elif anz == 0 and self.queueMessages > 0:
            self.statusBar().showMessage(self.tr("[%1] All messages were sent").arg(time),  5000)

        self.queueMessages = anz

    def closeConnection(self):
        self.connectionClosedByUser = True

        self.connection.closeConnection()
        self.fileWidget.closeConnection()

    def connectionClosed(self):
        self.refreshTimer.stop()

        self.statusLabel.setText(self.tr("No active connection!"))
        self.devicesBox.setEnabled(True)
        self.connectButton.setEnabled(True)
        self.establishConnectionStack.setCurrentWidget(self.emptyWidget)
        self.connectionStack.setCurrentWidget(self.connectionWidget)

        self.disconnectButton.setEnabled(False)
        self.refreshButton.setEnabled(False)
        self.connectBar.setValue(0)

        self.updateDevices()
        self.checkEditContactButton()
        self.checkSendButton()
        if not self.connectionClosedByUser:
            self.log.debug(QString("Automatic connection establishment: connection closed by error, restarting timer..."))
            self.loadAutomaticConnection()
        else:
            self.log.debug(QString("Automatic connection establishment: connection closed by user, timer is not started"))

    def automaticConnectionTimerFired(self):
        self.log.debug(QString("Timer for automatic connection establishment fired.. scanning for devices"))
        self.deviceScanner.start()

    def automaticConnectionScanStarted(self):
        self.log.debug(QString("Automatic connection establishment: Device scan started"))
        movie = QMovie(":/loading-2",  "",  self)
        movie.setScaledSize(QSize(16, 16))
        self.scanningMovie.setMovie(movie)
        self.scanningMovie.setToolTip(self.tr("There is an active device scan for the automatic connection establishment"))
        self.scanningMovie.movie().start()

    def automaticConnectionFoundDevice(self,  address,  name,  deviceClass):
        for device in self.database.devices():
            if device.bluetoothAddress() == address:
                self.log.info(QString("Automatic connection establishment: Matching device found, connecting..."))
                self.deviceScanner.stop()
                self.connectionAttemptByUser = False
                self.__connectToDevice(device)

    def automaticConnectionScanFinished(self):
        self.log.debug(QString("Automatic connection establishment: Device scan finished"))
        if self.scanningMovie.movie():
            self.scanningMovie.movie().stop()
        self.scanningMovie.setMovie(QMovie())
        self.scanningMovie.setToolTip("")

    @pyqtSignature("")
    def checkEditContactButton(self):
        if self.connection.connected() and self.contactsList.selectedItems():
            self.contactAddButton.setEnabled(True)
            self.contactsImportButton.setEnabled(True)
            self.contactEditButton.setEnabled(True)
        else:
            self.contactAddButton.setEnabled(False)
            self.contactsImportButton.setEnabled(False)
            self.contactEditButton.setEnabled(False)

    def checkSendButton(self):
        if self.toLine.text() and self.messageText.toPlainText() and self.connection.connected():
            self.sendButton.setEnabled(True)
        else:
            self.sendButton.setEnabled(False)

    def openChat(self,  contact):
        if contact:
            # Close all popup windows of the contact
            for popup in self.main.popups:
                try:
                    button = popup.buttons.buttons()[0] # Chat button
                    popupContact = button.property("contact").toPyObject()
                    if contact == popupContact:
                        popup.close()
                except:
                    pass

            #myChat = window.chat.Chat(None, self.main,  contact)
            self.main.chatManager.openChat(contact)

    def favoriteClicked(self,  action):
        type = action.property("type").toString()

        if type == "contact":
            contact = action.data().toPyObject()
            self.openChat(contact)
        elif type == "configureFavorites":
            self.showFavoriteDialog()

    def editContact(self):
        try:
            contact = self.contactsList.currentItem()
            contact = contact.data(Roles.ContactRole).toPyObject()
        except:
            contact = None

        dlg = window.contacts_edit.ContactsEdit(self,  self.main,  contact)

    def reinstallService(self):
        self.closeConnection()

        dlg = QDialog(self)
        dialog = ui.ui_connection_update_version.Ui_ConnectionUpdateVersionDialog()
        dialog.setupUi(dlg)

        if lib.obex_wrapper.FOUND_OBEX:
            dialog.obexStack.setCurrentWidget(dialog.obexFoundWidget)
            self.log.info(QString("OBEX support was found, trying to send installation file to device"))
        else:
            dialog.obexStack.setCurrentWidget(dialog.obexNotFoundWidget)
            self.log.info(QString("OBEX support was not found"))
            if LINUX:
                dialog.operatingSystemStack.setCurrentWidget(dialog.linuxWidget)
            else:
                dialog.operatingSystemStack.setCurrentWidget(dialog.windowsWidget)

        self.connect(dialog.sendApplicationButton,  SIGNAL("clicked()"),  lambda : self.sendApplicationFile(dialog.py20Box.isChecked()))
        self.connect(dialog.sendPythonButton,  SIGNAL("clicked()"),  lambda : self.sendPythonFile(dialog.py20Box.isChecked()))
        self.connect(dialog.openFolderButton,  SIGNAL("clicked()"),  self.helper.openFolder)

        dlg.exec_()

    def sendApplicationFile(self,  usePy20):
        if usePy20:
            self.helper.sendFile(self,  self.devicesBox.currentDevice(), self.main.applicationSis_Py20)
        else:
            self.helper.sendFile(self,  self.devicesBox.currentDevice(), self.main.applicationSis_Py14)

    def sendPythonFile(self,  usePy20):
        if usePy20:
            self.helper.sendFile(self, self.devicesBox.currentDevice(), self.main.pythonSis_Py20)
        else:
            self.helper.sendFile(self,  self.devicesBox.currentDevice(), self.main.pythonSis_Py14)

    def connectionFailed(self,  errno,  errmsg):
        self.connectionClosedByUser = False

        if not self.connectionAttemptByUser:
           self.statusBar().showMessage(self.tr("Connection to device failed: %1 - %2").arg(errno).arg(errmsg), 6000)
           return

        dlg = QDialog(self)
        dialog = ui.ui_connection_failed.Ui_ConnectionFailedDialog()
        dialog.setupUi(dlg)

        dialog.errnoLabel.setText("<b>" + str(errno) + "</b>")
        dialog.errmsgLabel.setText("<b>" + errmsg + "</b>")

        self.main.setupButtonBox(dialog.buttonBox)
        self.connect(dialog.reinstallButton,  SIGNAL("clicked()"),  self.reinstallService)

        self.connect(dialog.buttonBox.button(QDialogButtonBox.Retry),  SIGNAL("clicked()"),  self.connectToDevice)
        self.connect(dialog.buttonBox.button(QDialogButtonBox.Cancel),  SIGNAL("clicked()"),  self.closeConnection)

        dlg.exec_()

    def connectionVersionMismatch(self,  deviceVersion,  pcVersion):
        dlg = QDialog(self)
        dialog = ui.ui_connection_version_mismatch.Ui_ConnectionVersionMismatchDialog()
        dialog.setupUi(dlg)

        dialog.mobileVersionLabel.setText("<b>" + str(deviceVersion) + "</b>")
        dialog.pcVersionLabel.setText("<b>" + str(pcVersion) + "</b>")

        self.main.setupButtonBox(dialog.buttonBox)
        self.connect(dialog.updateButton,  SIGNAL("clicked()"),  self.reinstallService)

        self.connect(dialog.buttonBox.button(QDialogButtonBox.Cancel),  SIGNAL("clicked()"),  self.closeConnection)

        dlg.exec_()

    def updateCheckError(self,  errorMessage):
        self.statusBar().showMessage(self.tr("Update check failed: %1").arg(errorMessage),  5000)

    def updateCheckNewVersion(self,  version,  message):
        text = self.tr("The update to <b>%1</b> of Series60-Remote is available at <b>%2</b>. Would you like to get it?").arg(version, self.settings.setting("updateCheck/website").toString())
        if message:
            text += '<br /><br />' + self.tr("Update notes: %1").arg(message)

        button = QMessageBox.information(self,  self.tr("New version detected"), text,  QMessageBox.Yes | QMessageBox.No | QMessageBox.Ignore,  QMessageBox.Yes)
        if button == QMessageBox.Yes:
            QDesktopServices.openUrl(self.settings.setting("updateCheck/website"))
        elif button == QMessageBox.Ignore:
            self.settings.setSetting("updateCheck/interval",  0)

    def openDonateWebsite(self):
        QDesktopServices.openUrl(QUrl("http://sourceforge.net/donate/index.php?group_id=204429"))

    def addContact(self):
        dlg = window.contacts_edit.ContactsEdit(self,  self.main)

    def importContacts(self,  format):
        dlg = window.contacts_import.ContactsImport(self,  self.main,  format)

    def showFavoriteDialog(self):
        dlg = window.favorites.Favorites(self,  self.main)

    def showAboutDialog(self):
        dlg = window.about.About(self,  self.main)

    def showSettings(self):
        dlg = window.settings.Settings(self,  self.main)

    def showExportDialog(self):
        dlg = window.export.Export(self,  self.main)

    def showHistory(self):
        dlg = window.history.History(self,  self.main)

    def showStatistics(self):
        dlg = window.statistics.Statistics(self,  self.main)

    def showMessageQueue(self):
        dlg = window.message_queue.MessageQueue(self,  self.main)

    def showImportMessages(self):
        dlg = window.import_messages.ImportMessages(self,  self.main)

    def showLog(self):
        self.main.logWindow.show()

    def quit(self):
        self.main.app.closeAllWindows()
        self.main.app.quit()

    def closeEvent(self,  event):
        self.settings.beginGroup("windows")
        self.settings.beginGroup("main")
        self.settings.setSetting("size",  self.size())
        self.settings.setSetting("position",  self.pos())
        self.settings.setSetting("messagesSplitter",  self.messagesSplitter.saveState())
        self.settings.setSetting("contactsSplitter",  self.contactsSplitter.saveState())

        close = self.settings.setting("windows/main/minimizeOnClose")
        if close == 0:
            message = QMessageBox.question(None, self.tr("Quit"),
                self.tr("Should the application stay in the system tray?"),
                QMessageBox.StandardButtons( QMessageBox.No | QMessageBox.Yes), QMessageBox.Yes)

            if message == QMessageBox.Yes:
                self.settings.setSetting("minimizeOnClose",  1)
            else:
                self.settings.setSetting("minimizeOnClose",  2)

        self.settings.endGroup()
        self.settings.endGroup()

        close = self.settings.setting("windows/main/minimizeOnClose")
        if close == 1:
            self.hide()
        else:
            for popup in self.main.popups:
                popup.close()

            if hasattr(self.main,  "trayicon"):
                self.main.trayicon.hide()
            if self.connection.connected():
                self.connection.closeConnection()
            if self.fileWidget.connected():
                self.fileWidget.closeConnection()
            self.settings.sync()
            self.database.close()
            self.hide()
            self.main.app.quit()
