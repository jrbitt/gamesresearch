# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

#Import scrapy package
import scrapy
import datetime

class Shot(scrapy.Item):
    """Save image data in a JPEG file.

    Class used by Scrapy to save images.

    Attributes:
        code (Field): MD5 created by scrapy that is used like filename.
        image_urls (Field): The image's URL
        images (Field): The data image

    """
    code=scrapy.Field()
    image_urls=scrapy.Field()
    images=scrapy.Field()

class Screenshot(scrapy.Item):
    """Description of a screenshot.

    This classe describes a screenshot consider an URL, un title and image data.

    Attributes:
        url (Field): MD5 created by scrapy that is used like filename.
        title (Field): The image's URL
        shots (Field): The data image
    """
    url = scrapy.Field()
    title = scrapy.Field()
    shots = scrapy.Field()
    
class Platform(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    publisher = scrapy.Field()
    developer = scrapy.Field()
    release = scrapy.Field()
    screens = scrapy.Field()
    
    def setCoreGameRelease(self,left):
        state = -1
        for sel in left:
            v = sel.xpath("text()").extract()
            if len(v) == 1:
                text = v[0]
                if "Published" in text:
                    state = 1
                elif "Released" in text:
                    state = 2
                elif "Developed" in text:
                    state = 5  
                elif "Also" in text:
                    state = 3 
            elif len(v) == 0:
                if state == 1:
                    self['publisher'] = sel.xpath('a/text()').extract_first()
                elif state == 2:
                    self['release'] = sel.xpath('a/text()').extract_first()
                elif state == 5:
                    self['developer'] = sel.xpath('a/text()').extract_first()
    

class Game(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    publisher = scrapy.Field()
    developer = scrapy.Field()
    release = scrapy.Field()
    perspectives = scrapy.Field()    
    platforms = scrapy.Field()
    genres = scrapy.Field()
    gameplays = scrapy.Field()
    narratives = scrapy.Field()
    created = scrapy.Field()
    
    def updatePlatform(self,p):
        for i in range(0,len(platforms)):
            if p.name == platforms[i]['name']:
                platforms[i] = dict(p)
                
    def setNarratives(self,v):
        temp = []
        for i in v:
            if "/" in i:
                strs = i.split('/')
                for j in strs:
                    temp.append(j)    
            else:
                temp.append(i)
        self['narratives'] = temp
                
    def setGameplays(self,v):
        temp = []
        for i in v:
            if "/" in i:
                strs = i.split('/')
                for j in strs:
                    temp.append(j)    
            else:
                temp.append(i)
        self['gameplays'] = temp


    def setPerspectives(self,v):
        temp = []
        for i in v:
            if "/" in i:
                strs = i.split('/')
                for j in strs:
                    temp.append(j)    
            else:
                temp.append(i)
        self['perspectives'] = temp

    
    def setGenres(self,v):
        temp = []
        for i in v:
            if "/" in i:
                strs = i.split('/')
                for j in strs:
                    temp.append(j)    
            else:
                temp.append(i)
        self['genres'] = temp
        
    def setPlatform(self,sel):
        plats = sel.xpath('a')
        temp = []
        for selp in plats:
            p = Platform()
            p['name'] = selp.xpath('text()').extract_first()
            p['url'] = selp.xpath('@href').extract_first()
            temp.append(p)
        self['platforms'] = temp
        state = -1
        self['created'] = datetime.datetime.now()
    
    def setCoreGameRelease(self,left):
        state = -1
        for sel in left:
            v = sel.xpath("text()").extract()
            if len(v) == 1:
                if ", " in v and state == 3:
                    self.setPlatform(sel)
                else:
                    text = v[0]
                    if "Published" in text:
                        state = 1
                    elif "Released" in text:
                        state = 2
                    elif "Platforms" in text:
                        state = 3                  
                    elif "Platform" in text:
                        state = 4
                    elif "Developed" in text:
                        state = 5  
            elif len(v) == 0:
                if state == 1:
                    self['publisher'] = sel.xpath('a/text()').extract_first()
                    state = -1
                elif state == 2:
                    self['release'] = sel.xpath('a/text()').extract_first()
                    state = -1
                elif state == 5:
                    self['developer'] = sel.xpath('a/text()').extract_first()
                    state = -1
                elif state == 4:
                    temp = []
                    p = Platform()
                    p['name'] = sel.xpath('a/text()').extract_first()
                    p['url'] = sel.xpath('a/@href').extract_first()
                    #{'name':'xbox','url':'/game/xbox'}
                    temp.append(p)        
                    self['platforms'] = temp
                    state = -1
            else:
                if ", " in v and state == 3:
                    self.setPlatform(sel)
                
    
    def setCoreGameGenre(self,right):
        state = -1
        for sel in right:
            v = sel.xpath("text()").extract()
            if len(v) == 0:
                g = sel.xpath("a/text()").extract()
                if state == 1:
                    self.setGenres(g)
                    state = -1
                elif state == 2:
                    self.setPerspectives(g)
                    state = -1
                elif state == 3:
                    self.setGameplays(g)       
                    state = -1
                elif state == 4:
                    self.setNarratives(g)       
                    state = -1
            elif len(v) == 1:
                text = v[0]
                if "Genre" in text:
                    state = 1
                elif "Perspective" in text:
                    state = 2
                elif "Gameplay" in text:
                    state = 3
                elif "Narrative" in text:
                    state = 4  
                else:
                    state = -1