import csv
import pickle


#ノード、エッジデータの生成(CSV形式)
def Nodedatagenerate(targetdir, dirnum, data):
    print("Writing in data/csv/TTNet/%d/nodes.csv" % dirnum)
    csvfile = open('../data/csv/TTNet/%d/nodes.csv' % dirnum, 'w', newline='')
    writer = csv.writer(csvfile, lineterminator='\n')
    for AS in data:
        writer.writerow([AS])
    csvfile.close()

#data[0] = []で、なぜか消せないのでdata[1]から
#アナウンス
def Edgedatagenerate(targetdir, dirnum, data):
    targetpath = "../data/csv/" + targetdir + str(dirnum) + "/nonweightededges.csv"
    print("Writing in %s" % targetpath)
    csvfile = open('%s' % targetpath, 'w', newline='')
    writer = csv.writer(csvfile, lineterminator='\n')
    for i in range(1, len(data)):
        writer.writerow(data[i])
    csvfile.close()

def WeightedEdgedatagenerate(targetdir, dirnum, data):
    targetpath = "../data/csv/" + targetdir + str(dirnum) + "/edges.csv"
    print("Writing in data/csv/" + targetdir + "%d/edges.csv" % dirnum)
    csvfile = open('%s' % targetpath, 'w', newline='')
    writer = csv.writer(csvfile, lineterminator='\n')
    for i in range(0, len(data)):
        writer.writerow(data[i])
    csvfile.close()

def OverallNodedatagenerate(targetdir, data):
    targetpath = "../data/csv/" + targetdir + "overall/nodes.csv"
    print("Writing in %s" % targetpath)
    csvfile = open('%s' % targetpath, 'w', newline='')
    writer = csv.writer(csvfile, lineterminator='\n')
    for i in range(1, len(data)):
        writer.writerow(data[i])
    csvfile.close()

def OverallEdgedatagenerate(targetdir, data):
    targetpath = "../data/csv/" + targetdir + "overall/edges.csv"
    print("Writing in %s" % targetpath)
    csvfile = open('%s' % targetpath, 'w', newline='')
    writer = csv.writer(csvfile, lineterminator='\n')
    for i in range(1, len(data)):
        writer.writerow(data[i])
    csvfile.close()

#取り消し
def WeightedWithdrawEdgedatagenerate(targetdir, dirnum, data):
    targetpath = "../data/csv/" + targetdir + str(dirnum) + "/withdrawedges.csv"
    print("Writing in %s" % targetpath)
    csvfile = open('%s' % targetpath, 'w', newline='')
    writer = csv.writer(csvfile, lineterminator='\n')
    for i in range(0, len(data)):
        writer.writerow(data[i])
    csvfile.close()

def OverallWithdrawEdgedatagenerate(targetdir, data):
    targetpath = "../data/csv/" + targetdir + "overall/withdrawedges.csv"
    print("Writing in %s" % targetpath)
    csvfile = open('%s' % targetpath, 'w', newline='')
    writer = csv.writer(csvfile, lineterminator='\n')
    for i in range(1, len(data)):
        writer.writerow(data[i])
    csvfile.close()

#アナウンス、取り消しのデータの生成(pickle形式)
def makePickle(data, picklefilename):
    picklefile = open("../data/pickles/%s.pickle" % picklefilename, mode="wb")
    pickle.dump(data, picklefile)