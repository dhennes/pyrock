from time import time
from datetime import datetime

import pyrock

@staticmethod
def now():
    usecs = long(time() * 1000000L)
    return pyrock.base.Time(microseconds=usecs)
pyrock.base.Time.now = now
del(now)

def repr(self):
    return datetime.fromtimestamp(self.microseconds/1000000.).strftime('%Y-%m-%d %H:%M:%S.%f')
pyrock.base.Time.__repr__ = repr
del(repr)
