#encoding=utf-8

import struct
from math import ceil
import StringIO

import random

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
        print struct.unpack_from("<i", self.raw_data, SIZE_OFFSET)[0]
        self.height = struct.unpack_from("<i", self.raw_data, HEIGHT_OFFSET)[0]
        self.data_offset = ord(self.raw_data[DATA_OFFSET])
        print "data offset:", self.data_offset
        print "bisize", struct.unpack_from("<i", self.raw_data, BISIZE_OFFSET)[0]
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
        return self.bitmap

    def save_to(self, data, filename):
        '''Export the bmp saving the changes done to the bitmap'''
        print (len(data)*len(data[0]*3))+54
        ##############
        #     BMP头文件
        #############
        width = len(data)
        height = len(data[0])
        width_byte = width*(self.bpp/8)
        rowstride = ceil(width_byte/4.0)*4
        padding = int(rowstride - width_byte)

        raw_copy = StringIO.StringIO()
        raw_copy.write(struct.pack('c', 'B'))
        print "rawdata",raw_copy.read()
        raw_copy.write(struct.pack('c', 'M'))
        bfSize = rowstride*height + 54
        bfSize = struct.pack('<I', bfSize)
        raw_copy.write(bfSize)
        raw_copy.write(struct.pack('<h', 0)) # 保留字节1必须为0
        raw_copy.write(struct.pack('<h', 0)) # 保留字节2必须为0
        raw_copy.write(struct.pack('<I', 54)) # 从文件头到实际数据的偏移量，没有调色板情况为54


        #######
        #   位图信息头
        ######
        raw_copy.write(struct.pack('<i', 14)) # BITMAPINFOHEADER所需字节数
        raw_copy.write(struct.pack('<i', rowstride)) # 以像素为单位的图像宽度
        raw_copy.write(struct.pack('<i', height)) # 以像素为单位的图像
        raw_copy.write(struct.pack('<h', 1)) # 颜色平面数， 总被设为1
        raw_copy.write(struct.pack('<h', 24)) # 比特数/像素 24位图为24
        raw_copy.write(struct.pack('<i', 0)) # 图片压缩类型，0 不压缩（BI_RGB）
        raw_copy.write(struct.pack('<i', 0)) # 图像大小, 当为BI_RGB格式时， 可设置为0
        raw_copy.write(struct.pack('<i', 0)) # 水平分辨率，设为缺省值0
        raw_copy.write(struct.pack('<i', 0)) # 垂直分辨率，设为缺省值0
        raw_copy.write(struct.pack('<i', 0)) # 颜色索引数, 0表示使用所有颜色索引
        raw_copy.write(struct.pack('<i', 0)) # 重要的索引， 0表示所有颜色索引都重要

        ########
        #     位图数据
        ######
        bitmap = self.bitmap[::-1]
        for y in xrange(len(data)):
            for x in xrange(len(data[0])):
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
            self.bitmap
            self.bitmap[:][distance:self.width] = self.bitmap[:][:self.width - distance]



if __name__ == '__main__':
    img =readImg('../bear.bmp')
    bitmap = img.create_bitmap()
    #img.rgb2gray()
    #img.mirror(VERTICAL)
    #img.move(distance=40, direction=HORIZONTAL)
    img.save_to(filename="../bear1107.bmp", data = bitmap)




