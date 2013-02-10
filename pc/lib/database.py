# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import hashlib
import re
import copy
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from lib.classes import *

THUMBNAIL = "thumbnail_image"

# For hash functions
CONTACT_SEP = chr(0x1F) # Unit Separator
ENTRY_SEP = chr(0x1F) # Unit Separator
FIELD_SEP = chr(0x1E) # Record Separator
INFO_SEP = chr(0x1D) # Group Separator

class Database(QObject):
    def __init__(self,  parent,  main):
        super(Database,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.settings = main.settings

        self.database = None
        self.__connected = False
        self.__type = ""
        self.__lastError = ""

        self.deviceFieldsInDatabase = ("display",  "imei",  "model",  "s60_version",  "total_ram",  "total_rom")

    def __str__(self):
        return "\"Database\""

    def openDatabase(self,  type,  data):
        self.close()

        type = type.lower()
        if type == "sqlite":
            self.__type = "sqlite"
            return self.__openSqliteDatabase(data["filename"])
        elif type == "mysql":
            self.__type = "mysql"
            return self.__openMysqlDatabase(data["host"], data["port"], data["user"],  data["pass"],  data["database"])
        else:
            return self.__setError(QString("Unknown database type"))

    def __openSqliteDatabase(self,  file):
        self.log.info(QString("Creating new SQLite-Database in file %1").arg(file))

        self.database = QSqlDatabase.addDatabase("QSQLITE")
        self.database.setDatabaseName(file)

        return self.__checkDatabase()

    def __openMysqlDatabase(self,  host,  port,  user,  pw,  database):
        self.log.info(QString("Creating MySQL-Database %1 on host %2 (Port: %3) as user %4").arg(database,  host, str(port),  user))

        self.database = QSqlDatabase.addDatabase("QMYSQL")
        self.database.setHostName(host)
        self.database.setPort(port)
        self.database.setUserName(user)
        self.database.setPassword(pw)
        self.database.setDatabaseName(database)

        return self.__checkDatabase()

    def __open(self):
        if self.database.isOpen():
            return True

        if not self.database.open():
            return self.__setError(QString("Couldn't connect to database!"))

        self.__connected = True
        return True

    def __checkDatabase(self):
        if not self.__open():
            return False

        if self.database.tables().isEmpty():
            return self.__createTables()
        else:
            return self.__checkTables()

    def __checkTables(self):
        tables = self.database.tables()

        if not tables.contains("messages"):
            return self.__setError(QString("Table 'messages' not found"))
        if not tables.contains("contacts"):
            return self.__setError(QString("Table 'contacts' not found"))
        if not tables.contains("contact_details"):
            return self.__setError(QString("Table 'contact_details' not found"))
        if not tables.contains("devices"):
            return self.__setError(QString("Table 'devices' not found"))
        if not tables.contains("config"):
            # Table config was added in version 0.3, so update to this version if the table is not found
            self.log.warning(QString("Table 'config' not found, trying to update database"))
            ret = Update(self.database,  self.main).update( (0,  2),  self.main.databaseVersion)
            if not ret[0]:
                self.__setError(ret[1])

        query = self.__queryReturn("SELECT value FROM config WHERE name='version'")
        if query and query.last():
            versionStr = str(query.value(0).toString())
            version = versionStr.split(".")
            gen = ( int(i[0]) for i in version )
            version = tuple(gen)

            if versionStr != self.main.databaseVersionStr:
                self.log.warning(QString("Database version mismatch (%1 != %2), trying to update").arg(versionStr,  self.main.databaseVersionStr))
                ret = Update(self.database,  self.main).update(version,  self.main.databaseVersion)
                if ret[0]:
                    self.log.info(ret[1])
                else:
                    return self.__setError(ret[1])
        else:
            return self.__setError(QString("Database version not found (check data table)!"))

        return True

    def __createTables(self):
        ret = self.__query("""CREATE TABLE contacts (
        contactId INT UNSIGNED NOT NULL PRIMARY KEY,
        contactIdOnPhone INT UNSIGNED,
        name VARCHAR(255),
        thumbnail_image TEXT,
        alias INT UNSIGNED,
        ignoreContact SMALLINT UNSIGNED NOT NULL DEFAULT 0 CHECK(ignoreContact IN (0, 1)),
        favoriteContact SMALLINT UNSIGNED NOT NULL DEFAULT 0 CHECK(favoriteContact IN (0, 1))
        )
        """)

        if not ret:
            return False

        ret = self.__query("""CREATE TABLE contact_details (
        contactId INT UNSIGNED NOT NULL,
        detailOnPhone SMALLINT UNSIGNED NOT NULL DEFAULT 1 CHECK(detailOnPhone IN (0, 1)),
        type VARCHAR(255) NOT NULL,
        value VARCHAR(255) NOT NULL,
        location VARCHAR(255) NOT NULL,
        PRIMARY KEY (contactId, type, location, value),
        FOREIGN KEY (contactId) REFERENCES contacts
        )
        """)

        if not ret:
            return False

        ret = self.__query("""CREATE TABLE devices (
        deviceId INT UNSIGNED PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        deviceClass INT UNSIGNED,
        display  VARCHAR(255),
        imei INT UNSIGNED,
        model VARCHAR(255),
        s60_version VARCHAR(255),
        total_ram INT UNSIGNED,
        total_rom INT UNSIGNED,
        showDevice INT UNSIGNED NOT NULL CHECK(showDevice IN (0, 1))
        )
        """)

        if not ret:
            return False

        ret = self.__query("""CREATE TABLE messages (
        messageId INT UNSIGNED NOT NULL PRIMARY KEY,
        messageIdOnPhone INT,
        device INT UNSIGNED NOT NULL,
        type SMALLINT UNSIGNED NOT NULL CHECK(type IN (1, 2)),
        time DATETIME NOT NULL,
        contact INT UNSIGNED NOT NULL,
        message TEXT NOT NULL,
        FOREIGN KEY (device) REFERENCES devices,
        FOREIGN KEY (contact) REFERENCES contacts
        )
        """)

        if not ret:
            return False

        ret = self.__query("""CREATE TABLE calendar (
        entryId INT UNSIGNED NOT NULL PRIMARY KEY,
        entryIdOnPhone INT,
        device INT UNSIGNED NOT NULL,
        type VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        location TEXT,
        startTime DATETIME,
        endTime DATETIME,
        lastModifiedTime DATETIME,
        replication VARCHAR(255) NOT NULL,
        alarmTime DATETIME,
        priority INT UNSIGNED NOT NULL,
        repeatType VARCHAR(255),
        repeatDays VARCHAR(255),
        repeatExceptions VARCHAR(255),
        repeatStartTime DATETIME,
        repeatEndTime DATETIME,
        repeatInterval INT UNSIGNED,
        crossedOut SMALLINT UNSIGNED NOT NULL DEFAULT 0 CHECK(crossedOut IN (0, 1)),
        crossOutTime DATETIME
        )
        """)

        if not ret:
            return False

        ret = self.__query("""CREATE TABLE config (
        name VARCHAR(255) PRIMARY KEY,
        value VARCHAR(255)
        )
        """)

        if not ret:
            return False

        # Save database version in data table
        query = QSqlQuery()
        query.prepare("""INSERT INTO config (name, value)
        VALUES (:name, :value)""")
        query.bindValue(":name",  QVariant("version"))
        query.bindValue(":value",  QVariant(self.main.databaseVersionStr))

        if not self.__queryExec(query):
            return False

        self.log.info(QString("All tables were successfully created."))

        return True

    def __queryReturn(self,  myQuery):
        self.log.log(9,  QString("Execute query: %1").arg(myQuery))
        query = QSqlQuery()
        query.prepare(myQuery)
        ret = query.exec_()

        if ret:
            return query
        else:
            return self.__setError(QString("Query failed: %1").arg(query.lastError().text()))

    def __queryExec(self,  myQuery):
        ret = myQuery.exec_()
        if self.main.sqlDebug:
            log = str(myQuery.lastQuery())
            for key,  value in myQuery.boundValues().iteritems():
                log = re.sub( str(key) + r"([\s|)|,])", unicode(value.toString()) + r"\1", log, 1)
            self.log.log(9,  QString("Execute query: %1").arg(log))
        return ret

    def __query(self,  myQuery):
        if self.main.sqlDebug:
            self.log.log(9,  QString("Execute query: %1").arg(myQuery))
        query = QSqlQuery()
        ret = query.exec_(myQuery)

        if ret:
            return True
        else:
            return self.__setError(QString("Query failed"))

    def __setError(self,  error):
        self.__lastError = error
        self.log.error(self.error())
        return False

    def __make(self, keyword,   *conditions):
        if type(conditions) == type(str()):
            return keyword +" " + conditions
        else:
            ret = ""
            i = 0
            for condition in conditions:
                if type(condition) == type(list()):
                    for condition_2 in condition:
                        if condition_2:
                            if i != 0:
                                ret += " and "
                            else:
                                ret += keyword + " "
                            ret += condition_2
                            i+=1
                else:
                    if condition:
                        if i != 0:
                            ret += " and "
                        else:
                            ret += keyword + " "
                        ret += condition_2
                        i+=1
            return ret

    def __makeWhere(self,  *conditions):
        return self.__make("WHERE",  *conditions)

    def __makeHaving(self,  *conditions):
        return self.__make("HAVING",  *conditions)

    def __getYear(self):
        if self.__type == "mysql":
            return "EXTRACT(YEAR FROM time)"
        elif self.__type == "sqlite":
            return "strftime('%Y', time)"

    def __getMonth(self):
        if self.__type == "mysql":
            return "EXTRACT(MONTH FROM time)"
        elif self.__type == "sqlite":
            return "strftime('%m', time)"

    def __getDay(self):
        if self.__type == "mysql":
            return "EXTRACT(DAY FROM time)"
        elif self.__type == "sqlite":
            return "strftime('%d', time)"

    def __getWeekday(self):
        if self.__type == "mysql":
            return "WEEKDAY(time)"
        elif self.__type == "sqlite":
            return "strftime('%w', time)"

    def __getHour(self):
        if self.__type == "mysql":
            return "EXTRACT(HOUR FROM time)"
        elif self.__type == "sqlite":
            return "strftime('%H', time)"

    def error(self):
        err = unicode(self.__lastError).strip()
        if not err:
            err = unicode(self.tr("Unknown error"))

        return err

    def contactCount(self,  onPhone=False):
        where = ""
        if onPhone:
            where = "WHERE contactIdOnPhone!=''"
        query = self.__queryReturn("SELECT COUNT(contactId) FROM contacts " + where)

        if not query:
            return 0

        if query.last():
            return query.value(0).toInt()[0]
        else:
            return 0

    def __contactNextContactId(self):
        query = self.__queryReturn("SELECT MAX(contactId) FROM contacts")
        if query.last():
            return query.value(0).toInt()[0] +1
        else:
            return 1

    def __contactDict(self):
        contactDict = dict()

        for contact in self.contacts(True):
            contactDict[contact.idOnPhone()] = list()

            for field,  value in contact.values():
                contactDict[contact.idOnPhone()].append((field.type(),  field.location(),  value))
            contactDict[contact.idOnPhone()].sort()

        return contactDict

    def contactHash(self):
        contacts = self.__contactDict()

        hash = unicode()

        for key in sorted(contacts):
            hash += str(key)
            hash += FIELD_SEP
            for type,  location, value in contacts[key]:
                hash += type + INFO_SEP + location + INFO_SEP + value
                hash += FIELD_SEP
            hash += CONTACT_SEP

        hash = hash.encode("utf8")
        hash = hashlib.md5(hash).hexdigest()
        return hash

    def contactHashSingle(self):
        contacts = self.__contactDict()
        hashes = dict()

        for key in sorted(contacts):
            hash = unicode()
            for type,  location, value in contacts[key]:
                hash += type + INFO_SEP + location + INFO_SEP + value
                hash += FIELD_SEP
            hash = hash.encode("utf8")
            hash = hashlib.md5(hash).hexdigest()
            hashes[key] = hash

        return hashes

    def contactAdd(self,  contact):
        id = self.__contactNextContactId()

        query = QSqlQuery()
        query.prepare("""INSERT INTO contacts (contactId, contactIdOnPhone, name, thumbnail_image, ignoreContact)
        VALUES (:contactId, :contactIdOnPhone, :name, :thumb, :ignore)""")
        query.bindValue(":contactId",  QVariant(id))

        if contact.idOnPhone():
            query.bindValue(":contactIdOnPhone",   QVariant(contact.idOnPhone()))
        else:
            query.bindValue(":contactIdOnPhone",   QVariant(None))

        query.bindValue(":name",   QVariant(contact.name()))

        if THUMBNAIL in contact.types():
            query.bindValue(":thumb",   QVariant(contact.value(THUMBNAIL)[0]))
        else:
            query.bindValue(":thumb",   QVariant(None))

        query.bindValue(":ignore",  QVariant(int(contact.isIgnored())))

        self.__queryExec(query)

        for field,  value in contact:
            if field.isPicture():
                continue

            self.__contactDetailAdd(id,  field,  value)

        return id

    def __contactDetailAdd(self,  contactId,  field,  value):
        query = QSqlQuery()
        query.prepare("""INSERT INTO contact_details (contactId, detailOnPhone, type, location, value)
        VALUES (:contactId, 1, :type, :location, :value)""")
        query.bindValue(":contactId",  QVariant(contactId))
        query.bindValue(":type",  QVariant(field.type()))
        query.bindValue(":location",  QVariant(field.location()))
        query.bindValue(":value",  QVariant(value))
        self.__queryExec(query)

        # TODO: Where should the id come from?!?
        return id

    def contactRemove(self,  contactIdOnPhone):
        id = self.__contactId(contactIdOnPhone)
        self.__query("UPDATE contacts SET thumbnail_image=Null WHERE contactId='" + str(id) + "'")
        self.__query("DELETE FROM contact_details WHERE contactId='" + str(id) + "'")
        self.__query("UPDATE contacts SET contactIdOnPhone=Null WHERE contactId='" + str(id) + "'")

    def contactsRemove(self,  list):
        for contact in list:
            self.contactRemove(contact)

    def __contactId(self,  idOnPhone):
        query = self.__queryReturn("SELECT contactId FROM contacts WHERE contactIdOnPhone='" + str(idOnPhone)  + "'")
        if query.last():
            return query.value(0).toInt()[0]
        else:
            return None

    def __contactIdByName(self,  name):
        query = self.__queryReturn("SELECT contactId FROM contacts WHERE name='" + unicode(name)  + "'")
        if query.last():
            return query.value(0).toInt()[0]
        else:
            return None

    def contactByName(self,  name):
        id = self.__contactIdByName(name)
        if id:
            return self.contacts(contactId=id).next()
        else:
            return Contact(name=name)

    def __contactIdOnPhone(self,  id):
        query = self.__queryReturn("SELECT contactIdOnPhone FROM contacts WHERE contactId='" + str(id)  + "'")
        if query.last():
            return query.value(0).toInt()[0]
        else:
            return None

    def contactChange(self,  contact):
        id = self.__contactId(contact.idOnPhone())
        dbContact = self.contacts(contactId=id).next()

        self.__query("UPDATE contacts SET name='" + contact.name() + "' WHERE contactId='" + str(id) + "'")

        oldValues = set(dbContact.values())
        newValues = set(contact.values())

        # Remove old entries
        old = oldValues.difference(newValues)
        for field,  value in old:
            if field.type() == THUMBNAIL:
                self.__query("UPDATE contacts SET thumbnail_image=Null WHERE contactId='" + str(id) + "'")
            else:
                self.__query("DELETE FROM contact_details WHERE contactId='" + str(id)  + "' and type='" + field.type() +
                "' and location='" + field.location() + "' and value='" + value + "'")

        # Add new entries
        new = newValues.difference(oldValues)
        for field,  value in new:
            if field.type() == THUMBNAIL:
                self.__query("UPDATE contacts SET thumbnail_image='" + contact.value(THUMBNAIL)[0] + "' WHERE contactId='" + str(id) + "'")
            else:
                self.__contactDetailAdd(id,  field,  value)

        return old,  new

    def contacts(self,  onPhone=False,  contactId=None):
        ID,  IDONPHONE,   NAME,  THUMBNAIL_IMAGE,   IGNORE,  FAVORITE  = range(6)
        query = "SELECT contactId, contactIdOnPhone, name, thumbnail_image, ignoreContact, favoriteContact FROM contacts"
        if onPhone or contactId:
            query += " WHERE "
        if onPhone:
            query += "contactIdOnPhone!=''"
        if onPhone and contactId:
            query += " and "
        if contactId <> None:
            query += "contactId='" + str(contactId) + "'"

        query = self.__queryReturn(query)

        while query and query.next():
            contact = Contact()
            contact.setId(int(query.value(ID).toInt()[0]))
            contact.setIdOnPhone(int(query.value(IDONPHONE).toInt()[0]))
            contact.setName(unicode(query.value(NAME).toString()))
            contact.setIgnored(bool(int(query.value(IGNORE).toInt()[0])))
            contact.setFavorite(bool(int(query.value(FAVORITE).toInt()[0])))

            thumb = unicode(query.value(THUMBNAIL_IMAGE).toString())
            if thumb:
                contact.addValue(ContactField(THUMBNAIL,  "none"),   thumb)

            TYPE,  LOCATION,  VALUE = range(3)

            fields = "SELECT type, location, value from contact_details WHERE contactId='" + str(contact.id()) + "'"

            if onPhone:
                fields+= " and detailOnPhone=1"
            fields = self.__queryReturn(fields)
            while fields.next():
                type = str(fields.value(TYPE).toString())
                location = str(fields.value(LOCATION).toString()) or "none"
                value = unicode(fields.value(VALUE).toString())

                contact.addValue(ContactField(type,  location),  value)
            yield contact

    def contactsWithMessages(self):
        ID,  NAME = range(2)
        query = self.__queryReturn("SELECT DISTINCT m.contact, c.name from messages m JOIN contacts c ON m.contact=c.contactId ORDER BY c.name ASC")

        while query.next():
            name = unicode(query.value(NAME).toString())
            id = int(query.value(ID).toInt()[0])

            # Don't get contact details, because it takes to much time...
            yield Contact(id=id,  name=name)

    def contactFavoritesGenerator(self,  count=5,  days=None):
        contact,  messages = range(2)

        where = ""
        if days:
            # MySQL syntax
            if self.__type == "mysql":
                where = "AND DATE_SUB(CURDATE(),INTERVAL " + str(days) + " DAY) <= 'time'"
            # SQLite syntax
            elif self.__type == "sqlite":
                where = "AND date('now','-" + str(days) + " days') <= time"

        query = self.__queryReturn("""SELECT contact, COUNT(*) count FROM messages
                                                        GROUP BY contact
                                                        HAVING contact NOT IN (SELECT contactId FROM contacts WHERE contactIdOnPhone IS NULL)
                                                            AND contact NOT IN (SELECT contactId FROM contacts WHERE favoriteContact=1)
                                                            """ + where + """
                                                        ORDER BY count DESC LIMIT 0,""" + str(count))
        while query and query.next():
            id = int(query.value(contact).toInt()[0])
            yield self.contacts(contactId=id).next()

    def contactFavoritesField(self):
        query = self.__queryReturn("""SELECT contactId FROM contacts
                                                        WHERE favoriteContact=1""")
        while query and query.next():
            id = int(query.value(0).toInt()[0])
            yield self.contacts(contactId=id).next()

    def contactIgnoreUpdate(self,  contact):
        if contact.id():
            self.__query("UPDATE contacts SET ignoreContact=" + str(int(contact.isIgnored())) + " WHERE contactId='" + str(contact.id()) + "'")

    def contactUnignoreAll(self):
        self.__query("UPDATE contacts SET ignoreContact=0")

    def contactFavoriteUpdate(self,  contact):
        if contact.id():
            self.__query("UPDATE contacts SET favoriteContact=" + str(int(contact.isFavorite())) + " WHERE contactId='" + str(contact.id()) + "'")

    def contactUnfavoriteAll(self):
        self.__query("UPDATE contacts SET favoriteContact=0")

    def __calendarNextId(self):
        query = self.__queryReturn("SELECT MAX(entryId) FROM calendar")
        if query and query.last():
            return query.value(0).toInt()[0] +1
        else:
            return 1

    def calendarEntriesCount(self):
        query = self.__queryReturn("SELECT COUNT(entryIdOnPhone) FROM calendar")

        if not query:
            return 0

        if query.last():
            return query.value(0).toInt()[0]
        else:
            return 0

    def calendarEntries(self,  start=None,  end=None,  repeatedEntries=False):
        duration = list()
        repeations = list()

        # TODO: handle repeated entries...
        if start:
            duration.append("endTime >= '" + start.toString(Qt.ISODate) + "'")
            if repeatedEntries:
                repeations.append("(repeatEndTime >= '" + start.toString(Qt.ISODate) + "' OR repeatEndTime IS NULL)")
        if end:
            duration.append("startTime <= '" + end.toString(Qt.ISODate) + "'")
            if repeatedEntries:
                repeations.append("repeatStartTime <= '" + end.toString(Qt.ISODate) + "'")

        where = ""
        if duration or repeations:
            where += " WHERE"
            if duration:
                where += '(' + self.__make("",  duration) + ' )'
            if duration and repeations:
                where += " OR "
            if repeations:
                where += '(' + self.__make("",  repeations) + ' )'

        ID,  IDONPHONE,  DEVICE,  TYPE,  CONTENT,  LOCATION,  STARTTIME,  ENDTIME,  LASTMODIFIEDTIME,  REPLICATION,  ALARMTIME,  PRIORITY, \
        REPEATTYPE,  REPEATDAYS,  REPEATEXCEPTIONS,  REPEATSTARTTIME,  REPEATENDTIME,  REPEATINTERVAL,  CROSSEDOUT,  CROSSOUTTIME = range(20)
        query = """SELECT entryId, entryIdOnPhone, device, type, content, location, startTime, endTime, lastModifiedTime, replication, alarmTime,
                         priority, repeatType, repeatDays, repeatExceptions, repeatStartTime, repeatEndTime, repeatInterval, crossedOut, crossOutTime
                         FROM calendar """ + where + " ORDER BY entryIdOnPhone"
        query = self.__queryReturn(query)

        while query and query.next():
            entry = CalendarEntry()
            entry.setId(int(query.value(ID).toInt()[0]))
            entry.setIdOnPhone(int(query.value(IDONPHONE).toInt()[0]))
            entry.setDevice(self.devices(deviceId=int(query.value(DEVICE).toInt()[0])).next())
            entry.setType(str(query.value(TYPE).toString()))
            entry.setContent(unicode(query.value(CONTENT).toString()))
            entry.setLocation(unicode(query.value(LOCATION).toString()))
            entry.setStartTime(query.value(STARTTIME).toDateTime())
            entry.setEndTime(query.value(ENDTIME).toDateTime())
            entry.setLastModified(query.value(LASTMODIFIEDTIME).toDateTime())
            entry.setReplication(str(query.value(REPLICATION).toString()))
            entry.setAlarm(query.value(ALARMTIME).toDateTime())
            entry.setPriority(int(query.value(PRIORITY).toInt()[0]))
            entry.setRepeatType(str(query.value(REPEATTYPE).toString()))
            entry.setRepeatDays(str(query.value(REPEATDAYS).toString()))
            entry.setRepeatExceptions(str(query.value(REPEATEXCEPTIONS).toString()))
            entry.setRepeatStart(query.value(REPEATSTARTTIME).toDateTime())
            entry.setRepeatEnd(query.value(REPEATENDTIME).toDateTime())
            entry.setRepeatInterval(int(query.value(REPEATINTERVAL).toInt()[0]))
            entry.setCrossedOut(bool(int(query.value(CROSSEDOUT).toInt()[0])))
            entry.setCrossOutTime(query.value(CROSSOUTTIME).toDateTime())

            yield entry

            if entry.repeatType() and repeatedEntries:
                # This is a repeated entry...
                #print "repeated entry:",  repr(entry)
                date = start
                while True:
                    date = entry.next(date)

                    if date > end or date is None:
                        break
                    #print "date is",  date
                    repeatedEntry = copy.deepcopy(entry)
                    repeatedEntry.setRealStartTime(entry.startTime())
                    repeatedEntry.setRealEndTime(entry.endTime())
                    repeatedEntry.setStartTime(date)
                    repeatedEntry.setEndTime(date)
                    yield repeatedEntry
                #print "-----------------------------\n\n"

    def calendarHash(self):
        hash = unicode()

        for entry in self.calendarEntries():
            hash += str(entry.idOnPhone())
            hash += FIELD_SEP

            # Format the entry values....
            hash += entry.type() + FIELD_SEP + entry.content() + FIELD_SEP + entry.location() + FIELD_SEP
            if entry.startTime():
                hash += str(entry.startTime().toTime_t())
            hash += FIELD_SEP

            if entry.endTime():
                hash += str(entry.endTime().toTime_t())
            hash += FIELD_SEP

            hash += str(entry.lastModified().toTime_t()) + FIELD_SEP
            hash += entry.replication() + FIELD_SEP

            if entry.alarm():
                hash += str(entry.alarm().toTime_t())
            hash += FIELD_SEP

            hash += str(entry.priority()) + FIELD_SEP

            hash += entry.repeatType() + FIELD_SEP + entry.repeatDays() + FIELD_SEP + entry.repeatExceptions() + FIELD_SEP
            if entry.repeatStart():
                hash += str(entry.repeatStart().toTime_t())
            hash += FIELD_SEP
            if entry.repeatEnd():
                hash += str(entry.repeatEnd().toTime_t())
            hash += FIELD_SEP
            if entry.repeatInterval():
                hash += str(entry.repeatInterval())
            hash += FIELD_SEP

            if entry.type() == "todo":
                hash += str(int(entry.crossedOut())) + FIELD_SEP

                if entry.crossOutTime():
                    hash += str(entry.crossOutTime().toTime_t())
                hash += FIELD_SEP


            hash += FIELD_SEP
            hash += ENTRY_SEP

        #print "PC:::" + hash.replace(FIELD_SEP,  ";").replace(ENTRY_SEP,  "\n")

        hash = hash.encode("utf8")
        hash = hashlib.md5(hash).hexdigest()
        return hash

    def calendarIds(self):
        ret = list()
        query = self.__queryReturn("SELECT entryIdOnPhone FROM calendar")
        while query and query.next():
            id = int(query.value(0).toInt()[0])
            ret.append(id)
        return ret

    def __calendarEntryBind(self,  entry,  query):
        if entry.id():
            id = entry.id()
        else:
            id = self.__calendarNextId()

        query.bindValue(":entryId",  QVariant(id))
        query.bindValue(":entryIdOnPhone",  QVariant(entry.idOnPhone()))
        query.bindValue(":device",  QVariant(entry.device().id()))
        query.bindValue(":type",  QVariant(entry.type()))
        query.bindValue(":content",  QVariant(entry.content()))
        query.bindValue(":location",  QVariant(entry.location()))
        query.bindValue(":startTime",  QVariant(entry.realStartTime()))
        query.bindValue(":endTime",  QVariant(entry.realEndTime()))
        query.bindValue(":lastModifiedTime",  QVariant(entry.lastModified()))
        query.bindValue(":replication",  QVariant(entry.replication()))
        query.bindValue(":alarmTime",  QVariant(entry.alarm()))
        query.bindValue(":priority",  QVariant(entry.priority()))
        query.bindValue(":repeatType",  QVariant(entry.repeatType()))
        query.bindValue(":repeatDays",  QVariant(entry.repeatDays()))
        query.bindValue(":repeatExceptions",  QVariant(entry.repeatExceptions())) if entry.repeatExceptions() else QVariant()
        query.bindValue(":repeatStartTime",  QVariant(entry.repeatStart()))
        query.bindValue(":repeatEndTime",  QVariant(entry.repeatEnd())) if entry.repeatEnd() and entry.repeatEnd().isValid() else QVariant()
        query.bindValue(":repeatInterval",  QVariant(entry.repeatInterval()))
        query.bindValue(":crossedOut",  QVariant(int(entry.crossedOut())))
        query.bindValue(":crossOutTime",  QVariant(entry.crossOutTime()))

    def calendarEntryAdd(self,  entry):
        query = QSqlQuery()
        query.prepare("""INSERT INTO calendar (entryId, entryIdOnPhone, device, type, content, location, startTime, endTime, lastModifiedTime, replication, alarmTime,
        priority, repeatType, repeatDays, repeatExceptions, repeatStartTime, repeatEndTime, repeatInterval, crossedOut, crossOutTime)
        VALUES (:entryId, :entryIdOnPhone, :device, :type, :content, :location, :startTime, :endTime, :lastModifiedTime, :replication, :alarmTime,
        :priority, :repeatType, :repeatDays, :repeatExceptions, :repeatStartTime, :repeatEndTime, :repeatInterval, :crossedOut, :crossOutTime)""")

        self.__calendarEntryBind(entry,  query)
        return self.__queryExec(query)

    def calendarEntryUpdate(self,  entry):
        query = QSqlQuery()

        if entry.id():
            # This is used when the entry is updated on the PC with the calendar_edit dialog
            where = "WHERE entryId=" + str(entry.id())
        elif entry.idOnPhone():
            # This is needed during the synchronisation
            where = "WHERE entryIdOnPhone=" + str(entry.idOnPhone())

        query.prepare("""UPDATE calendar SET device=:device, type=:type, content=:content, location=:location, startTime=:startTime, endTime=:endTime,
        lastModifiedTime=:lastModifiedTime, replication=:replication, alarmTime=:alarmTime, priority=:priority, repeatType=:repeatType, repeatDays=:repeatDays,
        repeatExceptions=:repeatExceptions, repeatStartTime=:repeatStartTime, repeatEndTime=:repeatEndTime, repeatInterval=:repeatInterval, crossedOut=:crossedOut,
        crossOutTime=:crossOutTime """ + where)

        self.__calendarEntryBind(entry,  query)
        return self.__queryExec(query)

    def calendarEntryUpdateLastModifiedTime(self,  entryIdOnPhone,  time):
        query = QSqlQuery()
        query.prepare("UPDATE calendar SET lastModifiedTime=:lastModifiedTime WHERE entryIdOnPhone=" + str(entryIdOnPhone))
        query.bindValue(":lastModifiedTime",  QVariant(time))
        return self.__queryExec(query)

    def calendarEntryRemove(self,  entry):
        return self.__query("DELETE FROM calendar WHERE entryId='" + str(entry.id()) + "'")

    def calendarEntryRemoveByIdOnPhone(self,  id):
        return self.__query("DELETE FROM calendar WHERE entryIdOnPhone='" + str(id) + "'")

    def calendarEntriesRemove(self,  list):
        for entry in list:
            self.calendarEntryRemove(entry)

    def __deviceNextId(self):
        query = self.__queryReturn("SELECT MAX(deviceId) FROM devices")
        if query and query.last():
            return query.value(0).toInt()[0] +1
        else:
            return 1

    def deviceCount(self,  address=None):
        query = "SELECT COUNT(deviceId) FROM devices"
        if address <> None:
           query += " WHERE address='" + address + "'"
        query = self.__queryReturn(query)
        if query and query.last():
            return query.value(0).toInt()[0]
        else:
            return 0

    def deviceId(self,  address):
        if self.deviceCount(address) > 0:
            query = self.__queryReturn("SELECT deviceId FROM devices WHERE address='" + address + "'")
            query.last()
            return query.value(0).toInt()[0]
        else:
            return None

    def deviceAdd(self,  device,  show=True):
        id = self.deviceId(device.bluetoothAddress())
        if id <> None:
            self.deviceShow(device)
            return id

        id = self.__deviceNextId()

        query = QSqlQuery()
        query.prepare("""INSERT INTO devices (deviceId, name, address, deviceClass, showDevice)
        VALUES (:deviceId, :name, :address, :deviceClass, 1)""")
        query.bindValue(":deviceId",  QVariant(id))
        query.bindValue(":name",  QVariant(device.name()) )
        query.bindValue(":address",  QVariant(str(device.bluetoothAddress())))
        query.bindValue(":deviceClass",  QVariant(device.deviceClass()))
        self.__queryExec(query)

        return id

    def deviceAddDetails(self,  device):
        for type,  value in device.values():
            if type in self.deviceFieldsInDatabase:
                self.__query("UPDATE devices SET " + type + "='" + str(value) + "' WHERE address='" + str(device.bluetoothAddress()) + "'")

    def deviceRemove(self,  device):
        return self.__query("DELETE FROM devices WHERE address='" + str(device.bluetoothAddress())  + "'")

    def deviceHide(self,  device):
        return self.__query("UPDATE devices SET showDevice=0 WHERE address='" + str(device.bluetoothAddress()) + "'")

    def deviceHideAll(self):
        return self.__query("UPDATE devices SET showDevice=0")

    def deviceShow(self,  device):
        if not self.__query("UPDATE devices SET showDevice=1 WHERE address='" + str(device.bluetoothAddress()) + "'"):
            return False

        # TODO! Only needed when upgrading from old database version
        return self.__query("UPDATE devices SET deviceClass='" + str(device.deviceClass()) + "'"
                                        " WHERE address='" + str(device.bluetoothAddress()) + "'")

    def deviceCheckValues(self,  device):
        ID,  NAME,  ADDRESS,  DISPLAY,  IMEI,  MODEL,  S60,  RAM,  ROM = range(9)

        query = """SELECT deviceId, name, address, display, imei, model, s60_version, total_ram, total_rom
        from devices WHERE showDevice=1 and deviceId='""" + str(device.id()) + """'"""

        query = self.__queryReturn(query)
        query.next()
        return (query.value(DISPLAY).toBool() and  query.value(IMEI).toBool() and query.value(MODEL).toBool()
                and query.value(S60).toBool() and query.value(RAM).toBool() and query.value(ROM).toBool())

    def devices(self,  deviceId=None,  bluetoothAddress=None):
        ID,  NAME,  ADDRESS,  DEVICECLASS,  DISPLAY,  IMEI,  MODEL,  S60,  RAM,  ROM = range(10)

        query = """SELECT deviceId, name, address, deviceClass, display, imei, model, s60_version, total_ram, total_rom
        from devices WHERE showDevice=1"""

        if deviceId:
            query += " and deviceId='" + str(deviceId) + "'"
        if bluetoothAddress:
            query += " and address='" + bluetoothAddress + "'"

        query = self.__queryReturn(query)

        while query and query.next():
            device = Device()
            device.setId(int(query.value(ID).toInt()[0]))
            device.setName(unicode(query.value(NAME).toString()))
            device.setBluetoothAddress(str(query.value(ADDRESS).toString()))
            device.setDeviceClass(int(query.value(DEVICECLASS).toInt()[0]))

            if self.deviceCheckValues(device):
                device.addValue("display",  str(query.value(DISPLAY).toString()))
                device.addValue("imei",  int(query.value(IMEI).toInt()[0]))
                device.addValue("model",  str(query.value(MODEL).toString()))
                device.addValue("s60_version",  str(query.value(S60).toString()))
                device.addValue("total_ram",  int(query.value(RAM).toInt()[0]))
                device.addValue("total_rom",  int(query.value(ROM).toInt()[0]))

            yield device

    def messageLastIdOnPhone(self,  device):
        query = self.__queryReturn("SELECT MAX(messageIdOnPhone) FROM messages WHERE device='" + str(device.id()) + "' and messageIdOnPhone!=''")
        if query.last():
            return query.value(0).toInt()[0]
        else:
            return 0

    def __messageNextId(self):
        query = self.__queryReturn("SELECT MAX(messageId) FROM messages")
        if query.last():
            return query.value(0).toInt()[0] +1
        else:
            return 1

    def messageAdd(self,  message):
        if not self.settings.setting("messages/saveAllMessages"):
            return False

        if message.idOnPhone():
            query = self.__queryReturn("SELECT messageId FROM messages WHERE messageIdOnPhone='" + str(message.idOnPhone()) + "'")
            if query.last():
                return query.value(0).toInt()[0]

        id = self.__messageNextId()

        if not message.contact().id():
            conId = self.__contactIdByName(message.contact().name())
            if conId:
                message.contact().setId(conId)
            else:
                message.contact().setId(self.contactAdd(message.contact()))

        query = QSqlQuery()
        query.prepare("""INSERT INTO messages (messageId, messageIdOnPhone, device, type, time, contact, message)
        VALUES (:id, :idOnPhone, :device, :type, :time, :contact, :message)""")
        query.bindValue(":id",  QVariant(id))
        if message.idOnPhone():
            query.bindValue(":idOnPhone",  QVariant(message.idOnPhone()))
        else:
            query.bindValue(":idOnPhone",  QVariant(None))
        query.bindValue(":device",  QVariant(message.device().id()))
        query.bindValue(":type",  QVariant(message.type()))
        query.bindValue(":time",  QVariant(message.dateTime()))
        query.bindValue(":contact",  QVariant(message.contact().id()))
        query.bindValue(":message",  QVariant(message.message()))

        self.__queryExec(query)

        return id

    def messageUpdate(self,  message):
        try:
            phone = message.contact().value("s60remote-phone")[0]
        except:
            line = ""
        else:
            line = " and phone='" + str(self.__contactDetailPhoneId(phone,  True)) + "' "

        try:
            name = message.contact().name()
        except:
            pass
        else:
            line += " and contact='" + str(self.__contactIdByName(name)) + "' "

        ID,  IDONPHONE,  DEVICE,  TYPE,  TIME,  CONTACT,  MESSAGE = range(7)
        query = self.__queryReturn("""SELECT messageId, messageIdOnPhone, device, type, time, contact, message from messages
        WHERE (messageIdOnPhone='' or messageIdOnPhone IS NULL or messageIdOnPhone='""" + str(message.idOnPhone()) + """') and
        device='""" + str(message.device().id()) + """' and type='""" + str(message.type()) + """'
        """ + line  + """ and message='""" + message.message().replace("'",  "''") + """'
        ORDER by messageid DESC LIMIT 1""")

        if query and query.last():
            id = int(query.value(ID).toInt()[0])
            self.__query("UPDATE messages SET messageIdOnPhone='" + str(message.idOnPhone()) + "',time='" + message.dateTime().toString(Qt.ISODate) + "' WHERE messageId='" + str(id) + "'")
            return id
        else:
            return self.messageAdd(message)

    def messagesLast(self,  contact,  num):
        ID,  IDONPHONE,  DEVICE,  TYPE,  TIME,  CONTACT,  MESSAGE = range(7)
        query = self.__queryReturn("SELECT messageId, messageIdOnPhone, device, type, time, contact, message FROM messages WHERE contact='" + str(contact.id()) + "' ORDER by time DESC LIMIT 0," + str(num))

        ret = list()
        while query.next():
            msg = Message()
            msg.setId(int(query.value(ID).toInt()[0]))
            msg.setIdOnPhone(int(query.value(IDONPHONE).toInt()[0]))
            msg.setDevice(self.devices(deviceId=int(query.value(DEVICE).toInt()[0])).next())
            msg.setType(int(query.value(TYPE).toInt()[0]))
            msg.setDateTime(query.value(TIME).toDateTime())
            msg.setContact(self.contacts(contactId=int(query.value(CONTACT).toInt()[0])).next())
            msg.setMessage(unicode(query.value(MESSAGE).toString()))
            ret.insert(0,  msg)

        return ret

    def messageCount(self,  contactFilter=None):
        where = ""
        if contactFilter:
            where = "WHERE contact IN (" + ",".join([str(contact.id()) for contact in contactFilter]) + ")"

        query = self.__queryReturn("SELECT COUNT(messageId) FROM messages " + where)

        if not query:
            return 0

        if query.last():
            return query.value(0).toInt()[0]
        else:
            return 0

    def messages(self,  year=None,  month=None,  day=None,  contact=None,  filter=None,  messageId=None,
                 messageIdOnPhone=None,  order="DESC",  contactFilter=None):
        query = "SELECT messageId, messageIdOnPhone, type, time, contact, message FROM messages "
        conditions = list()

        # SQLite syntax
        if self.__type == "sqlite":
            if month:
                if month < 10:
                    month = "0" + str(month)
            if day:
                if day < 10:
                    day = "0" + str(day)

        if year:
            conditions.append(self.__getYear() + "='" + str(year) + "'")
        if month:
            conditions.append(self.__getMonth() + "='" + str(month) + "'")
        if day:
            conditions.append(self.__getDay() + "='" + str(day) + "'")

        if contact:
            conditions.append("contact='" + str(contact.id()) + "'")
        if filter:
            conditions.append("type=" + str(filter))
        if messageId:
            conditions.append("messageId=" + str(messageId))
        if messageIdOnPhone:
            conditions.append("messageIdOnPhone=" + str(messageIdOnPhone))
        if contactFilter:
            conditions.append("contact IN (" + ",".join([str(contact.id()) for contact in contactFilter]) + ")")

        query += self.__makeWhere(conditions)
        query += " ORDER by time " + order

        query = self.__queryReturn(query)
        ID,  IDONPHONE,  TYPE,  TIME,  CONTACT,  MESSAGE = range(6)
        while query.next():
            msg = Message()
            msg.setId(int(query.value(ID).toInt()[0]))
            msg.setIdOnPhone(int(query.value(IDONPHONE).toInt()[0]))
            msg.setType(int(query.value(TYPE).toInt()[0]))
            msg.setDateTime(query.value(TIME).toDateTime())
            msg.setContact(self.contacts(contactId=int(query.value(CONTACT).toInt()[0])).next())
            msg.setMessage(unicode(query.value(MESSAGE).toString()))
            yield msg


    def dates(self,  contact=None,  searchText=None,  searchOlder=None,  searchNewer=None):
        query = "SELECT " + self.__getYear() + " AS year, " + self.__getMonth() + " AS month, " + self.__getDay() + " AS day FROM messages "

        conditions = list()
        if contact:
            conditions.append("contact='" + str(contact.id()) + "'")
        if searchText:
            conditions.append("message LIKE '%" + searchText + "%'")
        if searchOlder:
            conditions.append("time < '" + searchOlder.toString(Qt.ISODate) + "'")
        if searchNewer:
            conditions.append("time > '" + searchNewer.toString(Qt.ISODate) + "'")

        query += self.__makeWhere(conditions)

        query += " GROUP BY year,month,day ORDER BY year DESC,month DESC,day DESC"

        query = self.__queryReturn(query)
        YEAR,  MONTH,  DAY = range(3)
        ret = HistoryDates()
        while query.next():
            year = int(query.value(YEAR).toInt()[0])
            month = int(query.value(MONTH).toInt()[0])
            day = int(query.value(DAY).toInt()[0])

            ret.addDay(year,  month,  day)

        return ret

    def statisticsGeneral(self):
        ret = dict()

        query = "SELECT SUM(CASE type WHEN 1 THEN 1 ELSE 0 END) incoming, SUM(CASE type WHEN 2 THEN 1 ELSE 0 END) outgoing FROM messages"
        query = self.__queryReturn(query)

        INCOMING,  OUTGOING = range(2)
        if query.last():
            ret["incoming"] = int(query.value(INCOMING).toInt()[0])
            ret["outgoing"] = int(query.value(OUTGOING).toInt()[0])
            ret["total"] = ret["incoming"] + ret["outgoing"]

        query = "SELECT COUNT(DISTINCT DATE(time)) FROM messages"
        query = self.__queryReturn(query)

        if query.last():
            ret["days"] = int(query.value(0).toInt()[0])

        query = "SELECT COUNT(DISTINCT contactIdOnPhone), COUNT(*) FROM contacts"
        query = self.__queryReturn(query)

        CONTACTSONPHONE,  CONTACTS = range(2)
        if query.last():
            ret["contactsShown"] = int(query.value(CONTACTSONPHONE).toInt()[0])
            ret["contacts"] = int(query.value(CONTACTS).toInt()[0])

        query = "SELECT ROUND(AVG(LENGTH(message)),2) FROM messages WHERE type='" + str(MessageType.Incoming) + "'"
        query = self.__queryReturn(query)

        if query.last():
            ret["incoming_avglength"] = str(query.value(0).toDouble()[0])

        query = "SELECT ROUND(AVG(LENGTH(message)),2) FROM messages WHERE type='" + str(MessageType.Outgoing) + "'"
        query = self.__queryReturn(query)

        if query.last():
            ret["outgoing_avglength"] = str(query.value(0).toDouble()[0])


        return ret

    def statistics(self,  data):
        period = data.period()
        start,  duration = data.range()

        if data.statisticsFor() == StatisticFor.Periods:
            conditions = list()
            if data.contact().id():
                conditions.append("contact='" + str(data.contact().id()) + "'")

            if data.year():
                if self.__type == "sqlite":
                    if 0 < data.year() < 10:
                        year = "0" + str(data.year())
                    else:
                        year = str(data.year())
                conditions.append(self.__getYear() + "='" + year + "'")

            if data.month():
                if self.__type == "sqlite":
                    if 0 < data.month() < 10:
                        month = "0" + str(data.month())
                    else:
                        month = str(data.month())
                conditions.append(self.__getMonth() + "='" + month + "'")

            if data.day():
                if self.__type == "sqlite":
                    if 0 < data.day() < 10:
                        day = "0" + str(data.day())
                    else:
                        day = str(data.day())
                conditions.append(self.__getDay() + "='" + day + "'")

            if data.type() and data.type() != MessageType.All:
                conditions.append("type=" + str(data.type()))

            where = self.__makeWhere(conditions)

            if data.type() == MessageType.Unknown:
                count = "COUNT(*) count"
            elif data.type() == MessageType.Incoming or data.type() == MessageType.Outgoing:
                count = "SUM(CASE type WHEN " + str(data.type()) + " THEN 1 ELSE 0 END) count"
            elif data.type() == MessageType.All:
                count = "SUM(CASE type WHEN 1 THEN 1 ELSE 0 END) incoming, SUM(CASE type WHEN 2 THEN 1 ELSE 0 END) outgoing"

            if period == StatisticPeriod.Years:
                query = "SELECT " + self.__getYear() + " AS year, " + count + " FROM messages " + where + " GROUP BY year "
            elif period == StatisticPeriod.YearsAndMonths:
                query = "SELECT " + self.__getYear() + " AS year, " + self.__getMonth() + " AS month, " + count + " FROM messages " + \
                                where + " GROUP BY year,month "
            elif period == StatisticPeriod.Months:
                query = "SELECT " + self.__getMonth() + " AS month, " + count + " FROM messages " + where + " GROUP BY month "
            elif period == StatisticPeriod.Days:
                query = "SELECT " + self.__getDay() + " AS days, " + count + " FROM messages " + where + " GROUP BY days "
            elif period == StatisticPeriod.Weekdays:
                query = "SELECT " + self.__getWeekday() + " AS weekdays, " + count + " FROM messages " + where + " GROUP BY weekdays "
            elif period == StatisticPeriod.Hours:
                query = "SELECT " + self.__getHour() + " AS hours, " + count + " FROM messages " + where + " GROUP BY hours "

            if start != None and duration != None:
                query += " LIMIT " + str(start) + "," + str(duration) +  " "

            next = 0
            if period == StatisticPeriod.YearsAndMonths:
                PERIOD0,  PERIOD1 = range(next,  next+2)
                next += 2
            else:
                PERIOD0,  = range(next,  next+1)
                next += 1

            if data.type() == MessageType.All:
                TYPE0,  TYPE1 = range(next,  next+2)
                next += 2
            else:
                TYPE0,  = range(next,  next+1)
                next += 1

            query = self.__queryReturn(query)

            ret = StatisticResponse(data)
            while query.next():
                year,  month,  day,  weekday,  hour,  incoming,  outgoing,  all = None,  None,  None,  None,  None,  None,  None,  None
                if data.year() > 0:
                    year = data.year()
                if data.month() > 0:
                    month = data.month()
                if data.day() > 0:
                    day = data.day()

                if period == StatisticPeriod.Years:
                    year = int(query.value(PERIOD0).toInt()[0])
                elif period == StatisticPeriod.YearsAndMonths:
                    year = int(query.value(PERIOD0).toInt()[0])
                    month = int(query.value(PERIOD1).toInt()[0])
                elif period == StatisticPeriod.Months:
                    month = int(query.value(PERIOD0).toInt()[0])
                elif period == StatisticPeriod.Days:
                    day = int(query.value(PERIOD0).toInt()[0])
                elif period == StatisticPeriod.Weekdays:
                    weekday = int(query.value(PERIOD0).toInt()[0])
                    if self.__type == "mysql":
                        weekday += 1
                    elif self.__type == "sqlite" and weekday == 0:
                        weekday = 7
                elif period == StatisticPeriod.Hours:
                    hour = int(query.value(PERIOD0).toInt()[0])

                if data.type() == MessageType.Unknown:
                    all = int(query.value(TYPE0).toInt()[0])
                elif data.type() == MessageType.All:
                    incoming = int(query.value(TYPE0).toInt()[0])
                    outgoing = int(query.value(TYPE1).toInt()[0])
                    all = incoming+outgoing
                elif data.type() == MessageType.Incoming:
                    incoming = int(query.value(TYPE0).toInt()[0])
                elif data.type() == MessageType.Outgoing:
                    outgoing = int(query.value(TYPE0).toInt()[0])

                ret.append(year,  month,  day,  weekday,  hour,  incoming,  outgoing,  all)
            return ret

        if data.statisticsFor() == StatisticFor.Contacts:
            count = "SUM(CASE type WHEN 1 THEN 1 ELSE 0 END) incoming, SUM(CASE type WHEN 2 THEN 1 ELSE 0 END) outgoing, " +\
                        "SUM(CASE type WHEN 1 THEN 1 ELSE 1 END) count"

            query = "SELECT contact, " + count + " FROM messages GROUP BY contact ORDER BY count DESC"
            if start != None and duration != None:
                query += " LIMIT " + str(start) + "," + str(duration) +  " "
            query = self.__queryReturn(query)

            ret = list()
            CONTACT,  INCOMING,  OUTGOING,  TOTAL = range(4)
            while query.next():
                ret.append( [self.contacts(contactId=int(query.value(CONTACT).toInt()[0])).next(),
                    int(query.value(INCOMING).toInt()[0]),  int(query.value(OUTGOING).toInt()[0]),  int(query.value(TOTAL).toInt()[0]) ] )

            return ret

    def close(self):
        self.__connected = False
        self.__type = ""
        if hasattr(self.database,  "isOpen"):
            if self.database.isOpen():
                old = self.database.connectionName()
                self.database = QSqlDatabase()
                self.database.removeDatabase(old)

class Update(object):
    def __init__(self, database,  main):
        self.database = database
        self.main = main

        self.versions = list()
        self.versions.append(( (0,  2),  (0,  3),  self.update_02_to_03 ))
        self.versions.append(( (0,  3),  (0,  4),  self.update_03_to_04 ))
        self.versions.append(( (0,  4),  (0,  5),  self.update_04_to_05 ))

    def update(self,  fromVersion,  toVersion):
        froms = ( i[0] for i in self.versions )
        froms = tuple(froms)
        if fromVersion not in froms:
            return False,  "Cannot update from " + str(fromVersion)

        tos = ( i[1] for i in self.versions )
        tos = tuple(tos)
        if toVersion not in tos:
            return False,  "Cannot update to " + str(toVersion)

        while True:
            for version in self.versions:
                if version[0] == fromVersion:
                    if not version[2]():
                        return False,  "Failed to update " + str(version[0]) + " to " + str(version[1])
                    fromVersion = version[1]
                    if version[1] == toVersion:
                        if self.writeVersion():
                            return True,  "Update successful"
                        else:
                            return False,  "Couldn't write version to database"

    def writeVersion(self):
        query = QSqlQuery(self.database)
        ret = query.exec_("UPDATE config SET value='" + self.main.databaseVersionStr + "' WHERE name='version'")

        if not ret:
            return False

        return True

    def update_02_to_03(self):
        query = QSqlQuery(self.database)
        ret = query.exec_("""ALTER TABLE contacts
        ADD COLUMN favoriteContact SMALLINT UNSIGNED NOT NULL DEFAULT 0 CHECK(favoriteContact IN (0, 1))""")

        if not ret:
            return False

        ret = query.exec_("""CREATE TABLE config (
        name VARCHAR(255) PRIMARY KEY,
        value VARCHAR(255)
        )
        """)

        if not ret:
            return False

        return True

        # Save database version in data table
        query = QSqlQuery(self.database)
        query.prepare("""INSERT INTO config (name, value)
        VALUES ('version', :version)""")
        query.bindValue(":version",  QVariant(self.main.databaseVersionStr))

        if not query.exec_():
            return False

        return True

    def update_03_to_04(self):
        query = QSqlQuery(self.database)

        # drop column is not supported with SQLite :-(
        if self.database.driverName() == "QSQLITE":
            ### Table: contact_details ###

            ret = query.exec_("""ALTER TABLE contact_details
            RENAME TO contact_details_old""")

            if not ret:
                return False

            ret = query.exec_("""CREATE TABLE contact_details (
            contactId INT UNSIGNED NOT NULL,
            detailOnPhone SMALLINT UNSIGNED NOT NULL DEFAULT 1 CHECK(detailOnPhone IN (0, 1)),
            type VARCHAR(255) NOT NULL,
            value VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            PRIMARY KEY (contactId, type, location, value),
            FOREIGN KEY (contactId) REFERENCES contacts
            )
            """)

            if not ret:
                return False

            ret = query.exec_("""INSERT INTO contact_details
            SELECT contactId, detailOnPhone, type, value, 'none' FROM contact_details_old""")

            if not ret:
                return False

            ret = query.exec_("""DROP TABLE contact_details_old""")

            if not ret:
                return False

            ### Table: messages ###

            ret = query.exec_("""ALTER TABLE messages
            RENAME TO messages_old""")

            if not ret:
                return False

            ret = query.exec_("""CREATE TABLE messages (
            messageId INT UNSIGNED NOT NULL PRIMARY KEY,
            messageIdOnPhone INT,
            device INT UNSIGNED NOT NULL,
            type SMALLINT UNSIGNED NOT NULL CHECK(type IN (1, 2)),
            time DATETIME NOT NULL,
            contact INT UNSIGNED NOT NULL,
            message TEXT NOT NULL,
            FOREIGN KEY (device) REFERENCES devices,
            FOREIGN KEY (contact) REFERENCES contacts
            )
            """)

            if not ret:
                return False

            ret = query.exec_("""INSERT INTO messages
            SELECT messageId, messageIdOnPhone, device, type, time, contact, message FROM messages_old""")

            if not ret:
                return False

            ret = query.exec_("""DROP TABLE messages_old""")

            if not ret:
                return False

        else:
            ### Table: contact_details ###

            ret = query.exec_("""ALTER TABLE contact_details
            DROP COLUMN detailId""")

            if not ret:
                return False

            ret = query.exec_("""ALTER TABLE contact_details
            DROP PRIMARY KEY""")

            if not ret:
                return False

            ret = query.exec_("""ALTER TABLE contact_details
            ADD PRIMARY KEY (contactId, type, location, value)""")

            if not ret:
                return False


            ret = query.exec_("""ALTER TABLE contact_details
            ADD COLUMN location VARCHAR(255) DEFAULT 'none'""")

            if not ret:
                return False

            ### Table: messages ###

            ret = query.exec_("""ALTER TABLE messages
            DROP COLUMN phone""")

            if not ret:
                return False

        ### Table: contact_fields ###
        ret = query.exec_("""DROP TABLE contact_fields""")

        if not ret:
            return False

        return True

    def update_04_to_05(self):
        query = QSqlQuery(self.database)
        ret = query.exec_("""ALTER TABLE devices
        ADD COLUMN deviceClass INT UNSIGNED""")

        if not ret:
            return False

        ret = query.exec_("""CREATE TABLE calendar (
        entryId INT UNSIGNED NOT NULL PRIMARY KEY,
        entryIdOnPhone INT,
        device INT UNSIGNED NOT NULL,
        type VARCHAR(255) NOT NULL,
        content TEXT NOT NULL,
        location TEXT,
        startTime DATETIME,
        endTime DATETIME,
        lastModifiedTime DATETIME,
        replication VARCHAR(255) NOT NULL,
        alarmTime DATETIME,
        priority INT UNSIGNED NOT NULL,
        repeatType VARCHAR(255),
        repeatDays VARCHAR(255),
        repeatExceptions VARCHAR(255),
        repeatStartTime DATETIME,
        repeatEndTime DATETIME,
        repeatInterval INT UNSIGNED,
        crossedOut SMALLINT UNSIGNED NOT NULL DEFAULT 0 CHECK(crossedOut IN (0, 1)),
        crossOutTime DATETIME
        )
        """)

        if not ret:
            return False

        return True
