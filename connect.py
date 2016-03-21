from pyrock import RTT, nameservice, orogen

consumer = nameservice.get('orogen_default_message_consumer__Task')
producer = nameservice.get('orogen_default_message_producer__Task')

for t in [consumer, producer]:
    if t.isRunning():
        t.stop()
        print('%s stopped'%t.getName())        
    
# easy way
#consumer.connectPorts(producer)

# hard way
consumer_ports = consumer.ports()
producer_ports = producer.ports()

print consumer_ports.getPorts()
print producer_ports.getPorts()


cm = RTT.corba.CData
clp = RTT.corba.CLockFree
cp = RTT.corba.CConnPolicy(cm, False, clp, False, 1, 1, 1, 'cp')

producer_ports.createConnection('messages', consumer_ports, 'messages', cp)
#producer_ports.removeConnection('messages', consumer_ports, 'messages')


for t in [consumer, producer]:
    t.configure()
    t.start()
