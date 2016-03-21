#import pyrock
import pyrock
from pyrock import RTT, nameservice, orogen
import omniORB.any as _any


#from pyrock import orogen
#from orogen.wrappers.Corba import *

names = nameservice.names()
print names

#task = nameservice.get('orogen_default_tut_brownian__Task') # last one usually is a logger
task = nameservice.get('orogen_default_message_consumer__Task') # last one usually is a logge
#task = nameservice.get('rock_tutorial_control') # last one usually is a logger
#task = nameservice.get('orogen_default_message_producer__Task') # last one usually is a logger

print task.getName()

if task.isRunning():
    print 'stopped task'
    task.stop()

ports = task.ports()
print ports.getPortDescriptions()


portname = 'messages'

cm = RTT.corba.CData
clp = RTT.corba.CLockFree
cp = RTT.corba.CConnPolicy(cm, False, clp, False, 0, 0, 0, '')
print cp
server_channel, cp = ports.buildChannelOutput(portname, cp)
print cp

print ports.channelReady(portname, server_channel, cp)


# configure must be called after port connection, even if already configured
task.configure()
print task.isConfigured()

task.start()
print task.isRunning()

import time
while True:
    t = pyrock.base.Time.now()
    print t
    #t = orogen.base.Corba.Time(long(time.time() * 1000000L))
    msg = orogen.message_driver.Corba.Message(content=r'hi', time=t)
    print msg
    print _any.to_any(msg)
    server_channel.write(_any.to_any(msg))
    time.sleep(.1)

# # input loop
# while True:
#     new, res = server_channel.read(False) # flag: repeat old
#     if new is RTT.corba.CNewData: # and res.value():
#         msg = _any.from_any(res, keep_structs=True)
#         print msg
