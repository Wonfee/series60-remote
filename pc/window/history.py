# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_history
from lib.classes import *

class History(QDialog,  ui.ui_history.Ui_History):
    def __init__(self, parent, main, contact=None):
        super(History,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)
        main.setupButtonBox(self.buttonBox)
        self.searchWidget.hide()

        self.filter = 0
        self.searchString = ""

        self.connect(self.searchButton,  SIGNAL("toggled(bool)"),  self.searchWidget,  SLOT("setVisible(bool)"))
        self.connect(self.applyButton,  SIGNAL("clicked()"),  self.search)
        self.connect(self.contactBox,  SIGNAL("currentIndexChanged(int)"),  self.contactChanged)
        self.connect(self.dateTree,  SIGNAL("currentItemChanged(QTreeWidgetItem *, QTreeWidgetItem *)"),  self.dateChanged)
        self.connect(self.filterBox,  SIGNAL("currentIndexChanged(int)"),  self.filterChanged)

        self.show()
        self.insertContacts(contact)

    def insertContacts(self,  currentContact):
        self.contactBox.addItem(self.tr("All"))
        self.contactBox.insertSeparator(1)

        for contact in self.database.contactsWithMessages():
            self.contactBox.addItem(contact.name(),  QVariant(contact))

        index = 0
        if currentContact:
            index = self.contactBox.findText(currentContact.name())
            if index == -1:
                index = 0

        self.contactBox.setCurrentIndex(index)

    def contactChanged(self,  index,  searchText=None,  searchOlder=None,  searchNewer=None):
        self.dateTree.clear()

        if self.contactBox.currentText() == self.tr("All"):
            contact = None
        else:
            contact = self.contactBox.itemData(index).toPyObject()

        dates = self.database.dates(contact,  searchText,  searchOlder,  searchNewer)
        for year in dates.years():
            yearItem = QTreeWidgetItem(self.dateTree)
            yearItem.setText(0,  str(year))
            yearItem.setData(0,  Roles.DateRole,  QVariant(year))

            for month in dates.months(year):
                monthItem = QTreeWidgetItem(yearItem)
                monthItem.setText(0, self.main.locale.standaloneMonthName(month))
                monthItem.setData(0,  Roles.DateRole,  QVariant(month))

                for day in dates.days(year,  month):
                    dayItem = QTreeWidgetItem(monthItem)
                    dayItem.setText(0,  str(day) + ". ")
                    dayItem.setData(0,  Roles.DateRole,  QVariant(day))

            yearItem.setExpanded(True)

        if self.dateTree.topLevelItemCount() > 0:
            first = self.dateTree.topLevelItem(0).child(0).child(0)
            self.dateChanged(first,  0)
        else:
            self.messageBrowser.clear()

    def dateChanged(self,  current,  previous):
        try:
            dayItem = current
            day = dayItem.data(0,  Roles.DateRole).toInt()[0]

            monthItem = dayItem.parent()
            month = monthItem.data(0,  Roles.DateRole).toInt()[0]

            yearItem = monthItem.parent()
            year = yearItem.data(0,  Roles.DateRole).toInt()[0]
        except:
            return

        contact = unicode(self.contactBox.currentText())
        if self.contactBox.currentText() == self.tr("All"):
            contact = None
        else:
            contact = self.contactBox.itemData(self.contactBox.currentIndex()).toPyObject()

        filter = self.filter

        browser = self.messageBrowser
        cursor = browser.textCursor()

        browser.clear()

        date = QDate(year,  month,  day)
        cursor.insertHtml("<font size=+1><b>" + date.toString(Qt.DefaultLocaleLongDate) + "</b></font><br />")

        showError = False
        for msg in self.database.messages(year,  month,  day,  contact,  filter):
            date =  unicode(msg.dateTime().time().toString())

            message = QString(msg.message())
            message = Qt.escape(message)
            message = unicode(message.replace("\n",  "<br />"))

            if not msg.idOnPhone():
                message = '<font color="red">' + message + "</font> (*)"
                showError = True

            name =  unicode(Qt.escape(msg.contact().name()))

            if msg.type() == MessageType.Incoming:
               type = '<font color="orangered"><b>&lt;</b></font>'
            else:
               type = '<font color="dodgerblue"><b>&gt;</b></font>'

            if contact:
                name = ""
            else:
                name = "<b>" + name + ": </b>"

            if self.searchString:
                pattern = re.compile("(" + re.escape(self.searchString) + ")",  re.IGNORECASE)
                message = pattern.sub(r'<span style="background-color: yellow">\1</span>',  message)

            cursor.insertHtml("<table cellspacing='5'><tr><td>[" + date + "]&nbsp;&nbsp;" + type + "</td><td>" + name + " " +  \
                               message + "</td></tr></table>")

        if showError:
            cursor.insertHtml("<font color='red'>" + self.trUtf8("(*): Potentially the message wasn't sent correctly.") + "</font>")

    def filterChanged(self,  index):
        self.filter = index

        item = self.dateTree.topLevelItem(0).child(0).child(0)
        self.dateChanged(item,  0)

    def search(self):
        index = self.contactBox.currentIndex()
        text = unicode(self.searchText.text())
        older = None
        newer = None

        if text:
            self.searchString = text
#        if not text:
#            return
#        if len(text) <= 2:
#            message = QMessageBox.critical(self,
#            self.tr("Text to short!"),
#            self.tr("The text must be at least two chars long!"),
#            QMessageBox.StandardButtons(\
#                    QMessageBox.Ok),
#            QMessageBox.Ok)
#            return

        if self.olderBox.checkState() == Qt.Checked:
            older = self.olderDate.date()
        if self.newerBox.checkState() == Qt.Checked:
            newer = self.newerDate.date()

        self.contactChanged(index,  text,  older,  newer)
