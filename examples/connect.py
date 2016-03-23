import sys
import time

import pyrock


consumer = pyrock.nameservice.get('orogen_default_message_consumer__Task')
producer = pyrock.nameservice.get('orogen_default_message_producer__Task')

for t in [consumer, producer]:
    if t.isRunning():
        t.stop()
        print('%s stopped' % t.getName())

# easy way
# consumer.connectPorts(producer)

# hard(er) way
consumer_ports = consumer.ports()
producer_ports = producer.ports()

producer_ports.createConnection(
    'messages', consumer_ports, 'messages', pyrock.RTT.DEFAULT_POLICY)

for t in [consumer, producer]:
    t.configure()
    t.start()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        producer_ports.removeConnection('messages', consumer_ports, 'messages')
        sys.exit()
