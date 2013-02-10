# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *

class Enum(object):
    def __init__(self, names, separator=None,  beginning=0):
        self.names = names.split(separator)
        for value, name in enumerate(self.names):
            setattr(self, name, value+beginning)
    def tuples(self):
        return tuple(enumerate(self.names))

class EnumBin(object):
    def __init__(self, names, separator=None,  beginning=0):
        self.names = names.split(separator)
        for value, name in enumerate(self.names):
            setattr(self, name, (2**value)+beginning)
    def tuples(self):
        return tuple(enumerate(self.names))

Roles = Enum("MessageRole ContactRole DeviceRole DateRole ApplicationRole VersionRole TypeRole LinkRole DirectoryRole",
                        beginning=Qt.UserRole+10)
MessageType = Enum("Unknown Incoming Outgoing Internal All")
MessageState = Enum("Unknown Created Pending Sending SendFailed SendOk")
MessagePriority = Enum("History Low High Medium")
StatisticFor = Enum("Unknown Periods Contacts")
StatisticPeriod = Enum("Unknown Years YearsAndMonths Months Days Weekdays Hours")
StatisticOrderBy = Enum("Unknown Number Name")
StatisticGraphLayout = Enum("Stacked Separate")
PopupTypes = Enum("Unknown Message ConnectionCompleted ConnectionClosed")
FallbackDate = Enum("IgnoreMonth ShowBefore ShowAfterwards")

# For message export
ExportItems = EnumBin("Contacts Messages Calendar")
ExportOptions = EnumBin("Period Order Graph GraphFormat Legend Thumbnails")
ExportExtraOptions = EnumBin("WriteCalendar ContactsInSeperateFiles")
ExportContacts = Enum("All ContactsWithMessages Filter None_")
ExportPeriod = Enum("Daily Monthly Yearly All")
ExportOrder = Enum("ASC DESC")
ExportGraph = Enum("Yes No")
ExportGraphFormat = Enum("PNG SVG")
ExportLegend = Enum("Yes No")
ExportThumbnails = Enum("Yes No")

class HistoryDates(object):
    def __init__(self):
        self.__dates = dict()

    def addYear(self,  year):
        if not year in self.__dates:
            self.__dates[year] = dict()

    def addMonth(self,  year,  month):
        self.addYear(year)

        if not month in self.__dates[year]:
           self.__dates[year][month] = list()

    def addDay(self,  year,  month,  day):
        self.addMonth(year,  month)

        if not day in self.__dates[year][month]:
            self.__dates[year][month].append(day)

    def years(self):
        years = self.__dates.keys()
        years.sort(reverse=True)
        return years

    def months(self,  year):
        months = self.__dates[year].keys()
        months.sort(reverse=True)
        return months

    def days(self,  year,  month):
        days = self.__dates[year][month]
        days.sort(reverse=True)
        return days

class ContactField(QObject):
    def __init__(self,  type,  location):
        super(ContactField,  self).__init__()

        self.setType(type)
        self.setLocation(location)

    def __repr__(self):
        return "ContactField('%s', '%s')" % (self.__type,  self.__location)

    def __hash__(self):
        return hash(self.__type + ":" + self.__location)

    def __eq__(self,  b):
        return self.type() == b.type() and self.location() == b.location()

    def setLocation(self,  location):
        assert location in ["none",  "home",  "work"],  "wrong argument '%s'" % location
        self.__location = location

    @staticmethod
    def types():
        return ["last_name",  "first_name",  "job_title",  "company_name",  "phone_number",  "mobile_number",
                               "pager_number",  "fax_number",  "email_address",  "url",  "postal_address", "po_box",
                               "extended_address",  "street_address",  "postal_code",  "city",  "state",  "country",
                               "dtmf_string",  "date",  "note",  "thumbnail_image",  "prefix",  "suffix",  "second_name",
                               "video_number",  "voip",  "push_to_talk",  "share_view",  "sip_id",  "personal_ringtone",
                               "locationid_indication",  "picture",  "first_name_reading",  "last_name_reading",
                               "speed_dial",  "voice_tag",  "wvid"]

    def setType(self,  type):
        # There was a Typo in 0.3.90:
        # TODO: Remove
        if type == "dmtf_string":
            type = "dtmf_string"

        assert type in self.types(),  "wrong argument '%s'" % type

        self.__type = type

    def isPicture(self):
        return self.type() == "thumbnail_image"

    def isDate(self):
        return self.type() == "date"

    def location(self):
        return self.__location

    def type(self):
        return self.__type

    def toString(self,  num=1,  printLocation=False):
        if self.type() == "last_name":
            string = self.tr("Last name:")
        elif self.type() == "first_name":
            string = self.tr("First name:")
        elif self.type() == "job_title":
            string = self.tr("Job title:")
        elif self.type() == "company_name":
            string = self.tr("Company:")
        elif self.type() == "phone_number":
            string = self.tr("Telephone:")
        elif self.type() == "mobile_number":
            string = self.tr("Mobile:")
        elif self.type() == "pager_number":
            string = self.tr("Pager:")
        elif self.type() == "fax_number":
            string = self.tr("Fax:")
        elif self.type() == "email_address":
            string = self.tr("E-mail:")
        elif self.type() == "url":
            string = self.tr("Web address:")
        elif self.type() == "postal_address":
            string = self.tr("Address:")
        elif self.type() == "po_box":
            string = self.tr("Post-office box:")
        elif self.type() == "extended_address":
            string = self.tr("Extension:")
        elif self.type() == "street_address":
            string = self.tr("Street:")
        elif self.type() == "postal_code":
            string = self.tr("Postal/ZIP code:")
        elif self.type() == "city":
            string = self.tr("City:")
        elif self.type() == "state":
            string = self.tr("State/Province:")
        elif self.type() == "country":
            string = self.tr("Country/Region:")
        elif self.type() == "dtmf_string":
            string = self.tr("DTMF:")
        elif self.type() == "date":
            string = self.tr("Birthday:")
        elif self.type() == "note":
            string = self.tr("Note:")
        elif self.type() == "thumbnail_image":
            string = self.tr("Thumbnail image:")
        elif self.type() == "prefix":
            string = self.tr("Title:")
        elif self.type() == "suffix":
            string = self.tr("Suffix:")
        elif self.type() == "second_name":
            string = self.tr("Nickname:")
        elif self.type() == "video_number":
            string = self.tr("Video call:")
        elif self.type() == "voip":
            string = self.tr("Internet telephone:")
        elif self.type() == "push_to_talk":
            string = self.tr("Push to talk:")
        elif self.type() == "share_view":
            string = self.tr("Share view:")
        elif self.type() == "sip_id":
            string = self.tr("SIP:")
        elif self.type() == "personal_ringtone":
            string = self.tr("Personal ringtone:")
        else:
            string = self.type() + ":"

        location = ""
        if printLocation:
            if self.location() == "home":
                location = self.tr(" (%1) ").arg(self.tr("Home"))
            elif self.location() == "work":
                location = self.tr(" (%1) ").arg(self.tr("Business"))

        if num > 1:
            string = self.tr("%1 (%2):").arg(unicode(string)[:-1] + location).arg(num)
        else:
            string = unicode(string)[:-1] + location + ":"

        return string

class __ContactFields(object): pass
ContactFields = __ContactFields()
for name in ContactField.types():
    setattr(ContactFields, name.title().replace("_",  ""), ContactField(name,  "none"))

class Contact(object):
    def __init__(self,  id = 0,  idOnPhone = 0,  name = "", ignore=False,  favorite=False,  values=list(),  internalValues=list()):
        self.setId(id)
        self.setIdOnPhone(idOnPhone)
        self.setName(name)
        self.setIgnored(ignore)
        self.setFavorite(favorite)
        #self.__values = values
        self.__values = list()
        self.__internalValues = dict()

    def __repr__(self):
        return u"Contact(%i, %i, '%s', %s, %s, %s, %s)" % (self.__id, self.__idOnPhone,  self.__name,  self.__ignored,  self.__favorite,
                                                          "",  self.__internalValues)

    def __contains__(self,  field):
        return self.contains(field)

    def __eq__(self,  b):
        if self.id() and b.id():
            return self.id() == b.id()
        elif self.name() and b.name():
            return self.name() == b.name()
        else:
            return False

    def __ne__(self,  b):
        return not self.__eq__(b)

    def __iter__(self):
        for item in self.__values:
            yield item

    def __nonzero__(self):
        return self.id() != 0 or self.idOnPhone() != 0

    def setId(self,  id):
        assert isinstance(id,  int),  "expected an int"
        self.__id = id

    def setIdOnPhone(self,  idOnPhone):
        assert isinstance(idOnPhone,  int),  "expected an int"
        self.__idOnPhone = idOnPhone

    def setName(self,  name):
        assert isinstance(name,  basestring),  "expected a string or unicode"
        self.__name = name

    def setIgnored(self,  ignore):
        self.__ignored = ignore

    def setFavorite(self,  favorite):
        self.__favorite = favorite

    def addValue(self,  field,  value):
        assert isinstance(field,  ContactField),  "expected a ContactField instance"
        assert isinstance(value,  unicode),  "expected a unicode"
        self.__values.append( (field,  value) )

    def addInternalValue(self,  key,  value):
        self.__internalValues[key] = value

    def internalValue(self,  key):
        return self.__internalValues[key]

    def internalValues(self):
        return self.__internalValues.keys()

    def ignore(self):
        self.setIgnored(True)

    def id(self):
        return self.__id

    def idOnPhone(self):
        return self.__idOnPhone

    def name(self):
        return self.__name

    def values(self):
        return self.__values

    def types(self,  location=None):
        if location == None:
            return set( value[0].type() for value in self.__values )
        else:
            ret = list()
            for value in self.__values:
                if value[0].location() == location:
                    ret.append(value[0].type())
            return set(ret)

    def isIgnored(self):
        return self.__ignored

    def isFavorite(self):
        return self.__favorite

    def value(self,  type,  location=None):
        tmp = list()
        for item in self.__values:
            if (location and item[0].location() == location) or (location == None):
                if item[0].type() == type:
                    tmp.append( item[1] )

        return tmp

#    def remove(self,  type):
#        tmp = list()
#        for item in self.__values:
#            if item[0] != type:
#                tmp.append(item)
#        self.__values = tmp

    def contains(self,  type):
        return type in self.types()

    def hasPicture(self):
        return "thumbnail_image" in self

    def picture(self):
        return self.value("thumbnail_image")[0]

class Device(object):
    def __init__(self,  id = 0, name = "",  bluetoothAddress = "00:00:00:00:00:00",  port = 0,  deviceClass = 0,  values=list()):
        self.setId(id)
        self.setName(name)
        self.setBluetoothAddress(bluetoothAddress)
        self.setPort(port)
        self.setDeviceClass(deviceClass)
        #self.__values = values
        self.__values = list()

    def __repr__(self):
        return "Device(%i, '%s', '%s', %i, %i, %s)" % (self.__id,  self.__name,  self.__bluetoothAddress,
                                                       self.__port,  self.__deviceClass,  self.__values)

    def __contains__(self,  type):
        return self.contains(type)

    def __eq__(self,  b):
        if self.bluetoothAddress() != "00:00:00:00:00:00" and b.bluetoothAddress() != "00:00:00:00:00:00":
            return self.bluetoothAddress() == b.bluetoothAddress()
        elif self.id() and b.id():
            return self.id() == b.id()
        else:
            return False

    def __ne__(self,  b):
        return not self.__eq__(b)

    def setId(self,  id):
        assert isinstance(id,  int),  "expected an int"
        self.__id = id

    def setName(self,  name):
        assert isinstance(name,  basestring),  "expected a string or unicode"
        self.__name = name

    def setBluetoothAddress(self,  bluetoothAddress):
        assert isinstance(bluetoothAddress,  str),  "expected a string"
        self.__bluetoothAddress = bluetoothAddress

    def setPort(self,  port):
        assert isinstance(port,  int),  "expected an int"
        self.__port = port

    def setDeviceClass(self,  deviceClass):
        self.__deviceClass = deviceClass

    def addValue(self,  type,  value):
        if (type != None) and (value != None):
            self.__values.append( [type,  value] )

    def id(self):
        return self.__id

    def name(self):
        return self.__name

    def bluetoothAddress(self):
        return self.__bluetoothAddress

    def port(self):
        return self.__port

    def deviceClass(self):
        return self.__deviceClass

    def values(self):
        return self.__values

    def types(self):
        return set( value[0] for value in self.__values )

    def value(self,  type):
        return self.__values[ [ value[0] for value in self.__values ].index(type) ][1]

    def contains(self,  type):
        return type in self.types()

    def clear(self):
        self.__values = list()

class CalendarEntry(object):
    def __init__(self,  id = 0,  idOnPhone = 0,  device = Device(),  type = "",  content = "",  location = "",  realStartTime = 0,  realEndTime = 0,  startTime = 0,
                 endTime = 0,  lastModified = 0,  replication = "",  alarm = 0,  priority = 0,  repeatType = "",  repeatDays = "",  repeatExceptions = "",  repeatStart = 0,
                 repeatEnd = 0,  repeatInterval = 0,  crossedOut = False,  crossOutTime = 0):
        self.setId(id)
        self.setIdOnPhone(idOnPhone)
        self.setDevice(device)
        self.setType(type)
        self.setContent(content)
        self.setLocation(location)
        self.setRealStartTime(startTime)
        self.setRealEndTime(endTime)
        self.setStartTime(startTime)
        self.setEndTime(endTime)
        self.setLastModified(lastModified)
        self.setReplication(replication)
        self.setAlarm(alarm)
        self.setPriority(priority)
        self.setRepeatType(repeatType)
        self.setRepeatDays(repeatDays)
        self.setRepeatExceptions(repeatExceptions)
        self.setRepeatStart(repeatStart)
        self.setRepeatEnd(repeatEnd)
        self.setRepeatInterval(repeatInterval)
        self.setCrossedOut(crossedOut)
        self.setCrossOutTime(crossOutTime)

    def __repr__(self):
        return u"CalendarEntry(%i, %i, %r, '%s', '%s', '%s', %r, %r, %r, %r, %r, '%s', %r, %i, '%s', '%s', '%s', %r, %r, %i, %r, %r)" % (
                                             self.__id,  self.__idOnPhone,  self.__device, self.__type,  self.__content,  self.__location,  self.__realStartTime,  self.__realEndTime,
                                             self.__startTime,  self.__endTime,  self.__lastModified,  self.__replication,  self.__alarm,  self.__priority,  self.__repeatType,
                                             self.__repeatDays,  self.__repeatExceptions,self.__repeatStart,  self.__repeatEnd,  self.__repeatInterval,  self.__crossedOut,
                                             self.__crossOutTime)

    def setId(self,  id):
        assert isinstance(id,  int),  "expected an int"
        self.__id = id

    def setIdOnPhone(self,  idOnPhone):
        assert isinstance(idOnPhone,  int),  "expected an int"
        self.__idOnPhone = idOnPhone

    def setDevice(self,  device):
        assert isinstance(device,  Device),  "expected a Device instance"
        self.__device = device

    def setType(self,  type):
        assert isinstance(type,  basestring),  "expected a string or unicode"
        self.__type = type

    def setContent(self,  content):
        assert isinstance(content,  basestring),  "expected a string or unicode"
        self.__content = content

    def setLocation(self,  location):
        assert isinstance(location,  basestring),  "expected a string or unicode"
        self.__location = location

    def setRealStartTime(self,  startTime):
        if isinstance(startTime,  (float,  int)):
            if startTime == 0:
                self.__realStartTime = QDateTime()
            else:
                self.__realStartTime = QDateTime.fromTime_t(int(startTime))
        elif isinstance(startTime,  QDateTime):
            self.__realStartTime = startTime
        else:
            assert False,  "expected a float, QDateTime or int"

    def setRealEndTime(self,  endTime):
        if isinstance(endTime,  (float,  int)):
            if endTime == 0:
                self.__realEndTime = QDateTime()
            else:
                self.__realEndTime = QDateTime.fromTime_t(int(endTime))
        elif isinstance(endTime,  QDateTime):
            self.__realEndTime = endTime
        else:
            assert False,  "expected a float, QDateTime or int"

    def setStartTime(self,  startTime):
        if isinstance(startTime,  (float,  int)):
            if startTime == 0:
                self.__startTime = QDateTime()
            else:
                self.__startTime = QDateTime.fromTime_t(int(startTime))
        elif isinstance(startTime,  QDateTime):
            self.__startTime = startTime
        else:
            assert False,  "expected a float, QDateTime or int"

    def setEndTime(self,  endTime):
        if isinstance(endTime,  (float,  int)):
            if endTime == 0:
                self.__endTime = QDateTime()
            else:
                self.__endTime = QDateTime.fromTime_t(int(endTime))
        elif isinstance(endTime,  QDateTime):
            self.__endTime = endTime
        else:
            assert False,  "expected a float, QDateTime or int"

    def setLastModified(self,  lastModified):
        if isinstance(lastModified,  (float,  int)):
            if lastModified == 0:
                self.__lastModified = QDateTime()
            else:
                self.__lastModified = QDateTime.fromTime_t(int(lastModified))
        elif isinstance(lastModified,  QDateTime):
            self.__lastModified = lastModified
        else:
            assert False,  "expected a float, QDateTime or int"

    def setReplication(self,  replication):
        assert isinstance(replication,  basestring),  "expected a string or unicode"
        self.__replication = replication

    def setAlarm(self,  alarm):
        if isinstance(alarm,  (float,  int)):
            if alarm == 0:
                self.__alarm = QDateTime()
            else:
                self.__alarm = QDateTime.fromTime_t(int(alarm))
        elif isinstance(alarm,  QDateTime):
            self.__alarm = alarm
        else:
            assert False,  "expected a float, QDateTime or int"

    def setPriority(self,  priority):
        assert isinstance(priority,  int),  "expected an int"
        self.__priority = priority

    def setRepeatType(self,  repeatType):
        assert isinstance(repeatType,  basestring),  "expected a string or unicode"
        self.__repeatType = repeatType

    def setRepeatDays(self,  repeatDays):
        assert isinstance(repeatDays,  basestring),  "expected a string or unicode"
        self.__repeatDays = repeatDays

    def setRepeatExceptions(self,  repeatExceptions):
        assert isinstance(repeatExceptions,  basestring),  "expected a string or unicode"
        self.__repeatExceptions = repeatExceptions

    def setRepeatStart(self,  repeatStart):
        if isinstance(repeatStart,  (float,  int)):
            if repeatStart == 0:
                self.__repeatStart = QDateTime()
            else:
                self.__repeatStart = QDateTime.fromTime_t(int(repeatStart))
        elif isinstance(repeatStart,  QDateTime):
            self.__repeatStart = repeatStart
        else:
            assert False,  "expected a float, QDateTime or int"

    def setRepeatEnd(self,  repeatEnd):
        if isinstance(repeatEnd,  (float,  int)):
            if repeatEnd == 0:
                self.__repeatEnd = QDateTime()
            else:
                self.__repeatEnd = QDateTime.fromTime_t(int(repeatEnd))
        elif isinstance(repeatEnd,  QDateTime):
            self.__repeatEnd = repeatEnd
        else:
            assert False,  "expected a float, QDateTime or int"

    def setRepeatInterval(self,  repeatInterval):
        assert isinstance(repeatInterval,  int),  "expected an int"
        self.__repeatInterval = repeatInterval

    def setCrossedOut(self,  crossedOut):
        assert isinstance(crossedOut,  int),  "expected a bool"
        self.__crossedOut = crossedOut

    def setCrossOutTime(self,  crossOutTime):
        if isinstance(crossOutTime,  (float,  int)):
            if crossOutTime == 0:
                self.__crossOutTime = QDateTime()
            else:
                self.__crossOutTime = QDateTime.fromTime_t(int(crossOutTime))
        elif isinstance(crossOutTime,  QDateTime):
            self.__crossOutTime = crossOutTime
        else:
            assert False,  "expected a float, QDateTime or int"

    def id(self):
        return self.__id

    def idOnPhone(self):
        return self.__idOnPhone

    def device(self):
        return self.__device

    def type(self):
        return self.__type

    def content(self):
        return self.__content

    def location(self):
        return self.__location

    def realStartTime(self):
            return self.__realStartTime or self.__startTime

    def realEndTime(self):
        return self.__realEndTime or self.__endTime

    def startTime(self):
        return self.__startTime

    def endTime(self):
        return self.__endTime

    def lastModified(self):
        return self.__lastModified

    def replication(self):
        return self.__replication

    def alarm(self):
        return self.__alarm

    def priority(self):
        return self.__priority

    def repeatType(self):
        return self.__repeatType

    def repeatDays(self):
        return self.__repeatDays

    def repeatExceptions(self):
        return self.__repeatExceptions

    def repeatStart(self):
        return self.__repeatStart

    def repeatEnd(self):
        return self.__repeatEnd

    def repeatInterval(self):
        return self.__repeatInterval

    def crossedOut(self):
        return self.__crossedOut

    def crossOutTime(self):
        return self.__crossOutTime

    def recurs(self):
        return bool(self.repeatType())

    def recurrenceParsedDaysFromEntry(self):
        return self.recurrenceParsedDays(self.repeatType(),  self.repeatDays())

    @staticmethod
    def typeString(type):
        if type == "anniversary":
            return QCoreApplication.translate("CalendarEntry",  "Anniversary/Birthday")
        elif type == "appointment":
            return QCoreApplication.translate("CalendarEntry",  "Appointment")
        elif type == "event":
            return QCoreApplication.translate("CalendarEntry",  "Memo")
        elif type == "todo":
            return QCoreApplication.translate("CalendarEntry",  "To-do")

    @staticmethod
    def recurrenceParsedDays(type,  days):

        ### PLEASE COPY CHANGES IN THIS FUNCTION ALSO TO
        ### mobile/mobile.py, function calendarEntryParseDays

        if type in ("weekly",   "monthly_by_dates"):
            # 0,1,2 -> [0, 1, 2]
            return [int(day) for day in days.split(',')]
        if type == "monthly_by_days":
            # week:1,day:1;week:4,day:0 -> [{'week': 1, 'day': 1}, {'week': 4, 'day': 0}]
            dates = []
            for date in days.split(";"):
                tmp = dict()
                for sub in date.split(","):
                    key, value = sub.split(":")
                    tmp[key] = int(value)
                dates.append(tmp)
            return dates
        if type == "yearly_by_day":
            # week:1,day:1,month:1 -> {'week': 1, 'day': 1, 'month': 1}
            dates = {}
            for subentry in days.split(","):
                key,  value = subentry.split(":")
                dates[key] = int(value)
            return dates

    def next(self,  date,  fallbackDateMethod = FallbackDate.ShowBefore):
        def monthsTo(fromDate, toDate):
            months = 0
            date = fromDate.addDays(0) # make a copy ;)
            while date < toDate:
                months += 1
                date = date.addMonths(1)
            return months

        def checkMonth(month,  day):
            if day > month.daysInMonth():
                if fallbackDateMethod == FallbackDate.ShowBefore:
                    return month.daysInMonth() - day
                elif fallbackDateMethod == FallbackDate.ShowAfterwards:
                    return -(day - month.daysInMonth() - 1)
            return 0

        def daysDictToDay(days,  date):
            # days is a dict in the following form: {'week': 4, 'day': 0}
            # date is a QDate
            firstDayInMonth = date.addDays(-date.day()+1)
            firstDayOfWeek = firstDayInMonth.dayOfWeek()-1
            if days['day'] >= firstDayOfWeek:
                day = firstDayInMonth.addDays(days['day'] - firstDayOfWeek)
            else:
                # go to next monday..
                day = firstDayInMonth.addDays(7 - firstDayOfWeek)
                day = day.addDays(days['day'])
            day = day.addDays(7*days['week'])

            if day.month() != date.month():
                # Oops, there aren't so many weeks with this weekday in this month
                return None

            return day.day()-1

        def weekInMonth(date):
            firstDayInMonth = date.addDays(-date.day()+1)
            firstDayOfWeek = firstDayInMonth.dayOfWeek()
            week = (date.day() - date.dayOfWeek() + firstDayOfWeek - 1) / 7
            if date.dayOfWeek() >= firstDayOfWeek:
                week += 1
            return week

        if not self.repeatType():
            return None

        if self.repeatEnd().isValid() and date > self.repeatEnd():
            return None

        #if date < self.repeatStart():
        #    return self.repeatStart()

        first = max(date,  self.repeatStart())
        dt = self.repeatStart().daysTo(first)
        days = self.recurrenceParsedDaysFromEntry()

        if self.repeatType() == "daily":
            daysAfterLast = dt % self.repeatInterval()
            daysToNext = self.repeatInterval() - daysAfterLast
            next = first.addDays(daysToNext)

        elif self.repeatType() == "weekly":
            currentDay = first.date().dayOfWeek()-1 # Qt weekdays are from 1 to 7,S60 weekdays from 0 to 6

            dt += self.repeatStart().date().dayOfWeek()-1 # pretend that the event starts on Monday
            dt -= currentDay # pretend that we are currently at the beginning of the week (Monday)
            week = dt / 7
            weeksAfterLast = week % self.repeatInterval()
            if weeksAfterLast > 0:
                # There is no event in the current week...
                weeksToNext = self.repeatInterval() - weeksAfterLast
                intervalDays = 7 * weeksToNext
                daysToNext = intervalDays
                daysToNext += min(days) - currentDay
            else:
                # There is an event in the current week...
                daysInWeek = [item for item in days if item>currentDay]
                if daysInWeek:
                    daysToNext = min(daysInWeek) - currentDay
                else:
                    # We missed the event
                    daysToNext = 7 * self.repeatInterval() + min(days) - currentDay
            next = first.addDays(daysToNext)

        elif self.repeatType() == "monthly_by_dates":
            currentDay = first.date().day()-1 # Qt days are from 1 to 7,S60 weekdays from 0 to 6

            dt += self.repeatStart().date().day()-1 # pretend that the event starts on the 1st
            dt -= currentDay # pretend that we are currently at the beginning of the month (1st)
            month = monthsTo(self.repeatStart(),  self.repeatStart().addDays(dt))
            monthsAfterLast = month % self.repeatInterval()
            if monthsAfterLast > 0:
                # There is no event in the current month...
                monthsToNext = self.repeatInterval() - monthsAfterLast
                nextMonth = first.addMonths(monthsToNext)
                intervalDays = first.daysTo(nextMonth) + checkMonth(nextMonth.date(),  min(days)+1)
                daysToNext = intervalDays
                daysToNext += min(days) - currentDay
            else:
                # There is an event in this month...
                daysInMonth = [item for item in days if item>currentDay]
                if daysInMonth:
                    month = QDate(first.date().year(),  first.date().month(),  1)
                    daysToNext = min(daysInMonth) - currentDay + checkMonth(month,  min(daysInMonth)+1)
                else:
                    # We missed the event
                    eventMonth = first.addMonths(self.repeatInterval())
                    eventMonth = eventMonth.addDays(-eventMonth.date().day() + 1)
                    daysToEventMonth = first.daysTo(eventMonth) + checkMonth(eventMonth.date(),  min(days)+1)
                    daysToNext = daysToEventMonth + min(days)

            if daysToNext == 0:
                # This happens when checkMonth return -1, and this would result in an endless loop
                return self.next(first.addDays(1))
            next = first.addDays(daysToNext)

        elif self.repeatType() == "monthly_by_days":
            currentDay = first.date().day()-1 # Qt days are from 1 to 31,S60 weekdays from 0 to 30
            currentDayOfWeek = first.date().dayOfWeek()-1 # Qt weekdays are from 1 to 7,S60 weekdays from 0 to 6

            dt += self.repeatStart().date().day()-1 # pretend that the event starts on the 1st
            dt -= currentDay # pretend that we are currently at the beginning of the month (1st)
            month = monthsTo(self.repeatStart(),  self.repeatStart().addDays(dt))
            monthsAfterLast = month % self.repeatInterval()
            if monthsAfterLast > 0:
                # There is no event in the current month...
                monthsToNext = self.repeatInterval() - monthsAfterLast
                nextMonth = first.addMonths(monthsToNext)
                intervalDays = first.daysTo(nextMonth)
                daysToNext = intervalDays
                firstEntry = filter(lambda item: daysDictToDay(item,  nextMonth.date()) is not None,  days)
                if firstEntry:
                    firstEntry = min(firstEntry, key=lambda item: daysDictToDay(item,  nextMonth.date()))
                    dayInMonth = daysDictToDay(firstEntry, nextMonth.date())
                    daysToNext += dayInMonth - currentDay
                else:
                    # The event would already be in the next month..
                    return self.next(first.addDays(first.date().daysInMonth() - first.date().day() + 1))
            else:
                # There is an event in this month...
                # get the current week
                #week = weekInMonth(first.date())
                #possibleDates = filter(lambda item:
                #                            (item['week']>weekInMonth(first.date().addDays(item['day'] - first.date().dayOfWeek() + 1))) or
                #                            (item['week']==week and item['day']>currentDayOfWeek),
                #                days)
                possibleDates = filter(lambda item: daysDictToDay(item,  first.date())>currentDay,  days)
                if possibleDates:
                    nextDate = min(possibleDates,  key=lambda item: daysDictToDay(item,  first.date()))
                    dayInMonth = daysDictToDay(nextDate,  first.date())
                    daysToNext = dayInMonth - currentDay
                else:
                    # We missed the event
                    eventMonth = first.addMonths(self.repeatInterval())
                    daysToEventMonth = first.daysTo(eventMonth)
                    firstEntry = filter(lambda item: daysDictToDay(item,  eventMonth.date()) is not None,  days)
                    if firstEntry:
                        firstEntry = min(firstEntry, key=lambda item: daysDictToDay(item,  eventMonth.date()))
                        daysToNext = daysToEventMonth + daysDictToDay(firstEntry, eventMonth.date())  - currentDay
                    else:
                        # The event would already be in the next month..
                        return self.next(first.addDays(first.date().daysInMonth() - first.date().day() + 1))
            next = first.addDays(daysToNext)

        elif self.repeatType() == "yearly_by_date":
            if first.date().month() > self.repeatStart().date().month() \
                or first.date().month() == self.repeatStart().date().month() and first.date().day() >= self.repeatStart().date().day():
                # The next event is next year
                year = first.date().year() + 1
            else:
                year = first.date().year()

            firstYear = self.repeatStart().date().year()
            nextYear = year + (firstYear-year) % self.repeatInterval()

            next = QDateTime(nextYear,  self.repeatStart().date().month(),  self.repeatStart().date().day(),  self.repeatStart().time().hour(), self.repeatStart().time().minute())

        elif self.repeatType() == "yearly_by_day":
            if first.date().month() > days['month']+1 \
                or first.date().month() == days['month']+1 and first.date().day() >= self.repeatStart().date().day():
                # The next event is next year
                year = first.date().year() + 1
            else:
                year = first.date().year()

            firstYear = self.repeatStart().date().year()
            nextYear = year + (firstYear-year) % self.repeatInterval()

            # HACK! Get the right date using the repeat type monthly_by_days
            oldInterval = self.__repeatInterval
            oldType = self.__repeatType
            oldDays = self.__repeatDays

            self.__repeatInterval = 1
            self.__repeatType = "monthly_by_days"
            self.__repeatDays = "week:" + str(days['week']) + ",day:" + str(days['day'])

            nextDate = QDateTime(nextYear,  days['month']+1,  1,  0,  0)

            next = self.next(nextDate)

            self.__repeatInterval = oldInterval
            self.__repeatType = oldType
            self.__repeatDays = oldDays

        if self.repeatEnd().isValid() and next > self.repeatEnd():
            return None

        if self.repeatExceptions() and next in [QDateTime.fromTime_t(int(date)) for date in self.repeatExceptions().split(",")]:
            return self.next(next)

        return next

class MessageStates(object):
    def __init__(self,  states=list()):
        # self.__states = states
        self.__states = list()
        self.__state = MessageState.Unknown

    def __repr__(self):
        return "MessageStates(%s)" % self.__states

    def __iter__(self):
        for i in self.__states:
            yield i

    def addState(self, state, message="",  date=None):
        if not date:
            date = QDateTime.currentDateTime()
        tmp = [date, state,  message]
        self.__states.append(tmp)
        if state != MessageState.Unknown:
            self.__state = state
        return tmp

    def created(self):
        return self.__state == MessageState.Created

    def sending(self):
        return self.__state == MessageState.Sending

    def pending(self):
        return self.__state == MessageState.Pending

    def sendOk(self):
        return self.__state == MessageState.SendOk

    def sendFailed(self):
        return self.__state == MessageState.SendFailed

    def states(self):
        for i in self.__states:
            yield i

class Message(QObject):
    def __init__(self, id = 0,  idOnPhone = 0,  type = MessageType.Unknown, priority = MessagePriority.Medium,  \
                  device = Device(),  contact = Contact(), states = MessageStates(),  dateTime = 0,  message = ""):
        super(Message,  self).__init__()

        self.setContact(contact)
        self.setDevice(device)
        self.setStates(MessageStates())

        self.setId(id)
        self.setIdOnPhone(idOnPhone)
        self.setType(type)
        self.setPriority(priority)
        self.setDateTime(dateTime)
        self.setMessage(message)

    def __repr__(self):
        return "Message(%i, %i, %r, %r, %r, %r, %r, %r, %r)" % (self.__id,  self.__idOnPhone,  self.__type,
                    self.__priority,  self.__device,  self.__contact, self.__states, self.__dateTime, self.__message)

    def __cmp__(self,  b):
        if self.id() and b.id():
            return self.id() - b.id()
        elif self.idOnPhone() and b.idOnPhone():
            return self.idOnPhone() - b.idOnPhone()
        else:
            return -1

    def setId(self,  id):
        assert isinstance(id,  int),  "expected an int"
        self.__id = id

    def setIdOnPhone(self,  idOnPhone):
        assert isinstance(idOnPhone,  int),  "expected an int"
        self.__idOnPhone = idOnPhone

    def setType(self,  _type):
        assert isinstance(_type,  int),  "expected an int"
        self.__type = _type

    def setPriority(self,  priority):
        assert isinstance(priority,  int),  "expected an int"
        self.__priority = priority

    def setDevice(self,  device):
        assert isinstance(device,  Device),  "expected a Device instance"
        self.__device = device

    def setContact(self,  contact):
        assert type(contact) == type(Contact()),  "expected a Contact instance"
        self.__contact = contact

    def setStates(self, states):
        assert isinstance(states,  MessageStates),  "expected a MessageStates instance"
        self.__states = states

    def setDateTime(self,  dateTime):
        if isinstance(dateTime,  (float,  int)):
            self.__dateTime = QDateTime.fromTime_t(int(dateTime))
        elif isinstance(dateTime,  QDateTime):
            self.__dateTime = dateTime
        else:
            assert False,  "expected a float, QDateTime or int"

    def setMessage(self,  message):
        assert isinstance(message,  basestring),  "expected a string or unicode"
        self.__message = message

    def addState(self,  state, message="",  date=None):
        last = self.states().addState(state,  message,  date)
        self.emit(SIGNAL("messageStateAdded"),  self,  last)

    def id(self):
        return self.__id

    def idOnPhone(self):
        return self.__idOnPhone

    def type(self):
        return self.__type

    def priority(self):
        return self.__priority

    def device(self):
        return self.__device

    def contact(self):
        return self.__contact

    def states(self):
        return self.__states

    def dateTime(self):
        return self.__dateTime

    def message(self):
        return self.__message

    def messageForPhone(self):
        return self.__message.replace(u'\n', u'\u2029') # LINE FEED (\u000a) replaced by PARAGRAPH SEPARATOR (\u2029)

class StatisticsRequest(object):
    def __init__(self,  statisticFor = StatisticFor.Unknown,  contact = Contact(),  period = StatisticPeriod.Unknown,  \
                 type = MessageType.Unknown,  start = None,  duration = None, orderBy = StatisticOrderBy.Number,  \
                 year = None,  month = None,  day = None):

        self.setStatisticFor(statisticFor)
        self.setContact(contact)
        self.setPeriod(period)
        self.setType(type)
        self.setRange(start, duration)
        self.setOrderBy(orderBy)
        self.setYear(year)
        self.setMonth(month)
        self.setDay(day)

    def __nonzero__(self):
        return self.statisticsFor() != StatisticFor.Unknown

    def setStatisticFor(self,  statisticFor):
        assert isinstance(statisticFor,  int),  "expected an int"
        self.__statisticsFor = statisticFor

    def setContact(self,  contact):
        assert isinstance(contact,  Contact),  "expected a Contact instance"
        self.__contact = contact

    def setPeriod(self,  period):
        assert isinstance(period,  int),  "expected a QDateTime instance"
        self.__period = period

    def setType(self,  _type):
        assert isinstance(_type,  int),  "expected an int"
        self.__type = _type

    def setRange(self,  start,  duration):
        assert type(start) in  [ type(int()), type(None) ],  "expected an int or NoneType"
        assert type(duration) in  [ type(int()), type(None) ],  "expected an int or NoneType"
        self.__start = start
        self.__duration = duration

    def setOrderBy(self,  orderBy):
        assert isinstance(orderBy,  int),  "expected an int"
        self.__orderBy = orderBy

    def setYear(self,  year):
        assert type(year) in  [ type(int()), type(None) ],  "expected an int or NoneType"
        self.__year = year

    def setMonth(self,  month):
        assert type(month) in  [ type(int()), type(None) ],  "expected an int or NoneType"
        self.__month = month

    def setDay(self,  day):
        assert type(day) in  [ type(int()), type(None) ],  "expected an int or NoneType"
        self.__day = day

    def statisticsFor(self):
        return self.__statisticsFor

    def contact(self):
        return self.__contact

    def period(self):
        return self.__period

    def type(self):
        return self.__type

    def range(self):
        return self.__start,  self.__duration

    def orderBy(self):
        return self.__orderBy

    def year(self):
        return self.__year

    def month(self):
        return self.__month

    def day(self):
        return self.__day

class StatisticResponseLine(object):
    def __init__(self,  values):
        self.__values = values

    def __str__(self):
        return "StatisticResponseLine('%s')" % repr(self.__values)

    def year(self):
        return self.__values[0]

    def month(self):
        return self.__values[1]

    def day(self):
        return self.__values[2]

    def weekday(self):
        return self.__values[3]

    def hour(self):
        return self.__values[4]

    def incoming(self):
        return self.__values[5]

    def outgoing(self):
        return self.__values[6]

    def total(self):
        return self.__values[7]

class StatisticResponse(object):
    def __init__(self,  request):
        self.__values = list()
        self.__request = request
        self.__containsChecked = False
        self.__year = False
        self.__month = False
        self.__day = False
        self.__weekday = False
        self.__hour = False
        self.__incoming = False
        self.__outgoing = False
        self.__total = False

    def __len__(self):
        return len(self.__values)

    def __getitem__(self,  key):
        return self.__values[key]

    def __iter__(self):
        for item in self.__values:
            yield item

    def __bool__(self):
        return len(self) != 0

    def append(self,  year,  month,  day,  weekday,  hour,  incoming,  outgoing,  total):
        self.__values.append( StatisticResponseLine( [year,  month,  day,  weekday,  hour,  incoming,  outgoing,  total] ) )

        if not self.__containsChecked:
            self.__year = year != None
            self.__month = month != None
            self.__day = day != None
            self.__weekday = weekday != None
            self.__hour = hour != None
            self.__incoming = incoming != None
            self.__outgoing = outgoing != None
            self.__total = total != None

            self.__containsChecked = True

    def request(self):
        return self.__request

    def values(self):
        for i in self.__values:
            yield i

    def containsYear(self):
        return self.__year

    def containsMonth(self):
        return self.__month

    def containsDay(self):
        return self.__day

    def containsWeekday(self):
        return self.__weekday

    def containsHour(self):
        return self.__hour

    def containsIncoming(self):
        return self.__incoming

    def containsOutgoing(self):
        return self.__outgoing

    def containsTotal(self):
        return self.__total

