#Combinar varias imagens em uma unica
#https://stackoverflow.com/questions/14211340/automatically-cropping-an-image-with-python-pil
#https://stackoverflow.com/questions/1616767/pil-best-way-to-replace-color

from PIL import Image
from PIL import ImageDraw
import numpy as np
import random


Image.MAX_IMAGE_PIXELS = 1000000000  
porX = False

name = 'nao_dieg_maq_avg'
n = 49
orig_color = (50,50,50,0)    
replacement_color = (0,0,0,0) 

class ponto:
    larg = 0
    alt = 0
    x = 0
    y = 0
    code = -1
    
    def __lt__(self, other):
        if porX:
            return self.x < other.x
        else:
            return self.y < other.y
        
    def __str__(self):
        return str(self.x)+','+str(self.y)+','+str(self.larg)+','+str(self.alt)
    
#Faz um blend de todas as imagens com sobreposicao
def mode01():
    layers = []
    for i in range(n):
        print 'open',i
        layer = Image.open('./'+name+'/'+str(i)+".png")
        layers.append(layer)

    final2 = Image.new("RGBA", layers[0].size,(50,50,50,255))

    for i in range(n):
        print 'create',i
        final2 = Image.alpha_composite(final2, layers[i])

    final2.save(name+'.png')
    
def crop(image,orig_color,replacement_color):
    data = np.array(image)
    try:
        data[(data == orig_color).all(axis = -1)] = replacement_color
    except AttributeError:
        print 'nothing'
    
    image_data_bw = data.max(axis=2)
    non_empty_columns = np.where(data.max(axis=0)>0)[0]
    non_empty_rows = np.where(data.max(axis=1)>0)[0]
    cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

    image_data_new = data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1 , :]

    new_image = Image.fromarray(image_data_new)
    
    return new_image,cropBox

  

def mode02():
    for i in range(n):
        print 'open',i
        filename = './'+name+'/'+str(i)+".png"
        try:
            image = Image.open(filename)
            image.load()
            new_image,posBox = crop(image,orig_color,replacement_color)
            box = new_image.getbbox()
            new_image.save('./'+name+'/'+str(i)+"_cropped.png")
        except IOError:
            print i,"not found"
        
def mode03():
    c = []
    lin = 10
    col = 5
    cont = 0
    maxW = -10000
    maxH = -10000
    for i in range(col):
        for j in range(lin):
            try:
                #filename = './'+name+'/'+str(cont)+".png"
                filename = './'+name+'/'+str(cont)+"_cropped.png"
                image = Image.open(filename)
                image.load()
                #new_image,posBox = crop(image,orig_color,replacement_color)
                box = image.getbbox()

                p = ponto()
                p.x = box[0]
                p.y = box[1]
                p.larg = box[2]
                p.alt = box[3]
                p.code = cont
                c.append(p)

                print p
                if p.larg>maxW:
                    maxW = p.larg
                if p.alt>maxH:
                    maxH = p.alt
            except IOError:
                print "error"
                p = ponto()
                p.x = -1
                p.y = -1
                p.larg = -1
                p.alt = -1
                p.code = cont
                c.append(p)
            cont += 1
    
    #c.sort()
    porX = True

    
    a = []
    cont = 0
    for i in range(lin):
        b = []
        for j in range(col):
            try:
                b.append(c[cont])
                cont += 1
            except IndexError:
                print "index error"
        #b.sort()
        a.append(b)

    maxW += 100
    maxH += 100
    final = Image.new("RGBA", (maxW*col,maxH*lin),(50,50,50,255))
    px = 0
    py = 0

    for i in range(lin):
        px = 0
        for j in range(col):
            try:
                cont = a[i][j].code
                try:
                    filename = './'+name+'/'+str(cont)+"_cropped.png"
                    print filename
                    image = Image.open(filename)
                    image = image.convert('RGBA')
                    box = image.getbbox()
                    offX = (maxW-box[2])/2
                    offY = (maxH-box[3])/2

                    final.paste(image,(px+offX,py+offY),image)
                except IOError:
                    print "error"
            except IndexError:
                print "index error"
            px += maxW
        py += maxH
    
    final.save(name+".png")

mode02()
mode03()
#mode01()