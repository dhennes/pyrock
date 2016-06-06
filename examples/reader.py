from __future__ import print_function
import pyrock

proxy = pyrock.TaskProxy('orogen_default_message_producer__Task')
proxy.subscripe('messages', lambda msg: print(msg.content, msg.time.__repr__()))

if not proxy.is_configured():
    proxy.configure()

if not proxy.is_running():
    proxy.start()

proxy.spin()
