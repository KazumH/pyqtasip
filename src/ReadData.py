import sys
import os
import numpy as np
import CSVGenerater

a = []
links = []
prefixes = []
fromases = []
toases = []
earlist_time = 0
latest_time = 0
ip = []
monitor_as = []
ASes = np.empty((0, 1), int)
# 複数ファイルの全集計先
overalllinks = [[]]
overallASes = []

firstfile = 200802241824
lastfile = 200802241909
filenum = 4
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

"""
class Prefix:
    def __init__(self, network, value, time. router, origin):
        self.prefix = network
        self.
"""


"""
class link:
    def __init__(self, t, from_AS, to_AS, hop):
        self.t = t
        self.fromasn = from_AS
        self.toasn = to_AS
        self.hops = hop
"""


#アプデデータ読み込み
def readupdatedata(targetdir, filelist):
    #bgpdumpの-Mオプションで復元した場合

    num_of_files = len(filelist)
    for fileindex in range(num_of_files):
        alllinks = [[]]  # []にするとnumpy.sortがうまく働かなくなる。data[0] = []となる。ここで初期化しないと各ファイルそれぞれのデータが分けられなくなる
        allASes = [] #1ファイル分の集計先
        target = "../data/updates/" + targetdir + filelist[fileindex]
        print("Reading ", target)
        for line in open("%s" % target, "r"):
            word = line.split("|")
            #word[0]="BGP4MP" word[1]= 02/24/08 word[2]= "A" or "W", word[3]= ルータのIPアドレス word[4]=アナウンスしたAS word[5]= IPプリフィックス word[6]= ASパス(最右がオリジン)
            """
            Pythonでは、switch文が使えない
            if, elifを使うが、条件に
            if str in {"a", "b"}:
                文...
            elif str in {"c", "d", "e"}:
                文...
            とやると、可読性上がる
            """
            #アナウンス
            if word[2] == "A":
                ip = word[5].split("/")
                prefixes.append(word[5]) # 131.112.0.0/16
                prefix_value = ip[1] # 16
                time = word[1] #月/日/年
                #timestamp = int(time.mktime( datetime.strptime(dtime,"%Y-%m-%d %H:%M:%S").timetuple()))
                router = word[3]
                receive_AS = word[4]
                ASpath = word[6] # [13 11 290]
                origin = ASpath[-1] # 290

                # パス内のASすべて抽出し、全ASリストへ集計
                ASlist = ASpath.split(" ")
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

                #リンクデータの収集
                for i in range(len(ASlist) - 1):
                    if ASlist[i+1][0] == "{" : #6762 701 7381 {14033,14455}の"{14033,14455}"部分
                        break #出現頻度は低いので現段階ではとりあえず
                    elif ASlist[i] != ASlist[i+1]:
                        alllinks.append([ASlist[i], ASlist[i+1]]) #1ファイル分のみのリンク
                        overalllinks.append([ASlist[i], ASlist[i+1]]) #全ファイル分集計するためのリンク
                    else:
                        continue

            #取り消し
            elif word[2] == "W":
                ip = word[5].split("/")
                prefixes.append(word[5].rstrip("\n")) # 131.112.0.0/16
                prefix_value = ip[1] # 16
                time = word[1] #月/日/年
                #timestamp = int(time.mktime( datetime.strptime(dtime,"%Y-%m-%d %H:%M:%S").timetuple()))
                router = word[3]
                receive_AS = word[4]
            else:
                print("----------------------Data Load Error----------------------")
                exit(1)

        print("----------------------Dataset Load Success!----------------------")
#プリフィックス
        #print(prefixes)
        alluniqueprefixes = np.unique(prefixes)
        #print(alluniqueprefixes)
        #print("The number of announced IP Prefixes:", len(prefixes))
        #print("The number of unique IP Prefixes:", len(alluniqueprefixes))
#AS(ノード)
        alluniqueASes = np.unique(allASes)
        #print("The number of appeared ASes:", len(allASes))
        #print("All unique ASes: ", alluniqueASes)
        #print("The number of unique ASes:", len(alluniqueASes))
#リンク(エッジ)
        #print("All links: ", alllinks)
        #print("The number of appeared links:", len(alllinks))
        alluniquelinks = np.unique(alllinks)
        #print("The number of unique links: ", len(alluniquelinks))
        linkdata = np.sort(alllinks)
        #del linkdata[0:1] 先頭の[]を消したい・・・

        # エッジの重み集計
        weightedlinkdata = weightcounter(linkdata)

    #CSVに書き込む
        dirnum = fileindex + 1
        #重みなし(集計前)の全エッジ
        #CSVGenerater.Edgedatagenerate(dirnum, linkdata)
        #ノード(AS)
        CSVGenerater.Nodedatagenerate(targetdir, dirnum, alluniqueASes)
        #リンク(重みつき)
        CSVGenerater.WeightedEdgedatagenerate(targetdir, dirnum, weightedlinkdata)
    #全体ASデータを一旦一意にする(多くなりすぎる)
        #overallASes = np.unique(overallASes)

#複数ファイル分すべて集計したもの
    print("Processing Overall Data...")
    overalluniqueASes = np.unique(overallASes)
    overallASdata = np.sort(overalluniqueASes)
    overalluniquelinks = np.unique(overalllinks)
    overalllinkdata = np.sort(overalllinks)

    #重み集計なしでCSVへ書き込む
    #CSVGenerater.OverallEdgedatagenerate(overalllinkdata)
#重み集計
    weightedoveralllinkdata = weightcounter(overalllinkdata)

#CSVへ書き込む
    #全ファイル分のノード
    CSVGenerater.OverallNodedatagenerate(targetdir, overallASdata)
    #重み集計済みエッジ
    CSVGenerater.OverallEdgedatagenerate(targetdir, weightedoveralllinkdata)


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
    #print(nextpointer)
    #print(output)
    #再起は1000回まで。
    #count(input, nextpointer, output)  <- NG
    return nextpointer, output