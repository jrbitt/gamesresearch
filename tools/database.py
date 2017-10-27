
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
from datetime import datetime

class ShotData(object):
    filename = ""
    oid = ""
    code = ""
    
class GamesDatabase(object):
    """Game data collection using MongoDB

    Class used to connect MongoDB and running some queries in database.

    Attributes:
        client: relationship with MongoClient created by driver
        db: default database
        collection: link to games collection in database
        path: where is the images files

    """
    connection = None
    db = None
    collection = None
    path = ""
    screens = []
    
    def __init__(self):
        self.connection = pymongo.MongoClient('localhost',27017)
        self.db = self.connection['gamesresearch']
        self.collection = self.db['games']
        random.seed(datetime.now())
            
    def init(self,p,shuffle=False,oidGame=None):
        self.path = p

        #cursor = self.collection.find({ "platforms.screens.shots.code":{'$ne':'null'}},{"platforms.screens.shots.code":1,"_id":1})
        if(oidGame!=None):
            cursor = self.db.games.find({"_id":ObjectId(oidGame)})
            print "include screens to "+cursor[0]['name']
        else:
            cursor = self.collection.find({})

        #arq = open('urls.txt','w')
        for doc in cursor:
            print doc['_id']
            pl = doc['platforms']
            for p in pl:
                if p.has_key('screens'):
                    s = p['screens']
                    for sh in s:
                        if "shots" in sh:
                            shots = sh['shots'][0]
                            if self.db.screens.find({"code":shots['code']}).count()==0:
                                print "include",shots['code'] 
                                sd = ShotData()
                                sd.filename=self.path+shots['code']+".jpg"
                                sd.oid=doc['_id']
                                sd.code=shots['code']
                                self.screens.append(sd)
                                
                                #arq.write(shots['image_urls'][0]+'\n')
                                
        if shuffle:
            random.shuffle(self.screens)
        
        #arq.close()
        
    def addGameByJSON(self,data):
        f = self.collection.find_one(data)
        if f==None:
            game_id = self.collection.insert_one(data).inserted_id
            return game_id
        else:
            return f['_id']
        
    def getScreen(self,code):
        cr = self.db.screens.find({"code":code})
        for s in cr:
            return s
    
    def getGameByObject(self,code):
        cr = self.db.games.find({"_id":ObjectId(code)})
        for s in cr:
            return s
        
    def getGame(self,code):
        cr = self.db.games.find({"_id":ObjectId(code)})
        for s in cr:
            return s
        
    def getGameCodes(self):
        cr = self.db.games.find({},{"_id":1})
        codes = []
        for s in cr:
            codes.append(s["_id"])    
        return codes
    
    def getScreenCodes(self):
        cr = self.db.screens.find({},{"code":1,"_id":0})
        codes = []
        for s in cr:
            codes.append(s["code"])    
        return codes
        
    def getGameByImage(self,code):
        cr = self.db.games.find({"platforms.screens.shots.code":code})
        if cr == None:
            return None
        else:
            print code
            print cr.count()
            return cr[0]
        
    def updateGame(self,code,data):
        self.db.games.update({"_id":ObjectId(code)},data,upsert=False)
        
    def addImageAverage(self,data):
        data['created'] = datetime.now()
        self.db.avgscreens.insert_one(data)
        
    def getImageAverage(self,goid):
        d = self.db.avgscreens.find({"goid":goid})
        if d.count()>0:
            return d[0]['image_average_rgb']
        else:
            return None
        
    def setType(self,typ,code,features=None,cells=None,tw=0,th=0):
        d = {}
        d["code"]=code
        d["type"]=typ
        if features != None:
            d.update(features)
            
        if cells != None:
            d["tile_width"]=tw
            d["tile_height"]=th
            d["cells"]=cells
        d['created'] = datetime.now()
        self.db.screens.update({"code":code},d,upsert=True)
        
    def getPublisherId(self,name):
        """Static method to get publisher ID give some name.
        
        If don't find plataform's name insert a new platform in database.
        Othwerwise returns the publisher ID.

        Args:
            name: name of publisher.

        Returns:
            Publisher ID.

        """
        size = self.db.publishers.find({"name": name}).count()
        if size==0 :
            p = {"name": name}
            return str(self.db.publishers.insert_one(p).inserted_id)
        else:
            return str(self.db.publishers.find({"name": name})[0]['_id'])
        
    def getDeveloperId(self,name):
        size = self.db.developers.find({"name": name}).count()
        if size==0 :
            p = {"name": name}
            return str(self.db.developers.insert_one(p).inserted_id)
        else:
            return str(self.db.developers.find({"name": name})[0]['_id'])
        
    def getPlatformId(self,name):
        size = self.db.platforms.find({"name": name}).count()
        if size==0 :
            p = {"name": name}
            return str(self.db.platforms.insert_one(p).inserted_id)
        else:
            return str(self.db.platforms.find({"name": name})[0]['_id'])
        
    def getPerspectiveId(self,name):
        size = self.db.perspectives.find({"name": name}).count()
        if size==0 :
            p = {"name": name}
            return str(self.db.perspectives.insert_one(p).inserted_id)
        else:
            return str(self.db.perspectives.find({"name": name})[0]['_id'])
        
    def getGenreId(self,name):
        size = self.db.genres.find({"name": name}).count()
        if size==0 :
            p = {"name": name}
            return str(self.db.genres.insert_one(p).inserted_id)
        else:
            return str(self.db.genres.find({"name": name})[0]['_id'])  
        
    def getGameplayId(self,name):
        size = self.db.gameplays.find({"name": name}).count()
        if size==0 :
            p = {"name": name}
            return str(self.db.gameplays.insert_one(p).inserted_id)
        else:
            return str(self.db.gameplays.find({"name": name})[0]['_id'])

    def getNarrativeId(self,name):
        size = self.db.narratives.find({"name": name}).count()
        if size==0 :
            p = {"name": name}
            return str(self.db.narratives.insert_one(p).inserted_id)
        else:
            return str(self.db.narratives.find({"name": name})[0]['_id'])
