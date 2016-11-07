import sys
import os
import time as tm
from datetime import datetime, date, time
import numpy as np
import DataFileGenerater
import MOASEventChecker
import pickle

a = []
links = []
prefixes = []
ip = []
global everyMinutesAnnounce
everyMinutesAnnounce = {} #1分ずつ全て保存し、ピクル
global everyMinutesWithdraw
everyMinutesWithdraw = {} #1分ずつ全て保存し、ピクル
global observerASes
observerASes = {} #各観測点
ASes = np.empty((0, 1), int)
# 複数ファイルの全集計先
overalllinks = [[]]
overallWithdrawlinks = [[]]
overallASes = []

filenum = 4

# 現在生きている(有効になっている)IPプリフィックスとそのパスの辞書データ
# {"1.1.1.1": {"prefixValue": 16, "originAS": 10, "pathes": [[2, 10], [1, 2, 10]]}}
validPrefixesDict = {}
#dir = "../data/updates/YoutubePakistan/"

#15分刻みのファイルのみに対応、bgpdumpの*.bz2ファイルの読み込みに多分使う
def bz2filelisting(first, last, num):
    namelist = []
    for i in range(num):
        if (first + i * 15) % 100 > 59: # 1869だと読み込めないので1909にする
            return namelist
        else:
            print("Data Load Error")
            exit(1)
    return namelist
#import osで一気にディレクトリ内全部を引っ張ってくるのが賢いのか・・・。復元した生データの読み込みに使う
def rawfilelisting(dir):
    targetdir = "../data/updates/" + dir
    files = os.listdir(targetdir)
    print("Loading Target: ", files)
    return files

#アプデデータ読み込み
def readupdatedata(targetdir, filelist):
    #bgpdumpの-Mオプションで復元した場合
    num_of_files = len(filelist)

    #ファイル1つ分
    for fileindex in range(num_of_files):
        alllinks = [[]]  # []にするとnumpy.sortがうまく働かなくなる。data[0] = []となる。ここで初期化しないと各ファイルそれぞれのデータが分けられなくなる
        global allWithdrawlinks
        allWithdrawlinks = [[]]
        allASes = [] #1ファイル分の集計先
        target = "../data/updates/" + targetdir + filelist[fileindex]
        currentFile = filelist[fileindex]
        currentMinute = int(currentFile[-2:len(currentFile)]) # ファイル名のしも二桁を開始分とする
        print("Reading ", target)
        for line in open("%s" % target, "r"):
            word = line.split("|")
            #word[0]="BGP4MP" word[1]= 02/24/08 word[2]= "A" or "W", word[3]= ルータのIPアドレス word[4]=アナウンスしたAS word[5]= IPプリフィックス word[6]= ASパス(最右がオリジン)
#アナウンス
            if word[2] == "A":
                prefix = word[5].split("/") #["131.112.0.0", "16"]
                addressPrefix = prefix[0] #"131.112.0.0"
                prefixLength = int(prefix[1]) # 16
                ASpath = word[6]  # "13 11 290"
                ASlist = ASpath.split(" ") #[13, 11, 290]
                originAS = ASlist[-1]  # "290"
                #このアナウンスは以前他のASがアナウンスしたものと競合しないかをチェックする(MOASイベント)
                MOASEventChecker.multipleOriginASCheck(addressPrefix, prefixLength, originAS, validPrefixesDict)
                #時間(str型)
                #月/日/年
                announceYear = word[1].split(" ")[0].split("/")[2]
                announceMonth = word[1].split(" ")[0].split("/")[0]
                announceDay = word[1].split(" ")[0].split("/")[1]
                #時:分:秒
                announceHour = word[1].split(" ")[1].split(":")[0]
                announceMinute = word[1].split(" ")[1].split(":")[1]
                announceSecond = word[1].split(" ")[1].split(":")[2]
                announceTime = announceYear + announceMonth + announceDay + announceHour + announceMinute
                #分が新しく切り替わったら
                if currentMinute != announceMinute:
                    currentMinute = announceMinute
                router = word[3]
                observerAS = word[4]
                # パス内のASすべて抽出し、全ASリストへ集計
                for AS in ASlist:
                    if AS[0] == "{": #6762 701 7381 {14033,14455}の"{14033,14455}"部分
                        #ASset = AS
                        #print(ASset)
                        #for AS_in_ASset in ASset:
                        #    allASes.append(int(AS_in_ASset))
                        break #出現頻度は低いので現段階ではとりあえず
                    else:
                        allASes.append(int(AS))
                        #全ファイル集計分
                        #overallASes.append(int(AS))

                # 有効アナウンス辞書に追加
                # {"1.1.0.0": {"min": int型のIPアドレス最小値, "max": int型のIPアドレス最大値, "prefixLength": 16, "originAS": 10, "pathes": {"12:00": [2, 10], "12:03":[1, 2, 10]} }}
                if addressPrefix in validPrefixesDict: #二回め以降のアナウンスはアナウンス時間とパスを追加
                    if announceTime in validPrefixesDict[addressPrefix]["pathes"]: #同じ時間に複数のアナウンスがある場合、パスを追加
                        #print("current:",validPrefixesDict[addressPrefix]["pathes"])
                        temp = validPrefixesDict[addressPrefix]["pathes"][announceTime] #[[1, 2], [3, 4]]
                        temp.append(ASlist) #[[1, 2], [3, 4], [13, 11, 290]]
                        #print("temp:", temp)
                        validPrefixesDict[addressPrefix]["pathes"][announceTime] = temp
                    else: #違う時間にアナウンスされている時
                        validPrefixesDict[addressPrefix]["pathes"][announceTime] = [ASlist]
                        #print("!! Multiple Announce !!")
                else: #初めてのアナウンス
                    announcedPath = [ASlist] # []
                    validPrefixesDict[addressPrefix] = {"prefixLength": prefixLength, "originAS": originAS, "pathes": {announceTime: announcedPath} }

                    #print("!! First Announce !!", validPrefixesDict[addressPrefix]["pathes"][announceTime])

                #ASパス部分からリンクペアデータの収集
                for i in range(len(ASlist) - 1):
                    if ASlist[i+1][0] == "{" : #6762 701 7381 {14033,14455}の"{14033,14455}"部分
                        break #出現頻度は低いので現段階ではとりあえず
                    elif ASlist[i] != ASlist[i+1]:
                        alllinks.append([ASlist[i], ASlist[i+1]]) #1ファイル分のみのリンク
                        overalllinks.append([ASlist[i], ASlist[i+1]]) #全ファイル分集計するためのリンク
                        if announceTime in everyMinutesAnnounce: #
                            temp = everyMinutesAnnounce[announceTime]
                            temp.append([ASlist[i], ASlist[i+1]])
                            everyMinutesAnnounce[announceTime] = temp
                        else: #分が新しくなって1番目にきたアナウンス
                            everyMinutesAnnounce[announceTime] = [[ASlist[i], ASlist[i+1]]] # [[1, 2]]
                            #print(everyMinutesAnnounce)
                    else:
                        continue
#取り消し 前回取り消しされてからこの取り消しまでの間で行われたプリフィックスアナウンス情報をファイルをまたがって引っ張ってくる必要がある
            elif word[2] == "W":
                withdrawPrefix = word[5].rstrip("\n").split("/") # 131.112.0.0/16
                withdrawAddressPrefix = withdrawPrefix[0] #"131.112.0.0"
                prefixLength = int(withdrawPrefix[1]) # 16
                #月/日/年
                withdrawYear = word[1].split(" ")[0].split("/")[2]
                withdrawMonth = word[1].split(" ")[0].split("/")[0]
                withdrawDay = word[1].split(" ")[0].split("/")[1]
                #時:分:秒
                withdrawHour = word[1].split(" ")[1].split(":")[0]
                withdrawMinute = word[1].split(" ")[1].split(":")[1]
                withdrawSecond = word[1].split(" ")[1].split(":")[2]
                global withdrawTime
                withdrawTime = withdrawYear + withdrawMonth + withdrawDay + withdrawHour + withdrawMinute
                if withdrawAddressPrefix in validPrefixesDict: #過去にアナウンスされていたプリフィックスなら
                    #print(validPrefixesDict[withdrawAddressPrefix])
                    withdrawPathes = validPrefixesDict[withdrawAddressPrefix]["pathes"].values() #[[1, 1], [[1, 2], [1, 2, 3]]]
                    #取り消しリンクデータの収集
                    for pathes in withdrawPathes:
                        for path in pathes:
                            withdrawPathSeparater(path)

                    #辞書からそのプリフィックスを削除する
                    del validPrefixesDict[withdrawAddressPrefix]
                router = word[3]
                receiveAS = word[4]
            else:
                print("----------------------Data Load Error----------------------")
                exit(1)
        print("----------------------Dataset Load Success!----------------------")

#プリフィックス
        #print(validPrefixesDict)
        alluniqueprefixes = np.unique(prefixes)
        #print(alluniqueprefixes)
        #print("The number of announced IP Prefixes:", len(prefixes))
        #print("The number of unique IP Prefixes:", len(alluniqueprefixes))
#AS(ノード)
        alluniqueASes = np.unique(allASes)
        #print("The number of appeared ASes:", len(allASes))
        #print("All unique ASes: ", alluniqueASes)
        #print("The number of unique ASes:", len(alluniqueASes))

#アナウンスリンク(エッジ)
        #print("All links: ", alllinks)
        #print("The number of appeared links:", len(alllinks))
        alluniquelinks = np.unique(alllinks)
        #print("The number of unique links: ", len(alluniquelinks))
        linkdata = np.sort(alllinks)
        #del linkdata[0:1] 先頭の[]を消したい・・・

        # エッジの重み集計
        weightedlinkdata = weightcounter(linkdata)

#取り消しリンク
        withdrawlinkdata = np.sort(allWithdrawlinks)
    # エッジの重み集計
        weightedWithdrawlinkdata = weightcounter(withdrawlinkdata)

    #CSVに書き込む
        dirnum = fileindex + 1
        #重みなし(集計前)の全エッジ
        #DataFileGenerater.Edgedatagenerate(dirnum, linkdata)
        #ノード(AS)
        DataFileGenerater.Nodedatagenerate(targetdir, dirnum, alluniqueASes)
        #1ファイル分のリンク(重みつき)
        DataFileGenerater.WeightedEdgedatagenerate(targetdir, dirnum, weightedlinkdata)
        #1ファイル分の取り消しリンク(重みあり)
        DataFileGenerater.WeightedWithdrawEdgedatagenerate(targetdir, dirnum, weightedWithdrawlinkdata)
    #全体ASデータを一旦一意にする(多くなりすぎる)
        #overallASes = np.unique(overallASes)

#複数ファイル分すべて集計したもの
    print("Processing Overall Data...")
    overalluniqueASes = np.unique(overallASes)
    overallASdata = np.sort(overalluniqueASes)
    overalluniquelinks = np.unique(overalllinks)
    overalllinkdata = np.sort(overalllinks)
    #重み集計なしでCSVへ書き込む
    #DataFileGenerater.OverallEdgedatagenerate(overalllinkdata)
#重み集計
    weightedoveralllinkdata = weightcounter(overalllinkdata)

#CSVへ書き込む
    #全ファイル分のノード
    DataFileGenerater.OverallNodedatagenerate(targetdir, overallASdata)
    #重み集計済みエッジ
    DataFileGenerater.OverallEdgedatagenerate(targetdir, weightedoveralllinkdata)

#1分ごとのアナウンス、取り消しデータをピクル化
    DataFileGenerater.makePickle(everyMinutesAnnounce, "a.20080224.1824-20080224.1923")
    DataFileGenerater.makePickle(everyMinutesWithdraw, "w.20080224.1824-20080224.1923")

#同リンクが複数ある時、その分重みをインクリメントする・・・という集計。あらかじめデータは整理されていることが前提。
def weightcounter(data):
    pointer = 1
    weighteddata = []
    print("----------------------Counting weight of edges...----------------------")
    #print(data)
    while pointer < len(data):
        pointer, weighteddata = count(data, pointer, weighteddata)
    print("----------------------Finished!!!----------------------")
    #print(weighteddata)
    return weighteddata

def count(input, pointer, output):
    weight = 1
    for j in range(pointer, len(input)):
        #最終行のリンク
        if j == len(input) - 1:
            if weight >= 1:
                newdata = input[j]
                newdata.append(weight)  # ["10026", "75292, 3]
                output.append(newdata)
                break
            else:
                exit(1)
        elif input[j] == input[(j + 1)]:
            #print(input[j], input[(j + 1)])
            #print("Same")
            weight += 1
            #print(weight)
        elif input[j] != input[(j + 1)]:
            #print(input[j], input[j + 1])
            #print("Wrong")
            newdata = input[j] # ["10026", "75292"]
            #print("Edgedata:", newdata)
            newdata.append(weight)  # ["10026", "75292", 3]
            #print("Newdata:", newdata)
            output.append(newdata)
            break
        else:
            exit(1)
    nextpointer = pointer + weight
    return nextpointer, output

#取り消しリンク用。ASのリストが引数
def withdrawPathSeparater(path):
    for i in range(len(path) - 1):
        if path[i + 1][0] == "{":  # 6762 701 7381 {14033,14455}の"{14033,14455}"部分
            break  # 出現頻度は低いので現段階ではとりあえず
        elif path[i] != path[i + 1]:
            #print(path[i], path[i + 1])
            allWithdrawlinks.append([path[i], path[i + 1]])  # 1ファイル分のみの取り消しリンク
            overallWithdrawlinks.append([path[i], path[i + 1]])  # 全ファイル分集計するための取り消しリンク
            if withdrawTime in everyMinutesWithdraw:  #分ごと辞書
                temp = everyMinutesWithdraw[withdrawTime]
                temp.append([path[i], path[i + 1]])
                everyMinutesWithdraw[withdrawTime] = temp
            else:  # 分が新しくなって1番目にきたアナウンス
                everyMinutesWithdraw[withdrawTime] = [[path[i], path[i + 1]]]  # [[1, 2]]
        else:
            continue



