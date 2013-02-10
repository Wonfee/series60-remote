# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class SearchLineEdit(QLineEdit):
    def __init__(self,  parent):
        super(SearchLineEdit,  self).__init__(parent)
        self.search = self.tr("Search")

        self.__color = self.palette().color(QPalette.Text)
        self.__hasEdited = False
        self.connect(self,  SIGNAL("editingFinished()"),  self.__editFinshed)

    def __editFinshed(self):
        if self.text() == QString():
            self.setSearchText()

    def keyPressEvent(self,  event):
        if not self.__hasEdited and event.text():
            self.removeSearchText()
        QLineEdit.keyPressEvent(self,  event)

    def mousePressEvent(self,  event):
        if event.button() != Qt.LeftButton:
            event.ignore()
        else:
            event.accept()
        if self.text() == self.search:
            self.removeSearchText()

    def removeSearchText(self):
        self.__hasEdited = True
        
        self.clear()

        font = QFont()
        font.setItalic(False)
        self.palette().setColor(QPalette.Text,  self.__color)
        self.setFont(font)
        
    def searchText(self):
        if self.__hasEdited:
            return self.text()
        else:
            return QString()

    def setSearchText(self):
        self.__hasEdited = False
        
        font = QFont()
        font.setItalic(True)

        color = QColor(Qt.darkGray)
        self.palette().setColor(QPalette.Text,  color)

        self.setText(self.search)
        self.setFont(font)
