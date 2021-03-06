from PIL import Image
from PIL import ImageDraw
import math, random, sys, codecs
from database import GamesDatabase
from imglib import createImages
from imglib import compareImages
from imglib import drawSpiral
        
from sklearn.decomposition import PCA
from shapely.geometry import Point
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
        
class Screen(object):
    code = ""
    cluster = 0
    img = None
    values = None
    distance = -1
    goid = None
    platform = -1
    
    def __init__(self,values,path,code,gid,cls=None,tks=None):
        self.values = values
        self.tokens = tks
        self.goid = gid
        self.path = path                                    #Path for image file
        self.code = code                                 #Code to image
        self.cluster = cls                                  #Cluster ID
        #For each value after cluster ID
        #add in values of screen
        #temp = Image.open(path+self.code+".jpg")
        #self.img = temp.copy()
        #temp.close()
        #self.img.thumbnail((100,100),Image.ANTIALIAS)
    
    def createImage(self,thumb_size):
        try:
            temp = Image.open(self.path+self.code+".jpg")
            self.img = temp.copy()
            temp.close()
            self.img.thumbnail((thumb_size,thumb_size),Image.ANTIALIAS)
        except:
            print "no create image"
        
    def compare(self,avgValues):
        dist = 0
        for i in range(len(self.values)):
            dist = dist + pow(avgValues[i]-self.values[i],2)
        self.distance = math.sqrt(dist)
    
    def delImage(self):
        self.img.close()

class Centroid(object):
    values = []
    grid = None
    images = []
    canvas = None
    average_image = None
    image_width = 0
    image_height = 0
    _id = -1
            
    
    def __init__(self,line,c):
        self._id = c
        self.values = line.split('\t')
        for i in range(len(self.values)):
            self.values[i] = float(self.values[i])      
        self.images = []
    
    def add(self,im):
        #i = im.thumbnail((100,100),Image.ANTIALIAS)
        self.images.append(im)
    
    def distance(self, ivalues):
        s = 0
        for i in range(0,len(self.values)):
            s += (float(ivalues[i])-float(self.values[i]))**2
        return math.sqrt(s)
    
    def findDistances(self):
        val = sys.float_info.max
        ind = -1
        i = 0
        for img in self.images:
            v = self.distance(img.values)
            img.distance = v
                
    def defineIndex(self, size):
        print "s "+str(size)
        d = False
        i = 1
        while not d:
            if size <= i**2:
                d = True
            else:
                i += 1
        print "i "+str(i)
        return i

    def plotManovich(self,colorsByCol):
        if len(self.images) == 0:
            return
        if len(self.images) == 1:
            im = Image.open(self.images[0].path+self.images[0].code+".jpg")
            im.thumbnail((100,100),Image.ANTIALIAS)
            im.save(str(self._id)+".png")
            return
                
        print colorsByCol
        tmp = []
        for i in self.images:
            tmp.append(i.values)
        df = pd.DataFrame(tmp)
        
        p = PCA(n_components=2)
        X = df.as_matrix()
        
        p.fit(X)
        subspace = pd.DataFrame(p.fit_transform(X),columns=["x","y"])
        
        num_bins = 100
        x = [subspace.x.min()*1.5,subspace.x.max()*1.5]
        y = [subspace.y.min()*1.5,subspace.y.max()*1.5]
        tmp = pd.DataFrame(x,columns=["x"])
        tmp["y"] = y
        subspace = subspace.append(tmp)
        subspace['x_bin'] = pd.cut(subspace['x'],num_bins,labels=False)
        subspace['y_bin'] = pd.cut(subspace['y'],num_bins,labels=False)

        subspace = subspace[:-2]
        factor = 1
        subspace["x_grid"] = subspace.x_bin * factor
        subspace["y_grid"] = subspace.y_bin * factor
        centroid_point = []
        n = len(subspace.index)
        for j in range(n):
            tx = subspace.x_grid.loc[j].astype(float)
            ty = subspace.y_grid.loc[j].astype(float)
            centroid_point.append(Point(tx,ty))
    
        subspace['centroid_point'] = centroid_point
        grid_side = num_bins * factor
        
        x,y = range(grid_side) * grid_side, np.repeat(range(grid_side),grid_side)
        grid_list = pd.DataFrame(x,columns=['x'])
        grid_list['y'] = y
        point = []
        n = len(grid_list.index)
        for i in range(n):
            point.append(Point(grid_list.x.loc[i],grid_list.y.loc[i]))

        grid_list['point'] = point
        open_grid = list(grid_list.point)
        centroids = list(subspace.centroid_point)
        

        collection = pd.DataFrame()
        n = len(collection.index)
        local_path = []
        cls = []
        dst = []
        for i in self.images:
            local_path.append(i.path+i.code+".jpg")
            cls.append(i.cluster)
            dst.append(i.distance)
        collection['local_path'] = local_path            
        collection['clusters'] = cls    
        collection['cluster_dist'] = dst  
        
        
        thumb_side = 100
        px_w = thumb_side * grid_side
        px_h = thumb_side * grid_side
        self.canvas = Image.new('RGBA',(px_w,px_h),(50,50,50,0))
        n = len(subspace.index)

        print n,len(self.images),self._id
        for i in self.images:
            centroid = subspace.centroid_point.loc[0]
            try:
                # again, a workaround for indexing difference
                candidates = collection[collection.clusters==i.cluster]
                candidates.sort_values("cluster_dist",inplace=True)
                best = candidates.iloc[0]
                im = Image.open(best.local_path)
                im.thumbnail((thumb_side,thumb_side),Image.ANTIALIAS)
                i.img = im
                self._paintCols(5,colorsByCol,i,2)
                closest_open = min(open_grid,key=lambda x: centroid.distance(x))
                x = int(closest_open.x) * thumb_side
                y = int(closest_open.y) * thumb_side
                self.canvas.paste(im,(x,y))
                idx = collection[collection.local_path==best.local_path].index
                collection.drop(idx,inplace=True)
                open_grid.remove(closest_open)
            except:
                print "cluster empty"
        self.canvas.save(str(self._id)+".png")
        
        
        
    def filterGames(self,maxGames,thumb=100):
        f = []
        s = []
        for i in self.images:
            if i.goid not in f:
                f.append(i.goid)
                s.append(i.code)
        if maxGames != -1:
            lim = min(maxGames,len(f))
        else:
            lim = len(f)
        
        gdb = GamesDatabase()
        self.images = self.images[:lim]
        arq = codecs.open('nomes'+str(self._id)+".txt",'w',"utf-8")
        for i in range(lim):
            print f[i]
            if maxGames != -1:
                c = gdb.getImageAverage(f[i])
                if c!= None:
                    self.images[i].code = "/avg_rgb/"+c
                else:
                    self.images[i].code = s[i]
            g = gdb.getGameByObject(f[i])
            w = g['name'].replace(u'\xe3', u' ')
            arq.write(w+"\t"+self.images[i].code+"\t"+str(g['_id'])+'\n')
            self.images[i].createImage(thumb)
        arq.close()
            
    def selectGames(self,target,maxGames,thumb):
        for i in self.images:
            pass
        
    
    def organizeByAverageGames(self,thumb=100):
        #cada centroid deve obter sua imagem media da base
        self.findDistances()
        self.images.sort(key=lambda image: image.distance)
        self.filterGames(-1,thumb)
        
        temp = []
        for i in range(len(self.images)):
            temp.append(self.images[i].img)
        #calcular a media usando essas imagens medias
        if len(temp)>0:
            self.average_image = createImages(temp)
            self.average_image.save("saida_media_"+str(self._id)+".png")
        
        #aproximar os kj dessa imagem media
        #quando plotar pinta a media principal e as imagens medias dos kjs
        
    def organizeByGames(self,colorsByCol,maxGames):
        self.findDistances()
        print "tot.images: "+str(len(self.images))
        self.images.sort(key=lambda image: image.distance)
        self.filterGames(maxGames)
        self.plotManovich(colorsByCol)
            
    def organize(self,colorsByCol,maxImgs=-1):
        self.findDistances()
        self.plotManovich(colorsByCol)
        #print "tot.images: "+str(len(self.images))
        #sorted(self.images, key=lambda image: Screen.distance)
        #if maxImgs != -1:
        #    self.images = self.images[:maxImgs]            
        
    def _paintCols(self,size,colorsByCol,s,offset):
        px = 0
        ws = size
        d = ImageDraw.Draw(s.img)
        for i in colorsByCol.keys():
            color = colorsByCol[i][s.tokens[i]]
            d.ellipse((px, 0, px+ws, ws), fill = color, outline =color)
            px += (ws + offset)   
        del d
            
class ImageCreator(object):  
    centroids = []
    images = []
    colorsByCol = {}
    genres = None
    
    def initNoClasses(self,centroids,clusters,path, colsPrint,colsDist=None):
        self.init(centroids,None,clusters,path, colsPrint,colsDist)

    def setGenres(self, g):
        self.genres = g
        
    def getClass(self,vls2):
        mx = sys.float_info.max
        ind = -1
        ic = 0
        for c in self.centroids:
            i = 0
            tot = 0
            for v in range(len(vls2)):
                tot += (float(vls2[v]) - float(c.values[i]))**2
                i += 1
            tot = math.sqrt(tot)
            if tot < mx:
                mx = tot
                ind = ic
            ic += 1
        return ind,mx
    
    def breakLine(self,line,colsDist):
        tokens = line.split('\t')
        vls = []
        i = 0
        for t in tokens:
            if i in colsDist:
                vls.append(float(t))
            i+=1
        return tokens,vls
    
    def rep(self,dic):
        c = 0
        for i in dic:
            s = i.replace(u'\xa0', u' ')
            dic[c] = s
            c += 1
        
    def init(self,centroids,cls,samples,path, colsPrint,colsDist):
        gdb = GamesDatabase()
        
        #Ler os centroids
        arq = open(centroids, 'r')
        lines = arq.readlines()    
        code = 0
        for line in lines:
            c = Centroid(line,code)
            self.centroids.append(c)
            code += 1
        arq.close()

    
        if cls != None:
            #Ler as classes atribuidas aos exemplos
            arq = open(cls, 'r')
            classes = []
            lines = arq.readlines()
            for line in lines:
                classes.append(int(line))
            arq.close()
        
        #Criar as telas usando a base de exemplos
        arq = open(samples, 'r')
        arq.readline()
        lines = arq.readlines()
        i = 0
        out = open('clusters_para_tese.txt','w')
        for line in lines:
            img = None
            if cls != None:
                img = Screen(line,path,classes[i])
            else:
                tokens,vls = self.breakLine(line,colsDist)
                code= tokens[1]
                gid = tokens[0]
                #Aplicando filtro de genero
                gm = gdb.getGameByObject(gid)
                if gm.has_key('genres'):
                    self.rep(gm['genres'])
                    if self.genres != None:
                        for g in self.genres:
                            if any(ig == g for ig in gm['genres']):
                                c,mx = self.getClass(vls)

                                out.write(str(c)+" ")
                                out.write(code+" ")
                                out.write(gid+"\n")

                                img = Screen(vls,path,code,gid,c,tokens)
                                img.distance = mx

                                self.addValue(img.tokens,colsPrint)
                                self.images.append(img)
                                print i
                                i += 1
                                break 
                    else:
                        c,mx = self.getClass(vls)

                        out.write(str(c)+" ")
                        out.write(code+" ")
                        out.write(gid+"\n")

                        img = Screen(vls,path,code,gid,c,tokens)
                        img.distance = mx

                        self.addValue(img.tokens,colsPrint)
                        self.images.append(img)
                        print i
                        i += 1

                                                       
        arq.close()
        out.close()
        
        #Associa as telas aos centroides
        for i in self.images:
            self.centroids[i.cluster].add(i)
                        
    def addValue(self,vls,colsPrint):
        #Para cada coluna para ser pintada
        for c in colsPrint:
            #Se a coluna nao esta adicionada
            if c not in self.colorsByCol.keys():
                #adiciona a coluna sem nenhum valor
                self.colorsByCol[c] = {} 
            #se ainda nao tem esse valor da coluna adicionada
            if vls[c] not in self.colorsByCol[c].keys():
                self.colorsByCol[c][vls[c]] =  (random.randint(0,255),random.randint(0,255),random.randint(0,255))

    def createAverageImageByGames(self,maxImgs,thumb=100):
        temp = []
        for c in self.centroids:
            c.organizeByAverageGames(thumb)
            if c.average_image != None:
                temp.append(c.average_image)

        if len(temp)>0:
            average_image = createImages(temp)
            average_image.save("saida_media.png")
    
    def createImagesByGames(self,rgb,offset,maxGames=-1):
        i = 0
        self.colorsByCol = {10: {'1990': (207, 25, 49), '2000': (135, 82, 128), '2010': (57, 75, 79), '1980': (79, 36, 118), '1970': (103, 249, 226)}}
        for c in self.centroids:
            c.organizeByGames(self.colorsByCol,maxGames)
            #c.drawSpiral(rgb,offset,self.colorsByCol,"centro"+str(i)+".png")
            #i += 1

        
    def createImages(self,rgb,offset,maxImgs=-1):
        i = 0
        self.colorsByCol = {10: {'1990': (207, 25, 49), '2000': (135, 82, 128), '2010': (57, 75, 79), '1980': (79, 36, 118), '1970': (103, 249, 226)}}
        for c in self.centroids:
            c.organize(self.colorsByCol,maxImgs)
            #c.drawSpiral(rgb,offset,self.colorsByCol,"centro"+str(i)+".png")
            #i += 1
    
    def createImage(self,offset,filename,dim,rgb):
        px = 0
        py = offset
        
        height = 0
        width = 0
        hmax = 0
        wmax =0
        i = 0
        for r in range(dim[0]):
            tw = 0
            th = 0
            for c in range(dim[1]):
                tw += self.centroids[i].image_width+offset
                temp = self.centroids[i].image_height+offset
                if temp > th:
                    th = temp
                if self.centroids[i].image_width>wmax:
                    wmax = self.centroids[i].image_width
                if self.centroids[i].image_height>hmax:
                    hmax = self.centroids[i].image_height
                i += 1
                
            height += th
            if tw > width:
                width = tw
        
        out = Image.new("RGB", (wmax*dim[0]+((dim[0]+1)*offset),hmax*dim[1]+((dim[1]+1)*offset)), rgb)
        i = 0
        
        for r in range(dim[0]):
            px = offset
            for c in range(dim[1]):
                out.paste(self.centroids[i].canvas,(px,py))
                px += wmax+offset
                i+=1
            py += hmax+offset
        out.save(filename)
    
    def selectGames(self,maxGames,thumb=100):
        allImages = []
        centers = []
        for c in self.centroids:
            allImages = allImages + c.images
            centers.append(c.values)
        
        a = np.array(centers)
        avgCentroids = np.mean(a,axis=0)
        print avgCentroids
        pass

        filtered = []
        for i in allImages:
            i.compare(avgCentroids)
            filtered.append(i)
        
        filtered.sort(key=lambda image: image.distance)
        
        f = []
        g = []
        for i in filtered:
            if i.goid not in g:
                f.append(i)
                g.append(i.goid)

        lim = min(maxGames,len(f))
        
        gdb = GamesDatabase()
        h = []
        arq = codecs.open('jogos.txt','w',"utf-8")
        for i in range(lim):
            g = gdb.getGameByObject(f[i].goid)
            print f[i].values
            w = g['name'].replace(u'\xe3', u' ')
            arq.write(w+"\t"+str(g['_id'])+'\n')
            c = gdb.getImageAverage(f[i].goid)

            f[i].code = "/avg_rgb/"+c
            f[i].createImage(thumb)
            h.append(f[i])
        arq.close()
        
        drawSpiral((128,128,128),h,50,'jogos.png',thumb)
        
    def _paintCols(self,size,img,tokens,offset):
        px = 0
        ws = size
        d = ImageDraw.Draw(img)
        for i in self.colorsByCol.keys():
            color = self.colorsByCol[i][tokens[i]]
            d.ellipse((px, 0, px+ws, ws), fill = color, outline =color)
            px += (ws + offset)   
        del d
        
#5795 exemplos
def main():
    ic = ImageCreator()
    
    #ic.setGenres(['Puzzle','Artgame','Compilation'])
    #ic.setGenres(['Adventure'])
    #ic.setGenres(['Action'])
    #ic.setGenres(['Strategy','Tactics','Role-Playing (RPG)','Simulation'])
    #ic.setGenres(['Puzzle','Artgame'])

    #Uso tese
    ic.initNoClasses('clusters_tese.txt','nova4_v2.csv','/Users/jrbitt/Dropbox/full2/',[10],[4,5,6,7,8,9,12])  
    
    #Uso do Weka SBGames
    #ic.initNoClasses('centroides_galloway.txt','nova3.csv','/Users/jrbitt/Dropbox/full2/',[10],##[4,5,6,7,8,9])  
    
    #ic.plot()
        
    #Usado para fazer as imagens do Galloway
    #ic.initNoClasses('centroides_galloway.txt','exemplo5.csv','/Users/jrbitt/Dropbox/full2/',[23])  
    #ic.init('centroides_shooter_25.txt','classes_shooter_25.txt','base_shooter.csv','/Users/jrbitt/gamesresearch/games/games/spiders/screens/full/',[0])
    
    #Gerar as imagens
    #ic.createImages((128,128,128),10)
    
    #Gerar imagens pra cada cluster usando a imagem media do jogo
    #ic.createImagesByGames((128,128,128),10,25)
    
    #Gerar uma imagem dos k clusters
    #ic.createAverageImageByGames(10,600)
    
    ic.selectGames(10,600)
    
    
    #ic.createImage(50,"clusters_galloway.png",(3,1),(128,128,128))
                
        
if __name__ == '__main__': main()
