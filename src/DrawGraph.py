
import numpy as np
import pickle
from matplotlib import pyplot as plt
from matplotlib import cm as cm

plt.style.use('mystyle')

#import pygraphviz as pgv

import networkx as nx
import csv
import time

colors = ["#ff0000", "#ff7f00", "#ffff00", "#7fff00", "#00ff00", "#00ff7f",
          "#00ffff", "#007fff", "#0000ff", "#7f00ff", "#ff00ff", "#ff007f"]

# YoutubePakistan用ASラベル
YoutubePakistanlabels = [r"17557", r"36561", r"3549", r"3491"]

# TTNet用ASラベル
TTNetspecialnodes = [r"9121", r"6762", r"6939", r"6453", r"701", r"702",
                     r"703", r"577", r"3491", r"3292", r"7018", r"7911",
                     r"209", r"721", r"3549", r"5511", r"2914", r"3356",
                     r"5400", r"1257"]

# 複数CSVデータまとめて読み込む(現時点ではまだdraw()に組み込んだまま
def graphdata(datanum):
    G = nx.Graph()
    for i in range(datanum):  # i = 0 ~ 3
        # ノードデータ
        dirnum = i + 1
        nodelist = []
        edgelist = []
        print("Loading ../data/csv/YoutubePakistan/%d/nodes.csv Node data..." % dirnum)
        nodefile = open("../data/csv/YoutubePakistan/%d/nodes.csv" % dirnum, "r")
        reader = csv.reader(nodefile)
        for row in reader:
            nodelist.append(row[0])

        list_of_nodelist.append(nodelist)
        print(list_of_nodelist)
        # エッジデータ
        print("Loading ../data/csv/YoutubePakistan/%d/edges.csv Edge data..." % dirnum)
        edgefile = open("../data/csv/YoutubePakistan/%d/edges.csv" % dirnum, "r")
        reader = csv.reader(edgefile)
        for row in reader:
            G.add_edge(row[0], row[1], weight=int(row[2]), color="yellow")

#CSVの重みつきエッジ、ノードデータからグラフ描画
def draw(targetdir, num_of_files):
    labels = None
    graph_layout = 'shell'
    node_size = 100
    node_alpha = 0.3
    node_text_size = 12
    edge_color = 'blue'
    edge_alpha = 0.3
    edge_tickness = 1
    edge_text_pos = 0.3
    text_font = 'sans-serif'

    list_of_nodelist = []
    list_of_edgelist = []

    G = nx.Graph()
#CSVファイル読み込み
#ノード
    for i in range(num_of_files):  # i = 0 ~ 8
        # ノードリストのリストを作る
        dirnum = i + 1
        nodelist = []
        edgelist = []
        targetpath = "../data/csv/" + targetdir + str(dirnum) + "/nodes.csv" #"../data/csv/TTNet/" + "1" + "/nodes.csv"
        print("Loading %s Node data..." % dirnum)
        nodefile = open("%s" % targetpath, "r")
        reader = csv.reader(nodefile)
        for row in reader:
            nodelist.append(row[0])
        list_of_nodelist.append(nodelist)
#エッジ
# 1ファイルずつエッジデータを読む。
    #dirnum = 5
    #targetpath = "../data/csv/" + targetdir + str(dirnum) + "/edges.csv"
    #print("Loading %s Edge data..." % targetpath)
    #edgefile = open("%s" % targetpath, "r")
    #reader = csv.reader(edgefile)
    #for row in reader:
    #    G.add_edge(row[0], row[1], weight=int(row[2]))  # iごとに色が変わるようにする

#時間窓全体分を集計したエッジデータ読み込み
    targetpath = "../data/csv/" + targetdir + "overall/overalledges.csv"
    print("Loading %s Edge data..." % targetpath)
    edgefile = open("%s" % targetpath, "r")
    reader = csv.reader(edgefile)
    for row in reader:
        G.add_edge(row[0], row[1], weight=int(row[2]))  # iごとに色が変わるようにする

#各エッジファイル全て一つずつ読み込む
    #for i in range(9):
    #    G.add_nodes_from(list_of_nodelist[i])

    #
    picklededge = G.edges(data = True)
#ノーど分別
    #""" Youtubepakistan用
    nodeset1 = set(list_of_nodelist[0]) #{'1', '2', '3'}
    nodeset2 = set(list_of_nodelist[1]) #{'2', '3', '4'}
    nodeset3 = set(list_of_nodelist[2]) #{'3', '4', '5'}
    nodeset4 = set(list_of_nodelist[3]) #{'4', '5', '6'}

    mergeset1_2 = nodeset1 | nodeset2 # {'1', '2', '3', '4'}
    mergeset1_2_3 = mergeset1_2 | nodeset3 # {'1', '2', '3', '4', '5'}
    mergeset1_2_3_4 = mergeset1_2_3 | nodeset4 # {'1', '2', '3', '4', '5', '6'}

    newnodeset2 = mergeset1_2 ^ nodeset1 #{'4'}
    newnodeset3 = mergeset1_2_3 ^ mergeset1_2 #{'5'}
    newnodeset4 = mergeset1_2_3_4 ^ mergeset1_2_3 #{'6'}

    newnodelist1 = list(nodeset1)
    newnodelist2 = list(newnodeset2)
    newnodelist3 = list(newnodeset3)
    newnodelist4 = list(newnodeset4)


# TTNet用
#フィルタリング
    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 20]
    ehuge = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 200]
    eextreme = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] > 1000]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d['weight'] <= 20]

# 一部ASノードにラベル付け
    speciallabels = {}
    for node in YoutubePakistanlabels:
        speciallabels[node] = node #"r"はraw文字列

#グラフ描画開始
    print("Drawing Graph...")
    start_time = time.time()

#ばねモデル(Fruchterman-Reingold)で計算したnetworkxの位置情報オブジェクトをファイルへ保存(毎回位置計算は無駄)
#辞書(ノードキーとポジション)が帰ってくる
#ノードのピクル
    pos = nx.spring_layout(G)
    #picklefile = open("../data/pickles/n.20080224.1824-20080224.1923.pickle", mode="wb")
    #picklefile = open("../data/pickles/n.20041224.0816-20041224.1018.pickle", mode="wb")
    #pickle.dump(pos, picklefile)

#エッジのピクル
    #picklefile = open("../data/pickles/e.20041224.0816-20041224.1018.pickle", mode="wb")
    #pickle.dump(picklededge, picklefile)

#エッジのみ
    #picklefile = open("../data/pickles/20041224.0816-20041224.1018.pickle", mode="rb")
    #pos = pickle.load(picklefile)

    #ノード(色は色相360度をノード種類数で割った値ずつずらしていく 0, 90, 180, 270といった感じ) hsv(0,100,100), hsv(90,100,100)
    #"""Youtube pakistan用
    """
    nx.draw_networkx_nodes(G, pos, nodelist=newnodelist1,node_color="#ff0000", alpha=0.5, linewidths=0) #四角にするにはnode_shape='s'
    nx.draw_networkx_nodes(G, pos, nodelist=newnodelist2,node_color="#7fff00", alpha=0.5, linewidths=0)
    nx.draw_networkx_nodes(G, pos, nodelist=newnodelist3,node_color="#00ffff", alpha=0.5, linewidths=0)
    nx.draw_networkx_nodes(G, pos, nodelist=newnodelist4,node_color="#7f00ff", alpha=0.5, linewidths=0)
    """
    nx.draw_networkx_nodes(G, pos, nodelist=YoutubePakistanlabels,node_color="#ff0000", alpha=0.5, linewidths=0) #四角にするにはnode_shape='s'


    #TTNet用

#エッジ描画
    #nx.draw_networkx_edges(G, pos, edgelist=eextreme,width=10, edge_color="g", alpha=0.5)
    nx.draw_networkx_edges(G, pos, edgelist=ehuge,width=3, alpha=0.1)
    #nx.draw_networkx_edges(G, pos, edgelist=elarge,width=1, alpha=0.2, style='dashed')

#限定表示したい時間枠
    current = dirnum - 1

#ノード描画(サイズデフォルト = 300
    for i in range(9):
        if i == current:
            continue
        else:
            break
            #nx.draw_networkx_nodes(G, pos, nodelist=list_of_nodelist[i], node_size=250, node_color=colors[6], alpha=0.05,
                               #linewidths=0)
# 限定表示したい時間枠は最後に色付け
    #nx.draw_networkx_nodes(G, pos, nodelist=list_of_nodelist[current], node_size=250, node_color=colors[11], alpha=0.3,
                               #linewidths=0)

#LinkRankと同じノード
    #nx.draw_networkx_nodes(G, pos, nodelist=TTNetspecialnodes , node_size=250, node_color=colors[0], alpha=1, linewidths=0)
    #nx.draw_networkx_nodes(G, pos, nodelist=list_of_nodelist[0],node_size=250 ,node_color=colors[0], alpha=0.5, linewidths=0)
#ノードすべて
    #nx.draw_networkx_nodes(G, pos, node_size=250 ,node_color="#00ffff", alpha=0.5, linewidths=0)
#ラベル描画
    nx.draw_networkx_labels(G, pos, labels=speciallabels, font_size=14, font_family='sans-serif')
    #時間計測
    elapsed_time = time.time() - start_time
    print("Drawn in " + str(elapsed_time) + "[sec].")
    plt.xticks([])
    plt.yticks([])
    plt.show()


