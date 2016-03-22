import sys
import imp
import types


import omniORB
from omniORB import tcInternal


def _register_class(c, mod_path):
    obj = None
    for name in mod_path.split('.'):
        if not obj:
            obj = sys.modules[name] # resolve anchor via system modules
            continue
        if hasattr(obj, name):
            subobj = getattr(obj, name)
            obj = subobj
        else:
            m = imp.new_module('.'.join((obj.__name__, name)))
            setattr(obj, name, m)
            obj = getattr(obj, name)

    desc = omniORB.typeMapping[c._NP_RepositoryId]
            
    def _default(self, **kwargs):
        d = _dict_from_desc(desc)
        d.update(**kwargs)
        return c.__init__(self, **d)
    
    new_class = type(c.__name__, (c, object,),
                      {'__module__': obj.__name__,
                       '__init__': _default,
                       '__doc__': str(desc)})
    setattr(obj, c.__name__, new_class)


def _find_classes(module):
    for k, v in module.__dict__.iteritems():
        if type(v) is types.ClassType:
            # strip _gen.orogen and Corba from module name
            mod_name = '.'.join(module.__name__.split('.')[3:-1])
            mod_name = '.'.join(('pyrock', mod_name))
            _register_class(v, mod_name)

            
def _walk(package):
    for k, v in  package.__dict__.iteritems():
        if type(v) is types.ModuleType:
            if k is 'Corba':
                _find_classes(v)
            elif k not in ['pyrock', 'omniORB']:
                _walk(v)
                

def _dict_from_desc(desc):

    # TODO tv_enum 17
    # TODO tv_alias
    
    if type(desc) is int:
        if desc is tcInternal.tv_null:
            return None

        if desc is tcInternal.tv_boolean:
            return bool(False)

        elif desc in [tcInternal.tv_char,
                    tcInternal.tv_octet,
                    tcInternal.tv_short,
                    tcInternal.tv_ushort]:
            return int(0)
        
        elif desc in [tcInternal.tv_long,
                    tcInternal.tv_ulong,
                    tcInternal.tv_longlong,
                    tcInternal.tv_ulonglong]:
            return long(0)

        elif desc in [tcInternal.tv_float, tcInternal.tv_double]:
            return float(0.0)
        
        elif desc in [tcInternal.tv_char, tcInternal.tv_string]:
            return ''

        else:
            raise Exception('Type not implemented: %s'%desc)

    k = desc[0]
    
    if k in [tcInternal.tv_any, tcInternal.tv_alias]:
        raise Exception('Type not implemented: %s'%k)

    elif k is tcInternal.tv_enum:
        pass
    
    elif k is tcInternal.tv_struct:
        d = {}
        for i in range(4, len(desc), 2):
            sm = desc[i]
            sd = desc[i+1]
            d[sm] = _dict_from_desc(sd)
        return d

    elif k in [tcInternal.tv_sequence, tcInternal.tv_array]:
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
del(_gen.orogen)


# import overwrites
import base


# RTT
from _gen import RTT
RTT.DEFAULT_POLICY = RTT.corba.CConnPolicy(RTT.corba.CData, False, RTT.corba.CLockFree, False, 1, 1, 1, '')


# init nameservice
_orb = omniORB.CORBA.ORB_init([], omniORB.CORBA.ORB_ID)

from .nameservice import NameService
nameservice = NameService(_orb)
