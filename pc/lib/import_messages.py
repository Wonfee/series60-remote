# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtSql import *
from lib.classes import *

class Import(object):
    def __init__(self, parent, main):
        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.__applications = list()
        self.__applications.append( S60_Remote(main) )

    def applications(self):
        return self.__applications

class Types(QObject):
    def __init__(self):
        super(Types,  self).__init__()

        self.MySQL = 1
        self.SQLite = 2

        self.dataMysql = ["host",  "port",  "user",  "pass",  "database"]
        self.dataSqlite = ["filename"]

        self.dataMysql.sort()
        self.dataSqlite.sort()

    def name(self,  type):
        if type == self.MySQL:
            return "MySQL"
        elif type == self.SQLite:
            return "SQLite"
        else:
            return self.tr("unknown")

class Database(Types):
    def __init__(self,  main):
        super(Database,  self).__init__()

        self.main = main
        self.log = main.log

        self.lastError = ""

    def setError(self,  error):
        self.lastError = error
        self.log.error(self.error())
        return False

    def error(self):
        err = str(self.lastError).strip()
        if not err:
            err = "Unknown error"

        return err

class S60_Remote(QObject):
    def __init__(self, main):
        super(S60_Remote,  self).__init__(main)

        self.main = main

    def versions(self):
        versions = list()
        versions.append( S60_Remote.Import_0_0_0(self.main) )
        versions.append( S60_Remote.Import_0_0_1(self.main) )
        versions.append( S60_Remote.Import_0_2_0(self.main) )
        versions.append( S60_Remote.Import_0_4_0(self.main) )

        return versions

    def applicationName(self):
        return self.tr("Old versions of Series60-Remote")

    class Import_0_0_0(Database):
        def __init__(self,  main):
            super(S60_Remote.Import_0_0_0,  self).__init__(main)

            self.main = main
            self.database = main.database

            self.type = None
            self.data = None
            self.old = QSqlDatabase()

        def version(self):
            return self.tr("0.0.0 (obsolete version, SVN-only)")

        def help(self):
            text = self.tr("Please note the following disadvantages:<br />")
            text += QString("<br /> ") + self.tr("- Umlauts will get replaced")
            text += QString("<br /> ") + self.tr("- Commas in contact names will get removed")
            return text

        def databases(self):
            db = list()
            db.append(self.MySQL)
            return db

        def use(self, type,  data):
            self.type = type
            self.data = data

            keys = data.keys()
            keys.sort()

            if QSqlDatabase.connectionNames().contains("old"):
                self.old = QSqlDatabase()
                QSqlDatabase.removeDatabase("old")

            if type not in self.databases():
                return self.setError("wrong database type")

            if not data:
                return self.setError("connection data missing")
            elif keys != self.dataMysql:
                return self.setError("connection data incorrect")

            if type == self.MySQL:
                self.old = QSqlDatabase.addDatabase("QMYSQL",  "old")
                self.old.setHostName(data["host"])
                self.old.setPort(data["port"])
                self.old.setUserName(data["user"])
                self.old.setPassword(data["pass"])
                self.old.setDatabaseName(data["database"])

            if not self.old.open():
                return self.setError("open failed")

            tables = self.old.tables()
            find = ("contacts",  "data",  "info")

            for table in find:
                if not tables.contains(table):
                    return self.setError("Table " + table + " not found!")

            return True

        def count(self):
            query = QSqlQuery(self.old)
            query.exec_("SELECT COUNT(*) FROM data")
            if query.last():
                return query.value(0).toInt()[0]
            else:
                return 0

        def import_(self):
            self.thread = self.ImportThread(self,  self.main,  self.old)

            self.connect(self.thread,  SIGNAL("finished()"),  lambda : self.emit(SIGNAL("importComplete")))
            self.connect(self.thread,  SIGNAL("messageImported"),  lambda sum : self.emit(SIGNAL("messageImported"), sum))
            self.thread.start()

        def stop(self):
            self.thread.stop()

        class ImportThread(QThread):
            def __init__(self,  parent,  main,  db):
                super(S60_Remote.Import_0_0_0.ImportThread,  self).__init__(parent)

                self.parent = parent
                self.main = main
                self.db = db

                self.__stop = False

            def __str__(self):
                return "\"s60 Import Messages/Thread\""

            def run(self):
                ID,  TYPE,  TIME,  CONTACT,  MESSAGE = range(5)
                query = QSqlQuery(self.db)
                query.exec_("SELECT id, type, time, addr, cont FROM data")

                sum = 0
                while query.next():
                    if self.__stop:
                        break
                    sum += 1
                    msg = Message()
                    msg.setIdOnPhone(int(query.value(ID).toInt()[0]))
                    msg.setType(int(query.value(TYPE).toInt()[0]))
                    msg.setDateTime(query.value(TIME).toDateTime())
                    msg.setContact(Contact(name=self.replace(query.value(CONTACT).toString(),  True)))
                    msg.setMessage(self.replace(query.value(MESSAGE).toString()))
                    self.main.database.messageAdd(msg)

                    if sum % 10 == 0:
                        self.emit(SIGNAL("messageImported"),  sum)

                self.quit()

            def replace(self,  string,  commas=False):
                if "\xc3" in string:
                    string = unicode(string.fromUtf8(string)).replace(u"\ufffd?", u"ß")
                else:
                    string = unicode(string)
                if commas:
                    string = string.replace(",", "")
                return string

            def stop(self):
                self.__stop = True

    class Import_0_0_1(Database):
        def __init__(self,  main):
            super(S60_Remote.Import_0_0_1,  self).__init__(main)

            self.main = main
            self.database = main.database

            self.type = None
            self.data = None
            self.old = QSqlDatabase()

        def version(self):
            return "0.0.1"

        def help(self):
            return QString()

        def databases(self):
            db = list()
            db.append(self.MySQL)
            db.append(self.SQLite)
            return db

        def use(self, type,  data):
            self.type = type
            self.data = data

            keys = data.keys()
            keys.sort()

            if QSqlDatabase.connectionNames().contains("old"):
                self.old = QSqlDatabase()
                QSqlDatabase.removeDatabase("old")

            if type not in self.databases():
                return self.setError("wrong database type")

            if not data:
                return self.setError("connection data missing")

            if type == self.MySQL:
                if keys != self.dataMysql:
                    return self.setError("connection data incorrect")
                self.old = QSqlDatabase.addDatabase("QMYSQL",  "old")
                self.old.setHostName(data["host"])
                self.old.setPort(data["port"])
                self.old.setUserName(data["user"])
                self.old.setPassword(data["pass"])
                self.old.setDatabaseName(data["database"])
            elif type == self.SQLite:
                if keys != self.dataSqlite:
                    return self.setError("connection data incorrect")
                self.old = QSqlDatabase.addDatabase("QSQLITE",  "old")
                self.old.setDatabaseName(data["filename"])

            if not self.old.open():
                return self.setError("open failed")

            tables = self.old.tables()
            find = ("alias",  "messages")

            for table in find:
                if not tables.contains(table):
                    return self.setError("Table " + table + " not found!")

            return True

        def count(self):
            query = QSqlQuery(self.old)
            query.exec_("SELECT COUNT(*) FROM messages")
            if query.last():
                return query.value(0).toInt()[0]
            else:
                return 0

        def import_(self):
            self.thread = self.ImportThread(self,  self.main,  self.old)

            self.connect(self.thread,  SIGNAL("finished()"),  lambda : self.emit(SIGNAL("importComplete")))
            self.connect(self.thread,  SIGNAL("messageImported"),  lambda sum : self.emit(SIGNAL("messageImported"), sum))
            self.thread.start()

        def stop(self):
            self.thread.stop()

        class ImportThread(QThread):
            def __init__(self,  parent,  main,  db):
                super(S60_Remote.Import_0_0_1.ImportThread,  self).__init__(parent)

                self.parent = parent
                self.main = main
                self.db = db

                self.__stop = False

            def __str__(self):
                return "\"s60 Import Messages/Thread\""

            def run(self):
                ID,  TYPE,  TIME,  CONTACT,  MESSAGE = range(5)
                query = QSqlQuery(self.db)
                query.exec_("SELECT id, type, time, addr, cont FROM messages")

                sum = 0
                while query.next():
                    if self.__stop:
                        break
                    sum += 1
                    msg = Message()
                    msg.setIdOnPhone(int(query.value(ID).toInt()[0]))
                    msg.setType(int(query.value(TYPE).toInt()[0]))
                    msg.setDateTime(query.value(TIME).toDateTime())
                    msg.setContact(Contact(name=unicode(query.value(CONTACT).toString())))
                    msg.setMessage(unicode(query.value(MESSAGE).toString()))
                    self.main.database.messageAdd(msg)

                    if sum % 10 == 0:
                        self.emit(SIGNAL("messageImported"),  sum)

                self.quit()

            def stop(self):
                self.__stop = True

    class Import_0_2_0(Database):
        def __init__(self,  main):
            super(S60_Remote.Import_0_2_0,  self).__init__(main)

            self.main = main
            self.database = main.database

            self.type = None
            self.data = None
            self.old = QSqlDatabase()

        def version(self):
            return "0.2.0 - 0.3.0"

        def help(self):
            return QString()

        def databases(self):
            db = list()
            db.append(self.MySQL)
            db.append(self.SQLite)
            return db

        def use(self, type,  data):
            self.type = type
            self.data = data

            keys = data.keys()
            keys.sort()

            if QSqlDatabase.connectionNames().contains("old"):
                self.old = QSqlDatabase()
                QSqlDatabase.removeDatabase("old")

            if type not in self.databases():
                return self.setError("wrong database type")

            if not data:
                return self.setError("connection data missing")

            if type == self.MySQL:
                if keys != self.dataMysql:
                    return self.setError("connection data incorrect")
                self.old = QSqlDatabase.addDatabase("QMYSQL",  "old")
                self.old.setHostName(data["host"])
                self.old.setPort(data["port"])
                self.old.setUserName(data["user"])
                self.old.setPassword(data["pass"])
                self.old.setDatabaseName(data["database"])
            elif type == self.SQLite:
                if keys != self.dataSqlite:
                    return self.setError("connection data incorrect")
                self.old = QSqlDatabase.addDatabase("QSQLITE",  "old")
                self.old.setDatabaseName(data["filename"])

            if not self.old.open():
                return self.setError("open failed")

            tables = self.old.tables()
            find = ("contact_details",  "contact_fields",  "contacts",  "devices",  "messages")

            for table in find:
                if not tables.contains(table):
                    return self.setError("Table " + table + " not found!")

            return True

        def count(self):
            query = QSqlQuery(self.old)
            query.exec_("SELECT COUNT(*) FROM messages")
            if query.last():
                return query.value(0).toInt()[0]
            else:
                return 0

        def import_(self):
            self.thread = self.ImportThread(self,  self.main,  self.old)

            self.connect(self.thread,  SIGNAL("finished()"),  lambda : self.emit(SIGNAL("importComplete")))
            self.connect(self.thread,  SIGNAL("messageImported"),  lambda sum : self.emit(SIGNAL("messageImported"), sum))
            self.thread.start()

        def stop(self):
            self.thread.stop()

        class ImportThread(QThread):
            def __init__(self,  parent,  main,  db):
                super(S60_Remote.Import_0_2_0.ImportThread,  self).__init__(parent)

                self.parent = parent
                self.main = main
                self.db = db

                self.__stop = False

            def __str__(self):
                return "\"s60 Import Messages/Thread\""

            def run(self):
                ID,  TYPE,  TIME,  CONTACT,  MESSAGE = range(5)
                query = QSqlQuery(self.db)
                query.exec_("SELECT m.messageIdOnPhone, m.type, m.time, c.name, m.message FROM messages m JOIN contacts c ON m.contact=c.contactId WHERE messageIdOnPhone IS NOT NULL")

                sum = 0
                while query.next():
                    if self.__stop:
                        break
                    sum += 1
                    msg = Message()
                    msg.setIdOnPhone(int(query.value(ID).toInt()[0]))
                    msg.setType(int(query.value(TYPE).toInt()[0]))
                    msg.setDateTime(query.value(TIME).toDateTime())
                    msg.setContact(Contact(name=unicode(query.value(CONTACT).toString())))
                    msg.setMessage(unicode(query.value(MESSAGE).toString()))
                    self.main.database.messageAdd(msg)

                    if sum % 10 == 0:
                        self.emit(SIGNAL("messageImported"),  sum)

                self.quit()

            def stop(self):
                self.__stop = True

    class Import_0_4_0(Database):
        def __init__(self,  main):
            super(S60_Remote.Import_0_4_0,  self).__init__(main)

            self.main = main
            self.database = main.database

            self.type = None
            self.data = None
            self.old = QSqlDatabase()

        def version(self):
            return "0.4.0"

        def help(self):
            return QString()

        def databases(self):
            db = list()
            db.append(self.MySQL)
            db.append(self.SQLite)
            return db

        def use(self, type,  data):
            self.type = type
            self.data = data

            keys = data.keys()
            keys.sort()

            if QSqlDatabase.connectionNames().contains("old"):
                self.old = QSqlDatabase()
                QSqlDatabase.removeDatabase("old")

            if type not in self.databases():
                return self.setError("wrong database type")

            if not data:
                return self.setError("connection data missing")

            if type == self.MySQL:
                if keys != self.dataMysql:
                    return self.setError("connection data incorrect")
                self.old = QSqlDatabase.addDatabase("QMYSQL",  "old")
                self.old.setHostName(data["host"])
                self.old.setPort(data["port"])
                self.old.setUserName(data["user"])
                self.old.setPassword(data["pass"])
                self.old.setDatabaseName(data["database"])
            elif type == self.SQLite:
                if keys != self.dataSqlite:
                    return self.setError("connection data incorrect")
                self.old = QSqlDatabase.addDatabase("QSQLITE",  "old")
                self.old.setDatabaseName(data["filename"])

            if not self.old.open():
                return self.setError("open failed")

            tables = self.old.tables()
            find = ("config", "contact_details",  "contacts",  "devices",  "messages")

            for table in find:
                if not tables.contains(table):
                    return self.setError("Table " + table + " not found!")

            return True

        def count(self):
            query = QSqlQuery(self.old)
            query.exec_("SELECT COUNT(*) FROM messages")
            if query.last():
                return query.value(0).toInt()[0]
            else:
                return 0

        def import_(self):
            self.thread = self.ImportThread(self,  self.main,  self.old)

            self.connect(self.thread,  SIGNAL("finished()"),  lambda : self.emit(SIGNAL("importComplete")))
            self.connect(self.thread,  SIGNAL("messageImported"),  lambda sum : self.emit(SIGNAL("messageImported"), sum))
            self.thread.start()

        def stop(self):
            self.thread.stop()

        class ImportThread(QThread):
            def __init__(self,  parent,  main,  db):
                super(S60_Remote.Import_0_4_0.ImportThread,  self).__init__(parent)

                self.parent = parent
                self.main = main
                self.db = db

                self.__stop = False

            def __str__(self):
                return "\"Import Messages/Thread\""

            def run(self):
                ID,  TYPE,  TIME,  CONTACT,  MESSAGE = range(5)
                query = QSqlQuery(self.db)
                query.exec_("SELECT m.messageIdOnPhone, m.type, m.time, c.name, m.message FROM messages m JOIN contacts c ON m.contact=c.contactId WHERE messageIdOnPhone IS NOT NULL")

                sum = 0
                while query.next():
                    if self.__stop:
                        break
                    sum += 1
                    msg = Message()
                    msg.setIdOnPhone(int(query.value(ID).toInt()[0]))
                    msg.setType(int(query.value(TYPE).toInt()[0]))
                    msg.setDateTime(query.value(TIME).toDateTime())
                    msg.setContact(Contact(name=unicode(query.value(CONTACT).toString())))
                    msg.setMessage(unicode(query.value(MESSAGE).toString()))
                    self.main.database.messageAdd(msg)

                    if sum % 10 == 0:
                        self.emit(SIGNAL("messageImported"),  sum)

                self.quit()

            def stop(self):
                self.__stop = True
