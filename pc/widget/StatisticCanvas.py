# -*- coding: utf-8 -*-

# Copyright (c) 2008 - 2009 Lukas Hetzenecker <LuHe@gmx.at>

from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Matplotlib
try:
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
    from matplotlib.figure import Figure
except ImportError:
    USE_MATPLOTLIB = False
else:
    USE_MATPLOTLIB= True

if USE_MATPLOTLIB:
    class StatisticCanvas(FigureCanvas):
            def __init__(self, parent=None, width = 10, height = 1.7, dpi = 100, sharex = None, sharey = None):
                    self.fig = Figure(figsize = (width, height), dpi=dpi, facecolor = '#FFFFFF')
                    self.ax = self.fig.add_subplot(111, sharex = sharex, sharey = sharey)
                    self.fig.subplots_adjust(left=0.1, bottom=0.1, right=0.9, top=0.9)
                    #self.xtitle="x-Axis"
                    self.ytitle= QApplication.translate("All Messages",  str(self))
                    #self.PlotTitle = "Some Plot"
                    self.grid_status = True
                    self.xaxis_style = 'linear'
                    self.yaxis_style = 'linear'
                    #self.format_labels()
                    #self.ax.hold(True)
                    FigureCanvas.__init__(self, self.fig)
                    FigureCanvas.setSizePolicy(self,
                            QSizePolicy.Expanding,
                            QSizePolicy.Expanding)
                    FigureCanvas.updateGeometry(self)

            def format_labels(self):
                    #self.ax.set_title(self.PlotTitle)
                    #self.ax.title.set_fontsize(10)
                    #self.ax.set_xlabel(self.xtitle, fontsize = 9)
                    self.ax.set_ylabel(self.ytitle, fontsize = 9)
                    labels_x = self.ax.get_xticklabels()
                    labels_y = self.ax.get_yticklabels()

                    for xlabel in labels_x:
                            xlabel.set_fontsize(8)
                    for ylabel in labels_y:
                            ylabel.set_fontsize(8)
                            ylabel.set_color('b')

            #def sizeHint(self):
            #        w, h = self.get_width_height()
            #        return QSize(w, h)

            def minimumSizeHint(self):
                    return QSize(10, 10)

else:
    class StatisticCanvas(QLabel):
            def __init__(self, parent=None):
                super(StatisticCanvas,  self).__init__(parent)
                self.setText(self.tr("Matplotlib not found - Please install it."))
