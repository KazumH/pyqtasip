import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np

import IPAddressConverter
import TimeCalculator
import ASListView
import CountermeasureView

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

selectedColor = QColor.fromHsvF(60/360, 1, 1)
selectedColor.setAlpha(127)

backgroundBrush = QBrush(QColor.fromHsvF(15/360, 1, 1))

# 被害AS、原因ASのデータ
victimASes = []
causeASes = []

IS_CAUSE_VIS = False
VIEWSCALE = 2 ** 9
PLOTHEIGHT = 150

target = "MOASEvents.csv"

incident = "YoutubePakistan"
overallTimeWindowFrom = "0802241824"
overallTimeWindowTo = "0802241925"

"""
incident = "TTNet" #0412240817 - 0412241033
overallTimeWindowFrom = "0412241000"
overallTimeWindowTo = "0412241015"
"""

DEBUG = True

class IPPrefix(QGraphicsRectItem):
    def __init__(self, victimP, victimAS, causeP, causeAS, time):
        QGraphicsRectItem.__init__(self)
        #self.setPen(ipSubnetColor)
        #self.setBrush(ipSubnetBrush)
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setToolTip(victimP)
        self._ipPrefix = victimP
        self._victimAS = victimAS
        self._causePrefix = causeP
        self._causeAS = causeAS
        self._time = time
        self._announcedTimes = 1
        self._isSelected = False

    def mousePressEvent(self, event):
        print("I'm %s By %s Conflicting with %s By %s at %s" % (self._ipPrefix, self._victimAS, self._causePrefix, self._causeAS, self._time))

    def mouseDoubleClickEvent(self, event):
        print("Call Remove Method?")
        if not self._isSelected:
            self._isSelected = True
            self.setBrush(selectedColor)
        else:
            self._isSelected = False
            self.setBrush(victimBrush)

class TimeWindowBar(QGraphicsRectItem):
    def __init__(self, barWidth):
        QGraphicsRectItem.__init__(self)
        self.setPen(victimPen)
        self.setBrush(victimBrush)
        #self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self._posX = 0
        self._barNum = 0
        self._width = barWidth
        self.setToolTip(str(TimeCalculator.timeAdd(overallTimeWindowFrom, self._barNum)))

    def mousePressEvent(self, event):
        self.update()

    def mouseMoveEvent(self, event):
        self.setPos(QPointF(event.scenePos().x() , 0))

    def mouseReleaseEvent(self, event):
        self._barNum = int(event.scenePos().x() // self._width)
        self.setToolTip(str(TimeCalculator.timeAdd(overallTimeWindowFrom, self._barNum)))
        self._posX = self._width * self._barNum
        self.setPos(QPointF(self._posX, 0))
        self.update()
        super(TimeWindowBar, self).mousePressEvent(event)

    def boundingRect(self):
        return QRectF(0, 0, PLOTHEIGHT, VIEWSCALE)

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
        self.ipPrefixScene.setSceneRect(QRectF(0, 0, VIEWSCALE, VIEWSCALE))
        #背景色
        #self.ipPrefixScene.setBackgroundBrush(backgroundBrush)
        self.setScene(self.ipPrefixScene)
        #データファイルから指定された全体時間窓内のMOASイベントを抽出
        self._blockList, self._allASes = targetPrefixListGenerate(target)
        self._selectedASes = self._allASes
        #抽出したMOASイベントをフィルタリングしてブロック化し、ビューに追加していく。返り値はフィルタをかけた後の新しいASリスト
        self._visualizedASes = self.addPrefixItems(self._blockList, self._zoomLevel, self._allASes)

    # 更新されたフィルタに応じて可視化するIPプリフィックスブロックの選別をした後、生成と追加
    def addPrefixItems(self, data, zoomLevel, selectedASes): #selectedASes = [victimASlist, causeASlist]
        #プリフィックス長について昇順(少ない順)にそーと
        prefixPairList = []
        newVictims = []
        newCauses = []
        isWithinTimeWindow = False
        #時間窓フィルタリング
        for moas in data: #[[被害プリ, 被害AS], [原因プリ, 原因AS], イベント時間]
            if moas[2] == self._timeWindow[0]:
                isWithinTimeWindow = True
            elif moas[2] == TimeCalculator.timeAdd(self._timeWindow[1], 1):
                isWithinTimeWindow = False
            if isWithinTimeWindow:
                # 選択されたASによるフィルタリング
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
            # プリフィックス長フィルタリング
            # 被害プリフィックス長がフィルタ(from)より短いor(To)より長い時はそのMOASを表示しない
            if (int(prefixPairList[i][0][1]) < self._prefixLengthThresholdFrom or int(prefixPairList[i][0][1]) > self._prefixLengthThresholdTo):
                continue
            if prefixPairList[i][0][0] == prefixPairList[i][1][0]: #被害範囲 ＝ 原因範囲
                isSameArea = True
            else:
                isSameArea = False
            if isSameArea: # 重複タイプのMOASは被害者のみ可視化、ASは両方追加
                victimPrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][0][0], prefixPairList[i][0][1], prefixPairList[i][0][2], prefixPairList[i][1][0], prefixPairList[i][1][1], prefixPairList[i][1][2], prefixPairList[i][2])
                newVictims.append(prefixPairList[i][0][2])
                newCauses.append(prefixPairList[i][1][2])
                victimPrefixBlock.setPen(equivalentAreaPen)
                victimPrefixBlock.setBrush(equivalentAreaBrush)
                self.ipPrefixScene.addItem(victimPrefixBlock)
                continue
            #被害アナウンスのブロックとそのASを記録
            victimPrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][0][0], prefixPairList[i][0][1], prefixPairList[i][0][2],prefixPairList[i][1][0], prefixPairList[i][1][1], prefixPairList[i][1][2], prefixPairList[i][2])
            newVictims.append(prefixPairList[i][0][2])
            newCauses.append(prefixPairList[i][1][2])
            victimPrefixBlock.setPen(victimPen)
            victimPrefixBlock.setBrush(victimBrush)
            self.ipPrefixScene.addItem(victimPrefixBlock)
            #原因アナウンスのブロックとそのASを記録
            if IS_CAUSE_VIS:
                causePrefixBlock = IPPrefixBlockGenerate(zoomLevel, prefixPairList[i][1][0], prefixPairList[i][1][1], prefixPairList[i][1][2], prefixPairList[i][1][0], prefixPairList[i][1][1], prefixPairList[i][1][2], prefixPairList[i][2])
                newCauses.append(prefixPairList[i][1][2])
                causePrefixBlock.setPen(causePen)
                causePrefixBlock.setBrush(causeBrush)
                self.ipPrefixScene.addItem(causePrefixBlock)
        #フィルタされたASリストを返り値にさせる
        newASes = [np.unique(newVictims), np.unique(newCauses)]

        return newASes
    def zoomLevelChanged(self, zlValue, twValue):
        self._zoomLevel = zlValue
        self._timeWindow = twValue
        self.clearAllBlocks()
        # フィルタされた新しいASリストをつくる
        self._visualizedASes = self.addPrefixItems(self._blockList, self._zoomLevel, self._selectedASes)

    def prefixLengthChanged(self, plfrm, plto, twValue):
        self._prefixLengthThresholdFrom = plfrm
        self._prefixLengthThresholdTo = plto
        self._timeWindow = twValue
        self.clearAllBlocks()
        # フィルタされた新しいASリストをつくる
        self._visualizedASes = self.addPrefixItems(self._blockList, self._zoomLevel, self._selectedASes)

    def timeWindowChanged(self, twValue):
        self._timeWindow = twValue
        self.clearAllBlocks()
        # フィルタされた新しいASリストをつくる
        self._visualizedASes = self.addPrefixItems(self._blockList, self._zoomLevel, self._selectedASes)

    def refreshButtonPushed(self, newASes):
        self.clearAllBlocks()
        self._selectedASes = newASes
        self._visualizedASes = self.addPrefixItems(self._blockList, self._zoomLevel, newASes)

    def asnFilterRemove(self):
        self.clearAllBlocks()
        self._selectedASes = self._allASes
        self._visualizedASes = self.addPrefixItems(self._blockList, self._zoomLevel, self._allASes)

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
        self.frequencyPlotScene.setSceneRect(QRectF(0, 0, VIEWSCALE, PLOTHEIGHT))
        self.setScene(self.frequencyPlotScene)
        self.plot(target, overallTimeWindowFrom, overallTimeWindowTo)
        self.setTimeWindowBar()

    def plot(self, file, timeWFrom, timeWTo):
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
        self._barWidth = VIEWSCALE / len(plotData)
        for i in range(len(plotData)):
            posX = i * self._barWidth
            bar = QGraphicsRectItem()
            barLength = plotData[i][1]
            bar.setRect(QRectF(posX, PLOTHEIGHT, self._barWidth, -barLength))
            self.frequencyPlotScene.addItem(bar)

    def setTimeWindowBar(self):
        self.timeWindowBar1 = TimeWindowBar(self._barWidth)
        self.timeWindowBar1.setRect(QRectF(0, 0, self._barWidth, PLOTHEIGHT))
        self.frequencyPlotScene.addItem(self.timeWindowBar1)
        self.timeWindowBar2 = TimeWindowBar(self._barWidth)
        self.timeWindowBar2.setRect(QRectF(0, 0, self._barWidth, PLOTHEIGHT))
        self.frequencyPlotScene.addItem(self.timeWindowBar2)
#ブロック
def IPPrefixBlockGenerate(zoomLevel, address, length, victimAS, causeAd, causeLength, causeAS, time): #引数: ["158.65.152.0", "22"]
    #初期化
    prefixLength = int(length)
    ipPrefix = address + "/" +  length
    addressBin = IPAddressConverter.ipToBin(address,prefixLength)
    bitPairs = [addressBin[i: i+2] for i in range(0, 32, 2)] #[0] = "01",  ~ [31] = "00"
    isRect = False
    posX , posY = 0, 0
    currentScale = VIEWSCALE
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
    causePrefix = causeAd + "/" + causeLength
    #Rectオブジェクト
    ipPrefix = IPPrefix(ipPrefix, victimAS, causePrefix, causeAS, time)
    if isRect:
        if bitPairs[repeatNumber] == "00":
            ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale // 2))
        elif bitPairs[repeatNumber] == "10":
            posY = posY + currentScale // 2
            ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale // 2))
    else:
        ipPrefix.setRect(QRectF(posX, posY, currentScale, currentScale))
    return ipPrefix

# MOASイベントのデータファイルから全体時間窓内にある、可視化するIPプリフィックスを返す。
# 時間以外同じのイベントは出現回数(これが色の濃さとする)のみ記録し、一意にする
# 全体時間窓にある全ての被害AS、原因ASのリストをつくる
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
        elif words[0] == overallTimeWindowTo or words[0] == TimeCalculator.timeAdd(overallTimeWindowTo, 1):
            if DEBUG: print(words[0])
            isWithinTimeWindow = False
            break
        # 時間窓内のMOASイベントを被害、原因にわけ、それぞれブロックにする
        if isWithinTimeWindow:
            time = words[0]
            if DEBUG: print(time)
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
    return targetPrefixList, overallASes#[[被害プリ, 被害AS], [原因プリ, 原因AS], イベント時間]と[全被害AS, 全原因AS]

class MainWindow(QWidget):
    def __init__(self, parent=None):  # 親がいないウィジェットはウィンドウになる
        super(MainWindow, self).__init__(parent)
        # 全体ウインドウ
        self.setWindowTitle("IP Prefixes Vis")
        # プリフィックスビュー部分
        self.ipPrefixView = IPPrefixView()
        # 対策案構築ビュー部分
        self.countermeasureView = CountermeasureView.CountermeasureView()
        # 時間窓プロット部分
        self.frequencyPlotView = FrequencyPlotView()
        #拡大レベル調整スライダー
        zlsldr = self.zoomLevelSlider = QSlider(Qt.Horizontal)
        zlsldr.setMinimum(1)
        zlsldr.setMaximum(16)
        zlsldr.setValue(1)
        zlsldr.setTickInterval(1)
        zlsldr.valueChanged.connect(self.zoomLevelSliderValueChanged)
        #プリフィックス長フィルタースライダーfrom(スライダーの値以下のプリフィックス長の被害プリフィックスを非表示)
        plffrmsldr = self.prefixLengthFromSlider = QSlider(Qt.Horizontal)
        plffrmsldr.setMinimum(1)
        plffrmsldr.setMaximum(32)
        plffrmsldr.setValue(0)
        plffrmsldr.setTickInterval(1)
        plffrmsldr.valueChanged.connect(self.prefixLengthSliderValueChanged)
        #プリフィックス長フィルタースライダーto
        plftosldr = self.prefixLengthToSlider = QSlider(Qt.Horizontal)
        plftosldr.setMinimum(1)
        plftosldr.setMaximum(32)
        plftosldr.setValue(32)
        plftosldr.setTickInterval(1)
        plftosldr.valueChanged.connect(self.prefixLengthSliderValueChanged)
        #被害ASリストビュー
        vlst = QListView()
        vlst.setMinimumSize(256, 100)
        vmdl = self.vmdl = QStandardItemModel(vlst)
        ASListView.addItemInRow(vmdl, self.ipPrefixView._allASes[0])
        #vmdl.itemChanged.connect(self.on_item_changed)
        vlst.setModel(vmdl)
        #原因ASリストビュー
        clst = QListView()
        clst.setMinimumSize(256, 100)
        cmdl = self.cmdl = QStandardItemModel(clst)
        ASListView.addItemInRow(cmdl, self.ipPrefixView._allASes[1])
        #cmdl.itemChanged.connect(self.on_item_changed)
        clst.setModel(cmdl)
        #ボタン
        #リストのチェック全消しボタン
        vunchckbtn = QPushButton("Enable All Check(V)")
        vunchckbtn.clicked.connect(self.vunchckbtnClicked)
        cunchckbtn = QPushButton("Enable All Check(C)")
        cunchckbtn.clicked.connect(self.cunchckbtnClicked)
        #表示AS選択後のビュー更新ボタン
        rfrshbtn = QPushButton("Apply ASN Filter")
        rfrshbtn.clicked.connect(self.rfrshbtnClicked)
        fltrrmvbtn = QPushButton("Remove ASN Filter")
        fltrrmvbtn.clicked.connect(self.fltrrmvbtnClicked)
        #ラベル
        tmwndwlbl = self.tm = QLabel("Time Window: %s - %s" % (overallTimeWindowFrom, overallTimeWindowTo))
        zmlbl = self.zmlbl = QLabel("Zoom Level")
        plffrmlbl = self.thfrm = QLabel("Prefix Length Filter: From")
        plftolbl = self.thto = QLabel("Prefix Length Filter: To")
        vaslbl = self.vaslbl = QLabel("Victim AS List")
        caslbl = self.caslbl = QLabel("Cause AS List")
        #各ウィジェットのレイアウト
        #左
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
        #右側
        widgetLayoutRight = QVBoxLayout()
        widgetLayoutRight.addWidget(self.countermeasureView)
        #VictimAS周り
        victimLabelLayout = QHBoxLayout()
        victimLabelLayout.addWidget(vaslbl)
        victimLabelLayout.addWidget(vunchckbtn)

        victimListLayout = QVBoxLayout()
        victimListLayout.addLayout(victimLabelLayout)
        victimListLayout.addWidget(vlst)
        # CauseAS周り
        causeLabelLayout = QHBoxLayout()
        causeLabelLayout.addWidget(caslbl)
        causeLabelLayout.addWidget(cunchckbtn)

        causeListLayout = QVBoxLayout()
        causeListLayout.addLayout(causeLabelLayout)
        causeListLayout.addWidget(clst)
        #Victim + Cause
        listLayout = QHBoxLayout()
        listLayout.addLayout(victimListLayout)
        listLayout.addLayout(causeListLayout)
        widgetLayoutRight.addLayout(listLayout)
        widgetLayoutRight.addWidget(rfrshbtn)
        widgetLayoutRight.addWidget(fltrrmvbtn)
        #左 + 右
        allLayout = QHBoxLayout()
        allLayout.addLayout(widgetLayout)
        allLayout.addLayout(widgetLayoutRight)
        self.setLayout(allLayout)

    def listRefresh(self):# 新しいASのリストに合わせてASリストビューを更新
        self.vmdl.clear()# リストを全消去
        self.cmdl.clear()# リストを全消去
        ASListView.addItemInRow(self.vmdl, self.ipPrefixView._visualizedASes[0])
        ASListView.addItemInRow(self.cmdl, self.ipPrefixView._visualizedASes[1])

    def vunchckbtnClicked(self):
        i = 0
        while self.vmdl.item(i):
            if self.vmdl.item(i).checkState():
                self.vmdl.item(i).setCheckState(False)
            i += 1
    def cunchckbtnClicked(self):
        i = 0
        while self.cmdl.item(i):
            if self.cmdl.item(i).checkState():
                self.cmdl.item(i).setCheckState(False)
            i += 1
    def rfrshbtnClicked(self):
        selectedItems = self.ipPrefixView.ipPrefixScene.items()
        print(selectedItems[0])
        self.countermeasureView.dataReceive(selectedItems[0])
        i = 0
        newVictims = []
        newCauses = []
        while self.vmdl.item(i):
            if self.vmdl.item(i).checkState():
                newVictims.append(self.vmdl.item(i).text())
            i += 1
        i = 0
        while self.cmdl.item(i):
            if self.cmdl.item(i).checkState():
                newCauses.append(self.cmdl.item(i).text())
            i += 1
        print([newVictims, newCauses])
        self.ipPrefixView.refreshButtonPushed([newVictims, newCauses])
        self.listRefresh()

    def fltrrmvbtnClicked(self):
        self.ipPrefixView.asnFilterRemove()
        self.listRefresh()

    def mousePressEvent(self, event):
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        print(newTimeWindow)
        self.ipPrefixView.timeWindowChanged(newTimeWindow)
        self.listRefresh()

    def zoomLevelSliderValueChanged(self):
        newZoomLevel = self.zoomLevelSlider.value()
        barNum1 = self.frequencyPlotView.timeWindowBar1._barNum
        barNum2 = self.frequencyPlotView.timeWindowBar2._barNum
        newTimeWindow = [barNum2, barNum1] if barNum1 > barNum2 else [barNum1, barNum2]
        newTimeWindowFrom = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[0])
        newTimeWindowTo = TimeCalculator.timeAdd(overallTimeWindowFrom, newTimeWindow[1])
        newTimeWindow = [newTimeWindowFrom, newTimeWindowTo]
        self.ipPrefixView.zoomLevelChanged(newZoomLevel, newTimeWindow)
        self.listRefresh()

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
        self.listRefresh()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())