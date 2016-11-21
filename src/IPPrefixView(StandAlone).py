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
equivalentAreaColor.setAlpha(32)
equivalentAreaPen = QPen(equivalentAreaColor)
equivalentAreaPen.setWidthF(gridWidth)
equivalentAreaBrush = QBrush(equivalentAreaColor)

backgroundBrush = QBrush(QColor.fromHsvF(15/360, 1, 1))

# 被害AS、原因ASのデータ
victimASes = []
causeASes = []

sampleVictims = ['12847', '10355', '18638', '22867', '17443', '9498', '36904', '7018', '2647', '23694', '3602', '9300', '32004', '19750', '6395', '7784', '14745', '20214', '5511', '5963', '7132', '4355', '39153', '28917', '4670', '9304', '39010', '8781', '9729', '9957', '151', '24835', '17639', '18231', '7482', '9930', '15475', '24063', '9908', '9299', '3786', '9396', '5618', '5051', '9513', '29049', '24326', '4618', '7693', '9835', '4750', '17887', '9649', '7470', '7616', '12127', '23395', '209', '3356', '8151', '9329', '18592', '6855', '34443']
sampleCauses  = ['24921', '36363', '18797', '3602', '39946', '10255', '9498', '17443', '13807', '5583']
sampleSelectedASes = [sampleVictims, sampleCauses]

isCauseVisualized = False
viewScale = 2 ** 9
plotHeight = 100

target = "MOASEvents.csv"

incident = "YoutubePakistan"
overallTimeWindowFrom = "0802241824"
overallTimeWindowTo = "0802241925"

"""
incident = "TTNet" #0412240817 - 0412241033
overallTimeWindowFrom = "0412240930"
overallTimeWindowTo = "0412240945"
"""
class IPPrefix(QGraphicsRectItem):
    def __init__(self, data, id, victimAS, causeAS, time):
        QGraphicsRectItem.__init__(self)
        #self.setPen(ipSubnetColor)
        #self.setBrush(ipSubnetBrush)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self._ipPrefix = data
        self._pairID = id
        self._victimAS = victimAS
        self._causeAS = causeAS
        self._time = time
        self._announcedTimes = 1

    def mousePressEvent(self, event):
        print("I'm %s Announced By AS: %s and Attacked By AS %s at %s" % (self._ipPrefix, self._victimAS, self._causeAS, self._time))

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
        self.setPos(QPointF(event.scenePos().x() , 0))

    def mouseReleaseEvent(self, event):
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
        self._prefixLengthThresholdFrom = 1
        self._prefixLengthThresholdTo = 32
        self._timeWindow = [overallTimeWindowFrom, overallTimeWindowTo]
        # 全体ビューに当たるQGraphicsSceneの作成、設定
        self.ipPrefixScene = IPPrefixScene(self)
        #サイズ設定
        self.ipPrefixScene.setSceneRect(QRectF(0, 0, viewScale, viewScale))
        #背景色
        #self.ipPrefixScene.setBackgroundBrush(backgroundBrush)
        self.setScene(self.ipPrefixScene)
        #データファイルから指定された時間窓内のMOASイベントを抽出
        self._blockList, self._allASes = targetPrefixListGenerate(target)
        #抽出したMOASイベントをブロック化し、ビューに追加していく
        self.addPrefixItems(self._blockList, self._zoomLevel, self._allASes)

    # 可視化するIPプリフィックスブロックの選別と生成と追加
    def addPrefixItems(self, data, zoomLevel, selectedASes): #selectedASes = [victimASlist, causeASlist]
        #プリフィックス長について昇順(少ない順)にそーと
        prefixPairList = []
        isWithinTimeWindow = False
        for moas in data: #[[被害プリ, 被害AS], [原因プリ, 原因AS], イベント時間]
            if moas[2] == self._timeWindow[0]:
                isWithinTimeWindow = True
            elif moas[2] == TimeCalculator.timeAdd(self._timeWindow[1], 1):
                isWithinTimeWindow = False
            if isWithinTimeWindow:
                if (moas[0][1] in selectedASes[0]) and (moas[1][1] in selectedASes[1]):
                    prefixPairList.append([[moas[0][0].split("/")[0], moas[0][0].split("/")[1], moas[0][1]],\
                                   [moas[1][0].split("/")[0], moas[1][0].split("/")[1], moas[1][1]],\
                                   moas[2]\
                                   ]) #[[["128.0.0.0", "9", "9302"], ["128.128.0.0", "18"], 時間], ...
                else:
                    continue
            else:
                continue
        for i in range(len(prefixPairList)):
            pairID = i
            #print(self._prefixLengthThresholdFrom, self._prefixLengthThresholdTo)
            # 被害プリフィックス長がフィルタ(from)より短いor(To)より長い時はそのMOASを表示しない
            if (int(prefixPairList[i][0][1]) < self._prefixLengthThresholdFrom or int(prefixPairList[i][0][1]) > self._prefixLengthThresholdTo):
                continue
            if prefixPairList[i][0][0] == prefixPairList[i][1][0]: #被害範囲 ＝ 原因範囲
                isSameArea = True
            else:
                isSameArea = False
            if isSameArea: # 重複タイプのMOASは被害者のみ可視化
                victimPrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][0][0], prefixPairList[i][0][1], pairID, prefixPairList[i][0][2], prefixPairList[i][1][2], prefixPairList[i][2])
                victimPrefixBlock.setPen(equivalentAreaPen)
                victimPrefixBlock.setBrush(equivalentAreaBrush)
                self.ipPrefixScene.addItem(victimPrefixBlock)
                continue
            #被害アナウンスのブロック
            victimPrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][0][0], prefixPairList[i][0][1], pairID, prefixPairList[i][0][2], prefixPairList[i][1][2], prefixPairList[i][2])
            victimPrefixBlock.setPen(victimPen)
            victimPrefixBlock.setBrush(victimBrush)
            self.ipPrefixScene.addItem(victimPrefixBlock)
            #原因アナウンスのブロック
            if isCauseVisualized:
                causePrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][1][0], prefixPairList[i][1][1], pairID, prefixPairList[i][1][2], "", prefixPairList[i][2])
                causePrefixBlock.setPen(causePen)
                causePrefixBlock.setBrush(causeBrush)
                self.ipPrefixScene.addItem(causePrefixBlock)
    def zoomLevelChanged(self, zlValue, twValue):
        self._zoomLevel = zlValue
        self._timeWindow = twValue
        self.clearAllBlocks()
        self.addPrefixItems(self._blockList, self._zoomLevel, self._allASes)

    def prefixLengthChanged(self, plfrm, plto, twValue):
        self._prefixLengthThresholdFrom = plfrm
        self._prefixLengthThresholdTo = plto
        self._timeWindow = twValue
        self.clearAllBlocks()
        self.addPrefixItems(self._blockList, self._zoomLevel, self._allASes)

    def timeWindowChanged(self, twValue):
        self._timeWindow = twValue
        self.clearAllBlocks()
        self.addPrefixItems(self._blockList, self._zoomLevel, self._allASes)

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
        self._timeWindowFrom = 1
        self._timeWindowTo = 32
        # 全体ビューに当たるQGraphicsSceneの作成、設定
        self.frequencyPlotScene = FrequencyPlotScene(self)
        #サイズ設定
        self.frequencyPlotScene.setSceneRect(QRectF(0, 0, viewScale, plotHeight))
        self.setScene(self.frequencyPlotScene)
        self.plot(target, overallTimeWindowFrom, overallTimeWindowTo)
        self.setTimeWindowBar()

    def plot(self, file, timeWFrom, timeWTo):
        isWithinTimeWindow = False
        current = timeWFrom
        endPoint = TimeCalculator.timeAdd(timeWTo, 1)
        counter = 0
        plotData = []
        isWithinOverallTimeWindow = False
        for line in open("../data/MOAS/%s/%s" % (incident, file), "r"):
            words = line.split(",")
            if words[0] == timeWFrom:
                isWithinOverallTimeWindow = True
            elif words[0] == endPoint:
                isWithinOverallTimeWindow = False
                break
            if isWithinOverallTimeWindow:
                if words[0] == current:
                    counter += 1
                else:
                    plotData.append([current, counter])
                    counter = 1
                    current = words[0]
        plotData.append([current, counter]) #最後の時間の集計分
        #プロット図のバーは画面幅ぴったりに配置
        self._barWidth = viewScale / len(plotData)
        for i in range(len(plotData)):
            posX = i * self._barWidth
            bar = QGraphicsRectItem()
            barLength = plotData[i][1]
            bar.setRect(QRectF(posX, plotHeight, self._barWidth, -barLength))
            self.frequencyPlotScene.addItem(bar)

    def setTimeWindowBar(self):
        self.timeWindowBar1 = TimeWindowBar(self._barWidth)
        self.timeWindowBar1.setRect(QRectF(0, 0, self._barWidth, 100))
        self.frequencyPlotScene.addItem(self.timeWindowBar1)
        self.timeWindowBar2 = TimeWindowBar(self._barWidth)
        self.timeWindowBar2.setRect(QRectF(0, 0, self._barWidth, 100))
        self.frequencyPlotScene.addItem(self.timeWindowBar2)
#ブロック
def IPPrefixBlockGenerate(zoomLevel, address, length, id, victimAS, causeAS, time): #引数: ["158.65.152.0", "22"]
    #初期化
    prefixLength = int(length)
    ipPrefix = address + "/" +  length
    addressBin = IPAddressConverter.ipToBin(address,prefixLength)
    bitPairs = [addressBin[i: i+2] for i in range(0, 32, 2)] #[0] = "01",  ~ [31] = "00"
    isRect = False
    posX , posY = 0, 0
    currentScale = viewScale
    #ビットペア何番目からスタートするか(拡大の時に変更する)
    startNumber = zoomLevel
    repeatNumber = prefixLength // 2
    isRect = True if prefixLength % 2 != 0 else False
    headerBits = ""
#座標、サイズ決定
    #頭2ビットずつ見て座標を決める
    #拡大適用後の無視する先頭ビット
    for i in range(startNumber):
        headerBits = headerBits + bitPairs[i]
    #先頭の幾つかのビットペアを無視して座標決めすることで拡大表現
    for i in range(startNumber, repeatNumber):
        if bitPairs[i] in {"00","01"}:
            if bitPairs[i] == "00":
                posX += currentScale // 2
        elif bitPairs[i] in {"10","11"}:
            posY = posY + currentScale // 2
            if bitPairs[i] == "10":
                posX += currentScale // 2
        currentScale //= 2
    #Rectオブジェクト
    attributes = []
    ipPrefix = IPPrefix(ipPrefix, id, victimAS, causeAS, time)
    if isRect:
        if bitPairs[repeatNumber] == "00":
            ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale // 2))
        elif bitPairs[repeatNumber] == "10":
            posY = posY + currentScale // 2
            ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale // 2))
    else:
        ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale))
    return ipPrefix

# MOASイベントのデータファイルから時間窓内にある、可視化するIPプリフィックスを返す。
# 時間以外同じのイベントは出現回数(これが色の濃さとする)のみ記録し、一意にする
# 被害AS、原因ASの辞書をつくる
def targetPrefixListGenerate(file):
    targetPrefixList = []
    isWithinTimeWindow = False
    currentListIndex = 0
    currentline = 1
    numLines = sum(1 for line in open("../data/MOAS/%s/%s" % (incident, file)))
    sameLineProsecced = False
    lastLineSame = False
    lastLineProcessed = False
    for line in open("../data/MOAS/%s/%s" % (incident, file), "r"):
        currentline += 1
        sameLineProsecced = False
        words = line.split(",")
        if words[0] == overallTimeWindowFrom:
            isWithinTimeWindow = True
        elif words[0] == overallTimeWindowTo:
            isWithinTimeWindow = False
            break
        # 時間窓内のMOASイベントを被害、原因にわけ、それぞれブロックにする
        if isWithinTimeWindow:
            time = words[0]
            victimPrefix = words[1]
            victimAS = words[2]
            causePrefix = words[3]
            causeAS = words[4].split("\n")[0]
            #データベースに登録
            if victimAS not in victimASes:
                victimASes.append(victimAS)
            if causeAS not in causeASes:
                causeASes.append(causeAS)
            #イベントの登録
            if currentListIndex == 0: #1行目
                targetPrefixList.append([[victimPrefix, victimAS], [causePrefix, causeAS], time, 1])
                currentListIndex += 1
                continue
            if currentListIndex == numLines - 1:  # 最終行
                for i in range(len(targetPrefixList)):  # 時間以外同じのイベントは出現回数(これが色の濃さとする)のみ記録し、一意にする
                    if [victimPrefix, victimAS] in targetPrefixList[i] and \
                        [causePrefix, causeAS] in targetPrefixList[i]:
                        targetPrefixList[i][3] += 1  # sameCounter + 1
                        lastLineSame = True
                        lastLineProcessed = True
                        break
                if not lastLineSame:
                    targetPrefixList.append([[victimPrefix, victimAS], [causePrefix, causeAS], time, 1])
                    lastLineProcessed = True
                    break
            #elif victimPrefix == targetPrefixList[currentListIndex-1][0][0] and \
            #                victimAS == targetPrefixList[currentListIndex-1][0][1] and \
            #                causePrefix == targetPrefixList[currentListIndex - 1][1][0] and \
            #                causeAS == targetPrefixList[currentListIndex - 1][1][1]:
                #targetPrefixList[currentListIndex - 1][3] += 1  # sameCounter + 1
                #continue
            if lastLineProcessed:
                break
            # 最初の行でも最終行でもない
            for i in range(len(targetPrefixList)):# 時間以外同じのイベントは出現回数(これが色の濃さとする)のみ記録し、一意にする
                if ([victimPrefix, victimAS] == targetPrefixList[i][0]) and ([causePrefix, causeAS] == targetPrefixList[i][1]) and time in targetPrefixList[i]:
                    targetPrefixList[i][3] += 1 #sameCounter + 1
                    sameLineProsecced = True
                    break
            if sameLineProsecced:
                continue
            targetPrefixList.append([[victimPrefix, victimAS], [causePrefix, causeAS], time, 1])
            currentListIndex += 1
    print(targetPrefixList)
    overallASes = [victimASes, causeASes]
    return targetPrefixList, overallASes#[[被害プリ, 被害AS], [原因プリ, 原因AS], イベント時間]

class MainWindow(QWidget):
    def __init__(self, parent=None):  # 親がいないウィジェットはウィンドウになる
        super(MainWindow, self).__init__(parent)
        # 全体ウインドウ
        self.setWindowTitle("IP Prefixes Vis")
        # プリフィックスビュー部分
        self.ipPrefixView = IPPrefixView()
        # 時間窓プロット部分
        self.frequencyPlotView = FrequencyPlotView()

        #拡大レベル調整スライダー
        zlsldr = self.zoomLevelSlider = QSlider(Qt.Horizontal)
        zlsldr.setMinimum(1)
        zlsldr.setMaximum(16)
        zlsldr.setValue(1)
        zlsldr.setTickInterval(1)
        zlsldr.valueChanged.connect(self.zoomLevelSliderValueChanged)

        #プリフィックス長フィルタースライダー(スライダーの値以下のプリフィックス長の被害プリフィックスを非表示)
        plffrmsldr = self.prefixLengthFromSlider = QSlider(Qt.Horizontal)
        plffrmsldr.setMinimum(1)
        plffrmsldr.setMaximum(32)
        plffrmsldr.setValue(0)
        plffrmsldr.setTickInterval(1)
        plffrmsldr.valueChanged.connect(self.prefixLengthSliderValueChanged)

        plftosldr = self.prefixLengthToSlider = QSlider(Qt.Horizontal)
        plftosldr.setMinimum(1)
        plftosldr.setMaximum(32)
        plftosldr.setValue(32)
        plftosldr.setTickInterval(1)
        plftosldr.valueChanged.connect(self.prefixLengthSliderValueChanged)
        #ラベル
        tmwndwlbl = self.tm = QLabel("Time Window: %s - %s" % (overallTimeWindowFrom, overallTimeWindowTo))
        zmlbl = self.zmlbl = QLabel("Zoom Level")
        plffrmlbl = self.thfrm = QLabel("Prefix Length Filter: From")
        plftolbl = self.thto = QLabel("Prefix Length Filter: To")

        #各ウィジェットのレイアウト
        widgetLayout = QVBoxLayout()
        widgetLayout.addWidget(self.ipPrefixView)
        widgetLayout.addWidget(tmwndwlbl)
        widgetLayout.addWidget(self.frequencyPlotView)
        widgetLayout.addWidget(zmlbl)
        widgetLayout.addWidget(zlsldr)
        widgetLayout.addWidget(plffrmlbl)
        widgetLayout.addWidget(plffrmsldr)
        widgetLayout.addWidget(plftolbl)
        widgetLayout.addWidget(plftosldr)
        self.setLayout(widgetLayout)

    def mousePressEvent(self, event):
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        print(newTimeWindow)
        self.ipPrefixView.timeWindowChanged(newTimeWindow)

    def zoomLevelSliderValueChanged(self):
        newZoomLevel = self.zoomLevelSlider.value()
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        self.ipPrefixView.zoomLevelChanged(newZoomLevel, newTimeWindow)

    def prefixLengthSliderValueChanged(self):
        newPrefixLengthFilterFrom = self.prefixLengthFromSlider.value()
        newPrefixLengthFilterTo = self.prefixLengthToSlider.value()
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        self.ipPrefixView.prefixLengthChanged(newPrefixLengthFilterFrom, newPrefixLengthFilterTo, newTimeWindow)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())