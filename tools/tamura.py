from PIL import Image, ImageStat
import math

'''
https://github.com/knime-ip/knip/blob/master/org.knime.knip.core/src/org/knime/knip/core/features/seg/Tamura.java
'''

class Tamura(object):
    dx = 0
    dy = 0
    m_greyValues = None
    s = None
    m_mean = 0
    m_numPix = 0
    filterH = [[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]]
    filterV = [[-1, -1, -1], [0, 0, 0], [1, 1, 1]]
    
    def __init__(self,image,x,y):
        self.dx = x
        self.dy = y
        image = image.convert('L')
        stat = ImageStat.Stat(image)
        self.m_mean = stat.mean[0]
        
        self.s = image.size
        self.m_numPix = self.s[0]*self.s[1] 
        self.m_greyValues = self.crie_matriz(self.s[0],self.s[1],0)
        for x in range(self.s[0]):
            for y in range(self.s[1]):
                self.m_greyValues[x][y] = image.getpixel((x,y))
    
    def crie_matriz(self,n_linhas, n_colunas, valor):
        matriz = [] # lista vazia
        for i in range(n_linhas):
            # cria a linha i
            linha = [] # lista vazia
            for j in range(n_colunas):
                linha.append(valor)
            # coloque linha na matriz
            matriz.append(linha)
        return matriz
    
    def averageOverNeighborhoods(self, x, y,k):
        result = 0 
        border = 2**(2*k)
        x0 = 0
        y0 = 0
        
        for i in range(border):
            for j in range(border):
                x0 = int(x - (2**(k - 1)) + i)
                y0 = int(y - (2**(k - 1)) + j)
                if x0 < 0:
                      x0 = 0
                if y0 < 0:
                      y0 =0
                if x0>= self.s[0]:
                      x0 = self.s[0]-1
                if y0>=self.s[1]:
                      y0 = self.s[1]-1
                result = result + self.m_greyValues[x0][y0]
        result = (1 / (2** (2 * k))) * result
        return result

    def diffBetweenNeighborhoodsHorizontal(self,x,y,k):
        result = abs(self.averageOverNeighborhoods(x+(2**(k-1)), y, k)-self.averageOverNeighborhoods(x-(2**(k-1)), y, k))
        return result
    
    def diffBetweenNeighborhoodsVertical(self,x,y,k):
        result = abs(self.averageOverNeighborhoods(x, y+(2**(k-1)), k)-self.averageOverNeighborhoods(x, y-(2**(k-1)), k))
        return result
    
    def sizeLeadDiffValue(self,x,y):
        result = 0
        tmp = 0
        maxK = 1
        
        for k in range(3):
            tmp = max(self.diffBetweenNeighborhoodsHorizontal(x, y, k),
self.diffBetweenNeighborhoodsVertical(x, y, k))
            if result < tmp:
                maxK = k
                result = tmp
        return maxK
    
    def calculateSigma(self):
        result = 0
        for i in range(1,self.s[0]):
            for j in range(1,self.s[1]):
                  result = result + ((self.m_greyValues[i][j] - self.m_mean)** 2)
        result = result / (self.s[0]*self.s[1])
        return math.sqrt(result)
    
    def calculateDeltaH(self,x,y):
        result = 0
        for i in range(3):
            for j in range(3):
                  result = result + (self.m_greyValues[(x - 1) + i][(y - 1) + j] * self.filterH[i][j])
        return result
                  
    def calculateDeltaV(self,x,y):
        result = 0
        for i in range(3):
            for j in range(3):
                  result = result + (self.m_greyValues[(x - 1) + i][(y - 1) + j] * self.filterV[i][j]);
        return result
    
    def coarseness(self):
        result = 0
        for i in range(1,self.s[0] - 1):
            for j in range(1,self.s[1] - 1):
                result = result + (2**self.sizeLeadDiffValue(i, j))
        result = (1.0 / self.m_numPix) * result
        return result

    def contrast(self):
        result = 0
        my4 = 0
        alpha4 = 0
        sigma = self.calculateSigma()
        for x in range(self.s[0]):
            for y in range(self.s[1]):
                my4 = my4 + (self.m_greyValues[x][y] - self.m_mean)**4;

        alpha4 = float(my4) / float(sigma**4)
        result = float(sigma) / float(alpha4** 0.25)
        return result
    
    def directionality(self):
        histogram = [0]*16
        maxResult = 3.
        binWindow = maxResult / float(len(histogram) - 1)
        bn = -1
        for i in range(1,self.s[0] - 1):
            for j in range(1,self.s[1] - 1):
                if self.calculateDeltaH(i, j) >0:
                    bn = int(((math.pi / 2.) + math.atan(self.calculateDeltaV(i, j) / self.calculateDeltaH(i, j))) / binWindow)
                    histogram[bn]+= 1       
        return histogram
    
    
                            

