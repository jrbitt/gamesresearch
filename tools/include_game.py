
import sys, getopt, os, glob
import json
from bson import json_util
import hashlib

from PIL import Image

from database import GamesDatabase


class GameManager(object):
    folderpath = ""
    foldertarget=""
    path_json = ""
    path_images = []
    image_codes = []
    suffix_path = ""
    json_data = None
    gdb = None
    
    def init(self, _folderpath,_foldertarget, _gdb,_suffix=""):
        self.folderpath = _folderpath
        self.suffix_path = _suffix
        self.foldertarget = _foldertarget
        self.gdb = _gdb
        
        #Troca para a folder
        os.chdir(_folderpath)
        #Para todos os arquivos da folder
        for f in glob.glob("*.*"):
            #se for json guarda o nome
            if f.find(".json") != -1:
                self.path_json=f;
            #senao guarda todos os nomes de imagens
            else:
                self.path_images.append(f)
        
        #Le o arquivo JSON
        with open(self.path_json) as data_file:    
            self.json_data = json.load(data_file)
            
    def run(self):
        #Atualizo o caminho e o codigo da imagem
        for p in self.json_data['platforms']:
            if p.has_key('screens'):
                for s in p['screens']:
                    for sh in s['shots']:
                        for i in sh['images']:
                            print i['path']
                            c = hashlib.sha1()
                            c.update(i['path'])
                            hc = c.hexdigest()
                            i['path'] = self.suffix_path+"/"+hc+".jpg"
                            sh['code'] = hc
                            self.image_codes.append(hc+".jpg")
        
        #Salvar as imagens na pasta alvo                    
        cnt = 0
        for pi in self.path_images:
            im = Image.open(pi)
            print self.foldertarget+"/"+self.image_codes[cnt]
            im.save(self.foldertarget+"/"+self.image_codes[cnt])
            cnt += 1
            
        data = json_util.loads(json.dumps(self.json_data, default=json_util.default))
        
        i = self.gdb.addGameByJSON(data)
        
        print "inclui no BD " + str(i)

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"ha")
    except getopt.GetoptError:
        print "include_game.py -h | -a"
        sys.exit(2)
        
    for opt, arg in opts:
        if opt == '-h':
            print 'include_game.py -a <folder path> <folder target> suffix'
            sys.exit()
        elif opt in ("-a"):
            gm = GameManager()
            gdb = GamesDatabase()
            gm.init(args[0],args[1],gdb,args[2])
            gm.run()

    
if __name__ == '__main__': 
    main(sys.argv[1:])