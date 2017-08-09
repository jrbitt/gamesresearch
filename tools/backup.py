'''
Codigo nao usado, mas nao deletado
Podera ser util no futuro
'''

EQUAL = 100
DIFF = 101
GREATER_THAN = 102
GREATER_EQUAL_THAN = 103
LESSER_THAN = 104
LESSER_EQUAL_THAN = 105

class Selector(object):
    
    def select(self,data):
        pass
    
class SimpleSelector(Selector):
    _attrb = ""
    _op = -1 
    _value = ""
    
    def __init(self,attrb, op, value):
        self._attrb = attrb
        self._op = op
        self._value = value
        
    def select(self,data):
        if(self.op == EQUAL):
            return data[attrb] == self.value
        elif (self.op == DIFF)
            return data[attrb] != self.value
        elif (self.op == GREATER_THAN)
            return data[attrb] > self.value
        elif (self.op == GREATER_EQUAL_THAN)
            return data[attrb] >= self.value
        elif (self.op == LESSER_THAN)
            return data[attrb] < self.value
        elif (self.op == LESSER_EQUAL_THAN)
            return data[attrb] <= self.value
        else
            return false
        
class GroupSelector(Selector):
    children = []
    
    def addSelector(self,s):
        children.append(s)
        
    def select(self,data):
        for c in children:
            if not c.select(data):
                return False
        return True
            
    
class Transformer(object):
    header = ""
    col = []
    
    def process(self,value,outfile)
        pass
    
class CopyValue(Transformer):
    
    def process(self,value,outfile)
        outfile.write(value[0])
    
class Convert(Transformer):
    dictValues = None
    
    def __init__(self,_dictV):
        self.dictValues = dictV
        
    def process(self,value,outfile)
        if self.dictValues.has_key(value[0]):
            outfile.write(self.dictValues[value[0])
        else:
            outfile.write(value[0])
            
class Normalize(Transformer):
    minValue = 0
    maxValue = 0
    diff = 0
    
    def __init__(self,minV, maxV):
        self.minValue = minV
        self.maxValue = maxV
        self.diff = maxV - minV
        
    def process(self,value,outfile)
        v = (value[0] - self.minValue)/self.diff
        outfile.write(v)
                                          
class Average(Transformer):
                                          
    def process(self,value,outfile):
        s = 0                        
        for i in value:
           s += i                               
        outfile.write(float(s)/len(value))    

class Proportion(Transformer):
    maxValue = 0
                                          
    def process(self,value,outfile):
        outfile.write(float(value)/maxValue)
                                          
class DatasetManager(object):
    gdb = None
    gameplays = []
    perspectives = []
    genres = []
    narratives = []
    games = []
                                          
    selector = None
                                          
    def __init__(self,g):
        self.gdb = g
        self.prepareDataset()
                                          
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
                                          
    def create(self,params,filename):
        data = None
        with open(params) as data_file:    
            data = json.load(data_file)
            
        samples = 0
        cursor = self.gdb.collection.find({})
        arq = open(filename, 'w')
        #vem o header
        for game in cursor: 
            if(self.selector.select(game)):
                self.games.append(game) 