import sys
import collections


import omniORB.any as _any
import pyrock


class Port(object):

    COutput = pyrock.RTT.corba.COutput
    CInput = pyrock.RTT.corba.CInput

    def __init__(self, task, name, type_name, port_type):
        self.task = task
        self.name = name
        self.type_name = type_name
        self.port_type = port_type


class Subscriber:

    def __init__(self, portname, callback, channel, policy):
        self.portname = portname
        self.callback = callback
        self.channel = channel
        self.policy = policy

    def disconnect(self):
        self.channel.disconnect()
        self.channel = None

    def __repr__(self):
        return 'Subscription \'%s\' -> %s' % (self.portname,
                                              self.callback.__name__)


class Publisher:

    def __init__(self, portname, channel, policy):
        self.portname = portname
        self.channel = channel
        self.policy = policy

    def write(self, msg):
        self.channel.write(_any.to_any(msg))

    def disconnect(self):
        self.channel.disconnect()

    def __repr__(self):
        return 'Publisher \'%s\'' % self.portname


class TaskProxy(object):

    def __init__(self, taskname):
        self.name = taskname
        self._task = pyrock.nameservice.get(self.name)
        self.subscribers = {}
        self.publishers = {}
        self._eventq = collections.deque()

    def ports(self, port_type=[Port.COutput, Port.CInput]):
        if not isinstance(port_type, collections.Iterable):
            port_type = [port_type]
        desc = self._task.ports().getPortDescriptions()
        return {p.name: Port(self, p.name, p.type_name, p.type)
                for p in desc if p.type in port_type}

    def publisher(self, portname, policy=pyrock.create_default_policy()):
        if portname in self.publishers.keys():
            return self.publishers[portname]
        channel, policy = self._task.ports().buildChannelOutput(portname, policy)
        pub = Publisher(portname, channel, policy)
        self.publishers[portname] = pub
        return pub

    def subscriber(self, portname, callback, policy=pyrock.create_default_policy()):
        if portname in self.subscribers.keys():
            return self.subscribers[portname]
        channel, policy = self._task.ports().buildChannelInput(portname, policy)
        sub = Subscriber(portname, callback, channel, policy)
        self.subscribers[portname] = sub
        self._eventq.append(sub)
        return sub

    def is_connected(self):
        try:
            self._task.getTaskState()
        except pyrock.omniORB.CORBA.TRANSIENT:
            return False
        return True

    def state(self):
        if not self.is_connected():
            return None
        return self._task.getTaskState()

    def is_configured(self):
        return self._task.isConfigured()

    def is_running(self):
        return self._task.isRunning()

    def configure(self):
        return self._task.configure()

    def cleanup(self):
        return self._task.cleanup()

    def start(self):
        return self._task.start()

    def stop(self):
        return self._task.stop()

    def spin_once(self):
        sub = self._eventq.popleft()
        if not sub.channel:
            return # no reschedule needed
        new, res = sub.channel.read(False)
        if new is pyrock.RTT.corba.CNewData:  # new data
            msg = res.value()
            sub.callback(msg)
        self._eventq.append(sub)  # reschedule

    def spin(self):
        try:
            while True:
                self.spin_once()

        except KeyboardInterrupt:
            self._teardown()
            sys.exit()

    def _teardown(self):
        self._eventq.clear()
        map(lambda s: s.disconnect(), self.subscribers.values())
        map(lambda p: p.disconnect(), self.publishers.values())
