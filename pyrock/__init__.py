import sys
import imp as _imp
import types as _types


import omniORB
from omniORB import tcInternal as _tcInternal


_class_repo = {}

def _register_class(C, mod_path):
    obj = sys.modules[__name__]
    for name in mod_path:
        if hasattr(obj, name):
            subobj = getattr(obj, name)
            obj = subobj
        else:
            m = _imp.new_module('.'.join((obj.__name__, name)))
            setattr(obj, name, m)
            obj = getattr(obj, name)

    desc = omniORB.typeMapping[C._NP_RepositoryId]
    if desc[0] is not _tcInternal.tv_struct:
        # skip non structs
        return

    C._old_ctor = C.__init__

    def ctor(self, *args, **kwargs):
        if len(args):
            C._old_ctor(self, *args)
        else:
            d = _dict_from_desc(desc, depth=0)
            d.update(**kwargs)
            C._old_ctor(self, **d)

    # override constructor and module name, then register with new module
    C.__init__ = ctor
    C.__module__ = obj.__name__
    C.__doc__ = desc  # TODO parsing of type description
    setattr(obj, C.__name__, C)
    _class_repo[C._NP_RepositoryId] = C

def _find_classes(module):
    for k, v in module.__dict__.iteritems():
        if type(v) is _types.ClassType:
            # strip _gen.orogen and Corba from module name
            mod_path = module.__name__.split('.')[3:-1]
            _register_class(v, mod_path)


def _walk(package):
    for k, v in package.__dict__.iteritems():
        if type(v) is _types.ModuleType:
            if k is 'Corba':
                _find_classes(v)
            elif k not in ['pyrock', 'omniORB']:
                _walk(v)


def _dict_from_desc(desc, depth):
    if type(desc) is int:
        tv = desc
        if tv is _tcInternal.tv_null:
            return None

        if tv is _tcInternal.tv_boolean:
            return bool(False)

        elif tv in [_tcInternal.tv_char,
                      _tcInternal.tv_octet,
                      _tcInternal.tv_short,
                      _tcInternal.tv_ushort]:
            return int(0)

        elif tv in [_tcInternal.tv_long,
                      _tcInternal.tv_ulong,
                      _tcInternal.tv_longlong,
                      _tcInternal.tv_ulonglong]:
            return long(0)

        elif tv in [_tcInternal.tv_float,
                      _tcInternal.tv_double]:
            return float(0.0)

        elif tv in [_tcInternal.tv_char,
                      _tcInternal.tv_string]:
            return ''

        else:
            raise Exception('Type not implemented: %s' % desc)

    else:
        tv = desc[0]
        if tv is _tcInternal.tv_string:
            # TODO what are desc[1:] for in a tv_string description?
            return _dict_from_desc(tv, depth+1)

        elif tv is _tcInternal.tv_alias and len(desc) is 4:
            return _dict_from_desc(desc[3], depth+1)

        elif tv is _tcInternal.tv_struct:
            d = {}
            for i in range(4, len(desc), 2):
                field_name, field_desc = desc[i:i+2]
                d[field_name] = _dict_from_desc(field_desc, depth+1)
            if depth > 0:
                return _class_repo[desc[1]._NP_RepositoryId](**d)
            else:
                return d

        elif tv in [_tcInternal.tv_sequence, _tcInternal.tv_array] and (len(desc) is 3 and
                                                                   type(desc[2]) is int):
            return [_dict_from_desc(desc[1], depth+1)] * desc[2]

        elif tv is _tcInternal.tv_enum:
            enum_name = desc[1].split(':')[1].split('/')
            enum = reduce(getattr, enum_name, _gen)
            return enum._items[0]

        else:
            raise Exception('Type not implemented: %s' % str(desc))


# register type classes in pyrock namespace
import _gen.orogen
_walk(_gen.orogen)


# overwrites for base
import _base
del(_base)


# RTT
from _gen import RTT

def create_default_policy():
    return RTT.corba.CConnPolicy(RTT.corba.CData, True, RTT.corba.CLockFree, False, 0, 1, 0, '')

# init nameservice
_orb = omniORB.CORBA.ORB_init([], omniORB.CORBA.ORB_ID)

from .nameservice import NameService
nameservice = NameService(_orb)

from .proxy import TaskProxy, Port
