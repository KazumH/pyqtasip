#参考: http://melpystudio.blog82.fc2.com/blog-entry-138.html
import pickle

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QIntValidator, QPixmap, QTransform, QCursor)
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QGraphicsPixmapItem, qApp,
                             QLabel, QLineEdit, QSizePolicy)

import networkx as nx
import csv

#ビューのサイズ
viewheight = 600
viewwidth = 900
targetdir = "TTNet/"
overalledges = []


class Node(QGraphicsItem):
    def __init__(self):
        super(Node, self).__init__()
        self.setFlags(QGraphicsItem.ItemIsFocusable |
                      QGraphicsItem.ItemIsMovable |
                      QGraphicsItem.ItemIsSelectable)
        self._colorNum = 0
        self._currentTimeWindow = 0
        self._weightThreshold = 50
        # ピクルデータからノードデータを読み込む

        f = open("../data/pickles/20041224.0816-20041224.1018.pickle", "rb")
        global pos
        pos = pickle.load(f)  # '29003': array([ 0.22507305,  0.59479266], dtype=float32)

        # ピクルデータからエッジデータを読む
        # [('33405', '22026', {'weight': 2}), ('22143', '7795', {'weight': 8})]
        """
        f = open("../data/pickles/e.20041224.0816-20041224.1018.pickle", "rb")
        global overalledges
        overalledges = pickle.load(f)
        """
        # CSVから各時間窓のエッジデータを読み込む

        for i in range(9):
            targetpath = "../data/csv/" + targetdir + str(i + 1) + "/edges.csv"
            edgefile = open("%s" % targetpath, "r")
            reader = csv.reader(edgefile)
            edges = []
            for row in reader:
                edges.append([row[0], row[1], int(row[2])])
            overalledges.append(edges)

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

#描画部分
    def paint(self, painter, option, widget):

#ノード描画
        painter.setPen(QColor.fromHsvF(330 / 360, 1, 1))


        for node in pos.values():
            #node = pos["701"]
            x = node[0]
            y = node[1]
            #x、yは 0 〜 1を取る400 * 600のビュー内に出すには 600 * x、400 * y、をしてやればpyplotと同じ座標になるはず
            x *= viewwidth
            y *= viewheight
            painter.drawEllipse(QPointF(x, y), 5, 5) #QPointFは浮動小数点制度の平面上の店を定義するクラス

#エッジ描画
        painter.setPen(QColor.fromHsvF(210 / 360, 1, 1))
        #for i in range(9):
        for edge in overalledges[self._currentTimeWindow]:
            u = edge[0]
            v = edge[1]
            weight = edge[2]
            if weight <= self._weightThreshold:
                continue
            u_pos_x = pos[u][0]
            u_pos_y = pos[u][1]
            u_pos_x *= viewwidth
            u_pos_y *= viewheight
            v_pos_x = pos[v][0]
            v_pos_y = pos[v][1]
            v_pos_x *= viewwidth
            v_pos_y *= viewheight
            #print(u_pos_x, u_pos_y, v_pos_x, v_pos_y)
            #if self._currentTimeWindow == i:
            #    painter.setPen(QColor.fromHsvF(30 / 360, 1, 1))
            #    painter.drawLine(u_pos_x, u_pos_y, v_pos_x, v_pos_y)
            #    painter.setPen(QColor.fromHsvF(210 / 360, 1, 1))
            painter.drawLine(u_pos_x, u_pos_y, v_pos_x, v_pos_y)

    def boundingRect(self):
        return QRectF(0, 0, 300, 300)

    def hoverEnterEvent(self, event):
        print("Node Hover!!")

    def mousePressEvent(self, event): #一応反応しているみたいだが・・・
        print("Node Clicked!!")
        pos = event.pos()
        self.select(int(pos.x() / 100), int(pos.y() / 100))
        self.update()
        super(Node, self).mousePressEvent(event)

# Nextボタンを押すと次のステップを実行
    def do_next(self):
        print("Next Button Clicked!!")
        #色変え
        if self._colorNum >= 360:
            self._colorNum = 0
        else:
            self._colorNum += 30
        #時間窓変更
        if self._currentTimeWindow >= 8:
            self._currentTimeWindow = 0
        else:
            self._currentTimeWindow += 1
        print(self._currentTimeWindow)
        self.update()

# Previousボタンを押すと次のステップを実行
    def do_back(self):
        print("Previous Button Clicked!!")
        # 色変え
        if self._colorNum >= 360:
            self._colorNum = 0
        else:
            self._colorNum += 30
        # 時間窓変更
        if self._currentTimeWindow <= 0:
            self._currentTimeWindow = 8
        else:
            self._currentTimeWindow -= 1
        print(self._currentTimeWindow)
        self.update()

#スライダで閾値が変わった時
    def thresholdchanged(self, currentValue):
        self._weightThreshold = currentValue
        print("Slider !!", self._weightThreshold)
        self.update()

# ノードリンク図部分全体
class NodeLinkScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(NodeLinkScene, self).__init__(*argv, **keywords)
        self._imageItem = None
        self._currentpos = None
        self._pressedButton = None
        self._zoom = 0

        self.setBackgroundBrush(QColor(0, 0, 0, 10)) #背景色。4つめは~255のアルファ値

    def setFile(self, filepath):
        # イメージをアイテムとしてシーンに追加するためのメソッド
        pixmap = QPixmap(filepath)
        #すでにシーンにPixmapアイテムがある時は削除する
        if self._imageItem:
            self.removeItem(self._imageItem)

        #与えられたイメージをPixmapアイテムとしてシーンに追加
        item = QGraphicsPixmapItem(pixmap)
        #アイテムを移動可能なアイテムにする
        item.setFlags(QGraphicsItem.ItemIsMovable)
        self.addItem(item)
        self.fitImage()

    def imageItem(self):
        return self._imageItem

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
        self._currentPos = event.scenePos()
        self._pressedButton = event.button()

        #右クリック
        if self._pressedButton == Qt.RightButton:
            print("Right Button Clicked!!")
            cursorShape = Qt.SizeAllCursor
        else:
            print("Left Button Clicked!!")
            cursorShape = Qt.ClosedHandCursor
        #qAppはQtWidgetの中
        qApp.setOverrideCursor(QCursor(cursorShape))

    # マウスのドラッグ中の処理イベント
    def mouseMoveEvent(self, event):
        if not self._currentPos:
            return

        #シーンの現在位置
        cur = event.scenePos()
        #差分(デルタ)
        value = cur - self._currentPos
        self._currentPos = cur

        print(cur, value)
    def mouseReleaseEvent(self, event):
        self._currentPos = None
        self._pressedButton = None
        qApp.restoreOverrideCursor()
        super(NodeLinkScene, self).mouseReleaseEvent(event)

    #マウスホイールで拡大縮小
    def wheelEvent(self, event):
        if event.delta() > 0:
            factor = 1.25
            self._zoom += 1
        else:
            factor = 0.8
            self._zoom -= 1

        if self._zoom > 0:
            self.scale(factor, factor)
        elif self._zoom == 0:
            self.fitInView()
        else:
            self._zoom = 0