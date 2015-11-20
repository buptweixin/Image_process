#encoding=utf-8
__author__ = 'weixin'
"""
File Name: constfile,py
Description: 本文件将图片格式用到的偏移量等常量集中起来管理，并增加了常量检查机制
Author: Wei Xin
Change Activity:
    Created at 2015.11.20
"""

class _const:
    class ConstError(TypeError): pass
    class ConstCaseError(ConstError): pass

    def __setattr__(self, key, value):
        if self.__dict__.has_key(key):
            raise self.ConstError, "Can't change const. %s" % key
        if not key.isupper():
            raise self.ConstCaseError, \
        "const name '%s' is not all uppercase" % key
        self.__dict__[key] = value
import sys
sys.modules[__name__]=_const()
import constfile

constfile.FORMAT_OFFSET = int('0',16)
constfile.SIZE_OFFSET = int('2',16)
constfile.DATA_OFFSET = int('0a', 16)
constfile.BISIZE_OFFSET = int('0e', 16)
constfile.WIDTH_OFFSET = int('12',16)
constfile.HEIGHT_OFFSET = int('16',16)
constfile.BPP_OFFSET = int('1c',16)
constfile.BIX = int('26', 16)
constfile.BICLR = int('2e', 16)
constfile.HORIZONTAL = 0
constfile.VERTICAL = 1
