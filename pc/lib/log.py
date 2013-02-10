# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import logging

class QtStreamHandler(logging.Handler):
    def __init__(self,  parent,  main):
        logging.Handler.__init__(self)
        self.parent = parent
        self.main = main

        self.textWidget = parent
        self.formater = logging.Formatter("%(message)s")

    def setFormatter(self,  format):
        self.formater = format

    def createLock(self):
        self.mutex = QMutex()

    def acquire(self):
        self.mutex.lock()

    def release(self):
        self.mutex.unlock()

    def emit(self,record):
        self.textWidget.appendPlainText(self.formater.format(record))
        self.textWidget.moveCursor(QTextCursor.StartOfLine)
        self.textWidget.ensureCursorVisible()

class QtOutput(object):
    def __init__(self, parent, out=None, color=None):
        self.textWidget = parent
        self.out = out
        self.color = color

    def write(self, m):
        self.textWidget.moveCursor(QTextCursor.End)

        if self.color:
            tc = self.textWidget.textColor()
            self.textWidget.setTextColor(self.color)

        self.textWidget.insertPlainText( m )

        if self.color:
            self.textWidget.setTextColor(tc)

        if self.out:
            if isinstance(m,  unicode):
                self.out.write(m.encode("utf8"))
            else:
                self.out.write(m)
