import time as _time

from . import orogen

class Time(orogen.base.Corba.Time):

    @staticmethod
    def now():
        usecs = long(_time.time() * 1000000L)
        return Time(microseconds=usecs)
