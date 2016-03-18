import sys
sys.path.append('pyrock/build')

import RTT
import orogen

from omniORB import CORBA
_orb = CORBA.ORB_init([], CORBA.ORB_ID)

from nameservice import NameService
nameservice = NameService(_orb)

# print nameservice.get_names()
# task = nameservice.get('orogen_default_lidar_velodyne__VelodynePointcloud')
