import sys
import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

VIEWSCALE = 2 ** 9

class CountermeasureScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(CountermeasureScene, self).__init__(*argv, **keywords)

class CountermeasureView(QGraphicsView):
    def __init__(self, parent=None):  # 親がいないウィジェットはウィンドウになる
        super(CountermeasureView, self).__init__()
        # QGraphicsViewの設定
        # self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self.countermeasureScene = CountermeasureScene(self)
        self.countermeasureScene.setSceneRect(QRectF(0, 0, VIEWSCALE, VIEWSCALE))
        self.setScene(self.countermeasureScene)
        self._clickedPos = QPoint(0, 0)

    def dataReceive(self, data):
        ipPrefix = data._ipPrefix
        victimAS = data._victimAS
        causeAS = data._causeAS
        time = data._time
        self.countermeasureScene.clear()

    def mousePressEvent(self, event):
        print("Clicked:", event.pos())
        self._clickedPos = event.pos()
        self._frame = QGraphicsRectItem()
        self._frame.setRect(self._clickedPos.x(), self._clickedPos.y(), 1, 10)
        self.countermeasureScene.addItem(self._frame)

    def mouseMoveEvent(self, event):
        #print(event.pos())
        if event.pos().x() - self._clickedPos.x() < 0:
            self._frame.setRect(event.pos().x(),
                                self._clickedPos.y(),
                                math.fabs(event.pos().x() - self._clickedPos.x()),
                                math.fabs(event.pos().y() - self._clickedPos.y())
                                )
            if event.pos().y() - self._clickedPos.y() < 0:#左上に向けてドラッグ
                self._frame.setRect(event.pos().x(),
                                    event.pos().y(),
                                    math.fabs(event.pos().x() - self._clickedPos.x()),
                                    math.fabs(event.pos().y() - self._clickedPos.y())
                                    )
                print(event.pos().y() - self._clickedPos.y())
        elif event.pos().y() - self._clickedPos.y() < 0:#右上に向けてドラッグ
                self._frame.setRect(self._clickedPos.x(),
                                    event.pos().y(),
                                    math.fabs(event.pos().x() - self._clickedPos.x()),
                                    math.fabs(event.pos().y() - self._clickedPos.y())
                                    )

        else:
            self._frame.setRect(self._clickedPos.x(),
                                self._clickedPos.y(),
                                math.fabs(event.pos().x() - self._clickedPos.x()),
                                math.fabs(event.pos().y() - self._clickedPos.y())
                                )