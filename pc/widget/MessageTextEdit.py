# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MessageTextEdit(QTextEdit):
    def __init__(self,  parent):
        super(MessageTextEdit,  self).__init__(parent)

        self.parent = parent
        self.__sendMessageOnReturn = False
    
    def sendMessageOnreturn(self):
        return self.__sendMessageOnReturn
    
    def setSendMessageOnReturn(self,  state):
        self.__sendMessageOnReturn = state

    def keyPressEvent(self,  event):
        if self.__sendMessageOnReturn:
            if event.key() == Qt.Key_Return:
                if event.modifiers() == Qt.ControlModifier:
                    event = QKeyEvent(QEvent.KeyPress,  Qt.Key_Return,  Qt.NoModifier)
                else:
                    self.emit(SIGNAL("sendMessage"))
                    return

        QTextEdit.keyPressEvent(self,  event)

