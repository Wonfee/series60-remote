# -*- coding: utf-8 -*-

# File kdepim/calendarviews/eventviews/month/monthgraphicsitems.cpp originally taken from the KDE project.
# Copyright (c) 2008 Bruno Virlet <bruno.virlet@gmail.com>
# Copyright (c) 2008 Thomas Thrainer <tom_t@gmx.at>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from lib.classes import Enum

ArrowDirection = Enum("Up Down")

class ScrollIndicator(QGraphicsItem):
    def __init__(self,  parent,  direction):
        super(ScrollIndicator,  self).__init__(None,  parent)

        self.setZValue(200) # on top of everything
        self.hide()

        self.direction = direction

        self.width = 30
        self.height = 10

    def boundingRect(self):
        return QRectF(-self.width / 2, -self.height / 2, self.width, self.height)

    def paint(self,  painter,  option,  widget):
        painter.setRenderHint(QPainter.Antialiasing)

        arrow = QPolygon(3)
        if self.direction == ArrowDirection.Up:
            arrow.setPoint(0, 0, -self.height / 2)
            arrow.setPoint(1, self.width / 2, self.height / 2)
            arrow.setPoint(2, -self.width / 2, self.height / 2)
        elif self.direction == ArrowDirection.Down:
            arrow.setPoint(1, self.width / 2, -self.height / 2)
            arrow.setPoint(2, -self.width / 2, -self.height / 2)
            arrow.setPoint(0, 0, self.height / 2)

        color = QColor(Qt.black)
        color.setAlpha(155)

        painter.setBrush(color)
        painter.setPen(color)
        painter.drawPolygon(arrow)
