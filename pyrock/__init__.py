import sys
import imp as _imp
import types as _types


import omniORB
from omniORB import tcInternal as _tcInternal


def _register_class(c, mod_path):
    obj = sys.modules[__name__]
    for name in mod_path:
        if hasattr(obj, name):
            subobj = getattr(obj, name)
            obj = subobj
        else:
            m = _imp.new_module('.'.join((obj.__name__, name)))
            setattr(obj, name, m)
            obj = getattr(obj, name)

    desc = omniORB.typeMapping[c._NP_RepositoryId]

    c._old__init__ = c.__init__
    def __init__(self, *args, **kwargs):
        if len(args):
            return c._old__init__(self, *args)
        else:
            d = _dict_from_desc(desc)
            d.update(**kwargs)
            return c._old__init__(self, **d)

    # override constructor and module name, then register with new module
    c.__init__ = __init__
    c.__module__ = obj.__name__
    c.__doc__ = desc # TODO parsing of type description
    setattr(obj, c.__name__, c)


def _find_classes(module):
    for k, v in module.__dict__.iteritems():
        if type(v) is _types.ClassType:
            # strip _gen.orogen and Corba from module name
            mod_path = module.__name__.split('.')[3:-1]
            _register_class(v, mod_path)


def _walk(package):
    for k, v in  package.__dict__.iteritems():
        if type(v) is _types.ModuleType:
            if k is 'Corba':
                _find_classes(v)
            elif k not in ['pyrock', 'omniORB']:
                _walk(v)


def _dict_from_desc(desc):

    # TODO tv_enum 17
    # TODO tv_alias

    if type(desc) is int:
        if desc is _tcInternal.tv_null:
            return None

        if desc is _tcInternal.tv_boolean:
            return bool(False)

        elif desc in [_tcInternal.tv_char,
                    _tcInternal.tv_octet,
                    _tcInternal.tv_short,
                    _tcInternal.tv_ushort]:
            return int(0)

        elif desc in [_tcInternal.tv_long,
                    _tcInternal.tv_ulong,
                    _tcInternal.tv_longlong,
                    _tcInternal.tv_ulonglong]:
            return long(0)

        elif desc in [_tcInternal.tv_float, _tcInternal.tv_double]:
            return float(0.0)

        elif desc in [_tcInternal.tv_char, _tcInternal.tv_string]:
            return ''

        else:
            raise Exception('Type not implemented: %s'%desc)

    k = desc[0]

    if k in [_tcInternal.tv_any, _tcInternal.tv_alias]:
        raise Exception('Type not implemented: %s'%k)

    elif k is _tcInternal.tv_enum:
        pass

    elif k is _tcInternal.tv_struct:
        d = {}
        for i in range(4, len(desc), 2):
            sm = desc[i]
            sd = desc[i+1]
            d[sm] = _dict_from_desc(sd)
        return d

    elif k in [_tcInternal.tv_sequence, _tcInternal.tv_array]:
        if not (len(desc) is 3 and type(desc[1]) is int and type(desc[2]) is int):
            raise Exception('Type not implemented: %s'%desc)
        sd = desc[1]
        rl = [_dict_from_desc(sd)] * desc[2]
        return rl
    else:
        return _dict_from_desc(k)


# register type classes in pyrock namespace
import _gen.orogen
_walk(_gen.orogen)

# import overwrites
from _base import Time
base.Time = Time
del(Time)


# RTT
from _gen import RTT
RTT.DEFAULT_POLICY = RTT.corba.CConnPolicy(RTT.corba.CData, False, RTT.corba.CLockFree, False, 1, 1, 1, '')


# init nameservice
_orb = omniORB.CORBA.ORB_init([], omniORB.CORBA.ORB_ID)

from .nameservice import NameService
nameservice = NameService(_orb)
