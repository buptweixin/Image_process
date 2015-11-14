#encoding=utf-8

import struct
from math import ceil
from math import cos
from math import sin
from math import pi
import StringIO
import numpy as np
import pylab as pl

FORMAT_OFFSET = int('0',16)
SIZE_OFFSET = int('2',16)
DATA_OFFSET = int('0a', 16)
WIDTH_OFFSET = int('12',16)
HEIGHT_OFFSET = int('16',16)
BPP_OFFSET = int('1c',16)
HORIZONTAL = 0
VERTICAL = 1

class readImg:
    def __init__(self, filename):
        '''Main class to open and edit a 24 bits bmp image'''

        bmpfile = open(filename)
        self.raw_data = bmpfile.read()
        bmpfile.close()

        self.width = struct.unpack_from("<i", self.raw_data, WIDTH_OFFSET)[0]
        self.height = struct.unpack_from("<i", self.raw_data, HEIGHT_OFFSET)[0]
        self.data_offset = ord(self.raw_data[DATA_OFFSET])
        self.bpp = ord(self.raw_data[BPP_OFFSET])  # Bits Per Pixel
        self.bitmap = []

        if self.raw_data[0] != "B" and self.raw_data[1] != "M":
            raise TypeError, "Not a BMP file!"
        if self.bpp != 24:
            raise TypeError, "Not a 24 bits BMP file"



    def create_bitmap(self):
        '''Creates the bitmap from the raw_data'''

        off = self.data_offset
        width_bytes = self.width*(self.bpp/8)
        rowstride = ceil(width_bytes/4.0)*4
        padding = int(rowstride - width_bytes)

        for y in xrange(self.height):
            self.bitmap.append([])

            for x in xrange(self.width):
                b = ord(self.raw_data[off])
                g = ord(self.raw_data[off+1])
                r = ord(self.raw_data[off+2])

                off = off+3

                self.bitmap[y].append([r, g, b])

            off += padding

        self.bitmap = self.bitmap[::-1]

    def save_to(self, filename):
        '''Export the bmp saving the changes done to the bitmap'''

        raw_copy = StringIO.StringIO()
        bitmap = self.bitmap[::-1]

        width_bytes = self.width*(self.bpp/8)
        rowstride = ceil(width_bytes/4.0)*4
        padding = int(rowstride - width_bytes)

        # Same header as before until the width
        raw_copy.write(self.raw_data[:WIDTH_OFFSET])

        s = struct.Struct("<i")
        _w = s.pack(self.width)   # Transform width, height to
        _h = s.pack(self.height)  # little indian format
        raw_copy.write(_w)
        raw_copy.write(_h)

        # After the new width and height the header it's the same
        raw_copy.write(self.raw_data[HEIGHT_OFFSET+4:self.data_offset])

        for y in xrange(self.height):
            for x in xrange(self.width):
                r, g, b = bitmap[y][x]

                # Out of range control
                if r > 255: r = 255
                if g > 255: g = 255
                if b > 255: b = 255
                if r < 0: r = 0
                if g < 0: g = 0
                if b < 0: b = 0

                #Char transformation
                r = chr(r)
                g = chr(g)
                b = chr(b)

                raw_copy.write(b + g + r)

            raw_copy.write(chr(0)*padding)

        self.raw_data = raw_copy.getvalue()

        f = open(filename, "w")
        f.write(self.raw_data)
        f.close()
        f.close()

    def rgb2gray(self):
        for y in range(self.height):
            for x in range(self.width):
                try:
                    mean = sum(self.bitmap[y][x])/3
                    colour = (mean, mean, mean)
                    self.bitmap[y][x] = colour
                except IndexError as e:
                    continue

    def mirror(self, direction = HORIZONTAL):
        if direction == HORIZONTAL:
            for y in xrange(self.height):
                self.bitmap[y] = self.bitmap[y][::-1]
        elif direction == VERTICAL:
            self.bitmap= self.bitmap[::-1]

    def move(self, distance = 0, direction = HORIZONTAL):
        if distance > 0:
            self.bitmap[:][distance:self.width] = self.bitmap[:][:self.width - distance]

    def cut(self,point1=(0,0),point2=(100,100)):
        new_height=point2[0]-point1[0]
        new_width=point2[1]-point1[1]
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        for y in xrange(new_height):
            new_bitmap[y][:new_width]=self.bitmap[y+point1[0]][point1[1]:point2[1]]
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width

    def resize_nearest(self,new_height=100,new_width=100):
        fh=float(self.height)/new_height
        fw=float(self.width)/new_width
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        for y in xrange(new_height):
            i=int(round(y*fh))
            for x in xrange(new_width):
                j=int(round(x*fw))
                new_bitmap[y][x]=self.bitmap[i][j]
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width
        
        
    def resize_bilinear(self,new_height=100,new_width=100):
        fh=float(self.height)/new_height
        fw=float(self.width)/new_width
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        for y in xrange(new_height):
            y0=y*fh
            y1=int(y0)
            if y1==self.height:
                y2=y1
            else:
                y2=y1+1
            fy1=y1-y0
            fy2=1-fy1

            for x in xrange(new_width):
                x0=x*fw
                x1=int(x0)
                if x1==self.width:
                    x2=x1
                else:
                    x2=x1+1
                fx1=x1-x0
                fx2=1-fx1
                s1=fx2*fy2
                s2=fx1*fy2
                s3=fx1*fy1
                s4=fx2*fy1
                p1=np.array(self.bitmap[y1][x1])
                p2=np.array(self.bitmap[y1][x2])
                p3=np.array(self.bitmap[y2][x1])
                p4=np.array(self.bitmap[y2][x2])
                p=(p1*s1+p2*s2+p3*s3+p4*s4).astype(np.int)
                new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width

    def rotate(self,angle=30):
        theta=pi*angle/180
        fSrcX1 = (float) (- (self.width) / 2)  
        fSrcY1 = (float) (  (self.height) / 2)  
        fSrcX2 = (float) (  (self.width) / 2) 
        fSrcY2 = (float) (  (self.height) / 2)
        fSrcX3 = (float) (- (self.width) / 2)  
        fSrcY3 = (float) (- (self.height) / 2)  
        fSrcX4 = (float) (  (self.width) / 2)  
        fSrcY4 = (float) (- (self.height) / 2)
        fDstX1 =  cos(theta) * fSrcX1 + sin(theta) * fSrcY1
        fDstY1 = -sin(theta) * fSrcX1 + cos(theta) * fSrcY1
        fDstX2 =  cos(theta) * fSrcX2 + sin(theta) * fSrcY2
        fDstY2 = -sin(theta) * fSrcX2 + cos(theta) * fSrcY2
        fDstX3 =  cos(theta) * fSrcX3 + sin(theta) * fSrcY3
        fDstY3 = -sin(theta) * fSrcX3 + cos(theta) * fSrcY3
        fDstX4 =  cos(theta) * fSrcX4 + sin(theta) * fSrcY4
        fDstY4 = -sin(theta) * fSrcX4 + cos(theta) * fSrcY4
        new_width  =int ( max( abs(fDstX4 - fDstX1), abs(fDstX3 - fDstX2) ) + 0.5)  
        new_height = int( max( abs(fDstY4 - fDstY1), abs(fDstY3 - fDstY2) )  + 0.5)
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        dx = -0.5*new_width*cos(theta) - 0.5*new_height*sin(theta) + 0.5*self.width
        dy = 0.5*new_width*sin(theta) - 0.5*new_height*cos(theta) + 0.5*self.height
        for i in xrange(new_height):
            for j in xrange(new_width):
                x = float(j)*cos(theta) + float(i)*sin(theta) + dx 
                y = float(-j)*sin(theta) + float(i)*cos(theta) + dy
                if (x<0)or(x>self.width)or(y<0)or(y>self.height):
                    new_bitmap[i][j]=(0,0,0)
                else:
                    new_bitmap[i][j]=self.bitmap[int(y)][int(x)]
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width
        
    def Smooth_LPF(self,m=1):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        a=0
        for y in xrange(new_height):
            for x in xrange(new_width):
                print a
                a=a+1
                if(y-m<1)or(x-m<1)or(y+m>new_height-1)or(x+m>new_width-1):
                    new_bitmap[y][x]=self.bitmap[y][x]
                else:
                    for i in xrange (2*m+1):
                        for j in xrange (2*m+1):
                            p=p+np.array(self.bitmap[y-m+i][x-m+j])
                    p=p/((2*m+1)**2)
                    new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width
        
        
    def Smooth_midvaule(self,m=1):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        b=np.array([],np.int)
        g=np.array([],np.int)
        r=np.array([],np.int)
        for y in xrange(new_height):
            for x in xrange(new_width):
                if (y-m<1)or(x-m<1)or(y+m>new_height-1)or(x+m>new_width-1):
                    new_bitmap[y][x]=self.bitmap[y][x]
                else:
                    for i in xrange (2*m+1):
                        for j in xrange (2*m+1):
                            p=np.array(self.bitmap[y-m+i][x-m+j])
                            #print 'b'
                            b = np.append(b,p[0])
                            #print 'g'
                            g = np.append(g,p[1])
                            #print 'r'
                            r = np.append(r,p[2])
                    p=(int(np.median(b)),int(np.median(g)),int(np.median(r)))
                    new_bitmap[y][x]=p
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width

    def  Sharpen_HPF(self,m=1):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        a=0
        for y in xrange(new_height):
            for x in xrange(new_width):
                print a
                a=a+1
                if(y-m<0)or(x-m<0)or(y+m>new_height-1)or(x+m>new_width-1):
                    new_bitmap[y][x]=self.bitmap[y][x]
                else:
                    p=(((2*m+1)**2)-1)*np.array(self.bitmap[y][x])
                    for i in xrange (2*m+1):
                        for j in xrange (2*m+1):
                            if (i==m) and  (j==m) :
                                continue
                            p=p-np.array(self.bitmap[y-m+i][x-m+j])
                    new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width
        
        
    def  Sharpen_GFF(self,m=1,A=1.8):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        a=0
        for y in xrange(new_height):
            for x in xrange(new_width):
                print a
                a=a+1
                if(y-m<0)or(x-m<0)or(y+m>new_height-1)or(x+m>new_width-1):
                    p=(A)*np.array(self.bitmap[y][x])
                    p = p.astype(np.int)
                    new_bitmap[y][x]=tuple(p)
                else:
                    p=(((2*m+1)**2)-1)*np.array(self.bitmap[y][x])
                    for i in xrange (2*m+1):
                        for j in xrange (2*m+1):
                            if (i==m) and  (j==m) :
                                continue
                            p=p-np.array(self.bitmap[y-m+i][x-m+j])
                    p=(A-1)*np.array(self.bitmap[y][x])+p
                    p = p.astype(np.int)
                    new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width
       
       
       
    def  Sharpen_Roberts(self):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        for y in xrange(new_height):
            for x in xrange(new_width):
                if (y==new_height-1)or(x==new_width-1):
                    new_bitmap[y][x]=np.array(self.bitmap[y][x])
                else:
                    p=abs(np.array(self.bitmap[y][x])-np.array(self.bitmap[y+1][x+1]))+\
                    abs(np.array(self.bitmap[y][x+1])-np.array(self.bitmap[y+1][x]))
                    #p = p.astype(np.int)
                    new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width


    def  Sharpen_Prewitt(self):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        for y in xrange(new_height):
            for x in xrange(new_width):
                if (y==new_height-1)or(x==new_width-1)or(y==0)or(x==0):
                    new_bitmap[y][x]=np.array(self.bitmap[y][x])
                else:
                    p=abs(np.array(self.bitmap[y-1][x-1])+np.array(self.bitmap[y-1][x])+np.array(self.bitmap[y-1][x+1])\
                    -np.array(self.bitmap[y+1][x-1])-np.array(self.bitmap[y+1][x])-np.array(self.bitmap[y+1][x+1]))+\
                    abs(np.array(self.bitmap[y-1][x+1])+np.array(self.bitmap[y][x+1])+np.array(self.bitmap[y+1][x+1])\
                    -np.array(self.bitmap[y-1][x-1])-np.array(self.bitmap[y][x-1])-np.array(self.bitmap[y+1][x-1]))
                    #p = p.astype(np.int)
                    new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width        


    def  Sharpen_Sobel(self):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        for y in xrange(new_height):
            for x in xrange(new_width):
                if (y==new_height-1)or(x==new_width-1)or(y==0)or(x==0):
                    new_bitmap[y][x]=np.array(self.bitmap[y][x])
                else:
                    p=abs(np.array(self.bitmap[y-1][x-1])+2*np.array(self.bitmap[y-1][x])+np.array(self.bitmap[y-1][x+1])\
                    -np.array(self.bitmap[y+1][x-1])-2*np.array(self.bitmap[y+1][x])-np.array(self.bitmap[y+1][x+1]))+\
                    abs(np.array(self.bitmap[y-1][x+1])+2*np.array(self.bitmap[y][x+1])+np.array(self.bitmap[y+1][x+1])\
                    -np.array(self.bitmap[y-1][x-1])-2*np.array(self.bitmap[y][x-1])-np.array(self.bitmap[y+1][x-1]))
                    #p = p.astype(np.int)
                    new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width   
        
        
    def  Sharpen_Laplacian(self):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        for y in xrange(new_height):
            for x in xrange(new_width):
                if (y==new_height-1)or(x==new_width-1)or(y==0)or(x==0):
                    new_bitmap[y][x]=np.array(self.bitmap[y][x])
                else:
                    p=4*np.array(self.bitmap[y][x])-np.array(self.bitmap[y-1][x])-\
                    np.array(self.bitmap[y+1][x])-np.array(self.bitmap[y][x-1])-\
                    np.array(self.bitmap[y][x+1])
                    #p = p.astype(np.int)
                    new_bitmap[y][x]=tuple(p)
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width
        
        
    def plot_hist(self):
        b=np.array([],np.int)
        g=np.array([],np.int)
        r=np.array([],np.int)
        for y in xrange(self.height):
            for x in xrange(self.width):
                b=np.append(b,self.bitmap[y][x][0])
                g=np.append(g,self.bitmap[y][x][1])
                r=np.append(r,self.bitmap[y][x][2])
        pl.figure
        pl.subplot(231)
        fb=pl.hist(b,256,range=(0,255),facecolor='blue')
        #fb=pl.hist(b)
        pl.show()
        fre_b=np.array(fb[0])/(self.height*self.width)
        pl.subplot(232)
        fg=pl.hist(g,256,range=(0,255),facecolor='green')
        fre_g=np.array(fg[0])/(self.height*self.width)
        pl.show()
        
        pl.subplot(233)
        fr=pl.hist(r,256,range=(0,255),facecolor='red')
        fre_r=np.array(fr[0])/(self.height*self.width)
        pl.show()
        sum_b=np.zeros(256)
        sum_g=np.zeros(256)
        sum_r=np.zeros(256)
        for i in xrange(256):
            sum_b[i]=sum(fre_b[0:i+1])
            sum_g[i]=sum(fre_g[0:i+1])
            sum_r[i]=sum(fre_r[0:i+1])
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x][0]=int (sum_b[self.bitmap[y][x][0]]*255)
                self.bitmap[y][x][1]=int (sum_g[self.bitmap[y][x][1]]*255)
                self.bitmap[y][x][2]=int (sum_r[self.bitmap[y][x][2]]*255)
        b=np.array([],np.int)
        g=np.array([],np.int)
        r=np.array([],np.int)
        for y in xrange(self.height):
            for x in xrange(self.width):
                b=np.append(b,self.bitmap[y][x][0])
                g=np.append(g,self.bitmap[y][x][1])
                r=np.append(r,self.bitmap[y][x][2])
        pl.subplot(234)
        fb=pl.hist(b,256,range=(0,255),facecolor='blue')
        #fb=pl.hist(b)
        pl.show()
        pl.subplot(235)
        fg=pl.hist(g,256,range=(0,255),facecolor='green')
        pl.show()
        pl.subplot(236)
        fr=pl.hist(r,256,range=(0,255),facecolor='red')
        pl.show()
if __name__ == '__main__':
    img =readImg('../bear.bmp')
    img.create_bitmap()
    img.plot_hist()
    #print img.height
    #img.rgb2gray()
    #img.resize_nearest(100,100)
    #img.resize_bilinear(100,100)
    #img.rotate(-130)
    #img.Smooth_LPF()
    #img.resize_nearest()
    #img.cut()
    #img.resize_bilinear()
    #img.rotate()
    img.Smooth_midvaule()
    #img.Sharpen_HPF()
    
    #img.Sharpen_GFF()
    #img.Sharpen_Roberts()
    #img.Sharpen_Prewitt()
    #img.Sharpen_Sobel()
    #img.Sharpen_Laplacian()
    #img.move(distance=40, direction=HORIZONTAL)
    #img.plot_hist()    
    img.save_to(filename="../out5.bmp")
