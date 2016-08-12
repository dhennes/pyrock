import sys
import time

import pyrock
import omniORB.any as _any

proxy = pyrock.TaskProxy('message_consumer')
pub = proxy.publisher('messages')

if not proxy.is_configured():
    proxy.configure()

if not proxy.is_running():
    proxy.start()

while True:
    msg = pyrock.message_driver.Message()
    msg.time = pyrock.base.Time.now()
    msg.content = 'hello'

    print(msg)

    pub.write(msg)
    time.sleep(1)
