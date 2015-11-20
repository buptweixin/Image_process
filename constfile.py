#encoding=utf-8
__author__ = 'weixin'

class _const:
    class ConstError(TypeError): pass
    class ConstCaseError(ConstError): pass

    def __setattr__(self, key, value):
        if __dict__.has_key(key):
            raise co