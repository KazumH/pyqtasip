#参考1: http://melpystudio.blog82.fc2.com/blog-entry-138.html
#参考2: http://vivi.dyndns.org/vivi/docs/Qt/graphics.html
#参考3: http://d.hatena.ne.jp/mFumi/20141112/1415806010

import pickle
import sys

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPen, QIntValidator, QPixmap, QTransform, QCursor)
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QGraphicsPixmapItem, qApp,
                             QLabel, QLineEdit, QPushButton, QSlider, QCheckBox,QSizePolicy)

import ActivityPlot
import NodeLinkScene

imagepath = "./sample.png"
#とりあえず
YoutubePakistanTimeWindows = ["08/2/24 18:24 - 08/2/24 18:38",
                   "08/2/24 18:39 - 08/2/24 18:53",
                   "08/2/24 18:54 - 08/2/24 18:08",
                   "08/2/24 19:09 - 08/2/24 19:23"]
TTNetTimeWindows = ["04/12/24 08:16 - 04/12/24 08:32",
               "04/12/24 08:33 - 04/12/24 08:47",
               "04/12/24 08:16 - 04/12/24 09:02",
               "04/12/24 09:03 - 04/12/24 09:17",
               "04/12/24 09:18 - 04/12/24 09:32",
               "04/12/24 09:33 - 04/12/24 09:47",
               "04/12/24 09:48 - 04/12/24 10:02",
               "04/12/24 10:03 - 04/12/24 10:17",
               "04/12/24 10:18 - 04/12/24 10:32"]

#可視化システム全体のビュー
class MainWindow(QWidget):
    def __init__(self, parent=None): #親がいないウィジェットはウィンドウになる
        super(MainWindow, self).__init__(parent)
        self._pos = 0

# 全体ウインドウ
        self.setWindowTitle("AS-IP")
        self.graphicsView = QGraphicsView()

# ノードリンクビュー部分に当たるQGraphicsSceneの作成、設定
        nodelinkscene = NodeLinkScene.NodeLinkScene()
        nodelinkscene.setSceneRect(QRectF(0, 0, 900, 600))
        self.graphicsView.setScene(nodelinkscene) #メインウインドウにノードリンクビューを追加

        # いろんな設定した図形アイテムを追加するとき
        self.node = NodeLinkScene.Node()
        nodelinkscene.addItem(self.node)

        # 直接アイテムを追加するとき(ここでノードを追加するとクリックで拾える)
        """
        testPen = QPen(Qt.black, 0.0)
        self.testnode =  QGraphicsEllipseItem(100 + self._pos, 100 + self._pos, 200+ self._pos, 200 + self._pos)
        self.testnode.setPen(testPen)
        self.testnode.setBrush(QBrush(QColor.fromHsvF(0/360, 0.5, 1)))
        self.testnode.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        nodelinkscene.addItem(self.testnode)
        """

# ノードリンクビューの脇につけるボタンやスライダー
        #ボタン
        nbtn = self.nextButton = QPushButton("次の時間窓 >")
        nbtn.clicked.connect(self.nextButtonClicked)
        pbtn = self.previousButton = QPushButton("< 前の時間窓")
        pbtn.clicked.connect(self.previousButtonClicked)
        #スライダー周り
        wsldr= self.weightfilterSlider = QSlider(Qt.Horizontal)
        wsldr.setMinimum(0)
        wsldr.setMaximum(10000)
        wsldr.setValue(0)
        wsldr.setTickInterval(5)
        wsldr.valueChanged.connect(self.valuechanged)
        thlbl = self.th = QLabel("Weight Th")
        thtxtbx = self.thTextBox = QLineEdit()
        thtxtbx.setFixedWidth(40)
        thtxtbx.setText(str(self.node._weightThreshold))
        #時間窓
        tmlbl = self.timeWindowLabel = QLabel("TimeWindow")
        tmtxtbx = self.timeWindow = QLineEdit()
        #tmtxtbx.setText(TTNetTimeWindows[self.node._currentTimeWindow])
        tmtxtbx.setText(YoutubePakistanTimeWindows[self.node._currentTimeWindow])
        #チェックボックス
        achckbx = self.announce = QCheckBox("Announces")
        achckbx.setChecked(True)
        achckbx.clicked.connect(self.announceCheckBoxClicked)
        wchckbx = self.withdraw = QCheckBox("Withdrawals")
        wchckbx.clicked.connect(self.withdrawCheckBoxClicked)
#プロットず
        actplt = self.activityplot = ActivityPlot.ActivityPlot(self)

#ボタンレイアウト
        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(pbtn)
        buttonLayout.addWidget(nbtn)

#チェックボックスレイアウト
        checkboxLayout = QHBoxLayout()
        checkboxLayout.addWidget(achckbx)
        checkboxLayout.addWidget(wchckbx)

#エッジフィルタスライダー周りのレイアウト
        sliderLayout = QHBoxLayout()
        sliderLayout.addWidget(thlbl)
        sliderLayout.addWidget(wsldr)
        sliderLayout.addWidget(thtxtbx)

#時間窓周りのレイアウト
        timeWindowLayout = QHBoxLayout()
        timeWindowLayout.addWidget(tmlbl)
        timeWindowLayout.addWidget(tmtxtbx)

#左側のレイアウト用の箱に追加(上から順に上に)
        widgetLayout = QVBoxLayout()
        widgetLayout.addLayout(checkboxLayout)
        widgetLayout.addWidget(actplt)
        widgetLayout.addLayout(sliderLayout)
        widgetLayout.addLayout(timeWindowLayout)
        widgetLayout.addLayout(buttonLayout)


# 全体(左側の箱 + 中央 + 右側の箱)レイアウト
        mainLayout = QHBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        #きた順に左に追加していく
        mainLayout.addLayout(widgetLayout)
        mainLayout.addWidget(self.graphicsView)
        self.setLayout(mainLayout)

# ボタンクリック
    def nextButtonClicked(self):
        self.pos =  self._pos + 1
        self.node.do_next()
        #self.timeWindow.setText(TTNetTimeWindows[self.node._currentTimeWindow])
        self.timeWindow.setText(YoutubePakistanTimeWindows[self.node._currentTimeWindow])

    def previousButtonClicked(self):
        self.node.do_back()
        #self.timeWindow.setText(TTNetTimeWindows[self.node._currentTimeWindow])
        self.timeWindow.setText(YoutubePakistanTimeWindows[self.node._currentTimeWindow])

    # スライダ移動
    def valuechanged(self):
        currentvalue = self.weightfilterSlider.value()
        self.thTextBox.setText(str(currentvalue))
        self.node.thresholdchanged(currentvalue)
    #チェックボックス
    def announceCheckBoxClicked(self):
        announceBool = self.announce.checkState() #uncheck:0, partiallychecked:1. checked: 2
        print(announceBool)
        self.node.announceCheckBoxClicked(announceBool)

    def withdrawCheckBoxClicked(self):
        withdrawBool = self.withdraw.checkState()  # uncheck:0, partiallychecked:1. checked: 2
        print(withdrawBool)
        self.node.withdrawCheckBoxClicked(withdrawBool)
def run():
    myapp = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(myapp.exec_())