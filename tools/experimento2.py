#Verificar o tempo de lancamento dos jogos

from database import GamesDatabase

def getYear2(y):
    if y == None:
        return "-1"
    else:
        if "20" in y or "19" in y:
            return y[len(y)-4:len(y)].strip()
        else:
            return None
            
def getYear(year):
    tks = year.split(',')
    if len(tks) == 2:
        return tks[1][1:]
    else:
        return year

gdb = GamesDatabase()

gcodes = gdb.getGameCodes()

numPlats = []
totPlats = []
yearGame = []
for gc in gcodes:
    g = gdb.getGame(gc)
    if g.has_key('release'):
        if g['release'] != None:
            yearGame.append(getYear2(g['release']))
        else:
            yearGame.append(None)
    else:
        yearGame.append(g['release'])
    plats = g['platforms']
    yearPlats = []
    totPlats.append(len(plats))
    for p in plats:
        if p.has_key('release'):
            y = getYear(p['release'])
            if y.isdigit():
                yearPlats.append(y)    
            else:
                yearPlats.append(None)
        else:
            yearPlats.append(None)
        if len(yearPlats)==1 and yearPlats[0] == None:
            if g.has_key('release') and g['release']!=None:
                if g['release'].isdigit():
                    yearPlats = [g['release']]
                else:
                    yearPlats = [getYear(g['release'])]
            else:
                yearPlats = [None]
    numPlats.append(yearPlats)

print len(totPlats)
print len(numPlats)
print len(gcodes)

arq = open("jogos_plataformas.csv", 'w')
i = 0
for gc in gcodes:
    mn = min(numPlats[i])
    mx = max(numPlats[i])
    if mx==None or mn == None:
        arq.write(str(gc)+" "+str(totPlats[i])+" "+str(mn)+" "+str(mx)+" "+str(None)+" "+str(yearGame[i]))
    else:
        df = int(mx)-int(mn)
        arq.write(str(gc)+" "+str(totPlats[i])+" "+str(mn)+" "+str(mx)+" "+str(df)+" "+str(yearGame[i]))
    arq.write('\n')
    i += 1
arq.close