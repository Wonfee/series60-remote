# -*- coding: utf-8 -*-

# File kdepim/calendarviews/eventviews/month/monthscene.cpp originally taken from the KDE project.
# Copyright (c) 2008 Bruno Virlet <bruno.virlet@gmail.com>
# Copyright (c) 2010 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import widget.CalendarCell

class CalendarGraphicsView(QGraphicsView):
    def __init__(self,  parent):
        super(CalendarGraphicsView,  self).__init__(parent)

        # HACK: We need Main()
        main = qApp.property("main").toPyObject()

        self.main = main

        self.calendarView = parent

    def drawBackground(self,  p,  rect):
        p.setFont(QFont("Arial",  10))
        p.fillRect(rect,  Qt.white)

        # Headers
        font = QFont("Arial",  10)
        font.setBold(True)
        font.setPointSize(15)
        p.setFont(font)

        dayLabelsHeight = 20
        p.drawText( QRect( 0,  0, # top right
               self.__scene.sceneRect().width(),
               self.__scene.headerHeight() - dayLabelsHeight ),
            Qt.AlignCenter,
            self.tr( "%1 %2",  "monthname year" ).arg(self.main.locale.standaloneMonthName(self.calendarView.averageDate().month())).arg(self.calendarView.averageDate().year())
        )

        font.setPixelSize( dayLabelsHeight - 10 )
        p.setFont( font )

        # Draw headline with weekdays
        for day in [self.calendarView.actualStartDateTime().date().addDays(i) for i in range(7) ]:
            try:
                cell = self.__scene.cellMap[day]
            except KeyError:
                return
            p.drawText(QRect(
                                self.__scene.cellHorizontalPos( cell ),
                                self.__scene.cellVerticalPos( cell ) - 15,
                                self.__scene.columnWidth(),
                                15
                             ),
                             Qt.AlignCenter,
                             self.main.locale.standaloneDayName(day.dayOfWeek())
            )

        columnWidth = self.__scene.columnWidth()
        rowHeight = self.__scene.rowHeight()

        # Month grid
        for day in [self.calendarView.actualStartDateTime().date().addDays(i) for i in range(self.calendarView.actualStartDateTime().daysTo(self.calendarView.actualEndDateTime())+1)]:
            cell = self.__scene.cellMap[day]

            if day.dayOfWeek() < 6:
                # Monday to Friday are workdays
                color = QColor(225,  225,  255)
            else:
                color = QColor(Qt.white)

            if cell == self.__scene.selectedCell():
                color = color.dark(115)

            if cell.date() == QDate.currentDate():
                color = color.dark(140)

            # Draw cell
            p.setPen( QColor(Qt.white).dark( 150 ) )
            p.setBrush(color)
            p.drawRect( QRect( self.__scene.cellHorizontalPos( cell ), self.__scene.cellVerticalPos( cell ),
                        columnWidth, rowHeight ) )

            # Draw cell header
            cellHeaderX = self.__scene.cellHorizontalPos( cell ) + 1
            cellHeaderY = self.__scene.cellVerticalPos( cell ) + 1
            cellHeaderWidth = columnWidth - 2
            cellHeaderHeight = cell.topMargin() - 2
            bgGradient = QLinearGradient( QPointF( cellHeaderX, cellHeaderY ),
                                        QPointF( cellHeaderX + cellHeaderWidth,
                                                 cellHeaderY + cellHeaderHeight ) )
            bgGradient.setColorAt( 0, color.dark( 105 ) )
            bgGradient.setColorAt( 0.7, color.dark( 105 ) )
            bgGradient.setColorAt( 1, color )
            p.setBrush( bgGradient )

            p.setPen( Qt.NoPen )
            p.drawRect( QRect( cellHeaderX, cellHeaderY,
                                cellHeaderWidth, cellHeaderHeight ) )

        # Draw dates
        font = QFont("Sans Serif")
        font.setPixelSize( widget.CalendarCell.CalendarCell.topMargin() - 4 )
        p.setFont(font)

        oldPen =  QColor(Qt.white).dark(150)

        for day in [self.calendarView.actualStartDateTime().date().addDays(i) for i in range(self.calendarView.actualStartDateTime().daysTo(self.calendarView.actualEndDateTime())+1)]:
            cell = self.__scene.cellMap[day]
            font = p.font()
            if cell.date() == QDate.currentDate():
                font.setBold(True)
            else:
                font.setBold(False)
            p.setFont(font)

            if day.month() == self.calendarView.currentMonth():
                p.setPen(QPen(QPalette.Text))
            else:
                p.setPen(oldPen)

            # Draw arrows if all items won't fit

            # Up arrow if first item is above cell top
            if self.__scene.startHeight() != 0 and cell.hasEventBelow(self.__scene.startHeight()):
                cell.upArrow.setPos(self.__scene.cellHorizontalPos(cell) + self.__scene.columnWidth() / 2,
                                    self.__scene.cellVerticalPos(cell) + cell.upArrow.boundingRect().height() / 2 + 2 )
                cell.upArrow.show()
            else:
                cell.upArrow.hide()

            # Down arrow if last item is below cell bottom
            if not self.__scene.lastItemFit(cell):
                cell.downArrow.setPos(self.__scene.cellHorizontalPos(cell) + self.__scene.columnWidth() / 2,
                                      self.__scene.cellVerticalPos(cell) + self.__scene.rowHeight() - cell.downArrow.boundingRect().height() / 2 - 2 )
                cell.downArrow.show()
            else:
                cell.downArrow.hide()

            # Prepend month name if d is the first or last day of month
            if day.day() == 1 or day.day() == day.daysInMonth():
                dayText = self.tr("%1 %2",  "'Month day' for month view cells").arg(self.main.locale.standaloneMonthName(day.month(), QLocale.ShortFormat)).arg(day.day())
            else:
                dayText = str(day.day())

            p.drawText( QRect( self.__scene.cellHorizontalPos( cell ),
                        self.__scene.cellVerticalPos( cell ),
                        self.__scene.columnWidth() - 2,
                        cell.topMargin() ),
                 Qt.AlignRight,
                 dayText
            )

    def setScene(self,  scene):
        self.__scene = scene
        QGraphicsView.setScene(self,  scene)

    def resizeEvent(self,  event):
        self.__scene.setSceneRect(0, 0, event.size().width(), event.size().height())
        self.__scene.updateGeometry()
