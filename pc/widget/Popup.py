# -*- coding: utf-8 -*-

# File kpassivepopup.cpp originally taken from the KDE project.
# Copyright (c) 2001-2006 Richard Moore <rich@kde.org>
# Copyright (c) 2004-2005 Sascha Cunz <sascha.cunz@tiscali.de>
# Copyright (c) 2008 - 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from widget.PopupLabel import PopupLabel
from lib.classes import *

ANIMATION_SUPPORT = "QPropertyAnimation" in dir()

class Popup(QFrame):
    def __init__(self,  parent,  main):
        super(Popup,  self).__init__(parent)

        self.parent = parent
        self.main = main
        self.settings = self.main.settings

        self.log = main.log

        self.setWindowFlags(Qt.Tool| Qt.X11BypassWindowManagerHint | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setFrameStyle( QFrame.Box| QFrame.Plain )
        self.setLineWidth( 2 )

        self.BUTTON_1 = 0
        self.BUTTON_2 = 1
        
        self.closeAnimation = None
        self.closeTimer = QTimer(self)

        self.__parent = parent
        self.__mouseUnderWidget = self.underMouse()
        self.__target = None
        self.__interval = 0
        self.__maxWidth = 0
        self.__popupType = PopupTypes.Unknown
        self.__close = False
        self.__waitForClose = False
        self.__forceClose = False

        # Create the layout..
        self.__mainLayout = QHBoxLayout(self)
        self.__mainLayout.setMargin(8)
        self.__mainLayout.setSpacing(6)

        self.__textLayout = QVBoxLayout()
        self.__textLayout.setMargin(8)
        self.__textLayout.setSpacing(6)

        self.__iconLabel = QLabel(self)
        self.__iconLabel.setAlignment(Qt.AlignLeft)
        self.__mainLayout.addWidget(self.__iconLabel)

        self.__captionLabel = PopupLabel(self)
        fnt = self.__captionLabel.font()
        fnt.setBold(True)
        self.__captionLabel.setFont(fnt)
        self.__captionLabel.setAlignment(Qt.AlignHCenter)
        self.__textLayout.setStretchFactor(self.__captionLabel,  10)  # force centering
        self.__textLayout.addWidget(self.__captionLabel)

        self.__messageLabel = PopupLabel(self)
        self.__textLayout.addWidget(self.__messageLabel)

        self.__mainLayout.addLayout(self.__textLayout)

        self.buttons = QDialogButtonBox(self)
        self.buttons.setCenterButtons(True)

        self.connect(self.closeTimer,  SIGNAL("timeout()"),  lambda : self.waitForClose())
        self.connect(self, SIGNAL("clicked()"), self.forceClose)        
        self.connect(self.__iconLabel, SIGNAL("clicked()"), self.forceClose)        
        self.connect(self.__captionLabel, SIGNAL("clicked()"), self.forceClose)        
        self.connect(self.__messageLabel, SIGNAL("clicked()"), self.forceClose)        

    def __str__(self):
        return "\"Popup\""

    def setCaption(self,  caption):
        self.__captionLabel.setText(caption)

    def setText(self,  text):
        self.__messageLabel.setText(text)

    def setIcon(self,  icon):
        self.__iconLabel.setPixmap(QPixmap(icon))

    def setTarget(self,  target):
        self.__target = target

    def setTimeout(self,  interval):
        self.__interval = interval

    def setMaximumWidth(self,  width):
        QFrame.setMaximumWidth(self,  width)
        self.__messageLabel.setMaximumWidth(width - self.__iconLabel.frameGeometry().width())
        self.__captionLabel.setMaximumWidth(width - self.__iconLabel.frameGeometry().width())

    def setPopupType(self,  type):
        self.__popupType = type

    def addButton(self,  text):
        return self.buttons.addButton(text,  QDialogButtonBox.AcceptRole)

    def caption(self):
        return self.__captionLabel.text()

    def text(self):
        return self.__messageLabel.text()

    def icon(self):
        return self.__iconLabel.pixmap()

    def target(self):
        return self.__target

    def timeout(self):
        return self.__interval

    def maximalWidth(self):
        return self.__maxWidth

    def popupType(self):
        return self.__popupType

    def resetTimer(self):
        if self.closeTimer.isActive():
            self.closeTimer.stop()
            self.closeTimer.start()

    def showPopup(self,  caption=None,  text=None,  icon=None,  target=None,  interval=None,  popupType=None):
        if caption:
            self.setCaption(caption)

        if text:
            self.setText(text)

        if icon:
            self.setIcon(icon)

        if target:
            self.setTarget(target)

        if interval:
            self.setTimeout(interval)

        if popupType:
            self.setPopupType(popupType)

        if self.buttons.buttons():
            self.__textLayout.addWidget(self.buttons)
            self.connect(self.buttons, SIGNAL("clicked(QAbstractButton *)"), lambda btn: self.forceCloseWithoutAnimation())

        if self.timeout():
            self.closeTimer.setInterval(self.timeout() * 1000)
            self.closeTimer.setSingleShot(True)
            self.closeTimer.start()
        
        self.log.info(QString("Show Popup with caption %1 and text %2").arg(self.caption(),  self.text()))

        self.main.popups.append(self)
        
        if self.target():
            self.moveNear(self.target(),  animate=self.settings.setting("popups/animate"))
        else:
            target = QApplication.desktop().availableGeometry()
            self.moveNear(target,  bottomRight=True,  animate=False)

    def moveNear(self,  target,  bottomRight=False,  animate=False):
        pos = self.calculateNearbyPoint(self,  target,  bottomRight)
        
        if animate and ANIMATION_SUPPORT:
            # If we animate the move we place the popup next to target
            # After setGeometry is called we get a resizeEvent and the popup is moved to its location
            oldGeometry = QRect(pos.x(),  target.y(),  
                                self.sizeHint().width(),  self.sizeHint().height())

            self.setGeometry(oldGeometry)
            self.show()
        else:
            # When there is no animation support the popup is moved to the final location
            if len(self.main.popups) > 1: # The current popup is already in the list...
                # The final location is above (frameGeometry().top()) the last popup
                last = self.main.popups[len(self.main.popups)-2]
                target = QRect(target.x(),  last.frameGeometry().top()-self.sizeHint().height(),
                               self.sizeHint().width(),  self.sizeHint().height())
                pos = self.calculateNearbyPoint(self,  target,  bottomRight)
                
            self.move(pos)
            self.show()

    @staticmethod
    def calculateNearbyPoint(widget,  target,  bottomRight=False):
        if bottomRight:
            pos = target.bottomRight()
        else:
            pos = target.topLeft()
        x = pos.x()
        y = pos.y()
        w = widget.sizeHint().width()
        h = widget.height()

        r = QApplication.desktop().availableGeometry()

        if x < r.center().x():
            x = x + target.width()
        else:
            x = x - w

        # It's apparently trying to go off screen, so display it ALL at the bottom.
        if (y + h) > r.bottom():
            y = r.bottom() - h

        if (x + w) > r.right():
            x = r.right() - w
        
        if y < r.top():
            y = r.top()

        if x < r.left():
            x = r.left()

        return QPoint(x,  y)
    
    @staticmethod
    def repositionPopups(popups,  target,  animate=False):
        screen = QApplication.desktop().availableGeometry().center().y()
        newGeometry = None
        for popup in popups:
            if newGeometry:
                if popups[0].geometry().y() > screen:
                    # The popups are aligned from bottom to top..
                    newTarget = QRect(target.x(),  newGeometry.top() - popup.height(),  
                                      popup.sizeHint().width(),  popup.height())
                else:
                    # Popups are from top to bottom...
                    newTarget = QRect(target.x(),  newGeometry.bottom() + 1,  
                                      popup.sizeHint().width(),  popup.height())
            else:
                newTarget = target
            
            newPoint = Popup.calculateNearbyPoint(popup,  newTarget)
            newGeometry = QRect(newPoint.x(),  newPoint.y(),  
                                popup.sizeHint().width(),  popup.height())
            
            if animate and ANIMATION_SUPPORT:
                geometry = popup.geometry()
                if geometry.y() < 0:
                    geometry.setY(target.y())
            
                popup.moveAnimation = QPropertyAnimation(popup,  "geometry")
                popup.moveAnimation.setDuration(500)
                popup.moveAnimation.setStartValue(QVariant(geometry))
                popup.moveAnimation.setEndValue(QVariant(newGeometry))

                popup.moveAnimation.start()
            else:
                popup.move(newPoint)
    
    def mouseReleaseEvent(self,  e):
        self.emit(SIGNAL("clicked()"))
        self.emit(SIGNAL("clicked(QPoint)"),  e.pos())

    def waitForClose(self):
        self.__waitForClose = True
        if not self.__mouseUnderWidget:
            self.close()

    def forceClose(self):
        self.__close = False
        self.__forceClose = True
        self.close()

    def forceCloseWithoutAnimation(self):
        self.__close = True
        self.__forceClose = True
        self.close()

    def enterEvent(self,  event):
        self.__mouseUnderWidget = True
        if self.__close and not self.__forceClose and self.closeAnimation and self.closeAnimation.state() == QAbstractAnimation.Running:
            self.__close = False
            self.closeAnimation.stop()
            self.setWindowOpacity(1.0)

    def leaveEvent(self,  event):
        self.__mouseUnderWidget = False
        if self.__waitForClose:
            self.close()

    def closeEvent(self,  event):
        try:
            self.main.popups.remove(self)
        except ValueError:
            pass
        if self.__close or not ANIMATION_SUPPORT or not self.settings.setting("popups/animate"):
            event.accept()
            self.repositionPopups(self.main.popups,  self.target(),  animate=self.settings.setting("popups/animate"))
        else:
            event.ignore()
            self.__close = True
            self.closeAnimation = QPropertyAnimation(self,  "windowOpacity")
            self.closeAnimation.setDuration(500)
            self.closeAnimation.setStartValue(QVariant(1.0))
            self.closeAnimation.setEndValue(QVariant(0.0))

            self.connect(self.closeAnimation,  SIGNAL("finished()"),  self,  SLOT("close()"))
            self.closeAnimation.start()

    def resizeEvent(self,  event):
        self.repositionPopups(self.main.popups,  self.target(),  animate=self.settings.setting("popups/animate"))
