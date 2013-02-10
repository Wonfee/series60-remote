# -*- coding: utf-8 -*-

# File kdepim/calendarviews/eventviews/month/monthgraphicsitems.cpp originally taken from the KDE project.
# Copyright (c) 2008 Bruno Virlet <bruno.virlet@gmail.com>
# Copyright (c) 2008 Thomas Thrainer <tom_t@gmx.at>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import widget.ScrollIndicator

class CalendarCell(object):
    def __init__(self,  id,  date,  scene):
        #super(CaledarCell,  self).__init__()
        self.__heightHash = dict()

        self.__id = id
        self.__date = date
        self.__scene = scene

        self.upArrow = widget.ScrollIndicator.ScrollIndicator(scene,  widget.ScrollIndicator.ArrowDirection.Up)
        self.downArrow = widget.ScrollIndicator.ScrollIndicator(scene,  widget.ScrollIndicator.ArrowDirection.Down)

    def __del__(self):
        self.__scene.removeItem(self.upArrow)
        self.__scene.removeItem(self.downArrow)
        del self.upArrow
        del self.downArrow

    def id(self):
        return self.__id

    def date(self):
        return self.__date

    def x(self):
        return self.__id % 7

    def y(self):
        return self.__id / 7

    def hasEventBelow(self,  height):
        for i in range(0,  height):
            if i in self.__heightHash:
                return True
        return False

    def addMonthItem(self,  manager,  height):
        self.__heightHash[height] = manager

    def firstFreeSpace(self):
        i = 0
        while True:
            if i not in self.__heightHash:
                return i
            i += 1

    @staticmethod
    def topMargin():
        return 18
