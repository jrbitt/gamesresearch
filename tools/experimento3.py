#Calcular a imagem media

from database import GamesDatabase
import math
import sys

gdb = GamesDatabase()

def addArray(ar,other):
    for i in range(len(ar)):
        ar[i] += other[i]
    return ar

def avgArray(ar,size):
    for i in range(len(ar)):
        ar[i] = ar[i]/float(size)
    return ar

def minusPwrArray(a,b):
    c = [0.0]*len(a)
    for i in range(len(a)):
        c[i] = (a[i] -b[i])**2
    return c

def sumArray(ar):
    s = 0.0
    for i in ar:
        s+= i
    return s

def euclidian(a,b):
    vet = [0.0]*6
    vet[0] = (a['saturation']-b['saturation'])**2
    vet[1] = (a['brightness']-b['brightness'])**2
    vet[2] = (a['tamura_contrast']-b['tamura_contrast'])**2
    vet[3] = (a['arousal']-b['arousal'])**2
    vet[4] = (a['pleasure']-b['pleasure'])**2
    vet[5] = (a['dominance']-b['dominance'])**2
    
    e = minusPwrArray(a['entropy'],b['entropy'])
    #c = minusPwrArray(a['color_names'],b['color_names'])
    
    s = 0.0
    for v in vet:
        s += v
        
    s += sumArray(e)
    #s += sumArray(c)
        
    return math.sqrt(s)

def findScreen(scrCodes, ref):
    code = None
    value = sys.float_info.max
    for s in scrCodes:
        screen = gdb.getScreen(s)
        if screen != None:
            if screen.has_key('saturation'):
                e = euclidian(ref,screen)
                if e< value:
                    code = s
                    value = e
    return code,value
        
    
def createImageAverage(scrCodes):
    sat = 0
    brig = 0
    tamura = 0
    arousal = 0
    pleasure = 0
    dominance = 0
    ent = [0.0]*3
    color = [0.0]*11
    h = [0.0]*360
    st = [0.0]*100
    v = [0.0]*100
    tam = 0
    for s in scrCodes:
        screen = gdb.getScreen(s)
        if screen != None:
            if screen.has_key('saturation'):
                sat += screen['saturation']
                brig += screen['brightness']
                tamura += screen['tamura_contrast']
                arousal += screen['arousal']
                pleasure += screen['pleasure']
                dominance += screen['dominance']
                ent = addArray(ent,screen['entropy'])
                color = addArray(color,screen['color_names'])
                h = addArray(h,screen['hsv_histogram']['hue'])
                st = addArray(st,screen['hsv_histogram']['sat'])
                v = addArray(v,screen['hsv_histogram']['val'])
                tam += 1
    
    if tam>1:
        obj = {}
        obj['saturation'] = sat/float(tam)
        obj['brightness'] = brig/float(tam)
        obj['tamura_contrast'] = tamura/float(tam)
        obj['arousal'] = arousal/float(tam)
        obj['pleasure'] = pleasure/float(tam)
        obj['dominance'] = dominance/float(tam)
        obj['entropy'] = avgArray(ent,tam)
        obj['color_names'] = avgArray(color,tam)
        hsv ={}
        hsv['hue'] = avgArray(h,tam)
        hsv['sat'] = avgArray(st,tam)
        hsv['val'] = avgArray(v,tam)
        obj['hsv_histogram'] = hsv

        return obj
    else:
        return None

gcodes = gdb.getGameCodes()


gameCodes = []
print gcodes

for gc in gcodes:
    #g = gdb.getGame(gc)
    g = gdb.getGame('59389d13c63d15faf573a4b1')
    plats = g['platforms']
    screenCodes = []
    for p in plats:
        if p.has_key('screens'):
            scr = p['screens']
            for s in scr:
                if s.has_key('shots'):
                    sh = s['shots']
                    screenCodes.append(sh[0]['code'])
                    
    if len(screenCodes)>0:
        #Dado um game para a platforma n tenho os valores medios
        o = createImageAverage(screenCodes)
        if o != None:
            o['goid'] = str(gc)
            #Encontrar a screen mais semelhante a media
            scrCode, val = findScreen(screenCodes,o)
            o['near_screen'] = scrCode
            o['distance'] = val
            gdb.addImageAverage(o)

        