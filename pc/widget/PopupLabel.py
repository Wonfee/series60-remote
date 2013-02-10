# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

import re
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class PopupLabel(QLabel):
    def __init__(self,  parent=None):
        super(PopupLabel,  self).__init__(parent)
        
        self.setWordWrap(True)
        self.setAlignment(Qt.AlignLeft)
        self.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        self.setOpenExternalLinks(True)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Minimum,  QSizePolicy.Minimum))

    def mouseReleaseEvent(self,  e):
        self.emit(SIGNAL("clicked()"))
        self.emit(SIGNAL("clicked(QPoint)"),  e.pos())
    
    def sizeHint(self):
        # Ugly hack...
        metrics = self.fontMetrics()
        bFont = self.font()
        bFont.setBold(True)
        bMetrics = QFontMetrics(bFont)
        
        iFont = self.font()
        iFont.setItalic(True)
        iMetrics = QFontMetrics(iFont)
        
        maxWidth = 0
        
        for line in self.text().split("<br />"):
            width = 0
            
            # HACK: QFontMetrics doesn't handle HTML tags, so we have to
            # extract the bold words and calculate its width
            # Find bold words (in <b> tags)
            find = re.findall("(?i)<b>([^<]*)</b>", unicode(line))
            if find:
                for result in find:
                   width +=  bMetrics.width(result)
                   line = line.replace("<b>" + result + "</b>",  "",  1)

            # Find italic words (in <i> tags)
            find = re.findall("(?i)<i>([^<]*)</i>", unicode(line))
            if find:
                for result in find:
                   width +=  iMetrics.width(result)
                   line = line.replace("<i>" + result + "</i>",  "",  1)
            
            # Ignore all other HTML tags (like <div>)
            find = re.findall("(?i)(<.*>)", unicode(line))
            if find:
                for result in find:
                   line = line.replace(result,  "",  1)

            width += metrics.width(line)
            maxWidth = max(maxWidth,  width)
        
        maxWidth = min(maxWidth,  self.maximumWidth())
        maxWidth += self.frameWidth() # Should be 0
        maxWidth += 1
        return QSize(maxWidth,  self.heightForWidth(maxWidth))
    
