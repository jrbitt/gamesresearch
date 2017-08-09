import scrapy
import hashlib
import random
from random import randint


from games.items  import Game
from games.items  import Platform
from games.items  import Screenshot
from games.items import Shot

        
class ShotSpider(scrapy.Spider):
    name = "shots"
    start_url = "http://www.mobygames.com"
    saida = None
    
    def parseShot(self, response):
        goid = response.meta['goid']
        url = response.xpath("//div[@class='screenshot']/img/@src").extract()
        if len(url) == 0:
            url = response.xpath("//meta[contains(@property,'og:image')]/@content").extract()
            desc = response.xpath("//meta[contains(@name,'description')]/@content").extract()
            code = hashlib.sha1(url[0]).hexdigest()
            linha = goid+ ";" + code + ";" + url[0] +";"+desc[0]+"\n"
            self.saida.write(linha)
    
    def start_requests(self):  
        arq = open('sem_shots','r')
        self.saida = open('saida.txt','w')
        for linha in arq:
            tokens = linha.split(' ')
            req = scrapy.Request(url=self.start_url+tokens[1], callback=self.parseShot)
            req.meta['goid'] = tokens[0]
            yield req
        arq.close()
        
    
class GameSpider(scrapy.Spider):
    name = "games"
    root = "http://www.mobygames.com"

    #start: 0 end:100
    #start: 101 end:200
    #start: 201 end:300
    
    #301 66175
    def start_requests(self):
        urls = [] 
        
        #start = 201
        #end = 300
        
        pages = []
        count = 0
        while count<500:
            n = randint(301,66175)
            if (n-1)%25 == 0:
                pages.append(n)
                count += 1
         
        for p in pages:    
            st = 'http://www.mobygames.com/browse/games/offset,'+str(p)+'/so,0a/list-games/'
            urls.append(st)
            pass
        
        #for i in range(start,end):
        #    st = 'http://www.mobygames.com/browse/games/offset,'+str(i*25)+'/so,0a/list-games/'
        #    urls.append(st)
            
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parseShot(self, response):
        self.logger.info("Parse each shot")
        ind = response.meta['platform_index']
        screen_ind = response.meta['screen_index']
        screen = Screenshot(response.meta['screen'])
        g = Game(response.meta['game'])
        p = g['platforms'][ind]
        
        url = response.xpath("//div[@class='screenshot']/img/@src").extract()
        
        if len(url)==0:
            #url = response.xpath("//div[@class='screenshot']/a/@href").extract()     
            url = response.xpath("//meta[contains(@property,'og:image')]/@content").extract()

        
        if len(url)>0:
            temp = []
            self.logger.info(url)
            shot = Shot()
            shot['image_urls'] = [self.root+url[0]]  
            shot['code'] = hashlib.sha1(self.root+url[0]).hexdigest()
            temp.append(shot)
            screen['shots'] = temp
            p['screens'][screen_ind] = screen
            yield shot
        yield g
    
    def parseScreenshots(self, response):
        self.logger.info("Parse Screenshots")
        g = Game(response.meta['game'])
        ind = response.meta['platform_index']
        p = g['platforms'][ind]
        
        urls = response.xpath("//div[@class='thumbnail-image-wrapper']/a/@href").extract()
    
        self.logger.info(p)
        if len(urls)==0:
            pass
        else:
            captions = response.xpath("//div[@class='thumbnail-caption']/small/text()").extract()
            temp= []
            for i in range(0,len(urls)):
                s = Screenshot()
                s['url'] = urls[i]
                s['title'] = captions[i]
                temp.append(s)
            p['screens'] = temp
            
            for i in range(0,len(urls)):
                req = scrapy.Request(url=self.root+urls[i], callback=self.parseShot)
                req.meta['screen'] = temp[i]
                req.meta['game'] = g
                req.meta['platform_index'] = ind
                req.meta['screen_index'] = i
                yield req
        
    def parsePlatform(self, response):
        self.logger.info("Parse Platform")
        g = Game(response.meta['game'])
        ind = response.meta['platform_index']
        p = g['platforms'][ind]

    
        #Os divs do bloco da esquerda
        left = response.xpath("//div[@id='coreGameRelease']/div")
        p.setCoreGameRelease(left)
        g['platforms'][ind] = dict(p)
        
        screens = response.xpath("//div[@class='rightPanelHeader']/ul/li/a[contains(@href, '/screenshot')]/@href").extract()
        for s in screens:
            req = scrapy.Request(url=self.root+s, callback=self.parseScreenshots)
            req.meta['game'] = g
            req.meta['platform_index'] = ind
            yield req
            
    def parseGame(self, response):
        if response.url == 'http://www.mobygames.com/game/_' or response.url == 'http://www.mobygames.com/game/07-zgo-si':
            pass
        else:
            self.logger.info("Parse Game")
            g = Game()
            g['url'] = response.url
            g['name'] = response.xpath("//div[@class='rightPanelHeader']/h1/a/text()").extract()[0]
            self.logger.info("Parse Game "+g['name'])
            
            #Os divs do bloco da esquerda
            left = response.xpath("//div[@id='coreGameRelease']/div")
            g.setCoreGameRelease(left)
                
            #Os divs do bloco da direita
            right =  response.xpath("//div[@id='coreGameGenre']/div/div")
            g.setCoreGameGenre(right)

            #Para cada plataforma faz uma requisicao
            #Se tem uma plataforma trata de um jeito
            if len(g['platforms'])==1:
                self.logger.info("Parse Game - One platform")
                req = scrapy.Request(url=response.url, callback=self.parsePlatform, dont_filter=True)
                req.meta['game'] = g
                req.meta['platform_index'] = 0
                yield req
                
            else:
                ind = 0
                for p in g['platforms']:
                    self.logger.info("Parse Game - Platform - "+p['name'])
                    req = scrapy.Request(url=self.root+p['url'], callback=self.parsePlatform)
                    req.meta['platform_index'] = ind
                    req.meta['game'] = g
                    ind = ind + 1
                    yield req
        
        
    def parse(self, response):
        self.logger.info("Parse List Game")
        linksGames = response.xpath("//div[@class='molist']/table//a[contains(@href, '/game/')]/@href").extract()
        random.shuffle(linksGames)
        for i in range(5):
            yield scrapy.Request(url=self.root+linksGames[i], callback=self.parseGame)
            
'''
scrapy crawl onegame -a idgame=state-of-emergency
scrapy crawl onegame -a url=state-of-emergency

'''
class OneGameSpider(GameSpider):
    name = "onegame"
    start_url = ""

    def __init__(self, url=None, idgame='', *args, **kwargs):
        super(OneGameSpider, self).__init__(*args, **kwargs)
        
        if(url==None):
            self.start_url = "http://www.mobygames.com/game/"+idgame
        else:
            self.start_url = url
        
    def start_requests(self):  
            
        yield scrapy.Request(url=self.start_url, callback=self.parseGame)
            