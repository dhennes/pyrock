import time as _time

import pyrock

class Time(pyrock.base.Time):

    @staticmethod
    def now():
        usecs = long(_time.time() * 1000000L)
        return Time(microseconds=usecs)
