# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

import re
import datetime
import codecs
import base64
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from lib.classes import *
import lib.export_general

try:
    import matplotlib.figure
    import matplotlib.font_manager
    import matplotlib.backend_bases
except ImportError:
    USE_MATPLOTLIB = False
else:
    USE_MATPLOTLIB= True

class HTMLTemplateParser(object):
    """Helper class for parsing HTML templates"""
    @staticmethod
    def getIf(condition,  string):
        regex =  re.compile(
            re.escape("<!--[if " + condition + "]-->") +
            r"(.*)" +
            re.escape("<!--[endif " + condition + "]-->"),  re.DOTALL)
        match = regex.search(string).groups()[0]

        ret = match.split("<!--[else " + condition + "]-->")
        if len(ret) > 1:
            return [ret[0],  ret[1]]
        else:
            return [ret[0],  None]

    @staticmethod
    def getForeach(condition,  string):
        regex = re.compile(
            re.escape("<!--[foreach " + condition + "]-->") +
            r"(.*)" +
            re.escape("<!--[/foreach " + condition + "]-->"),  re.DOTALL)

        return regex.search(string).groups()[0]

    @staticmethod
    def replaceIf(condition,  string,  fulfilled = True):
        if_,  else_ = HTMLTemplateParser.getIf(condition,  string)
        if fulfilled:
            string = string.replace("<!--[if " + condition + "]-->",  "")
            if else_ == None:
                return string.replace("<!--[endif " + condition + "]-->", "")
            else:
                return string.replace("<!--[else " + condition + "]-->" + else_ + "<!--[endif " + condition + "]-->", "")
        else:
            string = string.replace("<!--[if " + condition + "]-->" +  if_,  "")
            if else_ != None:
                string = string.replace("<!--[else " + condition + "]-->",  "")
            return string.replace("<!--[endif " + condition + "]-->",  "")

    @staticmethod
    def replaceForeach(condition,  replacement,  string):
        return string.replace("<!--[foreach " + condition + "]-->" + HTMLTemplateParser.getForeach(condition,  string) +
                              "<!--[/foreach " + condition + "]-->",  replacement)

    @staticmethod
    def replaceVar(variable,  value,  string):
        return string.replace("<!--[var " + variable + "]-->",  value)

    @staticmethod
    def escape(text):
        html_escape_table = {
            "&": "&amp;",
            "\"": "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
            }

        return "".join(html_escape_table.get(c,  c) for c in text)

class FilelistAnalyzer(object):
    """Helper class for file manegement"""
    @staticmethod
    def nextDay(filelist,  currentFile):
        currentFile = currentFile.split("_")[1:]
        currentYear = int(currentFile[0])
        currentMonth = int(currentFile[1])
        currentDay = int(currentFile[2])

        for file in sorted(filelist):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])
            day = int(split[2])

            if year == currentYear and month == currentMonth and day > currentDay:
                return (year,  month,  day,  file)

        for file in sorted(filelist):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])
            day = int(split[2])

            if year == currentYear and month > currentMonth:
                return (year,  month,  day,  file)

        for file in sorted(filelist):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])
            day = int(split[2])

            if year > currentYear:
                return (year,  month,  day,  file)

        return (None,  None,  None,  None)

    @staticmethod
    def lastDay(filelist,  currentFile):
        currentFile = currentFile.split("_")[1:]
        currentYear = int(currentFile[0])
        currentMonth = int(currentFile[1])
        currentDay = int(currentFile[2])

        for file in sorted(filelist,  reverse=True):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])
            day = int(split[2])

            if year == currentYear and month == currentMonth and day < currentDay:
                return (year,  month,  day,  file)

        for file in sorted(filelist,  reverse=True):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])
            day = int(split[2])

            if year == currentYear and month < currentMonth:
                return (year,  month,  day,  file)

        for file in sorted(filelist,  reverse=True):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])
            day = int(split[2])

            if year < currentYear:
                return (year,  month,  day,  file)

        return (None,  None,  None,  None)

    @staticmethod
    def nextMonth(filelist,  currentFile):
        currentFile = currentFile.split("_")[1:]
        currentYear = int(currentFile[0])
        currentMonth = int(currentFile[1])

        for file in sorted(filelist):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])

            if year == currentYear and month > currentMonth:
                return (year,  month,  file)

        for file in sorted(filelist):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])

            if year > currentYear:
                return (year,  month,  file)

        return (None,  None,  None)

    @staticmethod
    def lastMonth(filelist,  currentFile):
        currentFile = currentFile.split("_")[1:]
        currentYear = int(currentFile[0])
        currentMonth = int(currentFile[1])

        for file in sorted(filelist,  reverse=True):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])

            if year == currentYear and month < currentMonth:
                return (year,  month,  file)

        for file in sorted(filelist,  reverse=True):
            split = file.split("_")[1:]
            year = int(split[0])
            month = int(split[1])

            if year < currentYear:
                return (year,  month,  file)

        return (None,  None,  None)

    @staticmethod
    def dayHasMessages(filelist,  year,  month,  day):
        return "Messages_" + str(year) + "_" + str(month).zfill(2) + "_" + str(day).zfill(2) in filelist

    @staticmethod
    def nextYear(filelist,  currentFile):
        currentFile = currentFile.split("_")[1:]
        currentYear = int(currentFile[0])

        for file in sorted(filelist):
            split = file.split("_")[1:]
            year = int(split[0])

            if year > currentYear:
                return (year,  file)

        return (None,  None)

    @staticmethod
    def lastYear(filelist,  currentFile):
        currentFile = currentFile.split("_")[1:]
        currentYear = int(currentFile[0])

        for file in sorted(filelist,  reverse=True):
            split = file.split("_")[1:]
            year = int(split[0])

            if year < currentYear:
                return (year,  file)

        return (None,  None)

    @staticmethod
    def monthHasMessages(filelist,  year,  month):
        for file in filelist:
            if file.startswith("Messages_" + str(year) + "_" + str(month).zfill(2)):
                return True
        return False

    @staticmethod
    def firstFileInMonth(filelist,  year,  month):
        for file in sorted(filelist):
            if file.startswith("Messages_" + str(year) + "_" + str(month).zfill(2)):
                return file
        return None

class HTMLFormatter(lib.export_general.GeneralFormatter):
    def __init__(self,  parent,  main,  exportProgressDialog,  *args,  **kwargs):
        lib.export_general.GeneralFormatter.__init__(self,  parent,  main,  exportProgressDialog,  *args,  **kwargs)

        self.main = main
        self.database = main.database
        self.helper = main.helper

        self.lastFile = QFile()
        self.tempSearch = ""
        self.tempString = ""
        self.tempFile = ""

        # Files
        self.fMessages = self.helper.findFolder("messages.html", "data",  ["export-templates",  "default"])
        self.fContacts = self.helper.findFolder("contacts.html", "data",  ["export-templates",  "default"])
        self.fIndex = self.helper.findFolder("index.html", "data",  ["export-templates",  "default"])
        self.fStylesheet = self.helper.findFolder("style.css", "data",  ["export-templates",  "default"])

        # Templates
        self.tMessage = codecs.open(self.fMessages,  'r',  'utf-8').read()
        self.tContacts = codecs.open(self.fContacts,  'r',  'utf-8').read()
        self.tIndex = codecs.open(self.fIndex,  'r',  'utf-8').read()
        self.tStylesheet = codecs.open(self.fStylesheet,  'r',  'utf-8').read()

        # Global strings
        self.tMessage = HTMLTemplateParser.replaceVar("homepage",  unicode(self.tr("Homepage")),  self.tMessage)
        self.tMessage = HTMLTemplateParser.replaceVar("messages",  unicode(self.tr("Messages")),  self.tMessage)
        self.tMessage = HTMLTemplateParser.replaceVar("contacts",  unicode(self.tr("Contacts")),  self.tMessage)
        self.tMessage = HTMLTemplateParser.replaceVar("homepage_link",  "../index.html", self.tMessage)
        self.tMessage = HTMLTemplateParser.replaceVar("messages_link",  "../messages/index.html", self.tMessage)
        self.tMessage = HTMLTemplateParser.replaceVar("contacts_link",  "../contacts/index.html", self.tMessage)

        self.tContacts = HTMLTemplateParser.replaceVar("homepage",  unicode(self.tr("Homepage")),  self.tContacts)
        self.tContacts = HTMLTemplateParser.replaceVar("messages",  unicode(self.tr("Messages")),  self.tContacts)
        self.tContacts = HTMLTemplateParser.replaceVar("contacts",  unicode(self.tr("Contacts")),  self.tContacts)
        self.tContacts = HTMLTemplateParser.replaceVar("homepage_link",  "../index.html", self.tContacts)
        self.tContacts = HTMLTemplateParser.replaceVar("messages_link",  "../messages/index.html", self.tContacts)
        self.tContacts = HTMLTemplateParser.replaceVar("contacts_link",  "../contacts/index.html", self.tContacts)

        self.tIndex = HTMLTemplateParser.replaceVar("homepage",  unicode(self.tr("Homepage")),  self.tIndex)
        self.tIndex = HTMLTemplateParser.replaceVar("messages",  unicode(self.tr("Messages")),  self.tIndex)
        self.tIndex = HTMLTemplateParser.replaceVar("contacts",  unicode(self.tr("Contacts")),  self.tIndex)

        if USE_MATPLOTLIB:
            self.fig = matplotlib.figure.Figure(figsize = (10, 4), dpi=100, facecolor = '#FFFFFF')
            self.ax = self.fig.add_subplot(111, sharex = None, sharey = None)
            self.canvas = matplotlib.backend_bases.FigureCanvasBase(self.fig)
            self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)

            self.request = StatisticsRequest()
            self.request.setStatisticFor(StatisticFor.Periods)
            self.request.setPeriod(StatisticPeriod.YearsAndMonths)
            self.request.setType(MessageType.All)

    @staticmethod
    def format():
        return "HTML"

    @staticmethod
    def supportedExportItems():
        return ExportItems.Contacts | ExportItems.Messages

    @staticmethod
    def supportedExportOptions():
        return ExportOptions.Period | ExportOptions.Order | ExportOptions.Graph | ExportOptions.GraphFormat | \
                    ExportOptions.Legend | ExportOptions.Thumbnails

    @staticmethod
    def extraExportOptions():
        return ExportExtraOptions.WriteCalendar | ExportExtraOptions.ContactsInSeperateFiles

    @staticmethod
    def fileExtension():
        return "html"

    def initialize(self):
        # Create needed directorys
        if not QDir(self.directory).exists():
            QDir().mkdir(self.directory)

        if not QDir(self.directory + "messages").exists():
            QDir(self.directory).mkdir("messages")

        if not QDir(self.directory + "thumbnails").exists() and self.thumbnails == ExportThumbnails.Yes:
            QDir(self.directory).mkdir("thumbnails")

        if not QDir(self.directory + "contacts").exists() and self.contacts != ExportContacts.None_:
            QDir(self.directory).mkdir("contacts")

        if not QDir(self.directory + "graph").exists() and self.graph == ExportGraph.Yes:
            QDir(self.directory).mkdir("graph")

        style = codecs.open(self.directory + 'style.css',  'w',  'utf-8')
        style.write(self.tStylesheet)
        style.close()

        return True

    def openMessageFile(self,  filename):
        self.lastFile = codecs.open(self.directory + 'messages/' + filename + '.html',  'w',  'utf-8')

        html = self.tMessage
        html = HTMLTemplateParser.replaceVar("headline",  unicode(self.tr("Exported messages")),  html)
        html = HTMLTemplateParser.replaceVar("pagetitle",  self.periodString(),  html)
        html = HTMLTemplateParser.replaceVar("caption",  self.periodString(),  html)
        html = HTMLTemplateParser.replaceIf("statistics_image",  html,  False)

        self.tempFile = html
        self.tempSearch = HTMLTemplateParser.getForeach("message",  self.tMessage)
        self.tempString = ""

        return True

    def writeCalender(self,  filename):
        file_ = codecs.open(self.directory + 'messages/' + filename + '.html',  'r',  'utf-8')
        content = file_.read()
        file_.close()

        if not self.files:
            # When there are no messages a calendar is useless...
            content = HTMLTemplateParser.replaceIf("calendar_sidebar",  content,  False)
            content = HTMLTemplateParser.replaceIf("last_page",  content,  False)
            content = HTMLTemplateParser.replaceIf("next_page",  content,  False)
        elif self.period == ExportPeriod.All:
            # Do not show a calendar when all messages are in one file
            content = HTMLTemplateParser.replaceIf("calendar_sidebar",  content,  False)
            content = HTMLTemplateParser.replaceIf("last_page",  content,  False)
            if filename == 'index':
                content = HTMLTemplateParser.replaceIf("next_page",  content,  True)
                content = HTMLTemplateParser.replaceVar("next_page_link",  "Messages.html",  content)
                content = HTMLTemplateParser.replaceVar("string_next_page",  unicode(self.tr("Next")),  content)
                content = HTMLTemplateParser.replaceVar("next_page",  unicode(self.tr("All messages")),  content)
            else:
                content = HTMLTemplateParser.replaceIf("next_page",  content,  False)
        else:
            files = self.files
            file = filename
            if filename == 'index':
                file = sorted(files)[0] # Change name to get a right date

            year = int(file.split("_")[1])
            if self.period == ExportPeriod.Daily or self.period == ExportPeriod.Monthly:
                month = int(file.split("_")[2])
            if self.period == ExportPeriod.Daily:
                day = int(file.split("_")[3])

            content = HTMLTemplateParser.replaceIf("calendar_sidebar",  content)

            if self.period != ExportPeriod.Daily:
                content = HTMLTemplateParser.replaceForeach("day_calendar",  "",  content)
            else:
                currentDate = QDate(year,  month,  1)
                dayCalendar = HTMLTemplateParser.getForeach("day_calendar",  content)
                dayCalendar = HTMLTemplateParser.replaceVar("month",  unicode(currentDate.toString("MMMM yyyy")),  dayCalendar)

                lastYear,  lastMonth,  lastFile = FilelistAnalyzer.lastMonth(files,  file)
                nextYear,  nextMonth,  nextFile = FilelistAnalyzer.nextMonth(files,  file)

                if lastFile:
                    dayCalendar = HTMLTemplateParser.replaceIf("last_month",  dayCalendar,  True)
                    dayCalendar = HTMLTemplateParser.replaceVar("back_month_link", lastFile + ".html",  dayCalendar)
                else:
                    dayCalendar = HTMLTemplateParser.replaceIf("last_month",  dayCalendar,  False)

                if nextFile:
                    dayCalendar = HTMLTemplateParser.replaceIf("next_month",  dayCalendar,  True)
                    dayCalendar = HTMLTemplateParser.replaceVar("next_month_link", nextFile + ".html",  dayCalendar)
                else:
                    dayCalendar = HTMLTemplateParser.replaceIf("next_month",  dayCalendar,  False)

                dayCalendar = HTMLTemplateParser.replaceVar("string_monday_short",  unicode(self.main.locale.standaloneDayName(1, QLocale.ShortFormat)),  dayCalendar)
                dayCalendar = HTMLTemplateParser.replaceVar("string_tuesday_short",  unicode(self.main.locale.standaloneDayName(2, QLocale.ShortFormat)),  dayCalendar)
                dayCalendar = HTMLTemplateParser.replaceVar("string_wednesday_short",  unicode(self.main.locale.standaloneDayName(3, QLocale.ShortFormat)),  dayCalendar)
                dayCalendar = HTMLTemplateParser.replaceVar("string_thursday_short",  unicode(self.main.locale.standaloneDayName(4, QLocale.ShortFormat)),  dayCalendar)
                dayCalendar = HTMLTemplateParser.replaceVar("string_friday_short",  unicode(self.main.locale.standaloneDayName(5, QLocale.ShortFormat)),  dayCalendar)
                dayCalendar = HTMLTemplateParser.replaceVar("string_saturday_short",  unicode(self.main.locale.standaloneDayName(6, QLocale.ShortFormat)),  dayCalendar)
                dayCalendar = HTMLTemplateParser.replaceVar("string_sunday_short",  unicode(self.main.locale.standaloneDayName(7, QLocale.ShortFormat)),  dayCalendar)

                if currentDate.dayOfWeek()== 1:
                    currentDate = currentDate.addDays(-7)

                for weekday in range(0,  currentDate.dayOfWeek()-1):
                    currentDate = currentDate.addDays(-1)

                monthString = ""
                weekLine = HTMLTemplateParser.getForeach("week",  dayCalendar)
                dayLine = HTMLTemplateParser.getForeach("day",  weekLine)
                for week in range(6):
                # 6 weeks per month
                    weekString = weekLine
                    weekTemp = ""
                    for dayInWeek in range(7):
                        dayString = dayLine
                        # 7 days per week
                        dayString = HTMLTemplateParser.replaceVar("day",  str(currentDate.day()),  dayString)
                        dayString = HTMLTemplateParser.replaceIf("day_in_other_month",  dayString,  currentDate.month() != month)
                        dayHasMessages = FilelistAnalyzer.dayHasMessages(files,  currentDate.year(),  currentDate.month(),  currentDate.day())
                        dayString = HTMLTemplateParser.replaceIf("day_has_messages",  dayString,  dayHasMessages)
                        if dayHasMessages:
                            link = "Messages_" + str(currentDate.year()) + "_" + \
                                        str(currentDate.month()) .zfill(2) + "_" + str(currentDate.day()).zfill(2)+ ".html"
                            dayString = HTMLTemplateParser.replaceVar("day_link",  link,  dayString)
                            if currentDate.month() == month:
                                dayString = HTMLTemplateParser.replaceIf("current_day",  dayString,
                                                                 currentDate.day() == day and filename != 'index')
                        weekTemp += dayString
                        currentDate = currentDate.addDays(1)
                    weekString = HTMLTemplateParser.replaceForeach("day",  weekTemp,  weekString)
                    monthString += weekString

                dayCalendar = HTMLTemplateParser.replaceForeach("week",  monthString,  dayCalendar)
                content = HTMLTemplateParser.replaceForeach("day_calendar",  dayCalendar,  content)

            monthCalendar = HTMLTemplateParser.getForeach("month_calendar",  content)
            monthCalendar = HTMLTemplateParser.replaceVar("year",  str(year),  monthCalendar)

            lastYear,  lastFile = FilelistAnalyzer.lastYear(files,  file)
            nextYear,  nextFile = FilelistAnalyzer.nextYear(files,  file)

            if lastFile:
                monthCalendar = HTMLTemplateParser.replaceIf("last_year",  monthCalendar,  True)
                monthCalendar = HTMLTemplateParser.replaceVar("back_year_link", lastFile + ".html",  monthCalendar)
            else:
                monthCalendar = HTMLTemplateParser.replaceIf("last_year",  monthCalendar,  False)

            if nextFile:
                monthCalendar = HTMLTemplateParser.replaceIf("next_year",  monthCalendar,  True)
                monthCalendar = HTMLTemplateParser.replaceVar("next_year_link", nextFile + ".html",  monthCalendar)
            else:
                monthCalendar = HTMLTemplateParser.replaceIf("next_year",  monthCalendar,  False)

            halfyearLine = HTMLTemplateParser.getForeach("six_months",  monthCalendar)
            monthLine = HTMLTemplateParser.getForeach("month",  halfyearLine)
            yearString = ""
            for halfYear in range(2):
                halfyearString = halfyearLine
                halfyearTemp = ""
                for monthInYear in range(1,  7):
                    monthString = monthLine
                    monthString = HTMLTemplateParser.replaceVar("month",
                                                                unicode(self.main.locale.standaloneMonthName(halfYear*6+monthInYear, QLocale.ShortFormat)),  monthString)
                    firstFileInMonth = FilelistAnalyzer.firstFileInMonth(files,  year,  halfYear*6+monthInYear)
                    monthString = HTMLTemplateParser.replaceIf("month_has_messages",  monthString,  firstFileInMonth != None)
                    if firstFileInMonth != None:
                        monthString = HTMLTemplateParser.replaceIf("current_month",  monthString,  halfYear*6+monthInYear == month
                                                                   and filename != 'index')
                        monthString = HTMLTemplateParser.replaceVar("month_link",  firstFileInMonth + ".html",  monthString)
                    halfyearTemp += monthString
                halfyearString = HTMLTemplateParser.replaceForeach("month",  halfyearTemp,  halfyearLine)
                yearString += halfyearString

            monthCalendar = HTMLTemplateParser.replaceForeach("six_months",  yearString,  monthCalendar)
            content = HTMLTemplateParser.replaceForeach("month_calendar",  monthCalendar,  content)

            if self.period == ExportPeriod.Daily:
                lastYear,  lastMonth,  lastDay,  lastFile = FilelistAnalyzer.lastDay(files,  file)
                nextYear,  nextMonth,  nextDay,  nextFile = FilelistAnalyzer.nextDay(files,  file)
                if lastFile:
                    lastString = unicode(QDate(lastYear,  lastMonth,  lastDay).toString(Qt.DefaultLocaleShortDate))
                if nextFile:
                    nextString = unicode(QDate(nextYear,  nextMonth,  nextDay).toString(Qt.DefaultLocaleShortDate))

            elif self.period == ExportPeriod.Monthly:
                lastYear,  lastMonth,  lastFile = FilelistAnalyzer.lastMonth(files,  file)
                nextYear,  nextMonth,  nextFile = FilelistAnalyzer.nextMonth(files,  file)
                if lastFile:
                    lastString = unicode(QDate(lastYear,  lastMonth,  1).toString("MMMM yyyy"))
                if nextFile:
                    nextString = unicode(QDate(nextYear,  nextMonth,  1).toString("MMMM yyyy"))

            elif self.period == ExportPeriod.Yearly:
                if filename == 'index':
                    nextYear,  nextFile = FilelistAnalyzer.nextYear(files,  "Messages_0000")
                else:
                    lastYear,  lastFile = FilelistAnalyzer.lastYear(files,  file)
                    nextYear,  nextFile = FilelistAnalyzer.nextYear(files,  file)
                    if lastFile:
                        lastString = str(lastYear)
                if nextFile:
                    nextString = str(nextYear)

            if lastFile and filename != 'index':
                content = HTMLTemplateParser.replaceIf("last_page",  content,  True)
                content = HTMLTemplateParser.replaceVar("last_page_link",  lastFile + ".html",  content)
                content = HTMLTemplateParser.replaceVar("string_last_page",  unicode(self.tr("Back")),  content)
                content = HTMLTemplateParser.replaceVar("last_page",  lastString,  content)
            else:
                content = HTMLTemplateParser.replaceIf("last_page",  content,  False)

            if nextFile and (filename != 'index' or self.period == ExportPeriod.Yearly):
                content = HTMLTemplateParser.replaceIf("next_page",  content,  True)
                content = HTMLTemplateParser.replaceVar("next_page_link",  nextFile + ".html",  content)
                content = HTMLTemplateParser.replaceVar("string_next_page",  unicode(self.tr("Next")),  content)
                content = HTMLTemplateParser.replaceVar("next_page",  nextString,  content)
            else:
                content = HTMLTemplateParser.replaceIf("next_page",  content,  False)

        file_ = codecs.open(self.directory + 'messages/' + filename + '.html',  'w',  'utf-8')
        file_.write(content)
        file_.close()

    def finalizeMessageFiles(self):
        self.createMessageIndexFile()

    def createMessageIndexFile(self):
        html = self.tMessage
        html = HTMLTemplateParser.replaceVar("pagetitle",  unicode(self.tr("Messages")),  html)
        html = HTMLTemplateParser.replaceVar("headline",  unicode(self.tr("Exported messages")),  html)
        html = HTMLTemplateParser.replaceVar("caption",  unicode(self.tr("Messages")),  html)

        content = unicode(self.tr("You can use the calendar in the left sidebar to browse through your message archive."))
        html = HTMLTemplateParser.replaceForeach("message",  content,  html)

        if self.graph == ExportGraph.Yes:
            html = HTMLTemplateParser.replaceVar("string_statistics",  unicode(self.tr("Message statistics")),  html)
            html = HTMLTemplateParser.replaceIf("statistics_image",  html,  True)
            html = HTMLTemplateParser.replaceVar("statistics_link",  '../' + self.generateStatisticImage(),  html)
        else:
            html = HTMLTemplateParser.replaceIf("statistics_image",  html,  False)

        file_ = codecs.open(self.directory + 'messages/index.html',  'w',  'utf-8')
        file_.write(html)
        file_.close()

        self.writeCalender('index')

    def subFormatMessage(self,  message):
        msg = message.message()
        msg = HTMLTemplateParser.escape(msg)
        msg = msg.replace('\n',  '<br />\n')
        name = HTMLTemplateParser.escape(message.contact().name())

        if self.period == ExportPeriod.Daily:
            date = unicode(message.dateTime().time().toString(Qt.DefaultLocaleLongDate))
        else:
            date = unicode(message.dateTime().toString(Qt.DefaultLocaleLongDate))

        html = self.tempSearch
        html = HTMLTemplateParser.replaceIf("message_is_incoming",  html,  message.type() == MessageType.Incoming)
        html = HTMLTemplateParser.replaceVar("message_address",  name,  html)
        html = HTMLTemplateParser.replaceVar("message_datetime",  date,  html)
        html = HTMLTemplateParser.replaceVar("message_text",  msg,  html)
        self.tempString += html

    def finalizeMessageFile(self,  file):
        out = HTMLTemplateParser.replaceForeach("message",  self.tempString,  self.tempFile)
        self.lastFile.write(out)

        self.lastFile.close()

    def openContactFile(self,  filename):
        self.lastFile = codecs.open(self.directory + 'contacts/' + filename + '.html',  'w',  'utf-8')

        html = self.tContacts
        html = HTMLTemplateParser.replaceVar("headline",  unicode(self.tr("Exported messages")),  html)

        self.tempFile = html
        self.tempString = ""

    def subFormatContact(self,  contact):
        html = self.tempFile
        html = HTMLTemplateParser.replaceVar("pagetitle",  unicode(self.tr("Contact - %1").arg(contact.name())),  html)
        html = HTMLTemplateParser.replaceVar("name",  contact.name(),  html)

        if self.thumbnails == ExportThumbnails.Yes:
            # Write thumbnail image in a special directory
            if "thumbnail_image" in contact:
                data = base64.decodestring(contact.value("thumbnail_image")[0])
                thumbLink = 'thumbnails/' + self.formatContactFile(contact) + '.jpg'
                thumbFile = open(self.directory + thumbLink,  'wb')
                thumbFile.write(data)
                thumbFile.close()

                html = HTMLTemplateParser.replaceIf("thumbnail_image",  html,  True)
                html = HTMLTemplateParser.replaceVar("thumbnail_link",  '../' + thumbLink,  html)
            else:
                html = HTMLTemplateParser.replaceIf("thumbnail_image",  html,  False)
        else:
            html = HTMLTemplateParser.replaceIf("thumbnail_image",  html,  False)

        if self.graph == ExportGraph.Yes:
            # Generate statistic image
            statisticsLink = self.generateStatisticImage(contact)
            if statisticsLink:
                html = HTMLTemplateParser.replaceIf("statistics_image",  html,  True)
                html = HTMLTemplateParser.replaceVar("string_statistics",  unicode(self.tr("Message statistics")),  html)
                html = HTMLTemplateParser.replaceVar("statistics_link",  '../' + statisticsLink,  html)
            else:
                html = HTMLTemplateParser.replaceIf("statistics_image",  html,  False)
        else:
            html = HTMLTemplateParser.replaceIf("statistics_image",  html,  False)

        entryField = HTMLTemplateParser.getForeach("detail",  html)
        entryString = ""
        for field,  value in contact:
            if field.isPicture():
                continue
            if field.isDate():
                # Parse birthdate
                value = QDate.fromString(value,  "yyyyMMdd").toString(Qt.DefaultLocaleLongDate)
            entryTmp = entryField
            entryTmp = HTMLTemplateParser.replaceVar("key",  field.toString(),  entryTmp)
            entryTmp = HTMLTemplateParser.replaceVar("value",  value,  entryTmp)
            entryString += entryTmp

        html = HTMLTemplateParser.replaceForeach("detail",  entryString,  html)

        self.tempFile = html

    def finalizeContactFile(self,  file):
        out = self.tempFile
        self.lastFile.write(out)

        self.lastFile.close()

    def finalizeContactFiles(self):
        self.createContactIndexFile()

    def createContactIndexFile(self):
        html = self.tIndex
        html = HTMLTemplateParser.replaceVar("homepage_link",  "../index.html", html)
        html = HTMLTemplateParser.replaceVar("messages_link",  "../messages/index.html", html)
        html = HTMLTemplateParser.replaceVar("contacts_link",  "../contacts/index.html", html)
        html = HTMLTemplateParser.replaceIf("style_in_parent_directory",  html,  True)
        html = HTMLTemplateParser.replaceVar("pagetitle",  unicode(self.tr("Contacts")),  html)
        html = HTMLTemplateParser.replaceVar("headline",  unicode(self.tr("Exported messages")),  html)
        html = HTMLTemplateParser.replaceVar("caption",  unicode(self.tr("Contacts")),  html)

        content = ""
        names = [[contact.name(),  contact.id(),  contact.idOnPhone()] for contact in self.contactList]
        for name,  id,  idOnPhone in sorted(names):
            if idOnPhone:
                content += '<a href="Contact_' + self.formatContactName(Contact(name=name,  id=id)) + '.html">' + \
                                 name + '</a><br />\n'

        html = HTMLTemplateParser.replaceVar("content",  content,  html)

        file_ = codecs.open(self.directory + 'contacts/index.html',  'w',  'utf-8')
        file_.write(html)
        file_.close()

    def finalizeFiles(self):
        self.createIndexFile()

    def createIndexFile(self):
        html = self.tIndex
        html = HTMLTemplateParser.replaceVar("homepage_link",  "index.html", html)
        html = HTMLTemplateParser.replaceVar("messages_link",  "messages/index.html", html)
        html = HTMLTemplateParser.replaceVar("contacts_link",  "contacts/index.html", html)
        html = HTMLTemplateParser.replaceIf("style_in_parent_directory",  html,  False)
        html = HTMLTemplateParser.replaceVar("pagetitle",  unicode(self.tr("Exported Messages - Homepage")),  html)
        html = HTMLTemplateParser.replaceVar("headline",  unicode(self.tr("Exported messages")),  html)
        html = HTMLTemplateParser.replaceVar("caption",  unicode(self.tr("Homepage")),  html)

        content = self.tr("""<p>These messages and contacts were exported using
<a href="http://series60-remote.sourceforge.net" target="_blank"><i>Series60-Remote</i></a>, a Software Suite for S60 mobile phones.<br />
To show your messages, click on the <a href="messages/index.html">Messages</a> tab in the navigation bar and to get an overview
of your contacts click on the <a href="contacts/index.html">Contact</a> tab.</p>
""")

        general = self.database.statisticsGeneral()
        if general["days"] == 0:
            incomingPerDay = 0
            outgoingPerDay = 0
        else:
            incomingPerDay = general["incoming"]/general["days"]
            outgoingPerDay = general["outgoing"]/general["days"]

        content += self.tr("""<p><h1>General statistics</h1></p>
<p><b>%1</b> incoming messages, <b>%2</b> outgoing messages, <b>%3</b> total messages.<br />
The total number of stored days is <b>%4</b>.<br />
You receive <b>%5</b> and send <b>%6</b> messages per day on average.<br />
There are alltogether <b>%7</b> contacts in my database, <b>%8</b> of them are shown on your mobile phone.<br />
The average length of an incoming message is <b>%9</b> chars, of an outgoing message <b>%10</b> chars.</p>""").arg(general["incoming"]).arg(general["outgoing"]).arg(general["total"]).arg(general["days"]).arg(incomingPerDay).arg(outgoingPerDay).arg(general["contacts"]).arg(general["contactsShown"]).arg(general["incoming_avglength"]).arg(general["outgoing_avglength"])

        content += self.tr("<p><i>This file was generated on %1</i></p>").arg(
                                        QDateTime.currentDateTime().toString(Qt.DefaultLocaleLongDate))


        html = HTMLTemplateParser.replaceVar("content",  unicode(content),  html)

        file_ = codecs.open(self.directory + 'index.html',  'w',  'utf-8')
        file_.write(html)
        file_.close()

    def generateStatisticImage(self,  contact=Contact()):
        if not USE_MATPLOTLIB:
            return False

        self.request.setContact(contact)
        get = self.database.statistics(self.request)

        if not get:
            return False

        first = get[0]
        last = get[-1]

        months = last.year() - first.year() + 1
        months *= 12
        months -= first.month() - 1
        months -= 12 - last.month()

        y1 = list()
        x = list()
        cur = QDate(first.year(),  first.month(),  1)
        for month in range(months):
            y1.append(0)
            x.append(datetime.datetime(cur.year(),  cur.month(),  1))
            cur = cur.addMonths(1)
        y2 = y1[:]

        for line in get:
            key = line.year() - first.year() + 1
            key *= 12
            key -= first.month() - 1
            key -= 12 - line.month()

            key -= 1

            y1[key] = line.incoming()
            y2[key] = line.total()

        self.ax.cla()

        self.fill_plot(x,  y1,  0,  'green',  unicode(self.tr("Incoming messages")))
        self.fill_plot(x,  y1,  y2,  'red',  unicode(self.tr("Outgoing messages")))

        if contact:
            file = "Graph_" + self.formatContactName(contact)
        else:
            file = "Graph_00_all"

        if self.graphFormat == ExportGraphFormat.PNG:
            file += '.png'
        elif self.graphFormat == ExportGraphFormat.SVG:
            file += '.svg'

        if self.legend == ExportLegend.Yes:
            self.ax.legend(shadow=True,  loc='best',  prop=matplotlib.font_manager.FontProperties(size=8))
        self.fig.autofmt_xdate()

        self.fig.savefig(self.directory + 'graph/' + file,  transparent=True)

        return 'graph/' + file

    def fill_plot(self,  x,  y1,  y2=0,  color='black',  label=''):
        self.ax.plot(x, y1, color=color,  label=label)
        self.ax.fill_between(x,  y2,  y1,  facecolor=color)
        self.ax.plot(x, y1,  color='black')

        self.ax.set_xbound(x[0],  x[len(x)-1])
