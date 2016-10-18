import pickle

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QIntValidator, QPixmap, QTransform, QCursor)
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QGraphicsPixmapItem, qApp,
                             QLabel, QLineEdit, QPushButton, QSlider, QSizePolicy)

#ビューのサイズ
viewheight = 600
viewwidth = 900

class Node(QGraphicsItem):
    def __init__(self):
        super(Node, self).__init__()
        self.board = [[-1, -1, -1], [-1, -1, -1], [-1, -1, -1]]
        self.O = 0
        self.X = 1
        self.turn = self.O

    def reset(self):
        for y in range(3):
            for x in range(3):
                self.board[y][x] = -1
        self.turn = self.O
        self.update()

    def select(self, x, y):
        if x < 0 or y < 0 or x >= 3 or y >= 3:
            return
        if self.board[y][x] == -1:
            self.board[y][x] = self.turn
            self.turn = 1 - self.turn

    def paint(self, painter, option, widget):
        # ノード色
        painter.setPen(QColor.fromHsvF(30 / 360, 1, 1))
        # 位置情報データ読み込み
        f = open("../data/pickles/20041224.0816-20041224.1018.pickle", "rb")
        pos = pickle.load(f)
        for node in pos.values():
            #node = pos["701"]
            x = node[0]
            y = node[1]
            #x、yは 0 〜 1を取る400 * 600のビュー内に出すには 600 * x、400 * y、をしてやればpyplotと同じ座標になるはず
            x *= viewwidth
            y *= viewheight

            #pos = '29003': array([ 0.22507305,  0.59479266], dtype=float32)

            painter.drawEllipse(QPointF(x, y), 5, 5) #QPointFは浮動小数点制度の平面上の店を定義するクラス

    def boundingRect(self):
        return QRectF(0, 0, 300, 300)

    def hoverEnterEvent(self, event):
        print("Node Hover!!")
    def mousePressEvent(self, event):
        print("Node Clicked!!")
        pos = event.pos()
        self.select(int(pos.x() / 100), int(pos.y() / 100))
        self.update()
        super(Node, self).mousePressEvent(event)

# ノードリンク図部分全体
class NodeLinkScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(NodeLinkScene, self).__init__(*argv, **keywords)
        self.__imageItem = None
        self.__currentpos = None
        self.__pressedButton = None

    def setFile(self, filepath):
        # イメージをアイテムとしてシーンに追加するためのメソッド
        pixmap = QPixmap(filepath)
        #すでにシーンにPixmapアイテムがある時は削除する
        if self.__imageItem:
            self.removeItem(self.__imageItem)

        #与えられたイメージをPixmapアイテムとしてシーンに追加
        item = QGraphicsPixmapItem(pixmap)
        #アイテムを移動可能なアイテムにする
        item.setFlags(QGraphicsItem.ItemIsMovable)
        self.addItem(item)
        self.fitImage()

    def imageItem(self):
        return self.__imageItem

    def fitImage(self):
        #イメージをシーンのサイズに合わせてフィットするためのメソッド
        if not self.imageItem():
            return
        #イメージの元の大きさを持つRectオブジェクト
        boundingRect = self.imageItem().boundingRect()
        sceneRect = self.sceneRect()

        itemAspectRatio = boundingRect.width() / boundingRect.height()
        sceneAspectRatio = sceneRect.width() / sceneRect.height()

        #最終的にイメージのアイテムに適応するためのTransformオブジェクト
        transform = QTransform()

        if itemAspectRatio >= sceneAspectRatio:
            #横幅に合わせて
            scaleRation = sceneRect.width() / boundingRect.width()
        else:
            #縦の高さに合わせてフィット
            scaleRatio = sceneRect.height() / boundingRect.height()

        #アスペクト比からスケール日を割出しTransformオブジェクトへ適用
        transform.scale(scaleRatio, scaleRatio)
        self.imageItem().setTransform(transform)

    def mouseDoubleClickEvent(self, QGraphicsSceneMouseEvent):
        self.fitImage()

    #マウスクリックの処理イベント
    def mousePressEvent(self, event):
        self.__currentPos = event.scenePos()
        self.__pressedButton = event.button()

        #右クリック
        if self.__pressedButton == Qt.RightButton:
            print("Right Button Clicked!!")
            cursorShape = Qt.SizeAllCursor
        else:
            print("Left Button Clicked!!")
            cursorShape = Qt.ClosedHandCursor
        #qAppはQtWidgetの中
        qApp.setOverrideCursor(QCursor(cursorShape))

    # マウスのドラッグ中の処理イベント
    def mouseMoveEvent(self, event):
        if not self.__currentPos:
            return

        #シーンの現在位置
        cur = event.scenePos()
        #差分(デルタ)
        value = cur - self.__currentPos
        self.__currentPos = cur

        print(cur, value)
    def mouseReleaseEvent(self, event):
        self.__currentPos = None
        self.__pressedButton = None
        qApp.restoreOverrideCursor()
        super(NodeLinkScene, self).mouseReleaseEvent(event)