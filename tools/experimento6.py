from scipy import stats
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def pearson(ia,ib):
    arq = open('nova2_v2_weka.csv','r')
    a = []
    b = []
    cont = 0
    for l in arq:
        if cont == 0:
            cont = 1
        else:
            tks = l.split('\t')     
            tks[len(tks)-1] = tks[len(tks)-1][:-1]
            a.append(float(tks[ia]))
            b.append(float(tks[ib]))
    arq.close()
    return a, b

def calculatePearson():
    for ai in range(1,18):
        for bi in range(1,18):
            #if ai==27 or bi==27:
            #    continue
            #else:
            a,b = pearson(ai,bi)
            res = stats.pearsonr(a,b)
            if res[0]>0.85 and ai != bi:
                print str(ai)+" "+str(bi)
                print res
'''
arq = open('nova2_v2_weka.csv','r')
cont = 0
clusters = [0]*40;
for line in arq:
    if cont == 0:
        cont = 1
    else:
        tks = line.split(' ')     
        tks[len(tks)-1] = tks[len(tks)-1][:-1]
        if tks[9] == '2010':
            clusters[int(tks[11])] += 1
            

arq =open('corr.txt','r')
lin = [0]*40
tot = int(arq.readline())
col = int(arq.readline())
for i in range(40):
    l = int(arq.readline())
    lin[i] = (l*col)/float(tot)
arq.close()
for i in lin:
    print i
    
arq.close()
'''

#a,b = pearson(1,9)
#res = stats.pearsonr(a,b)
#print res

#df = pd.DataFrame(a,columns=["cluster"])
#df["year"] = b
#corr = df.corr()
#ax = sns.heatmap(corr, annot=True,
#            xticklabels=corr.columns.values,
#            yticklabels=corr.columns.values)

#plt.show()

calculatePearson()