import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np

import IPAddressConverter
import TimeCalculator

gridWidth = 0.01

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

equivalentAreaColor = QColor.fromHsvF(240/360, 1, 1)
equivalentAreaPen = QPen(equivalentAreaColor)
equivalentAreaPen.setWidthF(gridWidth)
equivalentAreaBrush = QBrush(equivalentAreaColor)

backgroundBrush = QBrush(QColor.fromHsvF(15/360, 1, 1))

viewScale = 2 ** 9
plotHeight = 100

sampleIPPrefixes = [[['212.93.96.0', '19'], ['212.93.100.0', '23']],
                    [['12.128.0.0', '9'], ['12.192.0.0', '10']],
                    [['192.0.0.0', '8'], ['192.0.0.0', '8']]]
target = "MOASEvents.csv"
incident = "YoutubePakistan"
#incident = "TTNet"
timeWindowFrom = "0802241824"
timeWindowTo = "0802241925"


class IPPrefix(QGraphicsRectItem):
    def __init__(self, data, id, asn):
        QGraphicsRectItem.__init__(self)
        #self.setPen(ipSubnetColor)
        #self.setBrush(ipSubnetBrush)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self._ipPrefix = data
        self._pairID = id
        self._asn = asn
        self._announcedTimes = 1

    def mousePressEvent(self, event):
        print("I'm %s Announced By AS: %s" % (self._ipPrefix, self._asn))

    def mouseDoubleClickEvent(self, event):
        print("Call Remove Method?")

class TimeWindowBar(QGraphicsRectItem):
    def __init__(self, barWidth):
        QGraphicsRectItem.__init__(self)
        self.setPen(victimPen)
        self.setBrush(victimBrush)
        #self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self._posX = 0
        self._barNum = 0
        self._width = barWidth

    def mousePressEvent(self, event):
        self.update()

    def mouseMoveEvent(self, event):
        #print(event.scenePos())
        self.setPos(event.scenePos() - QPointF(5, 30))

    def mouseReleaseEvent(self, event):
        print("release")
        self._barNum = int(event.scenePos().x() // self._width)
        self._posX = self._width * self._barNum
        self.setPos(QPointF(self._posX, 0))
        self.update()
        super(TimeWindowBar, self).mousePressEvent(event)

    def boundingRect(self):
        return QRectF(0, 0, plotHeight, viewScale)



class IPPrefixScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(IPPrefixScene, self).__init__(*argv, **keywords)

class IPPrefixView(QGraphicsView):
    def __init__(self, parent=None): #親がいないウィジェットはウィンドウになる
        super(IPPrefixView, self).__init__()
        # QGraphicsViewの設定
        #self.setCacheMode(QGraphicsView.CacheBackground)
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self._zoomLevel = 0
        self._prefixLengthThreshold = 0
        self._timeWindow = [timeWindowFrom, timeWindowTo]
        # 全体ビューに当たるQGraphicsSceneの作成、設定
        self.ipPrefixScene = IPPrefixScene(self)
        #サイズ設定
        self.ipPrefixScene.setSceneRect(QRectF(0, 0, viewScale, viewScale))
        #背景色
        #self.ipPrefixScene.setBackgroundBrush(backgroundBrush)
        self.setScene(self.ipPrefixScene)
        #データファイルから指定された時間窓内のMOASイベントを抽出
        self.blockList = targetPrefixListGenerate(target)
        #抽出したMOASイベントをブロック化し、ビューに追加していく
        self.addPrefixItems(self.blockList, self._zoomLevel)

    # 可視化するIPプリフィックスブロックの選別と生成と追加
    def addPrefixItems(self, data, zoomLevel):
        #sample1 = IPPrefix()
        #sample1.setPos(200, 200)
        #self.scene.addItem(sample1)
        #プリフィックス長について昇順(少ない順)にそーと
        prefixPairList = []
        isWithinTimeWindow = False
        for moas in data:
            if moas[2] == self._timeWindow[0]:
                isWithinTimeWindow = True
            elif moas[2] == TimeCalculator.timeAdd(self._timeWindow[1], 1):
                isWithinTimeWindow = False
            if isWithinTimeWindow:
                prefixPairList.append([[moas[0][0].split("/")[0], moas[0][0].split("/")[1], moas[0][1]],
                                   [moas[1][0].split("/")[0], moas[1][0].split("/")[1], moas[1][1]],
                                   moas[2]
                                   ]) #[[["128.0.0.0", "9", "9302"], ["128.128.0.0", "18"], 時間], ...
            else:
                continue
        #print(prefixPairList)
        #prefixPairList.sort()
        #print(prefixPairList)
        for i in range(len(prefixPairList)):
            pairID = i
            if int(prefixPairList[i][0][1]) < self._prefixLengthThreshold: #被害プリフィックス長がフィルタより短い時はそのMOASをかしかしない
                continue
            if prefixPairList[i][0][0] == prefixPairList[i][1][0]: #被害範囲 ＝ 原因範囲
                isSameArea = True
            else:
                isSameArea = False
            if isSameArea:
                victimPrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][0][0], prefixPairList[i][0][1], pairID, prefixPairList[i][0][2])
                victimPrefixBlock.setPen(equivalentAreaPen)
                victimPrefixBlock.setBrush(equivalentAreaBrush)
                self.ipPrefixScene.addItem(victimPrefixBlock)
                continue
            victimPrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][1][0], prefixPairList[i][0][1], pairID, prefixPairList[i][0][2])
            victimPrefixBlock.setPen(victimPen)
            victimPrefixBlock.setBrush(victimBrush)
            self.ipPrefixScene.addItem(victimPrefixBlock)
            causePrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][1][0], prefixPairList[i][1][1], pairID, prefixPairList[i][0][2])
            causePrefixBlock.setPen(causePen)
            causePrefixBlock.setBrush(causeBrush)
            self.ipPrefixScene.addItem(causePrefixBlock)

    def zoomLevelChanged(self, zlValue, twValue):
        self._zoomLevel = zlValue
        self._timeWindow = twValue
        self.clearAllBlocks()
        self.addPrefixItems(self.blockList, self._zoomLevel)

    def prefixLengthChanged(self, plValue, twValue):
        self._prefixLengthThreshold = plValue
        self._timeWindow = twValue
        self.clearAllBlocks()
        self.addPrefixItems(self.blockList, self._zoomLevel)

    def timeWindowChanged(self, twValue):
        self._timeWindow = twValue
        self.clearAllBlocks()
        self.addPrefixItems(self.blockList, self._zoomLevel)

#アイテム(ブロック)全消し
    def clearAllBlocks(self):
        self.ipPrefixScene.clear()

#頻度のプロット
class FrequencyPlotScene(QGraphicsScene):
    def __init__(self, *argv, **keywords):
        super(FrequencyPlotScene, self).__init__(*argv, **keywords)

class FrequencyPlotView(QGraphicsView):
    def __init__(self, parent=None):  # 親がいないウィジェットはウィンドウになる
        super(FrequencyPlotView, self).__init__()
        self.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform | QPainter.TextAntialiasing)
        self._timeWindowFrom = 0
        self._timeWindowTo = 0
        self._barwidth = viewScale / 60
        # 全体ビューに当たるQGraphicsSceneの作成、設定
        self.frequencyPlotScene = FrequencyPlotScene(self)
        #サイズ設定
        self.frequencyPlotScene.setSceneRect(QRectF(0, 0, viewScale, plotHeight))
        self.setScene(self.frequencyPlotScene)
        self.plot(target, timeWindowFrom, timeWindowTo)
        self.setTimeWindowBar()

    def plot(self, file, timeWFrom, timeWTo):
        isWithinTimeWindow = False
        current = timeWFrom
        counter = 0
        plotData = []
        for line in open("../data/MOAS/%s/%s" % (incident, file), "r"):
            words = line.split(",")
            if words[0] == current:
                counter += 1
            else:
                plotData.append([current, counter])
                counter = 1
                current = words[0]
        plotData.append([current, counter]) #最後の時間の集計分
        #プロット図のバーは画面幅ぴったりに配置
        barWidth = viewScale / len(plotData)
        self._barWidth = barWidth
        for i in range(len(plotData)):
            posX = i * barWidth
            bar = QGraphicsRectItem()
            barLength = plotData[i][1]
            bar.setRect(QRectF(posX, plotHeight, barWidth, -barLength))
            self.frequencyPlotScene.addItem(bar)

    def setTimeWindowBar(self):
        self.timeWindowBar1 = TimeWindowBar(self._barWidth)
        self.timeWindowBar1.setRect(QRectF(0, 0, self._barwidth, 100))
        self.frequencyPlotScene.addItem(self.timeWindowBar1)

        self.timeWindowBar2 = TimeWindowBar(self._barWidth)
        self.timeWindowBar2.setRect(QRectF(0, 0, self._barwidth, 100))
        self.frequencyPlotScene.addItem(self.timeWindowBar2)
#ブロック
def IPPrefixBlockGenerate(zoomLevel, address, length, id, asn): #引数: ["158.65.152.0", "22"]
    #初期化
    prefixLength = int(length)
    ipPrefix = address + "/" +  length
    addressBin = IPAddressConverter.ipToBin(address,prefixLength)
    twoBits = [addressBin[i: i+2] for i in range(0, 32, 2)] #[0] = "01",  ~ [31] = "00"
    isRect = False
    posX , posY = 0, 0
    currentScale = viewScale
    #ビットペア何番目からスタートするか(拡大の時に変更する)
    startNumber = zoomLevel
    repeatNumber = prefixLength // 2
    #print(repeatNumber)
    isRect = True if prefixLength % 2 != 0 else False
    #頭2ビットずつ見て座標を決める
    #print(twoBits)
    for i in range(startNumber, repeatNumber):
        if twoBits[i] in {"00","01"}:
            if twoBits[i] == "00":
                posX += currentScale // 2
        elif twoBits[i] in {"10","11"}:
            posY = posY + currentScale // 2
            if twoBits[i] == "10":
                posX += currentScale // 2
        currentScale //= 2
    #Rectオブジェクト
    attributes = []
    ipPrefix = IPPrefix(ipPrefix, id, asn)
    if isRect:
        if twoBits[repeatNumber] == "00":
            ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale // 2))
        elif twoBits[repeatNumber] == "10":
            posY = posY + currentScale // 2
            ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale // 2))
    else:
        ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale))
    return ipPrefix

# MOASイベントのデータファイルから時間窓内の可視化するIPプリフィックスを返す
def targetPrefixListGenerate(file):
    targetPrefixList = []
    isWithinTimeWindow = False
    for line in open("../data/MOAS/%s/%s" % (incident, file), "r"):
        words = line.split(",")
        if words[0] == timeWindowFrom:
            isWithinTimeWindow = True
        elif words[0] == timeWindowTo:
            isWithinTimeWindow = False
            break

        # 時間窓内のMOASイベントを被害、原因にわけ、それぞれブロックにする
        if isWithinTimeWindow:
            time = words[0]
            victimPrefix = words[1]
            victimAS = words[2]
            causePrefix = words[3]
            causeAS = words[4].split("\n")[0]
            targetPrefixList.append([[victimPrefix, victimAS], [causePrefix, causeAS], time])
    return targetPrefixList#[[被害プリ, 被害AS], [原因プリ, 原因AS], イベント時間]

class MainWindow(QWidget):
    def __init__(self, parent=None):  # 親がいないウィジェットはウィンドウになる
        super(MainWindow, self).__init__(parent)
        # 全体ウインドウ
        self.setWindowTitle("IP Prefixes Vis")
        # プリフィックスビュー部分
        self.ipPrefixView = IPPrefixView()

        # プロット部分
        self.frequencyPlotView = FrequencyPlotView()


        #拡大レベル調整スライダー
        zlsldr = self.zoomLevelSlider = QSlider(Qt.Horizontal)
        zlsldr.setMinimum(1)
        zlsldr.setMaximum(16)
        zlsldr.setValue(1)
        zlsldr.setTickInterval(1)
        zlsldr.valueChanged.connect(self.zoomLevelSliderValueChanged)

        #プリフィックス長フィルタースライダー(スライダーの値以下のプリフィックス長の被害プリフィックスを非表示)
        plsldr = self.prefixLengthSlider = QSlider(Qt.Horizontal)
        plsldr.setMinimum(0)
        plsldr.setMaximum(32)
        plsldr.setValue(0)
        plsldr.setTickInterval(0)
        plsldr.valueChanged.connect(self.prefixLengthSliderValueChanged)

        widgetLayout = QVBoxLayout()
        widgetLayout.addWidget(self.ipPrefixView)
        widgetLayout.addWidget(self.frequencyPlotView)
        widgetLayout.addWidget(zlsldr)
        widgetLayout.addWidget(plsldr)
        self.setLayout(widgetLayout)

    def mousePressEvent(self, event):
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(timeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(timeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        print(newTimeWindow)
        self.ipPrefixView.timeWindowChanged(newTimeWindow)

    def zoomLevelSliderValueChanged(self):
        newZoomLevel = self.zoomLevelSlider.value()
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(timeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(timeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        self.ipPrefixView.zoomLevelChanged(newZoomLevel, newTimeWindow)

    def prefixLengthSliderValueChanged(self):
        newPrefixLengthTh = self.prefixLengthSlider.value()
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(timeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(timeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        self.ipPrefixView.prefixLengthChanged(newPrefixLengthTh, newTimeWindow)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())