#python painel.py ./FFI saida.png

from os import listdir
from PIL import Image, ImageFilter, ImageStat
import math, csv, sys
   
def main(args):
	path = args[0]
	lista_arqs = [arq for arq in listdir(path)]
	total_arq = len(lista_arqs)
	razao_x = math.ceil(math.sqrt(total_arq))
	razao_y = math.ceil(total_arq/razao_x)-1
	im = Image.open(path+"\\"+lista_arqs[0])
	dimensao_frames = im.size
	im.close()
	#Cria o canvas
	canvas = Image.new('RGB', (dimensao_frames[0]*razao_x, dimensao_frames[1]*razao_y))
	x =0
	y =0
	for img in lista_arqs:
		print(path+"\\"+img)
		frame = Image.open(path+"\\"+img)
		canvas.paste(frame, (x,y))
		frame.close()
		x = x + frame.size[0]
		if x > canvas.size[0]:
			x = 0
			y = y + frame.size[1]
	canvas.save(args[1])
	
		
if __name__ == '__main__':
	main(sys.argv[1:])