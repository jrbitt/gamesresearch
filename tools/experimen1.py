
import numpy as np
from scipy import stats
import pandas as pd

def loadSaveBase(loadfile,savefile):
    #Ler toda a base oficial
    #base = np.genfromtxt(loadfile,usecols=[0,1,2,3,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42],delimiter=",",skip_header=1, names= ['goid','code','year','platform','Strategy','Tactics','Action','Compilation','Adventure','Sports','Educational','Racing','Driving','Puzzle','Role-Playing(RPG)','DLC','Add-on','Simulation','SpecialEdition','Artgame','brightness','saturation','tamura_contrast','arousal','pleasure','dominance','hue_m','sat_m','val_m','black','blue','brown','green','gray','orange','pink','purple','red','white','yellow','entropy_r','entropy_g','entropy_b'],dtype= ['S100','S100','u4','S50','S10','S10','S10','S10','S10','S10','S10','S10','S10','S10','S10','S10','S10','S10','S10','S10','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4','f4'])
    
    base = pd.read_csv(loadfile,usecols=[0,1,2,3,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42],delimiter="\t")

    #np.savetxt('exemplo.csv',base,delimiter='\t', fmt="%s %i %s %.5f %.5f")
    #np.savetxt('exemplo2.csv',base,delimiter='\t', fmt="%s %i %s %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f")
    #np.savetxt(savefile,base,delimiter='\t', fmt="%s %s %i %s %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f %.5f")
    
    base.to_csv(savefile,sep=';', index=False)

#Adiciona a coluna do filename
def addFilename(filename):
    arq = open(filename,'r')
    linhas = []
    prim = True
    for l in arq:
        if prim:
            prim = False
        else:
            tks = l.split(';')
            tks[len(tks)-1] = tks[len(tks)-1][:-1]
            tks.append(tks[1]+".jpg")
            linhas.append(tks)
    arq.close()
    return linhas

def addShapes(shapefile):
    arq2 = open(shapefile,'r')
    mapa = {}
    for l in arq2:
        tks = l.split('\t')
        tks[len(tks)-1] = tks[len(tks)-1][:-1]
        mapa[tks[0]] = tks[1:]
    arq2.close()
    return mapa

def createBase(linhas, mapa,filename):
    arq = open(filename,'w')
    arq.write('goid\tcode\tyear\tplatform\tbrightness\tsaturation\ttamura_contrast\tarousal\tpleasure\tdominance\thue_m\tsat_m\tval_m\tblack\tblue\tbrown\tgreen\tgray\torange\tpink\tpurple\tred\twhite\tyellow\tentropy_r\tentropy_g\tentropy_b\tfilename\tcount\ttotal_area\tavg_size\tperc_area\tperimeter\tcirc\tsolidity\n')
    cont = 0
    for l in linhas:
        if l[2] != '1900' and l[2] != '4444':
            #if int(l[2]) >= 2010 and int(l[2]) < 2020:
            #linhas originais com filename
            for t in l:
                arq.write(t+'\t')

            #novas colunas
            tk = mapa[l[len(l)-1]]
            for k in tk:
                arq.write(k+'\t')

            arq.write('\n')
            cont += 1
    arq.close()
    print cont

a = []
b = []
def pearson(ia,ib):
    arq = open('exemplo4_10.csv','r')
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
    for ai in range(4,36):
        for bi in range(4,36):
            if ai==27 or bi==27:
                continue
            else:
                a,b = pearson(ai,bi)
                res = stats.pearsonr(a,b)
                if res[0]>0.3 and ai != bi:
                    print str(ai)+" "+str(bi)
                    print res
                
base = None
linhas = None
mapa = None
loadSaveBase("base_oficial_final_v2.csv",'nova1_v2.csv')
linhas = addFilename('nova1_v2.csv')
mapa = addShapes('shapes40mil.csv')
createBase(linhas,mapa,'nova3_v2.csv')

#calculatePearson()

'''
arq = open('exemplo4.csv','r')
arq2 = open('Clusters_weka.txt','r')
arq3 = open('exemplo4_clusters.csv','w')
arq.readline()
for l in arq:
    linha = arq2.readline()
    t = linha.split(',')
    nl = ""
    nl += l+'\t'+t[len(t)-1][:-1]+'\n'
    arq3.write(nl)
arq.close()
arq2.close()
arq3.close()
'''