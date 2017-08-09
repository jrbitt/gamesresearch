import sys
from PIL import Image
from PIL import ImageFilter
import numpy as np

def main():
    filenameIn=sys.argv[1]
    filenameOut=sys.argv[2]
    sampling= sys.argv[3]
    outName = filenameOut.split('.')
    
    image = Image.open(filenameIn)
    image = image.filter(ImageFilter.FIND_EDGES)
    image = image.convert('L')
    image.save(filenameOut)
    
    size = image.size
    vert = np.zeros((size[1], 1), dtype=np.uint8)
    for lin in range(0,size[1]):
        soma = 0
        for col in range(0,size[0]):
            soma = soma + image.getpixel((col,lin))
        vert[lin]= soma / size[0]
            
    horz = np.zeros((size[0], 1), dtype=np.uint8)
    for col in range(0,size[0]):
        soma = 0
        for lin in range(0,size[1]):
            soma = soma + image.getpixel((col,lin))
        horz[col]= soma / size[1]

    image_horz = Image.fromarray(horz, 'L')
    image_horz = image_horz.resize((1,int(100)),Image.LANCZOS)
    image_horz.save(outName[0]+"_image_horz.png")
        
    image_vert = Image.fromarray(vert, 'L')
    image_vert =image_vert.resize((int(100),1),Image.LANCZOS)   
    image_vert.save(outName[0]+"_image_vert.png")
    for i in range(0,100):
        print image_horz.getpixel((0,i))


if __name__ == '__main__': main()