# -*- coding: utf-8 -*-

# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class HelpLabel(QLabel):
    def __init__(self,  *args,  **kwargs):
        super(HelpLabel,  self).__init__(*args,  **kwargs)
        
        self.setMouseTracking(True)
        self.setText("<a href='#'>" + self.tr("Help") + "</a>")
        
    def mouseMoveEvent(self,  event):
        text = self.tr("""Python For S60 2.0.0 is supported on devices with
S60 3rd Edition and S60 5th Edition.
But there are some bugs on older S60 3rd Edition
devices. If you're using such device and get any error
during the installation of Python please uncheck this
box and send the installation files again to your device.""")
        
        QToolTip.showText(event.globalPos(),  text,  self,  self.geometry())
