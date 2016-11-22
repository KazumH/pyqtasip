import sys

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

    def dataReceive(self, data):

        time = data._time