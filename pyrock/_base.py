from time import time
from datetime import datetime

import pyrock


@classmethod
def now(cls):
    usecs = long(time() * 1000000L)
    return cls(microseconds=usecs)
pyrock.base.Time.now = now
del(now)


def to_str(self):
    return datetime.fromtimestamp(
            self.microseconds/1000000.).strftime('%Y-%m-%d %H:%M:%S.%f')
pyrock.base.Time.to_str = to_str
del(to_str)
