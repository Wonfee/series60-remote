# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.classes import *

class DateSortedListWidgetItem(QListWidgetItem):
    def __lt__(self,  other):
        return self.data(Roles.DateRole).toDate() < other.data(Roles.DateRole).toDate()
