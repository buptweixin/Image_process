#encoding=utf-8

import struct
from math import ceil

FORMAT_OFFSET = int('0',16)
SIZE_OFFSET = int('2',16)
DATA_OFFSET = int('0a', 16)
WiDTH_OFFSET = int('12',16)
HEIGHT_OFFSET = int('16',16)
BIBIT_OFFSET = int('1c',16)


class readImg:
    def __init__(self, filename):
        #初始化类， 参数为图像名
        bmpfile = open(filename)
        self.raw_data = bmpfile.read()
        if self.raw_data[0] != 'B' or self.raw_data[1] != 'M':
            raise TypeError, "The file is not a BMP image!"

        assert struct.unpack_from("<i", self.raw_data, BIBIT_OFFSET)[0] == 24
        self.width = struct.unpack_from("<i", self.raw_data, WiDTH_OFFSET)[0]
        self.height = struct.unpack_from("<i", self.raw_data, HEIGHT_OFFSET)[0]
        self.bpp = struct.unpack_from("<i", self.raw_data, BIBIT_OFFSET)[0]
        self.dataOff = struct.unpack_from("<i", self.raw_data, DATA_OFFSET)[0]
        self.bitmap = self.createBitmap()
        print self.height

    def getBitmap(self):
        return self.bitmap

    def createBitmap(self):
        bitmap = []

        #填充后的每行字节数
        rowsize = ceil(self.bpp * self.width / 32.0) * 4
        skip = int(rowsize - self.bpp*self.width/8)

        off = self.dataOff
        for col in xrange(self.height):
            bitmap.append([])

            for row in xrange(self.width):
                b = ord(self.raw_data[off])
                g = ord(self.raw_data[off+1])
                r = ord(self.raw_data[off+2])
                bitmap[col].append((r, g, b))
                off += 3
            off += skip
        # 由于bmp数据是从左下到右上的顺序的，所以对bitmap做逆序
        bitmap = bitmap[::-1]
        return bitmap

if __name__ == '__main__':
    img = readImg('../bear.bmp')
    bitmap = img.getBitmap()




