#Create to Final Fantasy
#python generate_data.py .\teste FFI saida_nova.csv

from os import listdir
from PIL import Image, ImageFilter, ImageStat
import math, csv, sys
   
casas = 5

def calcularPercentual(cores):
	total = 0
	for i in cores:
		total = total + i
	for i in range(0,len(cores)):
		cores[i] = round(cores[i]/total,casas)
	return cores
		
def contarCor(image):
	rgb_table = [(0,0,0),(0,0,255),(165,42,42),(0,255,0),(128,128,128),(255,165,0),(255,192,203),(128,0,128),(255,0,0),(255,255,255),(255,255,0)]
	colors_count = [0]*11
	size = image.size
	for x in range(size[0]):
		for y in range(size[1]):
			if(len(image.getpixel((x,y)))==4):
				r,g,b,a = image.getpixel((x,y))
			else:
				r,g,b = image.getpixel((x,y))
			value = 10000
			i = -1
			for t in range(len(rgb_table)):
				v = math.sqrt(((rgb_table[t][0]-r)**2)+((rgb_table[t][1]-g)**2)+((rgb_table[t][2]-b)**2))
				if v < value:
					value = v
					i = t
			colors_count[i] += 1
	return colors_count
		
def calcularEmocional(image,s,b):
	emocao = [0]*3
	emocao[0]= round(0.69*b+0.22*s,casas)
	emocao[1]= round(-0.31*b+0.6*s,casas)
	emocao[2]= round(0.76*b+0.32*s,casas)
	return emocao
		
def calcularEntropia(image):
	rgbHistogram = image.histogram()
	channels = [0]*3
	for rgb in range(3):
		totalPixels = sum(rgbHistogram[rgb * 256 : (rgb + 1) * 256])
		ent = 0.0
		for col in range(rgb * 256, (rgb + 1) * 256):
			freq = float(rgbHistogram[col]) / totalPixels
			if freq > 0:
				ent = ent + freq * math.log(freq, 2)
		ent = -ent
		channels[rgb] = round(ent,casas)
	return channels
		
def calcularSaturacao(image):
	image = image.convert('HSV')
	stat = ImageStat.Stat(image)
	return round(stat.mean[1],casas)
	
def calcularBrilho(image):
	stat = ImageStat.Stat(image)
	if(len(stat.mean)==4):
		r,g,b,a = stat.mean
	else:
		r,g,b = stat.mean
	brightness = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
	return round(brightness,casas)

def calcularAnoPlataforma(pref):
	r = [0]*2
	if pref == 'FFI':
		r[0] = 1987
		r[1] = 'NES'
	if pref == 'FFII':
		r[0] = 1988
		r[1] = 'NES'
	if pref == 'FFIII':
		r[0] = 1990
		r[1] = 'NES'		
	if pref == 'FFIV':
		r[0] = 1991
		r[1] = 'SNES'		
	if pref == 'FFV':
		r[0] = 1992
		r[1] = 'SNES'		
	if pref == 'FFVI':
		r[0] = 1994
		r[1] = 'SNES'		
	if pref == 'FFVII':
		r[0] = 1997
		r[1] = 'PS1'		
	if pref == 'FFVIII':
		r[0] = 1999
		r[1] = 'PS1'		
	if pref == 'FFIX':
		r[0] = 2000
		r[1] = 'PS1'		
	if pref == 'FFX':
		r[0] = 2001
		r[1] = 'PS2'		
	if pref == 'FFX2':
		r[0] = 2003
		r[1] = 'PS2'		
	if pref == 'FFXII':
		r[0] = 2006
		r[1] = 'PS2'		
	if pref == 'FFXIII':
		r[0] = 2009
		r[1] = 'PS3'		
	if pref == 'FFXIII2':
		r[0] = 2011
		r[1] = 'X360'		
	if pref == 'FFXIII3':
		r[0] = 2013
		r[1] = 'PS3'		
	if pref == 'FFXV':
		r[0] = 2016
		r[1] = 'PS4'				
	return r
	
def limpar(fin,fout):
	with open(fin, "r") as f:
		lines = f.readlines()
	with open(fout, "w") as f:
		for line in lines:
			if len(line) != 1:
				f.write(line)
def main(args):
	path = args[0]
	prefixo = args[1]
	outFile = args[2]
	cabecalho = ['filename','year','platform','saturation', 'brigthness', 'entropy_r', 'entropy_g', 'entropy_b','pleasure','arousal','dominance','black','blue','brown','green','gray','orange','pink','purple','red','white','yellow']
	csvData = []
	csvData.append(cabecalho)

	lista_arqs = [arq for arq in listdir(path)]
	cont = 1
	for image_file in lista_arqs:
		print(str(cont)+"/"+str(len(lista_arqs))+": "+image_file)
		im = Image.open(path+"\\"+image_file)
		im = im.convert("RGB") 
		s = calcularSaturacao(im)
		b = calcularBrilho(im)
		e = calcularEntropia(im)
		emo = calcularEmocional(im,s,b)
		cores = contarCor(im)
		pcores = calcularPercentual(cores)
		y, plt = calcularAnoPlataforma(prefixo)
		data = [image_file,y,plt,s,b,e[0],e[1],e[2],emo[0],emo[1],emo[2]]
		for i in pcores:
			data.append(i)
		csvData.append(data)
		cont = cont + 1

	with open(outFile, 'w') as csvFile:
		writer = csv.writer(csvFile,delimiter=',')
		writer.writerows(csvData)
	csvFile.close()
	
	limpar(outFile,outFile)

#path prefix saida
if __name__ == '__main__':
	main(sys.argv[1:])