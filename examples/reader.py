from __future__ import print_function
import pyrock


proxy = pyrock.TaskProxy('message_producer')
proxy.subscriber('messages', lambda msg: print('[%s] %s' % (msg.time.to_str(), msg.content)))

if not proxy.is_configured():
    proxy.configure()

if not proxy.is_running():
    proxy.start()

proxy.spin()
