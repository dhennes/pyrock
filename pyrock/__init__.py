import sys, os
sys.path.append(os.path.join(__path__[0], 'build')) # TODO fix import hack

import RTT
import orogen

from omniORB import CORBA
_orb = CORBA.ORB_init([], CORBA.ORB_ID)

from .nameservice import NameService
nameservice = NameService(_orb)

import base
