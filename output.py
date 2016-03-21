#import pyrock
from pyrock import RTT, nameservice, orogen
import omniORB.any as _any


#from pyrock import orogen
#from orogen.wrappers.Corba import *

names = nameservice.names()
print names

#task = nameservice.get('orogen_default_tut_brownian__Task') # last one usually is a logger
#task = nameservice.get('orogen_default_message_consumer__Task') # last one usually is a logger
task = nameservice.get('orocosrb_13758') # last one usually is a logger

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
#server_channel, cp = ports.buildChannelOutput('messages', cp)
server_channel, cp = ports.buildChannelInput('/rock_tutorial_control.motion_command.2', cp)


# configure must be called after port connection, even if already configured
task.configure()
print task.isConfigured()

task.start()
print task.isRunning()


# import time
# while True:
#     t = orogen.base.Corba.Time(0)
#     msg = orogen.message_driver.Corba.Message('hi', t)
#     print msg
#     server_channel.write(_any.to_any(msg))
#     time.sleep(1)

# input loop

output_msg = None
while True:
    new, res = server_channel.read(False) # flag: repeat old
    if new is RTT.corba.CNewData: # and res.value():
        if res.value().translation > 0.5:
            output_msg = res
        print res
        #msg = _any.from_any(res, keep_structs=True)
        #print msg
