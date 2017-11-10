from PIL import Image
import numpy as np

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