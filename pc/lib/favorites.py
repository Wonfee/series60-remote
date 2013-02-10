# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class FavoriteMenu(QObject):
    def __init__(self,  parent,  main):
        super(FavoriteMenu,  self).__init__(parent)

        self.parent = parent
        self.main = main

        self.database = main.database
        self.settings = main.settings
        self.helper = main.helper

    def menu(self,  menu):
        submenu = self.settings.setting("contacts/displayFavoritesInSubmenu")
        num = self.settings.setting("contacts/displayFavoritesNum")
        days = self.settings.setting("contacts/displayFavoritesDays")
        favCount = self.settings.setting("contacts/displayFavoritesCount")
        
        if num == 1:
            favGen = None
        elif num == 2:
            favGen = self.database.contactFavoritesGenerator(favCount)
        else:
            favGen = self.database.contactFavoritesGenerator(favCount, days)
        
        favField = self.database.contactFavoritesField()
        
        if submenu:
            useMenu = QMenu(self.tr("&Favorites"),  self.parent)
            menu .addMenu(useMenu)
        else:
            lbl = menu.addAction(self.tr("Favorites"))
            lbl.setEnabled(False)
            useMenu = menu
        
        i = 0
        if favGen:
            i = self.helper.addContactsToMenu(favGen,  useMenu)
        if favGen and favField:
            useMenu.addSeparator()
        if favField:
            self.helper.addContactsToMenu(favField,  useMenu,  i)
        
        conf = useMenu.addAction(self.tr("&Manage Favorites"))
        conf.setIcon(QIcon(":/configure"))
        conf.setProperty("type",  QVariant("configureFavorites"))
        if not self.settings.setting("contacts/displayFavoritesInSubmenu"):
            useMenu.addSeparator()
