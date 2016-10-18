from PyQt5.QtCore import *

import ReadData
import DrawGraph
import subprocess
import MainView

#各事件
youtubepakistan = "YoutubePakistan/" #ファイル数: 4
ttnet = "TTNet/" #ファイル数: 9


#ノードリンク図部分(matplotlib)
def run():
#ターミナルコマンド
    cmd = "ls"
    subprocess.call(cmd, shell=True)

#ターゲットファイルリストの取得
    rawdatafiles = ReadData.rawfilelisting(ttnet)

#データ読み込みと集計、結果をCSVで出力
    #ReadData.readupdatedata(ttnet, rawdatafiles) # 第一引数は事件名

#データチェック
#    ReadData.checklink()
#    ReadData.checkupdate()

# CSVからPyPlotグラフへ
    timerange = 60
    number_of_files = 9 #int(timerange / 15)
    #DrawGraph.draw(ttnet, number_of_files) #15分間分のファイル 4つ分読み込んでグラフへ

# PyQt5のシステム起動
    MainView.run()

if __name__ == "__main__":
    run()
