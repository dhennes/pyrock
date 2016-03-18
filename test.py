#import pyrock
from pyrock import RTT, nameservice
#from pyrock import orogen
#from orogen.wrappers.Corba import *

names = nameservice.names()
print names

task = nameservice.get('orogen_default_tut_brownian__Task') # last one usually is a logger
print task.getName()

if task.isRunning():
    print 'stopped task'
    task.stop()

ports = task.ports()
print ports.getPortDescriptions()


cm = RTT.corba.CData
clp = RTT.corba.CLockFree
cp = RTT.corba.CConnPolicy(cm, False, clp, False, 1, 1, 1, 'cp')
print cp
server_channel, cp = ports.buildChannelInput('cmd', cp)


# configure must be called after port connection, even if already configured
task.configure()
print task.isConfigured()

task.start()
print task.isRunning()

while True:
    new, res = server_channel.read(False) # flag: repeat old
    if new is RTT.corba.CNewData: # and res.value():
        r = res
        print res
        print res.value().__dict__
