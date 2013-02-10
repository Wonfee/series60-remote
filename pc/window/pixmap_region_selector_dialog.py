# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui.ui_pixmap_region_selector_dialog

class PixmapRegionSelectorDialog(QDialog, ui.ui_pixmap_region_selector_dialog.Ui_PixmapRegionSelectorDialog):
    def __init__(self,  parent=None):
        super(PixmapRegionSelectorDialog,  self).__init__(parent)
        
        self.setupUi(self)
        self.buttonBox.button(QDialogButtonBox.Ok).setIcon(QIcon(":/dialog-ok"))
        self.buttonBox.button(QDialogButtonBox.Cancel).setIcon(QIcon(":/dialog-close"))

    def pixmapRegionSelectorWidget(self):
        return self.pixmapSelectorWidget
    
    def getSelectedRegion(self,  pixmap,  aspectRatio=None,  parent=None):
        dialog = PixmapRegionSelectorDialog(parent)
        dialog.pixmapRegionSelectorWidget().setPixmap(pixmap)
        
        if aspectRatio:
            assert isinstance(aspectRatio,  list) or isinstance(aspectRatio,  tuple),  "expected a list or tuple"
            dialog.pixmapRegionSelectorWidget().setSelectionAspectRatio(aspectRatio[0],  aspectRatio[1])
        
        desktopWidget = QDesktopWidget()
        screen = desktopWidget.availableGeometry()
        dialog.pixmapRegionSelectorWidget().setMaximumWidgetSize(int(screen.width() * 4.0 / 5),  int(screen.height() * 4.0 / 5))
        
        result = dialog.exec_()
        rect = QRect()
        
        if result == QDialog.Accepted:
            rect = dialog.pixmapRegionSelectorWidget().unzoomedSelectedRegion()
        
        return rect
    
    def getSelectedImage(self,  pixmap,  aspectRatio=None,  parent=None):
        dialog = PixmapRegionSelectorDialog(parent)
        dialog.pixmapRegionSelectorWidget().setPixmap(pixmap)
        
        if aspectRatio:
            assert isinstance(aspectRatio,  list) or isinstance(aspectRatio,  tuple),  "expected a list or tuple"
            dialog.pixmapRegionSelectorWidget().setSelectionAspectRatio(aspectRatio[0],  aspectRatio[1])
        
        desktopWidget = QDesktopWidget()
        screen = desktopWidget.availableGeometry()
        dialog.pixmapRegionSelectorWidget().setMaximumWidgetSize(int(screen.width() * 4.0 / 5),  int(screen.height() * 4.0 / 5))
        
        result = dialog.exec_()
        image = QImage()
        
        if result == QDialog.Accepted:
            image = dialog.pixmapRegionSelectorWidget().selectedImage()
        
        return image
