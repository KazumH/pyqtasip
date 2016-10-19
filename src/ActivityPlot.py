import random

from PyQt5.QtWidgets import QSizePolicy

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

#matplotlibのアクティビティバープロット
class ActivityPlot(FigureCanvas):
    def __init__(self, parent=None, width=3, height=3, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axis = fig.add_subplot(111)

        self.fig = FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)

        FigureCanvas.updateGeometry(self)
        self.plot()

    #プロットデータ
    def plot(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        self.draw()