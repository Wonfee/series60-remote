# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ObexCompleter(QCompleter):
    def __init__(self,  parent,  model=None):
        QCompleter.__init__(self,  model, parent)
        self.setCaseSensitivity(Qt.CaseInsensitive)
    
        self.seperator = "\\"
    
    def splitPath(self,  path):
        return path.split(self.seperator)
    
    def pathFromIndex(self,  index):
        return index.internalPointer().path().replace(self.seperator,  "",  1)
