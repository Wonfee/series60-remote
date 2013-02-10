# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

import logging
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_log

class Log(QDialog,  ui.ui_log.Ui_Log):
    def __init__(self, parent, main):
        super(Log,  self).__init__(parent)
        
        self.parent = parent
        self.main = main
        
        self.settings = main.settings

        self.setupUi(self)

        level = self.settings.setting("log/level")
        if level == 9:
            self.levelBox.setCurrentIndex(0)
        else:
            self.levelBox.setCurrentIndex(level/10)
        
        self.formatBox.setChecked(self.settings.setting("log/long"))
        self.connect(self.levelBox,  SIGNAL("currentIndexChanged(int)"),  self.changeLevel)
        self.connect(self.formatBox,  SIGNAL("stateChanged(int)"),  self.changeFormat)
    
    def changeLevel(self,  index):
        if index == 0:
            level = 9
        else:
            level = index*10
        
        self.main.dialogHandler.setLevel(level)
        self.settings.setSetting("log/level",  level)

    def changeFormat(self,  state):
        if state == Qt.Checked:
            self.settings.setSetting("log/long",  True)
            format = logging.Formatter("[%(asctime)s] - %(levelname)-8s - %(message)s (%(module)s: %(funcName)s - line %(lineno)s, process %(process)s)", "%d.%m.%Y %H:%M:%S")
        else:
            self.settings.setSetting("log/long",  False)
            format = logging.Formatter("%(message)s")
        
        self.main.dialogHandler.setFormatter(format)
