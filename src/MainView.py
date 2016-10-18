#参考1: http://melpystudio.blog82.fc2.com/blog-entry-138.html
#参考2: http://vivi.dyndns.org/vivi/docs/Qt/graphics.html
#参考3: http://d.hatena.ne.jp/mFumi/20141112/1415806010

import pickle
import sys

from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QIntValidator, QPixmap, QTransform, QCursor)
from PyQt5.QtWidgets import (QApplication, QWidget, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsEllipseItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout, QGraphicsPixmapItem, qApp,
                             QLabel, QLineEdit, QPushButton, QSlider, QSizePolicy)

import ActivityPlot
import NodeLinkScene

imagepath = "./sample.png"

#可視化システム全体のビュー
class MainWindow(QWidget):
    def __init__(self, parent=None): #親がいないウィジェットはウィンドウになる
        super(MainWindow, self).__init__(parent)

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
        # 直接アイテムを追加するとき
        """
        self.testnode =  QGraphicsEllipseItem(100, 100, 200, 100)
        self.testnode.setBrush(QBrush(QColor.fromHsvF(0/360, 0.5, 1)))
        self.testnode.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
        nodelinkscene.addItem(self.testnode)
        """

# ノードリンクビューの脇につけるボタンやスライダー
        self.testButton = QPushButton("test")
        self.testButton.clicked.connect(self.testButtonClicked)

        self.weightfilterSlider = QSlider(Qt.Horizontal)
        self.weightfilterSlider.setMinimum(0)
        self.weightfilterSlider.setMaximum(100)
        self.weightfilterSlider.setValue(50)
        self.weightfilterSlider.setTickInterval(1)
        self.weightfilterSlider.valueChanged.connect(self.valuechanged)

#プロットず
        self.activityplot = ActivityPlot.ActivityPlot(self, width=5, height=4)

#左側のレイアウト用の箱に追加
        widgetLayout = QVBoxLayout()
        widgetLayout.addWidget(self.activityplot)
        widgetLayout.addWidget(self.testButton)
        widgetLayout.addWidget(self.weightfilterSlider)


# 全体(左側の箱 + 中央 + 右側の箱)レイアウト
        mainLayout = QHBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        #きた順に左に追加していく
        mainLayout.addLayout(widgetLayout)
        mainLayout.addWidget(self.graphicsView)
        self.setLayout(mainLayout)


    def testButtonClicked(self):
        print("Test Button Clicked!!")

    def valuechanged(self):
        currentvalue = self.weightfilterSlider.value()
        print("Slider !!", currentvalue)

def run():
    myapp = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(myapp.exec_())