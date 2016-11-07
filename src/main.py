from PyQt5.QtCore import *

import ReadData
import DrawGraph
import subprocess
import MainWindow

#各事件
yp = "YoutubePakistan/" #ファイル数: 4
ttn = "TTNet/" #ファイル数: 9

def run():
#ターミナルコマンド
    """
    cmd = "ls"
    subprocess.call(cmd, shell=True)
    """
#ターゲットファイルリストの取得
    rawdatafiles = ReadData.rawfilelisting(yp)

#生データ読み込み、MOAS判定、エッジの重み集計を行ったのち、グラフデータをCSVとPickleで出力
    #ReadData.readupdatedata(yp, rawdatafiles) # 第一引数は事件名

# CSVからピクル化し、PyPlotグラフで描画
    timerange = 60
    number_of_files = 4 #int(timerange / 15)
    #DrawGraph.draw(youtubepakistan, number_of_files) #15分間分のファイル 4つ分読み込んでグラフへ

# PyQt5のシステム起動
    MainWindow.run()

if __name__ == "__main__":
    run()
