# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_favorites
from lib.classes import *

class Favorites(QDialog,  ui.ui_favorites.Ui_Favorites):
    def __init__(self, parent, main):
        super(Favorites,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.log = main.log
        self.connection = main.connection
        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

        self.setupUi(self)
        main.setupButtonBox(self.buttonBox)

        self.loadSettings()

        self.connect(self,  SIGNAL("accepted()"),  self.saveFavorites)
        self.connect(self.addContactButton,  SIGNAL("clicked()"),  self.addContact)
        self.connect(self.removeContactButton,  SIGNAL("clicked()"),  self.removeContact)

        windowSize = self.settings.setting("windows/favorites/size")
        if windowSize.isValid():
            self.resize(windowSize)

        self.show()

    def loadSettings(self):
        self.addContacts()

        submenu = self.settings.setting("contacts/displayFavoritesInSubmenu")
        num = self.settings.setting("contacts/displayFavoritesNum")
        days = self.settings.setting("contacts/displayFavoritesDays")
        favCount = self.settings.setting("contacts/displayFavoritesCount")

        self.submenuBox.setCheckState(self.checkBoxValue(submenu))
        self.dayBox.setValue(days)
        self.numBox.setValue(favCount)

        if num == 1:
            self.noDynamicButtonButton.setChecked(True)
        elif num == 2:
            self.showDynFavoritesButton.setChecked(True)
        elif num == 3:
            self.showDynFavoritesWithDaysButton.setChecked(True)

    def addContacts(self):
        if not self.database.contactCount():
            item = QListWidgetItem(self.allContactsList)
            item.setText(self.tr("No contacts available"))
        else:
            for contact in self.database.contacts(True):
                if contact.isFavorite():
                    item = QListWidgetItem(self.favoriteContactsList)
                else:
                    item = QListWidgetItem(self.allContactsList)
                
                item.setData(Roles.ContactRole,  QVariant(contact))
                item.setText(contact.name())
            self.allContactsList.sortItems(Qt.AscendingOrder)

    def addContact(self):
        try:
            item = self.allContactsList.currentItem()
            contact = item.data(Roles.ContactRole).toPyObject()
            name = contact.name()
        except:
            return

        # Don't add contacts twice
        if self.favoriteContactsList.findItems(name,  Qt.MatchExactly):
            return

        contact.setFavorite(True)
        tmp = QListWidgetItem(item)
        self.favoriteContactsList.addItem(tmp)
    
    def removeContact(self):
        try:
            contact = self.favoriteContactsList.currentRow()
            self.favoriteContactsList.takeItem(contact)
        except:
            return

    def saveFavorites(self):
        self.database.contactUnfavoriteAll()
        for row in range(self.favoriteContactsList.count()):
            item = self.favoriteContactsList.item(row)
            contact = item.data(Roles.ContactRole).toPyObject()
            self.database.contactFavoriteUpdate(contact)

        submenu = bool(self.submenuBox.checkState())
        days = int(self.dayBox.value())
        favCount = int(self.numBox.value())

        num = 1
        if self.noDynamicButtonButton.isChecked():
            num = 1
        elif self.showDynFavoritesButton.isChecked():
            num = 2
        elif self.showDynFavoritesWithDaysButton.isChecked():
            num = 3
    
        self.settings.setSetting("contacts/displayFavoritesInSubmenu",  submenu)
        self.settings.setSetting("contacts/displayFavoritesNum",  num)
        self.settings.setSetting("contacts/displayFavoritesDays",  days)
        self.settings.setSetting("contacts/displayFavoritesCount",  favCount)

        self.main.emit(SIGNAL("favoriteListChanged"))

    def checkBoxValue(self,  bool):
        if bool:
            return Qt.Checked
        else:
            return Qt.Unchecked

    def hideEvent(self,  event):
        self.settings.setSetting("windows/favorites/size",  self.size())
        event.accept()
