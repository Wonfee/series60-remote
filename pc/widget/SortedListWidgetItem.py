# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class SortedListWidgetItem(QListWidgetItem):
    def __lt__(self,  other):
        # convert to lower case for case-insensitive sorting and 
        # normalize in a form where accents are seperate characters
        return self.text().toLower().normalized(QString.NormalizationForm_D) < \
                        other.text().toLower().normalized(QString.NormalizationForm_D)
