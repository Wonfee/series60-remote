# -*- coding: utf-8 -*-

# Copyright (c) 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class MovieDelegate(QItemDelegate):

    #needsRedraw = pyqtSignal()
    
    def __init__(self, movie, parent = None):
    
        QItemDelegate.__init__(self, parent)
        self.movie = movie
        self.connect(self.movie, SIGNAL("frameChanged(int)"),  SIGNAL("needsRedraw()"))
        #self.movie.frameChanged.connect(self.needsRedraw)
        self.playing = False
    
    @pyqtSignature("")
    def startMovie(self):
        self.movie.start()
        self.playing = True
    
    @pyqtSignature("")
    def stopMovie(self):
        self.movie.stop()
        self.playing = False
    
    def paint(self, painter, option, index):
        if index.column() == 0:
            waiting = index.data(Qt.UserRole).toBool()
            if waiting:
                option = option.__class__(option)
                pixmap = self.movie.currentPixmap()
                painter.drawPixmap(option.rect.topLeft(), pixmap)
                option.rect = option.rect.translated(pixmap.width(), 0)
            
        QItemDelegate.paint(self, painter, option, index)
