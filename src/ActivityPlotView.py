import random

from PyQt5.QtWidgets import QSizePolicy

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPen, QPainter, QPainterPath, QIntValidator, QPixmap, QTransform, QCursor)
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
                             QGraphicsPixmapItem, qApp,
                             QLabel, QLineEdit, QSizePolicy)
import pickle
import math
#ビューのサイズ
viewheight = 300
viewwidth = 300

#バーの色
announcebarColor = QColor.fromHsvF(145/360, 1, 1)
announcebarPen = QPen(announcebarColor)
announcebarBrush = QBrush(announcebarColor)
withdrawbarColor = QColor.fromHsvF(15/360, 1, 1)
withdrawbarPen = QPen(withdrawbarColor)
withdrawbarBrush = QBrush(withdrawbarColor)
barWidth = 10

#アクティビティバープロット
class ActivityPlotView(QGraphicsView):
    def __init__(self, height=50 ,width=100 ,size=5):
        super(ActivityPlotView, self).__init__()
        self.plotScene = PlotScene(QRectF(0, 0, 300, 500))
        #self.plotScene.setSceneRect(0, 0, viewheight, viewwidth)
        self.setScene(self.plotScene)
        self.width = width
        self.height = height
        self.size = size
        self._currentpos = None
        self._pressedButton = None
        self.plot()

    def plot(self):

        f = open("../data/pickles/a.20080224.1824-20080224.1923.pickle", "rb")
        self.announce = pickle.load(f)

        f = open("../data/pickles/w.20080224.1824-20080224.1923.pickle", "rb")
        self.withdraw = pickle.load(f)

        # withdrawならそのまま
        for i in range(30):
            time = "08022418" + str(i + 24)
            value = math.log(len(self.announce[time]), 1.1)
            print(value)
            announcebar = QGraphicsRectItem(i * barWidth, 200, barWidth, -value)
            announcebar.setPen(announcebarPen)
            announcebar.setBrush(announcebarBrush)
            announcebar.setFlags(QGraphicsItem.ItemIsSelectable)
            self.plotScene.addItem(announcebar)
            withdrawbar = QGraphicsRectItem(i * barWidth, 200, barWidth, value)
            withdrawbar.setPen(withdrawbarPen)
            withdrawbar.setBrush(withdrawbarBrush)
            withdrawbar.setFlags(QGraphicsItem.ItemIsSelectable)
            self.plotScene.addItem(withdrawbar)
        vertivalCenter = self.height / 2
        horizontalCenter = self.width / 2

    def boundingRect(self):
        return QRectF(0, 0, 300, 300)

    #ここで定義すると、QGraphicsScene内でのマウスイベントより、こちらが優先される
    #def mousePressEvent(self, event):
    #    pos_x = event.pos().x()
    #    pos_y = event.pos().y()
    #    print(pos_x, pos_y)
    #    print(self.announce["0802241900"])

class PlotScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(PlotScene, self).__init__(*argv, **keywords)
        self._imageItem = None
        self._currentpos = None
        self._pressedButton = None
        self._zoom = 0

    def mousePressEvent(self, event):
        clickedItem = self.itemAt(event.scenePos(), QTransform())
        print(event.scenePos())
        print(clickedItem)