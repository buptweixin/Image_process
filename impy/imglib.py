#encoding=utf-8

import struct
import StringIO
from math import pi, sin, cos
import copy
import pylab as pl
from math import ceil, sqrt, exp
import numpy as np
import random
from scipy.fftpack import dct,idct

FORMAT_OFFSET = int('0',16)
SIZE_OFFSET = int('2',16)
DATA_OFFSET = int('0a', 16)
BISIZE_OFFSET = int('0e', 16)
WIDTH_OFFSET = int('12',16)
HEIGHT_OFFSET = int('16',16)
BPP_OFFSET = int('1c',16)
BIX = int('26', 16)
BICLR = int('2e', 16)
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
        self.rotateAngle = 30
        self.b=np.array([])
        self.g=np.array([])
        self.r=np.array([])

        if self.raw_data[0] != "B" and self.raw_data[1] != "M":
            raise TypeError, "Not a BMP file!"
        if self.bpp != 24:
            raise TypeError, "Not a 24 bits BMP file"

        # 11.12 added
        self.create_bitmap()



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
        self.bitmap_backup = copy.deepcopy(self.bitmap)
        ## 11.12 deleted
        ## return self.bitmap

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

    def move(self, dx, dy):

        if dx > 0:
            for i in range(self.height):
                for j in range(1, self.width-dx):
                    self.bitmap[i][-j] = self.bitmap[i][-j-dx]
            for i in range(self.height):
                for j in range(dx):
                    self.bitmap[i][j] = (0, 0, 0)
        else:
            for i in range(self.height):
                for j in range(self.width+dx):
                    self.bitmap[i][j] = self.bitmap[i][j-dx]
            for i in range(self.height):
                for j in range(-1,dx,-1):
                    self.bitmap[i][j] = (0,0,0)
        if dy > 0:
            for i in range(1, self.height-dy):
                for j in range(self.width):
                    self.bitmap[-i][j] = self.bitmap[-i-dy][j]
            for i in range(dy):
                for j in range(self.width):
                    self.bitmap[i][j] = (0, 0, 0)
        else:
            for i in range(self.height+dy):
                for j in range(self.width):
                    self.bitmap[i][j] = self.bitmap[i-dy][j]
            for i in range(-1, dy, -1):
                for j in range(self.width):
                    self.bitmap[i][j] = (0,0,0)

    def cut(self,point1=(0,0),point2=(100,100)):
        new_height=abs(point2[0]-point1[0])
        new_width=abs(point2[1]-point1[1])
        len_y=min(point1[0],point2[0])
        len_x1=min(point1[1],point2[1])
        len_x2=max(point1[1],point2[1])
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        for y in xrange(new_height):
            new_bitmap[y][:new_width]=self.bitmap[y+len_y][len_x1:len_x2]
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width

    def rotate(self,angle=15):
        theta=pi*angle/180
        new_width  =self.width
        new_height = self.height
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
        self.bitmap=new_bitmap[:][:]
        self.height=new_height
        self.width=new_width

    def resize_nearest(self,rate = 1.0):
        new_height = int(self.height * rate)
        new_width = int(self.width * rate)
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        for y in xrange(new_height):
            i=int((y/rate))
            for x in xrange(new_width):
                j=int((x/rate))
                new_bitmap[y][x]=self.bitmap[i][j]
        self.bitmap=new_bitmap[:]
        self.height=new_height
        self.width=new_width

    def resize_bilinear(self,rate = 1.0):
        new_height = int(self.height * rate)
        new_width = int(self.width * rate)
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        for y in xrange(new_height):
            y0=y/rate
            y1=int(y0)
            if y1==self.height - 1:
                y2=y1
            else:
                y2=y1+1
            fy1=y1-y0
            fy2=1-fy1

            for x in xrange(new_width):
                x0=x/rate
                x1=int(x0)
                if x1==self.width - 1:
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

    def Smooth_LPF(self,m=1):
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        p=np.array([0,0,0])
        a=0
        for y in xrange(new_height):
            for x in xrange(new_width):
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
        n=(2*m+1)**2
        mid=(n-1)/2
        p=np.array([0,0,0])
        b=np.ones(n)
        g=np.ones(n)
        r=np.ones(n)
        for y in xrange(new_height):
            for x in xrange(new_width):
                if (y-m<1)or(x-m<1)or(y+m>new_height-1)or(x+m>new_width-1):
                    new_bitmap[y][x]=self.bitmap[y][x]
                else:
                    for i in xrange (2*m+1):
                        for j in xrange (2*m+1):
                            p=np.array(self.bitmap[y-m+i][x-m+j])
                            #print 'b'
                            b[(2*m+1)*i+j]=p[0]
                            #print 'g'
                            g[(2*m+1)*i+j]=p[1]
                            #print 'r'
                            r[(2*m+1)*i+j]=p[2]
                    #p=(int(np.median(b)),int(np.median(g)),int(np.median(r)))
                    b=sorted(b)
                    g=sorted(g)
                    r=sorted(r)
                    p=(int(b[mid]),int(g[mid]),int(r[mid]))
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

    def Sharpen_Roberts(self):
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

    def Sharpen_Prewitt(self):
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


    def Sharpen_Sobel(self):
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


    def Sharpen_Laplacian(self):
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

    def image_fft(self):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in xrange(self.height):
            for x in xrange(self.width):
                b[y][x]=self.bitmap[y][x][0]
                g[y][x]=self.bitmap[y][x][1]
                r[y][x]=self.bitmap[y][x][2]
        self.b= np.fft.fft2(b)
        self.g= np.fft.fft2(g)
        self.r= np.fft.fft2(r)
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        magnitude_spectrumb = 20*np.log(np.abs(fshiftb))
        magnitude_spectrumg= 20*np.log(np.abs(fshiftg))
        magnitude_spectrumr = 20*np.log(np.abs(fshiftr))
        pl.show()
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(magnitude_spectrumb[y][x]),int(magnitude_spectrumg[y][x]),int(magnitude_spectrumr[y][x]))

    def image_ifft(self):
        pb = np.fft.ifft2(self.b)
        pg = np.fft.ifft2(self.g)
        pr = np.fft.ifft2(self.r)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(pb[y][x]),int(pg[y][x]),int(pr[y][x]))

    def image_dct(self):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in xrange(self.height):
            for x in xrange(self.width):
                b[y][x]=self.bitmap[y][x][0]
                g[y][x]=self.bitmap[y][x][1]
                r[y][x]=self.bitmap[y][x][2]
        self.b= dct(dct(b.T).T)
        self.g= dct(dct(g.T).T)
        self.r= dct(dct(r.T).T)
        magnitude_spectrumb = 20*np.log(np.abs(self.b))
        magnitude_spectrumg= 20*np.log(np.abs(self.g))
        magnitude_spectrumr = 20*np.log(np.abs(self.r))
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(magnitude_spectrumb[y][x]),int(magnitude_spectrumg[y][x]),int(magnitude_spectrumr[y][x]))

    def image_idct(self):
        pb =  idct(idct(self.b.T).T)
        pg =  idct(idct(self.g.T).T)
        pr =  idct(idct(self.r.T).T)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(pb[y][x]/(4*self.width*self.height)),int(pg[y][x]/(4*self.width*self.height)),int(pr[y][x]/(4*self.width*self.height)))

    def hist(self):
        #self.rgb2gray()
        b=np.zeros((self.height,self.width))
        for y in xrange(self.height):
            for x in xrange(self.width):
                b[y][x]=int(sum(self.bitmap[y][x][:])/3)
        b.shape=(self.height*self.width)
        return b

    def hist_equalization(self, fb):
        fre_b=np.array(fb[0])/(self.height*self.width)
        sum_b=np.zeros(256)
        for i in xrange(256):
            sum_b[i]=sum(fre_b[0:i+1])
        new_width=self.width
        new_height=self.height
        new_bitmap = [[0 for j in range(new_width)] for i in range(new_height)]
        for y in xrange(self.height):
            for x in xrange(self.width):
                new_bitmap[y][x]=(int (sum_b[self.bitmap_backup[y][x][0]]*255+0.5),\
                int (sum_b[self.bitmap_backup[y][x][1]]*255+0.5),\
                int (sum_b[self.bitmap_backup[y][x][2]]*255+0.5))
        self.bitmap=new_bitmap[:]

    #################
    #频域滤波
    #################
    def Ideal_LPF(self,d=50):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                if sqrt((y-self.height/2)**2+(x-self.width/2)**2)<d:
                    b[y][x]=1
                    g[y][x]=1
                    r[y][x]=1
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)

        fb=np.multiply(fshiftb,b)
        fg=np.multiply(fshiftg,g)
        fr=np.multiply(fshiftr,r)

        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))


    def butterworth_LPF(self,n=3,d=50):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                b[y][x]=1.0/(1+(sqrt((y-self.height/2)**2+(x-self.width/2)**2)/d)**(2*n))
                g[y][x]=b[y][x]
                r[y][x]=b[y][x]
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        fb=np.multiply(fshiftb,b)
        fg=np.multiply(fshiftg,g)
        fr=np.multiply(fshiftr,r)
        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))



    def Gauss_LPF(self,d=50):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                b[y][x]=exp(-(((y-self.height/2)**2+(x-self.width/2)**2))/(2*d**2))
                g[y][x]=b[y][x]
                r[y][x]=b[y][x]
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        fb=np.multiply(fshiftb,b);
        fg=np.multiply(fshiftg,g);
        fr=np.multiply(fshiftr,r);
        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))


    def exponential_LPF(self,n=3,d=50):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                d0=sqrt((y-self.height/2)**2+(x-self.width/2)**2)
                b[y][x]=exp(-(d0/d)**n)
                g[y][x]=b[y][x]
                r[y][x]=b[y][x]
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        fb=np.multiply(fshiftb,b);
        fg=np.multiply(fshiftg,g);
        fr=np.multiply(fshiftr,r);
        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))


    def Ideal_HPF(self,d=50):
        b=np.ones((self.height,self.width))
        g=np.ones((self.height,self.width))
        r=np.ones((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                if sqrt((y-self.height/2)**2+(x-self.width/2)**2)<d:
                    b[y][x]=0
                    g[y][x]=0
                    r[y][x]=0
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        fb=np.multiply(fshiftb,b);
        fg=np.multiply(fshiftg,g);
        fr=np.multiply(fshiftr,r);
        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))


    def butterworth_HPF(self,n=3,d=50):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                d0=sqrt((y-self.height/2)**2+(x-self.width/2)**2)
                if y==self.height/2  and x==self.width/2:
                    d0=1
                b[y][x]=1.0/(1+(d/d0)**(2*n))
                g[y][x]=b[y][x]
                r[y][x]=b[y][x]
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        fb=np.multiply(fshiftb,b);
        fg=np.multiply(fshiftg,g);
        fr=np.multiply(fshiftr,r);
        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))


    def exponential_HPF(self,n=3,d=50):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                d0=sqrt((y-self.height/2)**2+(x-self.width/2)**2)
                if y==self.height/2  and x==self.width/2:
                    d0=1
                b[y][x]=exp(-(d/d0)**n)
                g[y][x]=b[y][x]
                r[y][x]=b[y][x]
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        fb=np.multiply(fshiftb,b);
        fg=np.multiply(fshiftg,g);
        fr=np.multiply(fshiftr,r);
        fb_=np.fft.ifftshift(fb)
        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))
    def Gauss_HPF(self,d=25):
        b=np.zeros((self.height,self.width))
        g=np.zeros((self.height,self.width))
        r=np.zeros((self.height,self.width))
        for y in range(self.height):
            for x in xrange(self.width):
                b[y][x]=1-exp(-(((y-self.height/2)**2+(x-self.width/2)**2))/(2*d**2))
                g[y][x]=b[y][x]
                r[y][x]=b[y][x]
        fshiftb = np.fft.fftshift(self.b)
        fshiftg= np.fft.fftshift(self.g)
        fshiftr = np.fft.fftshift(self.r)
        fb=np.multiply(fshiftb,b)
        fg=np.multiply(fshiftg,g)
        fr=np.multiply(fshiftr,r)
        self.b=np.fft.ifftshift(fb)
        self.g=np.fft.ifftshift(fg)
        self.r=np.fft.ifftshift(fr)
        for y in xrange(self.height):
            for x in xrange(self.width):
                self.bitmap[y][x]=(int(fb[y][x]),int(fg[y][x]),int(fr[y][x]))



    # 11.12added
    def getPix(self, point):
        return self.bitmap[point[1]][point[0]]





if __name__ == '__main__':
    img =readImg('../bear1107.bmp')
    img.Gauss_HPF()


    #img.save_to(filename="../bear1107.bmp", data = bitmap)




