import pygame
from pygame.locals import *
from sklearn.externals import joblib
from sklearn import tree


from PIL import Image, ImageFilter, ImageStat
import numpy as np

import colorsys, math,sys,getopt

from tamura import Tamura
from database import GamesDatabase

class HSVHistogram(object):
    h = [0]*360
    s = [0]*100
    v = [0]*100
    
    def create(self,image):
        size = image.size
        for col in range(0,size[0]):
            for lin in range(0,size[1]):
                px = image.getpixel((col,lin))
                h,s,v = colorsys.rgb_to_hsv(px[0]/255.,px[1]/255.,px[2]/255.)
                self.h[int(h*360)-1] += 1
                self.s[int(s*100)-1] += 1
                self.v[int(v*100)-1] += 1
    
class FeatureExtractor(object):

    def extract(self,image,features):
        pass

class TamuraExtractor(FeatureExtractor):
    
    def extract(self,image,features):
        t = Tamura(image,2,2)
        #d = {}
        #d["coarseness"] = t.coarseness()
        #d["contrast"] = t.contrast()
        #d["directionality"] = t.directionality()
        features["tamura_contrast"] = t.contrast()
        
class ColorNamesExtractor(FeatureExtractor):

    def extract(self,image,features):
        rgb_table = [(0,0,0),(0,0,255),(165,42,42),(0,255,0),(128,128,128),(255,165,0),(255,192,203),(128,0,128),(255,0,0),(255,255,255),(255,255,0)]
        colors_count = [0]*11
        size = image.size
        for x in range(size[0]):
            for y in range(size[1]):
                r,g,b = image.getpixel((x,y))
                value = 10000
                i = -1
                for t in range(len(rgb_table)):
                    v = math.sqrt(((rgb_table[t][0]-r)**2)+((rgb_table[t][1]-g)**2)+((rgb_table[t][2]-b)**2))
                    if v < value:
                        value = v
                        i = t
                colors_count[i] += 1
        features["color_names"] = colors_count
    
class EntropyExtractor(FeatureExtractor):
    
    def extract(self,image,features):
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
            channels[rgb] = ent
        features["entropy"] = channels
    
class EmotionalExtractor(FeatureExtractor):
    
    def extract(self,image,features):
        s = features["saturation"]
        y = features["brightness"]
        features["pleasure"]= 0.69*y+0.22*s
        features["arousal"]= -0.31*y+0.6*s
        features["dominance"]= 0.76*y+0.32*s
    
class SaturationExtractor(FeatureExtractor):
    
    def extract(self,image,features):
        image = image.convert('HSV')
        stat = ImageStat.Stat(image)
        features["saturation"] = stat.mean[1]
        
class BrightnessExtractor(FeatureExtractor):
    
    def extract(self,image,features):
        stat = ImageStat.Stat(image)
        r,g,b = stat.mean
        brightness = math.sqrt(0.241*(r**2) + 0.691*(g**2) + 0.068*(b**2))
        features["brightness"] = brightness
        
        
class HSVExtractor(FeatureExtractor):
    
    def extract(self,image,features):
        hist = HSVHistogram()
        hist.create(image)
        
        d = {}
        d["hue"] = hist.h
        d["sat"] = hist.s
        d["val"] = hist.v
        
        features["hsv_histogram"] = d
        
class EdgesExtractor(FeatureExtractor):
    sampling = 100
    
    def __init__(self,s=100):
        self.sampling = s
    
    def extract(self,image, features):
        image = image.filter(ImageFilter.FIND_EDGES)
        image = image.convert('L')

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
        image_horz = image_horz.resize((1,self.sampling),Image.LANCZOS)
        
        image_vert = Image.fromarray(vert, 'L')
        image_vert =image_vert.resize((1,self.sampling),Image.LANCZOS)        

        out_horz = list(image_horz.getdata())
        features["edges_horz"] = np.array(out_horz).tolist()
        out_vert = list(image_vert.getdata())
        features["edges_vert"] = np.array(out_vert).tolist()

class ImageClassifierGui(object):
    screen = None
    myimage = None
    background = None
    current = 0
    grid = False
    load = False
    gdb = None
    tw = 0
    th =0
    cells = []
    extractors = []
    cell = 6
    
    def featuresToLine(self,features):
        line = ""
        for f in features.keys():
            if f != "gui" and f != "north" and f != "south" and f != "west" and f != "east" and f != "pos":
                if isinstance(features[f],list):
                    for t in features[f]:
                        line += str(t)+"," 
                else:
                    line += str(features[f])+","
                    
        line += str(features["north"])+","
        line += str(features["south"])+","
        line += str(features["west"])+","
        line += str(features["east"])+","
        line += str(features["pos"])+","
        if features["gui"] == 1:
            line += str("1,0").encode('ascii', 'ignore')
        else:
            line += str("0,1").encode('ascii', 'ignore')
        return line+"\n"
    
    def featuresToHeader(self,features):
        line = ""
        for f in features.keys():
            if f != "gui" and f != "north" and f != "south" and f != "west" and f != "east" and f != "pos":
                if isinstance(features[f],list):
                    suf = ""
                    if f == "color_names": suf = "color"
                    if f == "edges_horz": suf = "ehorz"
                    if f == "edges_vert": suf = "evert"
                    for t in range(len(features[f])):
                        line += suf+str(t)+"," 
                else:
                    line += str(f)+","
        line += "north,"
        line += "south,"
        line += "weast,"
        line += "east,"
        line += "pos,"
        line += "gui_yes,gui_no"
        print line
        return line+"\n"
    
    def createDataGui(self,db,filename):
        print filename
        self.gdb = db
        pygame.init()

        codes = self.gdb.getScreenCodes()
        arq = open(filename, 'w')
        samples = 0
        first = True
        for c in codes: 
            scr = self.gdb.getScreen(c)
            if scr["type"] == "ingame":
                tw = scr["tile_width"]
                th = scr["tile_height"]
                img = None
                try:
                    img = image = Image.open(self.gdb.path+c+".jpg")
                except IOError:
                    img = None
                if img != None:
                    print "Sample"+str(samples)
                    size = img.size
                    cells = scr["cells"]
                    i = 0
                    for px in xrange(0,size[0],tw):
                        for py in xrange(0,size[1],th):
                            if i<36:
                                cropped = img.crop((px, py, px+tw, py+th))
                                features = {}
                                features["pos"] = i
                                for e in self.extractors:
                                    e.extract(cropped,features)
                                if cells[i] == True:
                                    features["gui"] = 1
                                else:
                                    features["gui"] = 0
                                
                                if(i-6)<0:
                                    features["north"] = -1
                                else:
                                    features["north"] = int(cells[i-6])

                                if(i+6)>35:
                                    features["south"] = -1
                                else:
                                    features["south"] = int(cells[i+6])

                                if(i-1)<0:
                                    features["west"] = -1
                                else:
                                    features["west"] = int(cells[i-1])

                                if(i+1)>35:
                                    features["east"] = -1
                                else:
                                    features["east"] = int(cells[i+1])

                                i += 1
                                if first:
                                    arq.write(self.featuresToHeader(features))
                                    first = False
                                line = self.featuresToLine(features)
                                arq.write(line)
                                samples += 1
        arq.close()
        print "Samples: "+str(samples)
        
    def getFeatures(self,filename):
        if len(self.extractors) == 0:
            return None
        else:
            temp = {}
            try:
                image = Image.open(filename)
                for e in self.extractors:
                    e.extract(image,temp)
                return temp
            except IOError:
                print "Error:"+filename
                return None
            
    def addExtractor(self,e):
        self.extractors.append(e)
        
    def markCell(self,pos):
        col = pos[0]/self.tw
        row = pos[1]/self.th
        self.cells[row*6+col] = not self.cells[row*6+col]

    def drawCells(self):
        for i in range(0,36):
            if self.cells[i] == True:
                col = i % self.cell
                row = (i-col)/self.cell
                pygame.draw.rect(self.background, (255,255,255), (col*self.tw,row*self.th,self.tw,self.th), 0)
            
    def drawGrid(self):
        self.drawCells()
        size = self.background.get_size()
        self.tw = size[0]/self.cell
        self.th = size[1]/self.cell
        for j in range(1,self.cell):
            pygame.draw.lines(self.background, (255,0,0), False, [(j*self.tw,0), (j*self.tw,size[1]-1)], 1)
        for i in range(1,self.cell):
            pygame.draw.lines(self.background, (255,0,0), False, [(0,i*self.th), (size[0]-1,i*self.th)], 1)    

        
    def init(self,g,auto=False):
        self.gdb = g
        self.cells = [False]*36
        
        # Initialise screen
        if not auto:
            pygame.init()
            self.screen = pygame.display.set_mode((640, 480))
            pygame.display.set_caption('Game Image Classifier')

            if len(self.gdb.screens) >0:
                self.myimage = pygame.image.load(self.gdb.screens[self.current].filename)
                #if self.myimage.get_size()[0]>1900:
                    #self.myimage = self.myimage.resize((self.screen.get_size()))
            #else:
                #pass
                #self.myimage = pygame.image.create((200,200))
            self.screen = pygame.display.set_mode(self.myimage.get_rect().size)

            # Fill background
            self.background = pygame.Surface(self.screen.get_size())
            self.background = self.background.convert()
            self.background.fill((250, 250, 250))
            self.background.blit(self.myimage, (0,0))
            size = self.background.get_size()
            self.tw = size[0]/self.cell
            self.th = size[1]/self.cell

            self.screen.blit(self.background,(0,0))
            pygame.display.flip()
    
    def autoClassify(self):
        i = 0
        for px in xrange(0,size[0],self.tw):
            for py in xrange(0,size[1],self.th):
                if i<36:
                    cropped = img.crop((px, py, px+tw, py+th))
                    features = {}
                    features["pos"] = i
                    for e in self.extractors:
                        e.extract(cropped,features)
                    if cells[i] == True:
                        features["gui"] = 1
                    else:
                        features["gui"] = 0

                    if(i-6)<0:
                        features["north"] = -1
                    else:
                        features["north"] = int(cells[i-6])

                    if(i+6)>35:
                        features["south"] = -1
                    else:
                        features["south"] = int(cells[i+6])

                    if(i-1)<0:
                        features["west"] = -1
                    else:
                        features["west"] = int(cells[i-1])

                    if(i+1)>35:
                        features["east"] = -1
                    else:
                        features["east"] = int(cells[i+1])

                    i += 1
                    if first:
                        arq.write(self.featuresToHeader(features))
                        first = False
                    line = self.featuresToLine(features)
    
    def runBatch(self):
        self.current = 0
        count = 0
        tot =len(self.gdb.screens)
        print "Total:"+str(tot)
        for s in self.gdb.screens:
            print str(count+1)+"/"+str(tot)
            ft = self.getFeatures(self.gdb.screens[self.current].filename)
            self.gdb.setType('auto',self.gdb.screens[self.current].code,ft)
            count += 1
            self.current += 1            

    def run(self):
        # Event loop
        while 1:
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONUP:
                    pos = pygame.mouse.get_pos()
                    self.markCell(pos)
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        return
                    elif event.key == K_h:
                        self.cells = [False]*36
                        self.grid = not self.grid
                        self.autoClassify()
                    elif event.key == K_g:
                        self.cells = [False]*36
                        self.grid = not self.grid
                    elif event.key == K_1:
                        self.gdb.setType('offscreen',self.gdb.screens[self.current].code,self.getFeatures(self.gdb.screens[self.current].filename))
                        self.load = True
                    elif event.key == K_2:          
                        self.gdb.setType('cutscene',self.gdb.screens[self.current].code,self.getFeatures(self.gdb.screens[self.current].filename))
                        self.load = True
                    elif event.key == K_3:
                        self.gdb.setType('ingame',self.gdb.screens[self.current].code,self.getFeatures(self.gdb.screens[self.current].filename),self.cells,self.tw, self.th)
                        self.cells = [False]*36
                        self.grid = False
                        self.load = True
                    elif event.key == K_SPACE:
                        self.load = True


            if self.load:
                self.current = self.current + 1
                if self.current < len(self.gdb.screens):
                    self.myimage = pygame.image.load(self.gdb.screens[self.current].filename) 
                    size = self.background.get_size()
                    self.tw = size[0]/self.cell
                    self.th = size[1]/self.cell
        
                    self.screen = pygame.display.set_mode(self.myimage.get_rect().size)
                    self.background = pygame.Surface(self.screen.get_size())
                    self.background = self.background.convert()
                    self.background.fill((250, 250, 250))
                    self.load = False

            self.background.blit(self.myimage, (0,0))
            if self.grid:
                self.drawGrid()
            
            self.screen.blit(self.background,(0,0))
            pygame.display.flip()

def main(argv):
    gui = ImageClassifierGui()
    gdb = GamesDatabase()
    
    path = '/Users/jrbitt/Dropbox/full2/'
    #gdb.init('/Users/jrbitt/gamesresearch/games/games/spiders/screens/full/',True)
    

    
    try:
        opts, args = getopt.getopt(argv,"hci")
    except getopt.GetoptError:
        print "classify_gui.py -c | -i"
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print 'classify_gui.py -c |auto| |OID do game| || -i ==> -c is classifier (interactive ou auto) and -i create image dataset'
            sys.exit()
        elif opt in ("-c"):
            gdb.init(path,True,None)
            if args[0] == "auto":
                gui.init(gdb,True)
            gui.addExtractor(TamuraExtractor())
            gui.addExtractor(ColorNamesExtractor())    
            gui.addExtractor(BrightnessExtractor())
            gui.addExtractor(SaturationExtractor())
            gui.addExtractor(EmotionalExtractor())
            #gui.addExtractor(EdgesExtractor())
            gui.addExtractor(HSVExtractor())
            gui.addExtractor(EntropyExtractor())
            if args[0] == "auto":
                gui.runBatch()
            else:
                gui.run()
            
        elif opt in ("-i"):
            gdb.init(path,True)
            #gui.addExtractor(TamuraExtractor())
            gui.addExtractor(ColorNamesExtractor())    
            gui.addExtractor(BrightnessExtractor())
            gui.addExtractor(SaturationExtractor())
            gui.addExtractor(EdgesExtractor())
            gui.addExtractor(EntropyExtractor())
            gui.createDataGui(gdb,args[0])
            

    # Display some text
    #font = pygame.font.Font(None, 36)
    #text = font.render("Hello There", 1, (10, 10, 10))
    #textpos = text.get_rect()

    #coarseness, contrast, directionality
    #
    
if __name__ == '__main__': 
    main(sys.argv[1:])


            
# Depois do dia 24/6/2017 as 15:04 nao tem mais edges detector
       