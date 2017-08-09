from database import GamesDatabase
import json
from bson.objectid import ObjectId
                                          
class DatasetCreator(object):
    gdb = None
    gameplays = []
    perspectives = []
    genres = []
    narratives = []
                                          
    
    def __init__(self,g):
        self.gdb = g

    def preparaDataset(self):
        cursor = self.gdb.collection.find({})
        for game in cursor:
            if game.has_key("gameplays"):
                gp = game["gameplays"]
                for sgp in gp:
                    if sgp not in self.gameplays:
                        self.gameplays.append(sgp)
            if game.has_key("perspectives"):
                per = game["perspectives"]
                for sper in per:
                    if sper not in self.perspectives:
                        self.perspectives.append(sper)
            if game.has_key("genres"):
                gn = game["genres"]
                for sgn in gn:
                    if sgn not in self.genres:
                        self.genres.append(sgn)
            if game.has_key("narratives"):
                nar = game["narratives"]
                for snar in nar:
                    if snar not in self.narratives:
                        self.narratives.append(snar)
                        
        print self.genres

    def createNarratives(self,nr):
        temp = ""
        if nr != None:
            for n in self.narratives:
                if n in nr:
                    temp += "yes,"
                else:
                    temp += "no,"
        else:
            for n in self.narratives:
                temp += "none,"
        return temp.strip()
    
    def createGenres(self,gnr):
        temp = ""
        if gnr != None:
            for g in self.genres:
                if g in gnr:
                    temp += "yes,"
                else:
                    temp += "no,"
        else:
            for g in self.genres:
                temp += "none,"
        return temp.strip()
    
    def createPerspectives(self,pers):
        temp = ""
        if pers != None:
            for p in self.perspectives:
                if p in pers:
                    temp += "yes,"
                else:
                    temp += "no,"
        else:
            for p in self.perspectives:
                temp += "none,"
        return temp.strip()
    
    def createGameplays(self,gmp):
        temp = ""
        if gmp != None:
            for g in self.gameplays:
                if g in gmp:
                    temp += "yes,"
                else:
                    temp += "no,"
        else:
            for g in self.gameplays:
                temp += "none,"
        return temp.strip()
    
    def getYear(self,y):
        if y == None:
            return "-1"
        else:
            if "20" in y or "19" in y:
                return y[len(y)-4:len(y)].strip()
            else:
                return None
    
    def getPlatform(self,name):
        a = name.split()
        if len(a) == 1:
            return a[0]
        else:
            tmp = ""
            for s in a:
                tmp += s
            return tmp.strip()
    
    def getHSV(self,line,hsv):
        for h in range(len(hsv["hue"])):
            line += str(hsv["hue"][h])+","
        for s in range(len(hsv["sat"])):
            line += str(hsv["sat"][s])+","
        for v in range(len(hsv["val"])):
            line += str(hsv["val"][v])+","
        return line.strip()
    
    def getHSVMean(self,line,hsv):
        sum_h = 0
        multi_h = 0
        sum_s = 0
        multi_s = 0
        sum_v = 0
        multi_v = 0
        for h in range(len(hsv["hue"])):
            sum_h += hsv["hue"][h]
            multi_h += (h*hsv["hue"][h])
        for s in range(len(hsv["sat"])):
            sum_s += hsv["sat"][s]
            multi_s += (s*hsv["sat"][s])
        for v in range(len(hsv["val"])):
            sum_v += hsv["val"][v]
            multi_v += (v*hsv["val"][v])
        
        mh = multi_h/float(sum_h)
        ms = multi_s/float(sum_s)
        mv = multi_v/float(sum_v)
        
        line += "{:.5f}".format(mh)+","+"{:.5f}".format(ms)+","+"{:.5f}".format(mv)+","
        return line.strip()
    
    def getCells(self,line,cells):
        if cells != None:
            for c in range(36):
                if cells[c] == False:
                    line += "0,"
                else:
                    line += "1,"
        else:
            for c in range(36):
                line += "none,"
        return line.strip()
    
    def getColorNames(self,line,cn):
        for c in cn:
            line += str(c)+","
        return line.strip()
    
    def getColorProps(self,line,cn):
        s = 0
        temp = [0]*len(cn)
        for c in cn:
            s += c
        i = 0
        for c in cn:
            temp[i] = c/float(s)
            i += 1
        for t in range(len(temp)):
            line += "{:.5f}".format(temp[t])+","            
        return line.strip()
    
    def getEntropy(self,line,etr):
        for e in etr:
            line += "{:.5f}".format(e)+","
        return line.strip()
    
    def getEdges(self,line,edges):
        for e in edges:
            line += str(e)+","
        return line.strip()
    
    def getHeader(self, params,filterGenre=None):
        names = ['black', 'blue', 'brown', 'green', 'gray', 'orange', 'pink', 'purple', 'red', 'white', 'yellow']
        h = "goid,"
        if params["code"] == "true": h += "code,"
        if params["year"] == "true": h += "year,"
        if params["platform"] == "true": h+= "platform,"
        if filterGenre == None:
            if params["gameplay"] == "true":
                for g in self.gameplays:
                    h += g.encode('ascii', 'ignore')+","
            if params["perspectives"] == "true":
                for p in self.perspectives:
                    h += p.encode('ascii', 'ignore')+","
            if params["genres"] == "true":
                for gr in self.genres:
                    h += gr.encode('ascii', 'ignore')+","
            if params["narratives"] == "true":
                for n in self.narratives:
                    h += n.encode('ascii', 'ignore')+","
        
        if params["type"] == "true": h+= "type,"
        if params["brightness"] == "true": h+= "brightness,"
        if params["saturation"] == "true": h+= "saturation,"
        if params["tamura_contrast"] == "true": h+= "tamura_contrast,"
        if params["arousal"] == "true": h+= "arousal,"
        if params["pleasure"] == "true": h+= "pleasure,"
        if params["dominance"] == "true": h+= "dominance,"

        if params["hsv_histogram"] == "true":
            for hue in range(360):
                h += "hue"+str(hue)+","
            for sat in range(100):
                h += "sat"+str(sat)+","
            for val in range(100):
                h += "val"+str(val)+","
        
        if params["hsv_mean"] == "true":
                h += "hue_m,sat_m,val_m,"
                
        if params["cells"] == "true":
            for c in range(36):
                h += "cell"+str(c)+","
        if params["color_names"] == "true":
            for cn in names:
                h += cn+","
        if params["color_prop"] == "true":
            for cn in names:
                h += cn+","
        if params["entropy"] == "true":
            h+= "entropy_r,"
            h+= "entropy_g,"
            h+= "entropy_b,"
        if params["edges_vert"] == "true":
            for e in range(100):
                h+= "edges_vert"+str(e)+","
        if params["edges_horz"] == "true":
            for e in range(100):
                h+= "edges_horz"+str(e)+","
        h += "\n"
        return h

    def getOtherYear(self,year):
        tks = year.split(',')
        if len(tks) == 2:
            return tks[1][1:]
        else:
            return year
    
    def countFeatures(self,data,filterGenre=None):
        s = 0
        if data["code"] == "true": s+=1
        if data["year"] == "true": s+=1
        if data["platform"] == "true": s+=1
        if filterGenre == None:
            if data["gameplay"] == "true": s+=len(self.gameplays)
            if data["perspectives"] == "true": s+=len(self.perspectives)
            if data["genres"] == "true": s+=len(self.genres)
            if data["narratives"] == "true": s+=len(self.narratives)
        if data["type"] == "true": s+=1
        if data["brightness"] == "true": s+=1
        if data["saturation"] == "true": s+=1
        if data["tamura_contrast"] == "true": s+=1
        if data["arousal"] == "true": s+=1
        if data["pleasure"] == "true": s+=1
        if data["dominance"] == "true": s+=1
        if data["hsv_histogram"] == "true": s+=560
        if data["cells"] == "true": s+=36
        if data["color_names"] == "true": s+=10
        if data["entropy"] == "true": s+=3
        if data["edges_vert"] == "true": s+=100
        if data["edges_horz"] == "true": s+=100
        if data["hsv_mean"] == "true": s+=3
        if data["color_prop"] == "true": s+=10    
        return s
    
    def includeShots(self):
        #goid code url title
        arq = open('saida.txt', 'r')
        for line in arq:
            tokens = line.split(";")
            if len(tokens[0])==24 and tokens[0][0]!='(':
                print tokens[0]
                game = self.gdb.getGameByObject(tokens[0])
                plats = game['platforms']
                for p in plats:
                    if p.has_key('screens'):
                        scr = p['screens']
                        for s in scr:
                            t = tokens[3][:-1]
                            t = t.split(':')[1]
                            t = t[1:]
                            if t == s['title']:
                                v = [{'code':tokens[1], 'image_urls':[tokens[2]]}]
                                s['shots'] = v
                                self.gdb.updateGame(tokens[0],game)
        arq.close()
    
    def createDataset(self,params,filename,filterGenre=None, goids=None):
        codesGames = []
        if goids == None:
            codesGames = self.gdb.getGameCodes()
        else:
            for i in goids:
                codesGames.append(ObjectId(i))
                
        data = None
        with open(params) as data_file:    
            data = json.load(data_file)
            
        samples = 0
        arq = open(filename, 'w')
        line = self.getHeader(data,filterGenre)
        arq.write(line)
        
        gamesShot = []
        gamesId = []
        platsName = []
        platsYear = []
        for codeg in codesGames:
            game = self.gdb.getGameByObject(codeg)
            plats = game['platforms']
            for p in plats:
                if p.has_key('screens'):
                    scr = p['screens']
                    for s in scr:
                        if s.has_key('shots'):
                            sh = s['shots']
                            gamesShot.append(sh[0]['code'])
                            gamesId.append(codeg)
                            platsName.append(p['name'])
                            if p.has_key("release"):
                                platsYear.append(p["release"])
                            else:
                                platsYear.append(None)
                
        i = 0
        for sh in gamesShot:
            s = self.gdb.getScreen(sh)
            g = self.gdb.getGame(gamesId[i])
            line = ""
            gplay = ""
            pers = ""
            gnr = ""
            nrt = ""
            plat = g["platforms"]    
            year = self.getYear(g["release"])

            if filterGenre == None:
                if g.has_key("gameplays"):
                    gplay += self.createGameplays(g["gameplays"])
                else:
                    gplay += self.createGameplays(None)

                if g.has_key("perspectives"):
                    pers += self.createPerspectives(g["perspectives"])
                else:
                    pers += self.createPerspectives(None)

                if g.has_key("genres"):
                    gnr += self.createGenres(g["genres"])
                else:
                    gnr += self.createGenres(None)

                if g.has_key("narratives"):
                    nrt += self.createNarratives(g["narratives"])
                else:
                    nrt += self.createNarratives(None)
                    
            if s != None:
                line += str(gamesId[i])+","
                if data["code"] == "true": line += s["code"]+","
                if platsYear[i] != None:
                    y = self.getOtherYear(platsYear[i])
                    if y.isdigit():
                        if data["year"] == "true":line += y+","
                    else:
                        if data["year"] == "true":line += str(1900)+","
                else:
                    if data["year"] == "true":line += str(1900)+","
                
                if data["platform"] == "true":line += self.getPlatform(platsName[i])+","
                if data["gameplay"] == "true":line += gplay
                if data["perspectives"] == "true":line += pers
                if data["genres"] == "true":line += gnr
                if data["narratives"] == "true":line += nrt
                if data["type"] == "true":line += s["type"]+","
                if s.has_key("brightness"):
                    if data["brightness"] == "true":line +="{:.5f}".format(s["brightness"])+","
                    if data["saturation"] == "true":line += "{:.5f}".format(s["saturation"])+","
                    if data["tamura_contrast"] == "true":line +=    "{:.5f}".format(s["tamura_contrast"])+","
                    #if data["arousal"] == "true":line += str(s["arousal"])+","
                    #if data["pleasure"] == "true":line += str(s["pleasure"])+","
                    #if data["dominance"] == "true":line += str(s["dominance"])+","
                    if data["arousal"] == "true":line += "{:.5f}".format(s["arousal"])+","
                    if data["pleasure"] == "true":line += "{:.5f}".format(s["pleasure"])+","
                    if data["dominance"] == "true":line += "{:.5f}".format(s["dominance"])+","
                    if data["hsv_histogram"] == "true":line = self.getHSV(line,s["hsv_histogram"])
                    if data["hsv_mean"] == "true":line = self.getHSVMean(line,s["hsv_histogram"])
                    if data["cells"] == "true":
                        if s.has_key("cells"):
                            line = self.getCells(line,s["cells"])
                        else:
                            line = self.getCells(line,None)
                    if data["color_names"] == "true":line = self.getColorNames(line,s["color_names"])
                    if data["color_prop"] == "true":line = self.getColorProps(line,s["color_names"])
                    if data["entropy"] == "true":line = self.getEntropy(line,s["entropy"])
                    if data["edges_vert"] == "true":line = self.getEdges(line,s["edges_vert"])
                    if data["edges_horz"] == "true":line = self.getEdges(line,s["edges_horz"])
                    line = line[:-1]
                    line += "\n"
                    samples += 1
                    arq.write(line)
                    line = ""
                    print samples
                    i+=1
                
    def foo(self):
        codesGames = self.gdb.getGameCodes()
        
        gamesShot = []
        for codeg in codesGames:
            game = self.gdb.getGame(codeg)
            plats = game['platforms']
            for p in plats:
                if p.has_key('screens'):
                    scr = p['screens']
                    for s in scr:
                        if s.has_key('shots'):
                            sh = s['shots']
                            gamesShot.append(sh[0]['code'])
        print len(gamesShot)
        
    def recoverGamesNoScreens(self):
        codes = self.gdb.getScreenCodes()
        codesGames = self.gdb.getGameCodes()
        
        gamesNoShot = []
        urls = []
        arq = open('sem_shots', 'w')
        for codeg in codesGames:
            game = self.gdb.getGame(codeg)
            plats = game['platforms']
            for p in plats:
                if p.has_key('screens'):
                    scr = p['screens']
                    for s in scr:
                        if not s.has_key('shots'):
                            line = str(codeg) + " " +s['url'] +'\n'
                            arq.write(line)
        arq.close()
        
        print len(gamesNoShot)
        print len(urls)
        #for c in codes:
        #    scr = self.gdb.getScreen(c)
        #    g = self.gdb.getGameByImage(c)
        #    print g['name']
    
    
def main():
    gdb = GamesDatabase()
    
    dsc = DatasetCreator(gdb)
    
    dsc.preparaDataset()
    
    #Inclui os shots na base
    #dsc.includeShots()
    
    #Usado para recuperar os shots dos games que ficaram sem
    #dsc.recoverGamesNoScreens()
    
    dieg_maq = ["594c25a7b80738c53336e777","593efd09b80738c53336e776","593efca1b80738c53336e775"]
    nao_dieg_op = ["594c26a9b80738c53336e778","594c2f4db80738c53336e77f","594c284eb80738c53336e77a","594c2f0eb80738c53336e77e"]
    dieg_op = ["594c2761b80738c53336e779","594c287bb80738c53336e77b","594c289db80738c53336e77c"]
    nao_dieg_maq = ["594c2ec7b80738c53336e77d","594d77a3ed025f8dcdad2275","594d5de5b80738c53336e7ff"]
    
    #dsc.createDataset('dataset_exp3.json','base_dieg_maq.csv',None,dieg_maq)
    #dsc.createDataset('dataset_exp3.json','base_nao_dieg_op.csv',None,nao_dieg_op)
    #dsc.createDataset('dataset_exp3.json','base_dieg_op.csv',None,dieg_op)
    #dsc.createDataset('dataset_exp3.json','base_nao_dieg_maq.csv',None,nao_dieg_maq)

    
    #Oficial
    dsc.createDataset('dataset_exp3.json','base_oficial_final.csv')
    
    #dsc.createDataset('dataset_exp3.json','base_oficial_final.csv')
    
    #dsc.createDataGui()


if __name__ == '__main__': main()
