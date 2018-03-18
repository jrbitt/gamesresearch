from PIL import Image
from PIL import ImageChops
import math, operator

import numpy as np


def compareImages(im1,im2):
    h = ImageChops.difference(im1, im2).histogram()
    sq = (value*(idx**2) for idx, value in enumerate(h))
    sum_of_squares = sum(sq)
    rms = math.sqrt(sum_of_squares/float(im1.size[0] * im1.size[1]))
    return rms
    
def createImages(imgs):
    width = 0
    height = 0
    nulls = 0
    for i in imgs:
        if i!=None:
            width, height = i.size
            break
    
    rpx = []
    gpx = []
    bpx = []
    #pegar as dimensoes da imagem
    for i in imgs:
        if i!= None:
            w, h = i.size
            if w>width:
                width = w
            if h>height:
                height = h
        else:
            nulls = nulls + 1
            
    #pegar os canais
    for i in imgs:
        if i!=None:
            ri = i.resize((width,height),resample=Image.LANCZOS)
            red, green, blue = ri.split()
            rpx.append(red.getdata())
            gpx.append(green.getdata())
            bpx.append(blue.getdata())
            i.close()
            del i
    
    #criar para cada canal
    sr = [0.0]*width*height
    sg = [0.0]*width*height
    sb = [0.0]*width*height
    
    #somar os pixels por canal
    for k in range(width*height):
        for m in range(len(rpx)):
            sr[k] += rpx[m][k]
            sg[k] += gpx[m][k]
            sb[k] += bpx[m][k]
    
    #criar as tuplas atraves das medias
    tuplas = [0]*width*height
    for k in range(width*height):
        sr[k] = sr[k] / (len(imgs)-nulls)
        sg[k] = sg[k] / (len(imgs)-nulls)
        sb[k] = sb[k] / (len(imgs)-nulls)
        tuplas[k] = (int(sr[k]),int(sg[k]),int(sb[k]))
        
    im = Image.new('RGB',(width, height))
    im.putdata(tuplas)
    
    return im

def defineIndex(size):
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

def drawSpiral(rgb,images,offset,filename,thumb_size = 100):
    index = defineIndex(len(images))

    xi = yi = xf = yf = 0
    SIZE = (thumb_size*index,thumb_size*index)
    canvas = Image.new("RGB", (SIZE[0]*5,SIZE[1]*5), rgb)
    step = 1
    x = xi = SIZE[0]/2
    y = yi = SIZE[1]/2
    xf = xi +thumb_size
    yf = yi +thumb_size
    movement = [(thumb_size,0), (0,-thumb_size), (-thumb_size, 0), (0,thumb_size)]
    k = 0
    n = 1
    i = 0
    ind = 0
    while x >= 0 and y >= 0 and x <= SIZE[0] and y <= SIZE[1]:
        for j in xrange(step):	
            if ind < len(images): 
                s = images[ind]
                s.createImage(thumb_size)
                if s.img != None:
                    canvas.paste(s.img,(x,y))
                    s.delImage()
                if x<xi:
                    xi = x
                if y<yi:
                    yi = y
                if x+thumb_size>xf:
                    xf = x+thumb_size
                if y+thumb_size>yf:
                    yf = y+thumb_size
                orientation = movement[k]
                x += orientation[0]
                y += orientation[1]
                n += 1
                ind += 1
        k = (k+1)%4
        if (i%2)==1:
            step += 1
        i += 1
        if ind >= len(images):
            break
    canvas = canvas.crop((xi,yi,xf,yf))
    width, height = canvas.size
    image_width = width
    image_height = height
    canvas.save(filename)
        