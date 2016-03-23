import time
import sys


import omniORB.any as _any
import pyrock


task = pyrock.nameservice.get('orogen_default_message_consumer__Task')
print('Connected to %s' % task.getName())

if task.isRunning():
    task.stop()

ports = task.ports()
# print ports.getPortDescriptions()

portname = 'messages'
channel, policy = ports.buildChannelOutput(portname, pyrock.RTT.DEFAULT_POLICY)

if not ports.channelReady(portname, channel, policy):
    raise Exception('Channel is not ready')

task.configure()
if not task.isConfigured():
    raise Exception('Task is not yet configured')

task.start()
if not task.isRunning():
    raise Exception('Task is not running')

while True:
    try:
        msg = pyrock.message_driver.Message()
        msg.time = pyrock.base.Time.now()
        msg.content = 'test'

        print msg

        channel.write(_any.to_any(msg))
        time.sleep(1)
    except KeyboardInterrupt:
        channel.disconnect()
        sys.exit()
