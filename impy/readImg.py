#encoding=utf-8

import struct
from math import ceil
import StringIO

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

    def saveBitmap(self, filename):
        raw_copy = StringIO.StringIO()
        bitmap = self.bitmap[::-1]

        width_bytes = self.width*(self.bpp/8)
        rowstride = ceil(width_bytes/4.0)*4
        padding = int(rowstride - width_bytes)

        # Same header as before until the width
        raw_copy.write(self.raw_data[:WiDTH_OFFSET])

        s = struct.Struct("<i")
        _w = s.pack(self.width)   # Transform width, height to
        _h = s.pack(self.height)  # little indian format
        raw_copy.write(_w)
        raw_copy.write(_h)

        # After the new width and height the header it's the same
        raw_copy.write(self.raw_data[HEIGHT_OFFSET+4:DATA_OFFSET])

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



if __name__ == '__main__':
    img = readImg('../bear.bmp')
    bitmap = img.getBitmap()
    img.saveBitmap("..bear2.bmp")




