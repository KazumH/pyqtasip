import random

from PyQt5.QtWidgets import QSizePolicy

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPen, QPainter, QPainterPath, QIntValidator, QPixmap, QTransform, QCursor)
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                             QGraphicsPixmapItem, qApp,
                             QLabel, QLineEdit, QSizePolicy)

#アクティビティバープロット
class ActivityPlotScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(ActivityPlotScene, self).__init__(*argv, **keywords)
        self._imageItem = None
        self._currentpos = None
        self._pressedButton = None
        self._zoom = 0
    #プロットデータ
    def plot(self):
        data = [random.random() for i in range(25)]
        ax = self.figure.add_subplot(111)
        ax.plot(data, 'r-')
        self.draw()