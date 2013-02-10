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
    class ContactCanvas(FigureCanvas):
            def __init__(self, parent=None, width = 10, height = 3, dpi = 100, sharex = None, sharey = None):
                    self.fig = Figure(figsize = (width, height), dpi=dpi, facecolor = '#FFFFFF')
                    self.ax = self.fig.add_subplot(111, sharex = sharex, sharey = sharey)
                    FigureCanvas.__init__(self, self.fig)
                    FigureCanvas.setSizePolicy(self,
                            QSizePolicy.Expanding,
                            QSizePolicy.Expanding)
                    FigureCanvas.updateGeometry(self)

            def format_labels(self):
                    labels_x = self.ax.get_xticklabels()
                    labels_y = self.ax.get_yticklabels()
                    for xlabel in labels_x:
                            xlabel.set_fontsize(8)
                    for ylabel in labels_y:
                            ylabel.set_fontsize(8)
                            ylabel.set_color('b')

else:
    class ContactCanvas(QLabel):
            def __init__(self, parent=None):
                super(ContactCanvas,  self).__init__(parent)
                self.setText(self.tr("Matplotlib not found - Please install it."))
