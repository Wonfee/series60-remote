# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import os
import sys
import math
from PyQt4.QtCore import *
from devices.status_numbers import *
from lib.classes import *
import lib.helper

USE_PYBLUEZ = False
USE_LIGHTBLUE = False

try:
   # PyBluez module for Linux and Windows
   import bluetooth
   USE_PYBLUEZ = True
except ImportError:
   # Lightblue for Mac OS X
   import lightblue
   import socket
   USE_LIGHTBLUE = True

class BluetoothError(Exception): pass
class InvalidAddressError(BluetoothError): pass
class InvalidProtocolVersion(BluetoothError): pass
class NotConnectedError(BluetoothError): pass
class NotFoundError(BluetoothError): pass

class Connection(QObject):
    def __init__(self,  parent):
        """Plugin for connections to series60 mobile phones over bluetooth"""
        super(Connection,  self).__init__(parent)
        self.__helper = lib.helper.Helper(self,  None)

        self.PLUGIN_NAME = "series60"
        self.PLUGIN_VERSION = 0.1
        self.PLUGIN_DEVICES = "Series60"

    def useThisPlugin(self,  database,  saveAllMessages=False,  logger=None):
        """Use the plugin"""
        # Create logger
        if logger == None:
            import logging
            import sys
            handler = logging.StreamHandler(sys.stdout)
            format = logging.Formatter("%(levelname)-8s - %(message)s",
                            "%d.%m.%Y %H:%M:%S")
            handler.setFormatter(format)
            self.__log = logging.getLogger()
            self.__log.addHandler(handler)
            self.__log.setLevel(logging.ERROR)
        else:
            self.__log = logger

        self.__database = database

        self.__saveAllMessages = saveAllMessages

        self.__connected = False
        self.__scan = ScanDevices(self,  True)
        self.__listenThread = None
        self.__connectionStates = 4

    def __str__(self):
        return "\"Connection with series60\""

    def scanner(self):
        """Return an instance of a device scanner"""
        return ScanDevices(self)

    def scan(self):
        """Scan for devices"""
        self.__scan.start()

    def scanStop(self):
        self.__scan.stop()

    def connected(self):
        """Return connection state as Boolean"""
        return self.__connected

    def isValidBluetoothAddress(self,  address):
        if USE_PYBLUEZ:
           return bluetooth.is_valid_address(address)
        elif USE_LIGHTBLUE:
           return lightblue._lightbluecommon._isbtaddr(address)

    def connectToDevice(self,  device):
        """Connect to device"""
        if not self.isValidBluetoothAddress(device.bluetoothAddress()):
            raise InvalidAddressError,  str(device.bluetoothAddress()) + " is no valid address"

        self.__listenThread = Listen(self)
        self.__connected = False
        self.__connectionEstablishment = True
        self.__device = device
        self.__contacts = dict()
        self.__calendarEntries = dict()
        self.__contactHashes = dict()
        self.__addedContacts = list()
        self.__changedContacts = list()
        self.__deletedContacts = list()
        self.__setRead = list()
        self.__waitForContactEndReply = False
        self.__newMessagesNumber = 0
        self.__firstRequest = True
        self.__partialMessage = ""
        self.__messageInQueue = False
        self.__currentMessage = None
        self.__messagesSent = list()
        self.__messagesPending = list()
        self.__contactAddQueue = list()
        self.__calendarAddQueue = list()

        if USE_PYBLUEZ:
            self.connect(self.__listenThread,  SIGNAL("finished()"),  self._lostConnection)
        else:
            self.connect(self.__listenThread,  SIGNAL("lostConnection"),  self._lostConnection)
        self.connect(self.__listenThread,  SIGNAL("dataAvailable"),  self.__parseData)

        self.__listenThread.start()

    def __parseData(self,  header,  message):
        self.__log.debug(QString("Received data: Header: %1 - Message: %2").arg(header).arg(message.replace(NUM_SEPERATOR,  " - ")))

        if header != NUM_PARTIAL_MESSAGE and self.__partialMessage:
            message = self.__partialMessage + message
            self.__partialMessage = ""

        if header == NUM_PARTIAL_MESSAGE:
            self.__partialMessage += message

        elif header == NUM_CONNECTED:
            if not float(message) == PROTOCOL_VERSION:
                self.emit(SIGNAL("connectionVersionMismatchError"),  float(message),  PROTOCOL_VERSION)
                #raise InvalidProtocolVersion,  str(message) + " protocol version on device, but " + str(PROTOCOL_VERSION)  + " needed!"
                return

            self.emit(SIGNAL("connectionStateChanged"),  1)
            self.__send(NUM_HELLO_REQUEST)

        elif header == NUM_HELLO_REPLY:
            self.emit(SIGNAL("connectionStateChanged"),  2)
            self.emit(SIGNAL("connectionEstablished"))

            if self.__connectionEstablishment:
                self.refreshSysinfo()

        elif header == NUM_SYSINFO_REPLY_START:
            self.__device.clear()

        elif header == NUM_SYSINFO_REPLY_LINE:
            type = message.split(NUM_SEPERATOR)[0]
            value = message.split(NUM_SEPERATOR)[1]

            self.__log.debug(QString("Systeminfo - Type: %1 - Value: %2").arg(type,  value))

            if type == "model":
                value = self.__helper.getModel(value)

            self.__device.addValue(type,  value)

        elif header == NUM_SYSINFO_REPLY_END:
            if self.__database.deviceCheckValues(self.__device):
                for type,  value in self.__database.devices(bluetoothAddress=self.__device.bluetoothAddress()).next().values():
                    self.__device.addValue(type,  value)
            else:
                self.__database.deviceAddDetails(self.__device)

            self.emit(SIGNAL("sysinfoCompleted"))
            self.emit(SIGNAL("connectionStateChanged"),  3)

            if self.__connectionEstablishment:
                if self.__database.contactCount() > 0:
                    self.__send(NUM_CONTACTS_REQUEST_HASH_ALL)
                    self.__waitForContactEndReply = False
                else:
                    self.__log.info("No contactes saved, requesting all...")
                    self.__send(NUM_CONTACTS_REQUEST_CONTACTS_ALL)
                    self.__waitForContactEndReply = True

        elif header == NUM_CONTACTS_REPLY_HASH_ALL:
            mobileHash = message
            pcHash = self.__database.contactHash()

            self.__log.info(QString("Contact hash from device is %1 and pc hash is %2").arg(mobileHash).arg(pcHash))
            if mobileHash != pcHash:
                self.__log.info("Checksum of contacts aren't equal, requesting hash of each contact...")
                self.__send(NUM_CONTACTS_REQUEST_HASH_SINGLE)
            else:
                self.__log.info("Checksum of contacts on device and pc are equal")
                self.emit(SIGNAL("contactsCompleted"))
                self.emit(SIGNAL("connectionStateChanged"),  4)

                # The contacts are updated, let's get the calendar entries
                self.__requestCalendar()

        elif header == NUM_CONTACTS_REPLY_HASH_SINGLE_START:
            self.__contactHashes = dict()

        elif header == NUM_CONTACTS_REPLY_HASH_SINGLE_LINE:
            id = int(message.split(NUM_SEPERATOR)[0])
            hash = message.split(NUM_SEPERATOR)[1]
            self.__contactHashes[id] = hash

        elif header == NUM_CONTACTS_REPLY_HASH_SINGLE_END:
            self.__checkContactHashes()
            self.__contacts = dict()

        elif header == NUM_CONTACTS_REPLY_CONTACT_START:
            id = int(message.split(NUM_SEPERATOR)[0])
            name = message.split(NUM_SEPERATOR)[1]
            self.__contact = Contact(id=0,  idOnPhone=id,  name=name)

        elif header == NUM_CONTACTS_REPLY_CONTACT_LINE:
            id = int(message.split(NUM_SEPERATOR)[0])
            type = message.split(NUM_SEPERATOR)[1]
            location = message.split(NUM_SEPERATOR)[2]
            value = message.split(NUM_SEPERATOR)[3]
            self.__contact.addValue(ContactField(type,  location),  value)

        elif header == NUM_CONTACTS_REPLY_CONTACT_END:
            id = self.__contact.idOnPhone()
            assert id == int(message.split(NUM_SEPERATOR)[0]),  "ID mismatch"
            if id in self.__addedContacts:
                self.__addedContacts.remove(id)
                self.__database.contactAdd(self.__contact)
            elif self.__waitForContactEndReply:
                self.__database.contactAdd(self.__contact)
            elif id in self.__changedContacts:
                self.__changedContacts.remove(id)
                self.__database.contactChange(self.__contact)

            if not (self.__addedContacts  or self.__changedContacts or self.__waitForContactEndReply):
                self.emit(SIGNAL("contactsCompleted"))
                self.emit(SIGNAL("connectionStateChanged"),  4)
                self.__requestCalendar()

        elif header == NUM_CONTACTS_REPLY_CONTACTS_ALL_END:
            self.emit(SIGNAL("contactsCompleted"))
            self.emit(SIGNAL("connectionStateChanged"),  4)
            self.__requestCalendar()

        elif header == NUM_CALENDAR_REPLY_HASH_ALL:
            mobileHash = message
            pcHash = self.__database.calendarHash()

            self.__log.info(QString("Calendar hash from device is %1 and pc hash is %2").arg(mobileHash).arg(pcHash))

            if mobileHash != pcHash:
                self.__log.info("Checksum of calendar entries aren't equal, requesting all entries...")
                self.__send(NUM_CALENDAR_REQUEST_ENTRIES_ALL)
            else:
                self.__log.info("Checksum of calendar entries on device and pc are equal")
                self.emit(SIGNAL("calendarCompleted"))

                # We updated the contact and calendar database, so the connection is completed ;)
                self.__connectionCompleted()

        elif header == NUM_CALENDAR_REPLY_ENTRIES_START:
            self.__calendarEntries = dict()

        elif header == NUM_CALENDAR_REPLY_ENTRY:
            entry = CalendarEntry()
            entry.setDevice(self.device())

            ms = message.split(NUM_SEPERATOR)
            entry.setIdOnPhone(int(ms[0]))
            entry.setType(str(ms[1]))
            entry.setContent(ms[2])
            entry.setLocation(ms[3])
            if ms[4]:
                # Time could be an empty string, would result in:
                # ValueError: empty string for float()
                entry.setStartTime(float(ms[4]))
            if ms[5]:
                entry.setEndTime(float(ms[5]))
            if ms[6]:
                entry.setLastModified(float(ms[6]))
            entry.setReplication(str(ms[7]))
            if ms[8]:
                entry.setAlarm(float(ms[8]))
            entry.setPriority(int(ms[9]))
            entry.setRepeatType(ms[10])
            entry.setRepeatDays(ms[11])
            if ms[12]:
                entry.setRepeatExceptions(ms[12])
            if ms[13]:
                entry.setRepeatStart(float(ms[13]))
            if ms[14]:
                entry.setRepeatEnd(float(ms[14]))
            if ms[15]:
                # Repeat interval could be an empty string, this prevents:
                # ValueError: invalid literal for int() with base 10: ''
                entry.setRepeatInterval(int(ms[15]))
            if entry.type() == "todo":
                entry.setCrossedOut(bool(int(ms[16])))
                if ms[17]:
                    entry.setCrossOutTime(float(ms[17]))

            self.__calendarEntries[entry.idOnPhone()]= entry

        elif header == NUM_CALENDAR_REPLY_ENTRIES_END:
            self.__checkCalendar()

        elif header == NUM_MESSAGE_REPLY_LINE:
            msg = Message()

            type = message.split(NUM_SEPERATOR)[0]
            if type == "inbox":
                msg.setType(MessageType.Incoming)
            elif type == "sent":
                msg.setType(MessageType.Outgoing)

            msg.setDevice(self.__device)
            msg.setIdOnPhone(int(message.split(NUM_SEPERATOR)[1]))
            msg.setDateTime(float(message.split(NUM_SEPERATOR)[2]))
            msg.setContact(Contact(name=message.split(NUM_SEPERATOR)[3]))
            msg.setMessage(message.split(NUM_SEPERATOR)[4])
            msg.setId(self.__database.messageUpdate(msg))

            self.emit(SIGNAL("messageLine"),  msg)
            self.__newMessagesNumber += 1

            if msg.id() in self.__setRead:
                self.__log.info(QString("We got message with id %1 - set it read.").arg(msg.id()))
                self.setRead(msg)
                self.__setRead.remove(msg.id())

        elif header == NUM_MESSAGE_REPLY_END:
            self.emit(SIGNAL("messagesRequestComplete"),  self.__newMessagesNumber)
            if self.__firstRequest:
                self.__send(NUM_MESSAGE_REQUEST_UNREAD)
                self.__firstRequest = False

        elif header == NUM_MESSAGE_REPLY_UNREAD:
            if message:
                for id in message.split(NUM_SEPERATOR):
                    if id:
                        id = int(id)
                        msg = self.__database.messages(messageIdOnPhone=id).next()
                        self.emit(SIGNAL("messageUnread"),  msg)

        elif header == NUM_MESSAGE_SEND_REPLY_OK:
            self.__currentMessage.addState(MessageState.SendOk,  message)
            self.__prepareNextMessage()
            self.__newMessages()

        elif header == NUM_MESSAGE_SEND_REPLY_STATUS:
            self.__currentMessage.addState(MessageState.Unknown,  message)

        elif header == NUM_MESSAGE_SEND_REPLY_FAILURE:
            self.__currentMessage.addState(MessageState.SendFailed,  message)
            self.__prepareNextMessage()

        elif header == NUM_MESSAGE_SEND_REPLY_RETRY:
            if "wait" not in self.__currentMessage.contact().internalValues():
                self.__currentMessage.contact().addInternalValue("wait",  True)
            self.__currentMessage.addState(MessageState.SendFailed,  "retry sending (%s) " % message)
            self.__prepareNextMessage(retry=True)

        elif header == NUM_MESSAGE_NEW:
            msg = Message()
            msg.setType(MessageType.Incoming)
            msg.setDevice(self.__device)
            msg.setContact(self.__database.contactByName(message.split(NUM_SEPERATOR)[2]))
            msg.setDateTime(float(message.split(NUM_SEPERATOR)[1]))
            msg.setMessage(message.split(NUM_SEPERATOR)[3])

            # The message id shouldn't be saved in the database, because there could be other messages with a higher id
            msg.setIdOnPhone(0)
            msg.setId(self.__database.messageAdd(msg))

            msg.setIdOnPhone(int(message.split(NUM_SEPERATOR)[0]))
            self.__newMessages()

            self.emit(SIGNAL("messageNew"),  msg)

        elif header == NUM_CONTACTS_ADD_REPLY_ID:
            id = int(message)
            contact = self.__contactAddQueue.pop()
            contact.setIdOnPhone(id)
            contact.setId(self.__database.contactAdd(contact))
            self.contactChange(contact,  list(),  contact.values())

            self.emit(SIGNAL("contactsUpdated"))

        elif header == NUM_CALENDAR_ENTRY_ADD_REPLY:
            id = int(message.split(NUM_SEPERATOR)[0])
            time = int(message.split(NUM_SEPERATOR)[1])
            time = QDateTime.fromTime_t(time)

            entry = self.__calendarAddQueue.pop(0)
            entry.setIdOnPhone(id)
            entry.setLastModified(time)
            entry.setId(self.__database.calendarEntryAdd(entry))

            self.emit(SIGNAL("calendarUpdated"))

        elif header == NUM_CALENDAR_ENTRY_CHANGE_REPLY_TIME:
            # This updates the last modified time of an entry in the database (usually after an update of the entry on the PC)
            id = int(message.split(NUM_SEPERATOR)[0])
            time = int(message.split(NUM_SEPERATOR)[1])
            time = QDateTime.fromTime_t(time)

            self.__database.calendarEntryUpdateLastModifiedTime(id,  time)

            self.emit(SIGNAL("calendarUpdated"))

        elif header == NUM_DEBUG:
            self.__log.error(QString("Debug data: %1").arg(message))

        else:
            self.__log.error(QString("Unknown header: %1 - Data: %2").arg(header).arg(message))

    def __requestCalendar(self):
        self.__log.debug("The contacts are updated, let's get the calendar entries...")
        if self.__database.calendarEntriesCount() > 0:
            self.__send(NUM_CALENDAR_REQUEST_HASH_ALL)
        else:
            self.__log.info("No entries saved, requesting all...")
            self.__send(NUM_CALENDAR_REQUEST_ENTRIES_ALL)

    def __connectionCompleted(self):
        if self.__device and self.__device.name():
            self.__connected = True
            self.emit(SIGNAL("connectionStateChanged"),  5)
            self.__connectionEstablishment = False
            self.emit(SIGNAL("connectionCompleted"))
            self.__newMessages()

    def __checkHashes(self,  pcHashes,  mobileHashes):
        addedEntries = list()
        changedEntries = list()
        deletedEntries = list()
        for id,  hash in mobileHashes.iteritems():
            if not id in pcHashes:
                addedEntries.append(id)
            elif not hash == pcHashes[id]:
                changedEntries.append(id)

        for id,  hash in pcHashes.iteritems():
            if not id in mobileHashes:
                deletedEntries.append(id)

        return addedEntries,  changedEntries,  deletedEntries

    def __checkContactHashes(self):
        pcHashes = self.__database.contactHashSingle()
        self.__addedContacts,  self.__changedContacts,  self.__deletedContacts = self.__checkHashes(pcHashes,  self.__contactHashes)

        self.__log.info(QString("Requesting added contacts with id %1").arg(str(self.__addedContacts)))
        self.__requestContacts(self.__addedContacts)

        self.__log.info(QString("Requesting changed contacts with id %1").arg(str(self.__changedContacts)))
        self.__requestContacts(self.__changedContacts)

        self.__log.info(QString("Removing deleted contacts with id %1").arg(str(self.__deletedContacts)))
        self.__database.contactsRemove(self.__deletedContacts)

        if (self.__deletedContacts and not (self.__addedContacts or self.__changedContacts)):
            self.emit(SIGNAL("contactsCompleted"))
            self.emit(SIGNAL("connectionStateChanged"),  4)
            self.__requestCalendar()

#    def __checkCalendarHashes(self):
#        pcHashes = self.__database.calendarHashSingle()
#        self.__addedCalendarEntries,  self.__changedCalendarEntries,  self.__deletedCalendarEntries = self.__checkHashes(pcHashes,  self.__calendarHashes)
#
#        self.__log.info(QString("Requesting added calendar entries with id %1").arg(str(self.__addedCalendarEntries)))
#        self.__requestCalendarEntries(self.__addedCalendarEntries)
#
#        self.__log.info(QString("Requesting changed calendar entries with id %1").arg(str(self.__changedCalendarEntries)))
#        self.__requestCalendarEntries(self.__changedCalendarEntries)
#
#        self.__log.info(QString("Removing deleted calendar entries with id %1").arg(str(self.__deletedCalendarEntries)))
#        self.__database.calendarEntriesRemove(self.__deletedCalendarEntries)
#
#        if (self.__deletedCalendarEntries and not (self.__addedCalendarEntries or self.__changedCalendarEntries)):
#            self.emit(SIGNAL("calendarCompleted"))
#            self.connectionCompleted()

    def __checkCalendar(self):
        pcIds = self.__database.calendarIds()
        mobileIds = self.__calendarEntries.keys()

        for id in mobileIds:
            if id in pcIds:
                self.__database.calendarEntryUpdate(self.__calendarEntries[id])
            else:
                self.__database.calendarEntryAdd(self.__calendarEntries[id])

        for id in pcIds:
            if id not in mobileIds:
                self.__database.calendarEntryRemoveByIdOnPhone(id)

        self.emit(SIGNAL("calendarCompleted"))
        self.__connectionCompleted()

        # Cleanup
        self.__calendarEntries = dict()

    def __requestContacts(self,  list):
        for id in list:
            self.__send(NUM_CONTACTS_REQUEST_CONTACT,  id)

    def __requestCalendarEntries(self,  list):
        for id in list:
            self.__send(NUM_CALENDAR_REQUEST_ENTRY,  id)

    def __send(self,  header,  *message):
        new_message = ""

        if len(message) == 1:
            new_message = unicode(message[0])
        else:
            for part in message:
                new_message += unicode(part) + str(NUM_SEPERATOR)

        length = 600
        if len(new_message) > length:
            parts = int(math.ceil(len(new_message) / float(length)))
            sentParts = 0
            for i in range(parts):
                part = new_message[sentParts*length:sentParts*length+length]
                if sentParts == parts-1:
                    self.__send(header,  part)
                else:
                    self.__send(NUM_PARTIAL_MESSAGE,  part)
                sentParts += 1
            return

        self.__log.debug(QString("Sent data: Header: %1 - Message: %2").arg(header).arg(new_message.replace(NUM_SEPERATOR,  " - ")))

        self.emit(SIGNAL("requestSend(QString)"),  QString(str(header) + str(NUM_END_HEADER) + unicode(new_message).encode("utf8") + '\n'))

    def __sendMessage(self,  message):
        self.__messageInQueue = True
        self.__currentMessage = message

        name = message.contact().name()
        phone = message.contact().internalValue("phone")
        msg = message.messageForPhone()
        assert name and phone and message,  "invalid message"

        self.__send(NUM_MESSAGE_SEND_REQUEST,  name,  phone,  msg)

        message.addState(MessageState.Sending,  "Message transfered to device.")
        #self.emit(SIGNAL("messageStateChanged"))

    def __prepareNextMessage(self,  retry=False):
        if self.__messageInQueue:
            self.__messagesPending.remove(self.__currentMessage)

            if retry:
                self.__messagesPending.append(self.__currentMessage)
            else:
                self.__messagesSent.append(self.__currentMessage)

            self.emit(SIGNAL("messageSent"),  self.__currentMessage)
        self.__messageInQueue = False

        if self.__messagesPending:
            message = self.__messagesPending[0]
            if "wait" in message.contact().internalValues():
                sleep = QTimer(self)
                sleep.setInterval(10000)
                sleep.setSingleShot(True)
                sleep.start()
                self.connect(sleep,  SIGNAL("timeout()"),  lambda: self.__sendMessage(message))
            else:
                self.__sendMessage(message)

    def _lostConnection(self):
        if self.__device and self.__device.name():
            if self.__connected:
                self.emit(SIGNAL("connectionClosed"),  self.__device.name())
            else:
                self.emit(SIGNAL("connectionAborted"),  self.__device.name())

        self.__connected = False
        self.__newMessagesCompleted = False
        self.__contacts = dict()
        self.__device = Device()

    def __newMessages(self):
        if self.__saveAllMessages:
            self.__newMessagesNumber = 0
            last = self.__database.messageLastIdOnPhone(self.__device)
            self.emit(SIGNAL("messagesRequest"))
            self.__send(NUM_MESSAGE_REQUEST,  last)

    def sendMessage(self,  message):
        """Send a text message to the contact message.contact()"""
        message.setId(self.__database.messageAdd(message))
        message.addState(MessageState.Created, "Message created on computer.")
        self.__messagesPending.append(message)
        self.emit(SIGNAL("messageQueued"),  message)

        if not self.__messageInQueue:
            self.__prepareNextMessage()

    def setRead(self,  message,  state=True,  send=True):
        """Set a message as read or unread"""
        if send:
            if message.idOnPhone() == 0 and message.id() > 0:
                self.__log.info(QString("We don't know the message id on the phone, but we'll wait until we get it. PC id is %1").arg(message.id()))
                if message.id() not in self.__setRead:
                    self.__setRead.append(message.id())
            else:
                self.__send(NUM_SET_READ,  message.idOnPhone(),  state)
        if state:
            self.emit(SIGNAL("messageRead"),  message)

    def contactAdd(self,  contact):
        self.__contactAddQueue.append(contact)
        self.__send(NUM_CONTACTS_ADD)

    def contactRemove(self,  contact):
        self.__send(NUM_CONTACTS_DELETE,  contact.idOnPhone())

    def contactChange(self,  contact,  remove,  add):
        assert contact.idOnPhone() != 0
        for field,  value in remove:
            value = value.replace(u'\n', u'\u2029') # LINE FEED (\u000a) replaced by PARAGRAPH SEPARATOR (\u2029)
            self.__send(NUM_CONTACTS_CHANGE_REMOVEFIELD,  contact.idOnPhone(),  field.type(),  field.location(),  value)
        for field,  value in add:
            value = value.replace(u'\n', u'\u2029') # LINE FEED (\u000a) replaced by PARAGRAPH SEPARATOR (\u2029)
            self.__send(NUM_CONTACTS_CHANGE_ADDFIELD,  contact.idOnPhone(),  field.type(),  field.location(),  value)

    def __calendarEntryAddChangeOptions(self,  entry):
        content = entry.content()
        location = entry.location()
        start = entry.realStartTime().toTime_t() if entry.realStartTime().isValid() else str()
        end = entry.realEndTime().toTime_t() if entry.realEndTime().isValid() else str()
        replication = entry.replication()
        alarm = entry.alarm().toTime_t() if entry.alarm().isValid() else str()
        priority = entry.priority()
        repeat_type = entry.repeatType()
        repeat_days = entry.repeatDays()
        repeat_exceptions = entry.repeatExceptions()
        repeat_start = entry.repeatStart().toTime_t() if entry.repeatStart().isValid() else str()
        repeat_end = entry.repeatEnd().toTime_t() if entry.repeatEnd().isValid() else str()
        repeat_interval = entry.repeatInterval()
        return content,  location,  start,  end,  replication,  alarm,  priority,  repeat_type, repeat_days, \
                    repeat_exceptions,  repeat_start,  repeat_end,  repeat_interval

    def calendarEntryAdd(self,  entry):
        self.__calendarAddQueue.append(entry)
        self.__send(NUM_CALENDAR_ENTRY_ADD,  entry.type(),  *self.__calendarEntryAddChangeOptions(entry))

    def calendarEntryChange(self,  entry):
        id = entry.idOnPhone()

        self.__send(NUM_CALENDAR_ENTRY_CHANGE,  id,  *self.__calendarEntryAddChangeOptions(entry))

        self.__database.calendarEntryUpdate(entry)

    def calendarEntryRemove(self,  entry):
        self.__send(NUM_CALENDAR_ENTRY_DELETE,  entry.idOnPhone())
        self.__database.calendarEntryRemove(entry)

    def refreshSysinfo(self):
        """Refresh system informations"""
        self.__send(NUM_SYSINFO_REQUEST,  int(not self.__database.deviceCheckValues(self.__device)))

    def device(self):
        """Return connected device"""
        return self.__device

    def pendingMessages(self):
        """Return a list with all pending messages"""
        if not self.__connected:
            raise NotConnectedError,  "No active connection!"

        return self.__messagesPending

    def sentMessages(self):
        """Return a list with all sent messages"""
        if not self.__connected:
            raise NotConnectedError,  "No active connection!"

        return self.__messagesSent

    def closeConnection(self,  sendQuit=True):
        """Close connection"""
        self.__log.info(QString("Trying to close the connection"))

        if sendQuit:
            self.__send(NUM_QUIT)

        self._lostConnection()

if USE_PYBLUEZ:
    if sys.platform == "win32":
        if bluetooth.have_widcomm:
            # When we use the wicomm bluetooth stack use the asynchronous device scan
            # This is our only possibility to get the device class
            class ScanDevices(QThread):
                def __init__(self,  parent,  emitFromParent=False):
                    super(ScanDevices,  self).__init__(parent)
                    self.__parent = parent
                    if emitFromParent:
                        self.__emitter = self.__parent
                    else:
                        self.__emitter = self

                def stop(self):
                    # TODO: Kill this thread?
                    self.__emitter.emit(SIGNAL("scanCompleted"))

                def run(self):
                    try:
                        self.__emitter.emit(SIGNAL("scanStarted"))

                        inquirer = bluetooth.WCInquirer()
                        addresses = []

                        inquirer.start_inquiry()
                        while inquirer.inquiry_in_progress:
                            inquirer.read_msg()

                            if inquirer.recently_discovered:
                                bdaddr, devclass, bdname, connected = inquirer.recently_discovered[-1]
                                if bdaddr not in addresses:
                                    addresses.append(bdaddr)
                                    # convert string to int
                                    if len(devclass) == 3:
                                        hex = "%02X%02X%02X" % (ord(devclass[0]), ord(devclass[1]), ord(devclass[2]))
                                        devclass = int(hex, 16)
                                    else:
                                        devclass = 0
                                    self.__emitter.emit(SIGNAL("foundDevice"),  bdaddr,  bdname,  devclass)

                        self.__emitter.emit(SIGNAL("scanCompleted"))
                    except Exception,  msg:
                        self.__emitter.emit(SIGNAL("scanFailed"), msg[0])

        else:
            # Asynchronous mode isn't implemented
            # There is no way to get the bluetooth class currently
            # We would need to pass the flag LUP_RETURN_TYPE (Retrieves the type as lpServiceClassId)
            # to _msbt.c
            class ScanDevices(QThread):
                def __init__(self,  parent,  emitFromParent=False):
                    super(ScanDevices,  self).__init__(parent)
                    self.__parent = parent
                    if emitFromParent:
                        self.__emitter = self.__parent
                    else:
                        self.__emitter = self

                def stop(self):
                    # TODO: Kill this thread?
                    pass

                def run(self):
                    try:
                        self.__emitter.emit(SIGNAL("scanStarted"))

                        devices = bluetooth.discover_devices( lookup_names=True,  lookup_class=True)
                        for address,  name,  bdclass in devices:
                            self.__parent.emit(SIGNAL("foundDevice"),  address,  name,  bdclass)
                        self.__emitter.emit(SIGNAL("scanCompleted"))
                    except IOError,  msg:
                        self.__emitter.emit(SIGNAL("scanFailed"), msg[0])

    else:
        class ScanDevices(QThread,  bluetooth.DeviceDiscoverer):
            def __init__(self,  parent,  emitFromParent=False):
                QThread.__init__(self,  parent)
                bluetooth.DeviceDiscoverer.__init__(self)
                self.__parent = parent

                self.__running = False

                if emitFromParent:
                    self.__emitter = self.__parent
                else:
                    self.__emitter = self

            def run(self):
                self.__running = True

                try:
                   self.find_devices(lookup_names = True, flush_cache = True)
                   self.process_inquiry()
                except (bluetooth.btcommon.BluetoothError, bluetooth._bluetooth.error), msg:
                   self.__emitter.emit(SIGNAL("scanFailed"), msg[0])
                   self.__running = False

            def stop(self):
                if self.__running:
                    self.cancel_inquiry()
                    self.__emitter.emit(SIGNAL("scanCompleted"))

            def pre_inquiry(self):
                self.__emitter.emit(SIGNAL("scanStarted"))

            def device_discovered(self, address, deviceClass, name) :
                self.__emitter.emit(SIGNAL("foundDevice"),  address,  name,  deviceClass)

            def inquiry_complete(self):
                self.__emitter.emit(SIGNAL("scanCompleted"))
                self.__running = False

    class Listen(QThread):
        def __init__(self,  parent):
            super(Listen,  self).__init__(parent)
            self.parent = parent

        def run(self):
            self.connect(self.parent,  SIGNAL("requestSend(QString)"),  self.send)

            try:
                self.sock = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
                self.sock.connect((self.parent.device().bluetoothAddress(),  self.parent.device().port()))
            except Exception, msg:
                if os.name == "nt":
                    errno = msg.errno
                    errmsg = msg.message
                else:
                    errno, errmsg = eval(msg[0]) # msg.message has been deprecated as of Python 2.6
                errmsg = unicode(errmsg,  "utf8")
                self.parent.emit(SIGNAL("connectionFailed"),  errno,  errmsg)
                return

            data = u""
            while True:
                try:
                    recv = unicode(self.sock.recv(1000),  "utf8")
                    if recv:
                        data += recv

                        # Last part is either empty or the beginning of the next data segment
                        data = data.split(NUM_END_TEXT)
                        for part in data[:-1]:
                            # Extract header and message
                            header = int(part.split(NUM_END_HEADER)[0])
                            message = unicode(part.split(NUM_END_HEADER)[1])

                            # Quit the thread -> finished() signal emitted
                            if header  == NUM_QUIT:
                                return
                            self.emit(SIGNAL("dataAvailable"),  header,  message)

                        data = data[-1]
                    else:
                        # Got an empty string -> connection is closed
                        self.disconnect(self.parent,  SIGNAL("requestSend(QString)"),  self.send)
                        return
                except Exception:
                    self.disconnect(self.parent,  SIGNAL("requestSend(QString)"),  self.send)
                    return

        def send(self,  data):
            data = str(data.toAscii())
            try:
                self.sock.send(data)
            except Exception:
                self.disconnect(self.parent,  SIGNAL("requestSend(QString)"),  self.send)
                #self.emit(SIGNAL("lostConnection"))
                self.exit(1)

elif USE_LIGHTBLUE:
    class ScanDevices(object):
        def __init__(self,  parent,  emitFromParent=False):
            self.__parent = parent
            self.__scan = lightblue._lightblue._AsyncDeviceInquiry.alloc().init()
            self.__scan._setupdatenames(True)
            self.__scan.cb_started= self.scanStarted
            self.__scan.cb_completed = self.scanCompleted
            self.__scan.cb_founddevice = self.scanFoundDevice

            if emitFromParent:
                self.__emitter = self.__parent
            else:
                self.__emitter = self

        def start(self):
            ret = self.__scan.start()
            if ret != lightblue._macutil.kIOReturnSuccess:
                self.__emitter.emit(SIGNAL("scanFailed"), str(ret))

        def stop(self):
            self.__scan.stop()

        def scanStarted(self):
            self.__emitter.emit(SIGNAL("scanStarted"))

        def scanFoundDevice(self,  device):
            name = device.getName()
            if not name:
                name = lightblue.finddevicename(device.getAddressString())
            addr = device.getAddressString().replace("-", ":").encode('ascii').upper()
            deviceClass = device.getClassOfDevice()
            self.__emitter.emit(SIGNAL("foundDevice"),  addr,  name, deviceClass)

        def scanCompleted(self,  err, aborted):
            if err:
                self.__emitter.emit(SIGNAL("scanFailed"), str(err))
            else:
                self.__emitter.emit(SIGNAL("scanCompleted"))

    class Listen(QObject):
        def __init__(self,  parent):
            super(Listen,  self).__init__(parent)
            self.parent = parent

            self.connect(self.parent,  SIGNAL("requestSend(QString)"),  self.send)

        def start(self):
            self.__data = u""

            self.sock = lightblue.socket( lightblue.RFCOMM )
            self.sock.setblocking(False)
            try:
                self.sock.connect((self.parent.device().bluetoothAddress(),  self.parent.device().port()))
                self.startTimer(60)
            except socket.error,  msg:
                self.parent.emit(SIGNAL("connectionFailed"),  msg[0],  msg[1])

        def timerEvent(self,  event):
            try:
                recv = unicode(self.sock.recv(10000),  "utf8")
            except socket.error,  msg:
                if msg[0] != 35: # 35 = Resource temporarily unavailable (due to non-blocking mode)
                    self.parent._lostConnection()
                return
            except Exception:
                self.parent._lostConnection()
                return

            self.__data += recv
            # Last part is either empty or the beginning of the next data segment
            self.__data = self.__data.split(NUM_END_TEXT)
            for part in self.__data[:-1]:
                # Extract header and message
                header = int(part.split(NUM_END_HEADER)[0])
                message = unicode(part.split(NUM_END_HEADER)[1])

                # Quit the thread -> finished() signal emitted
                if header  == NUM_QUIT:
                    self.parent._lostConnection()
                    return
                self.emit(SIGNAL("dataAvailable"),  header,  message)

            self.__data = self.__data[-1]

        def send(self,  data):
            data = str(data.toAscii())
            try:
                self.sock.send(data)
            except:
                self.emit(SIGNAL("lostConnection"))
