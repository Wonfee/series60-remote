# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ChatTabWindow(QMainWindow):
    def __init__(self,  manager):
        super(ChatTabWindow,  self).__init__()

        self.manager = manager
        self.settings = manager.settings

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setMovable(True)
        self.tabWidget.setTabsClosable(True)

        self.setCentralWidget(self.tabWidget)

        self.setWindowIcon(QIcon(":/phone"))

        windowSize = self.settings.setting("windows/chat/size")
        if windowSize.isValid():
            self.resize(windowSize)

        self.show()

    def closeEvent(self,  event):
        self.settings.setSetting("windows/chat/size", self.size())
        self.manager.closeAllChats()

        event.accept()
