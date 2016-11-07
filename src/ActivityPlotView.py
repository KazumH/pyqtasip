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
timeRange = 50 #分数
announceFile = "a.0802241824-0802241923.pickle"
withdrawFile = "w.0802241824-0802241923.pickle"

#アクティビティバープロット(トポロジ全体)
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
        #時間がキーで、その時間にアナウンスされたエッジ全て(重み集計なし)
        f = open("../data/pickles/%s" % announceFile, "rb")
        self.announce = pickle.load(f)

        f = open("../data/pickles/%s" % withdrawFile, "rb")
        self.withdraw = pickle.load(f)
        timeRangeFrom = "0802241824"
        timeRangeTo = "0802241923"
        startDate = timeRangeFrom[:len(timeRangeFrom)-4]
        startMin = int(timeRangeFrom[len(timeRangeFrom)-2:])#下2桁
        startHour = int(timeRangeFrom[len(timeRangeFrom)-4:len(timeRangeFrom)-2])#下4桁〜下2桁
        # withdrawならそのまま
        for i in range(timeRange):
            min = i + startMin #時間繰り上げなしの分カウント
            if min > 59:
                currentMin = min % 60
                if currentMin < 10:
                    strMin = "0" + str(currentMin)#"00 ~ 09"
                else:
                    strMin = str(currentMin)#"10 ~ 59"
            else:
                strMin = str(min)
            hour = min // 60
            currentHour = startHour + hour
            strHour = str(currentHour)
            time = startDate + strHour + strMin
            print(time)
            value = math.log(len(self.announce[time]), 1.1)

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