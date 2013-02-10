# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ChatMainWindow(QMainWindow):
    def __init__(self,  manager):
        super(ChatMainWindow,  self).__init__()

        self.manager = manager
        self.settings = manager.settings

        # Destroy the window when it is closed
        # Otherwise all signals would be still connected - this causes wired problems
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowIcon(QIcon(":/phone"))

        windowSize = self.settings.setting("windows/chat/size")
        if windowSize.isValid():
            self.resize(windowSize)

        self.show()

    def closeEvent(self,  event):
        widget = self.centralWidget()

        self.settings.setSetting("windows/chat/size", self.size())
        self.settings.setSetting("windows/chat/splitter", widget.splitter.saveState())
        self.manager.closeChat(widget.contact)

        event.accept()
