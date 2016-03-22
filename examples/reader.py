import time, sys


import omniORB.any as _any
import omniORB.CORBA as CORBA
import pyrock

task = pyrock.nameservice.get('orogen_default_message_producer__Task')
print('Connected to %s'%task.getName())

if task.isRunning():
    task.stop()

ports = task.ports()
#print ports.getPortDescriptions()

portname = 'messages'
channel, policy = ports.buildChannelInput(portname, pyrock.RTT.DEFAULT_POLICY)

task.configure()
if not task.isConfigured():
    raise Exception('Task is not yet configured')

task.start()
if not task.isRunning():
    raise Exception('Task is not running')

while True:
    try:
        new, res = channel.read(False)
        if new is pyrock.RTT.corba.CNewData:
            v = res.value(CORBA.TypeCode(pyrock.message_driver.Message))
            if v is not None:
                print v

    except KeyboardInterrupt:
        channel.disconnect()
        sys.exit()
