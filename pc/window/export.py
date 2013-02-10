# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

import os
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import lib.export
import ui.ui_export
import window.export_progress
from lib.classes import *

try:
    import matplotlib.figure
    import matplotlib.font_manager
    import matplotlib.backend_bases
except ImportError:
    USE_MATPLOTLIB = False
else:
    USE_MATPLOTLIB= True

class Export(QDialog,  ui.ui_export.Ui_Export):
    def __init__(self, parent, main):
        super(Export,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)

        if not USE_MATPLOTLIB:
            self.graphBox.setCheckState(Qt.Unchecked)
            self.graphBox.setEnabled(False)

        # Complete directory names in export QLineEdit
        self.export = lib.export.Export(self,  main)
        self.completer = QCompleter()
        self.completionModel = QDirModel(self.completer)
        self.completionModel.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        self.completer.setModel(self.completionModel)
        self.exportLine.setCompleter(self.completer)
        self.exportLine.setText(QDir.homePath())

        self.exportButton = self.buttonBox.addButton(self.tr("Export..."),  QDialogButtonBox.AcceptRole)
        main.setupButtonBox(self.buttonBox)

        self.connect(self.formatBox,  SIGNAL("currentIndexChanged(int)"),  self.formatChanged)
        self.connect(self.contactsBox,  SIGNAL("stateChanged(int)"),  lambda x: self.itemSelectionChanged())
        self.connect(self.messagesBox,  SIGNAL("stateChanged(int)"),  lambda x: self.itemSelectionChanged())
        self.connect(self.calendarBox,  SIGNAL("stateChanged(int)"),  lambda x: self.itemSelectionChanged())
        self.connect(self.selectAllButton,  SIGNAL("clicked()"),  self.selectAllContacts)
        self.connect(self.deselectAllButton,  SIGNAL("clicked()"),  self.deselectAllContacts)
        self.connect(self.openBrowserButton,  SIGNAL("clicked()"),  self.openBrowser)
        self.connect(self.exportLine,  SIGNAL("textChanged(const QString &)"),  self.checkExportButton)
        self.connect(self,  SIGNAL("accepted()"),  self.startExport)

        self.loadContacts()
        self.loadPlugins()
        self.loadPeriods()
        self.loadOrder()
        self.loadGraphformats()
        self.checkExportButton(self.exportLine.text())
        self.show()

    def loadContacts(self):
        self.contactsList.clear()
        if not self.database.contactCount():
            item = QListWidgetItem(self.contactsList)
            item.setText(self.tr("No contacts available"))
        else:
            for contact in self.database.contacts(True):
                item = QListWidgetItem(self.contactsList)

                item.setData(Roles.ContactRole,  QVariant(contact))
                item.setText(contact.name())
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
            self.contactsList.sortItems(Qt.AscendingOrder)

    def loadPlugins(self):
        for format in self.export.formats():
            self.formatBox.addItem(format.format(),  QVariant(format))

    def loadPeriods(self):
        self.periodBox.addItem(self.tr("Daily"),  QVariant(ExportPeriod.Daily))
        self.periodBox.addItem(self.tr("Monthly"),  QVariant(ExportPeriod.Monthly))
        self.periodBox.addItem(self.tr("Yearly"),  QVariant(ExportPeriod.Yearly))
        self.periodBox.addItem(self.tr("All messages in one file"),  QVariant(ExportPeriod.All))

    def loadOrder(self):
        self.orderBox.addItem(self.tr("Ascending"),  QVariant(ExportOrder.ASC))
        self.orderBox.addItem(self.tr("Descending"),  QVariant(ExportOrder.DESC))

    def loadGraphformats(self):
        self.graphFormatBox.addItem("PNG",  QVariant(ExportGraphFormat.PNG))
        self.graphFormatBox.addItem("SVG",  QVariant(ExportGraphFormat.SVG))

    def formatChanged(self,  index):
        plugin = self.formatBox.itemData(self.formatBox.currentIndex()).toPyObject()
        items = plugin.supportedExportItems()
        options = plugin.supportedExportOptions()

        def enableWidget(condition,  widget,  widgetLabel = None):
            if items & condition == condition:
                widget.setEnabled(True)
                if widgetLabel:
                    widgetLabel.setEnabled(True)
            else:
                widget.setEnabled(False)
                if widgetLabel:
                    widgetLabel.setEnabled(False)
                if isinstance(widget,  QCheckBox):
                    widget.setCheckState(Qt.Unchecked)

        def showWidget(condition,  widget,  widgetLabel = None):
            if options & condition == condition:
                widget.setVisible(True)
                if widgetLabel:
                    widgetLabel.setVisible(True)
            else:
                widget.setVisible(False)
                if widgetLabel:
                    widgetLabel.setVisible(False)

        enableWidget(ExportItems.Contacts,  self.contactsBox)
        enableWidget(ExportItems.Messages,  self.messagesBox)
        enableWidget(ExportItems.Calendar,  self.calendarBox)

        if options == 0:
            self.pluginSettingsBox.setHidden(True)
        else:
            showWidget(ExportOptions.Period,  self.periodBox,  self.periodLabel)
            showWidget(ExportOptions.Order,  self.orderBox,  self.orderLabel)
            showWidget(ExportOptions.Graph,  self.graphBox)
            showWidget(ExportOptions.GraphFormat,  self.graphFormatBox,  self.graphFormatLabel)
            showWidget(ExportOptions.Legend,  self.legendBox)
            showWidget(ExportOptions.Thumbnails,  self.thumbnailsBox)
            self.pluginSettingsBox.setHidden(False)
        self.itemSelectionChanged()

    def itemSelectionChanged(self):
        items = self.exportItems()

        def enableWidget(condition,  widget,  widgetLabel = None):
            if items & condition == condition:
                widget.setEnabled(True)
                if widgetLabel:
                    widgetLabel.setEnabled(True)
            else:
                widget.setEnabled(False)
                if widgetLabel:
                    widgetLabel.setEnabled(False)
                if isinstance(widget,  QCheckBox):
                    widget.setCheckState(Qt.Unchecked)

        enableWidget(ExportItems.Messages,  self.periodBox,  self.periodLabel)
        enableWidget(ExportItems.Messages,  self.orderBox,  self.orderLabel)
        enableWidget(ExportItems.Contacts,  self.graphBox)
        enableWidget(ExportItems.Contacts,  self.graphFormatBox,  self.graphFormatLabel)
        enableWidget(ExportItems.Contacts,  self.legendBox)
        enableWidget(ExportItems.Contacts,  self.thumbnailsBox)

        enableWidget(ExportItems.Messages,  self.messageContactsButton)
        if self.messageContactsButton.isChecked():
            self.allContactsButton.setChecked(True)

        self.exportButton.setEnabled(bool(self.exportItems()))

    def exportItems(self):
        items = 0
        if self.contactsBox.checkState() == Qt.Checked:
            items |= ExportItems.Contacts
        if self.messagesBox.checkState() == Qt.Checked:
            items |= ExportItems.Messages
        if self.calendarBox.checkState() == Qt.Checked:
            items |= ExportItems.Calendar
        return items

    def selectAllContacts(self):
        for num in range(self.contactsList.count()):
            item = self.contactsList.item(num)
            if item.data(Roles.ContactRole).toPyObject():
                item.setCheckState(Qt.Checked)

    def deselectAllContacts(self):
        for num in range(self.contactsList.count()):
            item = self.contactsList.item(num)
            if item.data(Roles.ContactRole).toPyObject():
                item.setCheckState(Qt.Unchecked)

    def openBrowser(self):
        path = QFileDialog.getExistingDirectory(self,  self.tr("Select export directory"))
        if path:
            self.exportLine.setText(path)

    def checkExportButton(self,  path):
        if not path:
            self.directoryLabel.setText(self.tr("No export directory selected!"))
            self.exportButton.setEnabled(False)
        elif not QDir(path).exists():
            self.directoryLabel.setText(self.tr("Invalid export directory!"))
            self.exportButton.setEnabled(False)
        elif not os.access(path,  os.W_OK):
            self.directoryLabel.setText(self.tr("Cannot write to export directory!"))
            self.exportButton.setEnabled(False)
        else:
            self.directoryLabel.setText("")
            self.exportButton.setEnabled(True)

    def startExport(self):
        self.exportProgressDialog = window.export_progress.ExportProgress(self,  self.main,  self.export)
        self.plugin = self.formatBox.itemData(self.formatBox.currentIndex()).toPyObject()

        exportContacts = None
        if self.filterButton.isChecked():
            contacts = ExportContacts.Filter
            # Build a list of contacts which should be exported
            exportContacts = list()
            for row in range(self.contactsList.count()):
                contact = self.contactsList.item(row)
                if contact.checkState() == Qt.Checked:
                    exportContacts.append(contact.data(Roles.ContactRole).toPyObject())
        elif self.messageContactsButton.isChecked():
            contacts = ExportContacts.ContactsWithMessages
        else:
            contacts = ExportContacts.All

        if self.graphBox.isChecked():
            graph = ExportGraph.Yes
        else:
            graph = ExportGraph.No

        if self.legendBox.isChecked():
            legend = ExportLegend.Yes
        else:
            legend = ExportLegend.No

        if self.thumbnailsBox.isChecked():
            thumbnails = ExportThumbnails.Yes
        else:
            thumbnails = ExportThumbnails.No

        self.export.start(
                          self.exportProgressDialog,
                          self.plugin,
                          items=self.exportItems(),
                          contacts=contacts,
                          period=self.periodBox.itemData(self.periodBox.currentIndex()).toPyObject(),
                          graph=graph,
                          legend=legend,
                          thumbnails=thumbnails,
                          directory=unicode(self.exportLine.text() + u'/'),
                          order=self.orderBox.itemData(self.orderBox.currentIndex()).toPyObject(),
                          exportContacts=exportContacts,
                          graphFormat=self.graphFormatBox.itemData(self.graphFormatBox.currentIndex()).toPyObject()
                          )

