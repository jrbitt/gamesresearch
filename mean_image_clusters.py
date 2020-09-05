#python mean_image_clusters.py "e:\Diablo\D1" diablo1_C1.png e:\Diablo\diablo1_clusters.csv C1 0.69
#dir onde estao as imagens, imagem de saida, arquivo de clusters, nome do cluster, valor da silhueta minimo
'''
	Diablo 1
		C1	0.687
		C2	0.692
	Diablo 2
		C1	0.692
		C2	0.690
		C3	0.663
	Diablo 3
		C1	0.678
		C2	0.675
		C3	0.691
'''

from os import listdir
from PIL import Image, ImageFilter, ImageStat
import math, csv, sys

def createMeanImage(imgs):
    width, height = imgs[0].size
    rpx = []
    gpx = []
    bpx = []
	
    #pegar as dimensoes da imagem
    for i in imgs:
        w, h = i.size
        if w>width:
            width = w
        if h>height:
            height = h
			
    #pegar os canais
    for i in imgs:
        ri = i.resize((width,height),resample=Image.LANCZOS)
        red, green, blue = ri.split()
        rpx.append(red.getdata())
        gpx.append(green.getdata())
        bpx.append(blue.getdata())
        i.close()
        del i
    print("Canais capturados")

    #criar para cada canal
    sr = [0.0]*width*height
    sg = [0.0]*width*height
    sb = [0.0]*width*height

    #somar os pixels por canal
    tp = width*height
    cont = 1
    for k in range(width*height):
        for m in range(len(rpx)):
            sr[k] += rpx[m][k]
            sg[k] += gpx[m][k]
            sb[k] += bpx[m][k]
        print(str(cont)+"/"+str(tp))
        cont = cont + 1
    print("Pixels somados")
	
    #criar as tuplas atraves das medias
    tuplas = [0]*width*height
    cont = 1
    for k in range(width*height):
        sr[k] = sr[k] / len(imgs)
        sg[k] = sg[k] / len(imgs)
        sb[k] = sb[k] / len(imgs)
        tuplas[k] = (int(sr[k]),int(sg[k]),int(sb[k]))
        print(str(cont)+"/"+str(tp))
        cont = cont + 1
	
    im = Image.new('RGB',(width, height))
    im.putdata(tuplas)
    print("Imagem criada")
    return im

def main(args):
	path = args[0]
	outFile = args[1]
	file_clusters = args[2]
	cluster = args[3]
	value_min = float(args[4])
	images = []
	lista_arqs = []
	
	with open(file_clusters, 'r') as arquivo_csv:
		leitor = csv.reader(arquivo_csv, delimiter=',')
		for coluna in leitor:
			if coluna[1] == cluster and float(coluna[2])>=value_min:
				print(coluna[2]+" "+coluna[1]+" "+coluna[0])
				lista_arqs.append(coluna[0])

	cont = 1
	for image_file in lista_arqs:
		print(str(cont)+"/"+str(len(lista_arqs))+": "+image_file)
		im = Image.open(path+"\\"+image_file)
		images.append(im)
		cont = cont + 1
		
	imout = createMeanImage(images)
	imout.save(outFile)

if __name__ == '__main__':
	main(sys.argv[1:])

	