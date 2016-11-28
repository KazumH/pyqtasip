import sys
import math

import IPAddressConverter

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

gridWidth = 0.01
FRAMEGRIDWIDTH = 2

victimColor = QColor.fromHsvF(135/360, 1, 1)
victimColor.setAlpha(32)
victimPen = QPen(victimColor)
victimPen.setWidthF(gridWidth)
victimBrush = QBrush(victimColor)

causeColor = QColor.fromHsvF(330/360, 1, 1)
causeColor.setAlpha(127)
causePen = QPen(causeColor)
causePen.setWidthF(gridWidth)
causeBrush = QBrush(causeColor)

#フレーム
collectColor = QColor.fromHsvF(240/360, 1, 1)
collectColor.setAlpha(200)
collectPen = QPen(collectColor)
collectPen.setWidthF(FRAMEGRIDWIDTH)
collectBrush = QBrush(collectColor)

incollectColor = QColor.fromHsvF(0/360, 1, 1)
incollectColor.setAlpha(200)
incollectPen = QPen(incollectColor)
incollectPen.setWidthF(FRAMEGRIDWIDTH)
incollectBrush = QBrush(incollectColor)

VIEWSCALE = 2 ** 9
POINTSIZE = 10
COLLISIONRANGE = POINTSIZE // 2

DEBUG = False

class Frame(QGraphicsRectItem):
    def __init__(self, size):
        QGraphicsRectItem.__init__(self)
        self._size = size
        self._ipPrefix = ""

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
        self._isMouseButtonOn = False
        self._vertexInterval = VIEWSCALE

    def dataReceive(self, data):
        self.countermeasureScene.clear()
        vPrefix = data._ipPrefix
        vAS = data._victimAS
        cPrefix = data._causePrefix
        cAS = data._causeAS
        t = data._time
        self.blockPairGenerate(vPrefix, vAS, cPrefix, cAS, t)
        self.placeVertex()

    def blockPairGenerate(self, victimPrefix, victimAS, causePrefix, causeAS, time):
        victimp = victimPrefix.split("/")[0]
        victimpl = int(victimPrefix.split("/")[1])
        causep = causePrefix.split("/")[0]
        causepl = int(causePrefix.split("/")[1])
        victimAddressBin = IPAddressConverter.ipToBin(victimp, victimpl)
        victimBitPairs = [victimAddressBin[i: i + 2] for i in range(0, 32, 2)]
        CauseAddressBin = IPAddressConverter.ipToBin(causep, causepl)
        causeBitPairs = [CauseAddressBin[i: i + 2] for i in range(0, 32, 2)]
        isVictimRect = True if victimpl % 2 != 0 else False
        isCauseRect = True if causepl % 2 != 0 else False
        currentScale = VIEWSCALE
        self.victimSmallness = victimpl // 2
        self.causeSmallness = causepl // 2
        # 被害範囲
        posX, posY = 0, 0
        if victimBitPairs[self.victimSmallness]  == "10":
            posY = posY + currentScale // 2
        vBlock = QGraphicsRectItem(QRectF(posX, posY, currentScale, currentScale))
        vBlock.setPen(victimPen)
        vBlock.setBrush(victimBrush)
        self.countermeasureScene.addItem(vBlock)
        #ラベル
        vlbl = QGraphicsTextItem(victimPrefix)
        vlbl.setPos(0, posY)
        self.countermeasureScene.addItem(vlbl)

        #原因範囲ブロック
        posX, posY = 0, 0
        for i in range(self.victimSmallness, self.causeSmallness):
            if causeBitPairs[i] in {"00", "01"}:
                if causeBitPairs[i] == "00":
                    posX += currentScale // 2
            elif causeBitPairs[i] in {"10", "11"}:
                posY = posY + currentScale // 2
                if causeBitPairs[i] == "10":
                    posX += currentScale // 2
            currentScale //= 2
        cBlock = QGraphicsRectItem(QRectF(posX, posY, currentScale, currentScale))
        cBlock.setPen(causePen)
        cBlock.setBrush(causeBrush)
        self.countermeasureScene.addItem(cBlock)
        clbl = QGraphicsTextItem(causePrefix)
        clbl.setPos(posX, posY)
        self.countermeasureScene.addItem(clbl)

    def addBlockPair(self, largeBlock, smallBlock):
        self.countermeasureScene.addItem(largeBlock)
        self.countermeasureScene.addItem(smallBlock)

    def mousePressEvent(self, event):
        self._isMouseButtonOn = True
        idX = event.pos().x() // self._vertexInterval
        idY = event.pos().y() // self._vertexInterval
        self._clickedPosX, self._clickedPosY = self._vertexPos[idX][idY][1], self._vertexPos[idX][idY][0]
        print("click: ", self._clickedPosX, self._clickedPosY)
        self._frame = Frame(1)
        self._frame.setRect(self._clickedPosX, self._clickedPosY, 10, 10)
        self.countermeasureScene.addItem(self._frame)

    def mouseMoveEvent(self, event):
        if self._isMouseButtonOn:
            idX = event.pos().x() // self._vertexInterval
            idY = event.pos().y() // self._vertexInterval
            if event.pos().x() - self._clickedPos.x() < 0: #左下にドラッグ
                self._draggedPosX, self._draggedPosY = self.dragAdjust(event.pos(), idX, idY)
                print("Drag", self._draggedPosX, self._draggedPosY)
                self._frame.setRect(self._draggedPosX,
                                    self._clickedPos.y(),
                                    math.fabs(self._draggedPosX - self._clickedPos.x()),
                                    math.fabs(self._draggedPosY - self._clickedPos.y())
                                    )
                if event.pos().y() - self._clickedPos.y() < 0:#左上に向けてドラッグ
                    self._draggedPosX, self._draggedPosY = self.dragAdjust(event.pos(), idX, idY)
                    self._frame.setRect(event.pos().x(),
                                        event.pos().y(),
                                        math.fabs(event.pos().x() - self._clickedPos.x()),
                                        math.fabs(event.pos().y() - self._clickedPos.y())
                                        )
            elif event.pos().y() - self._clickedPos.y() < 0:#右上に向けてドラッグ
                self._draggedPosX, self._draggedPosY = self.dragAdjust(event.pos(), idX, idY)
                self._frame.setRect(self._clickedPos.x(),
                                    event.pos().y(),
                                    math.fabs(event.pos().x() - self._clickedPos.x()),
                                    math.fabs(event.pos().y() - self._clickedPos.y())
                                    )

            else: # 右下に
                self._draggedPosX, self._draggedPosY = self.dragAdjust(event.pos(), idX, idY)
                print("Drag", self._draggedPosX, self._draggedPosY)
                self._frame.setRect(self._clickedPosX,
                                    self._clickedPosY,
                                    math.fabs(self._draggedPosX - self._clickedPosX),
                                    math.fabs(self._draggedPosY - self._clickedPosY)
                                    )

    def mouseDoubleClickEvent(self, event):
        self.countermeasureScene.clear()

    def mouseReleaseEvent(self, event):
        self._frame.setBrush(collectBrush)
        self._isMouseButtonOn = False

    #調節したx , y座標を返す
    def dragAdjust(self, mousePos, neighborPointIDX, neighborPointIDY):
        #print(neighborPointIDX, neighborPointIDY)
        if (mousePos.x() <= (self._vertexPos[neighborPointIDX][neighborPointIDY][1] + COLLISIONRANGE) and
                    mousePos.x() >= (self._vertexPos[neighborPointIDX][neighborPointIDY][1] - POINTSIZE)) and \
                (mousePos.y() <= (self._vertexPos[neighborPointIDX][neighborPointIDY][0] + COLLISIONRANGE) and
                         mousePos.y() >= (self._vertexPos[neighborPointIDX][neighborPointIDY][0] - POINTSIZE)):
            print("Inside Neighbor Point!!!!")
            self._frame.setPen(collectPen)
            return self._vertexPos[neighborPointIDX][neighborPointIDY][1], self._vertexPos[neighborPointIDX][neighborPointIDY][0]
        else:
            self._frame.setPen(incollectPen)
            return mousePos.x(), mousePos.y()

    def placeVertex(self):
        self._vertexInterval = VIEWSCALE // (2 ** (self.causeSmallness - self.victimSmallness + 1))
        num = VIEWSCALE // self._vertexInterval + 1
        self._vertexPos = []
        rowPoints = [] # _vertexPos = [rowPoints1, rowPoints2, rowPoints3, ...]
        for i in range(num):
            for j in range(num):
                posX = j * self._vertexInterval
                posY = i * self._vertexInterval
                point = QGraphicsRectItem(QRectF(posX - COLLISIONRANGE, posY - COLLISIONRANGE, POINTSIZE, POINTSIZE))
                rowPoints.append([posX, posY])
                if DEBUG:
                    self.countermeasureScene.addItem(point)
            self._vertexPos.append(rowPoints)
            rowPoints = []