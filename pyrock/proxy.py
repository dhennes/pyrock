import pyrock

import sys
from collections import deque



class Port(object):

    COutput = pyrock.RTT.corba.COutput
    CInput = pyrock.RTT.corba.CInput

    def __init__(self, task, name, type_name, port_type):
        self.task = task
        self.name = name
        self.type_name = type_name
        self.port_type = port_type
 

class TaskProxy(object):

    def __init__(self, taskname):
        self.name = taskname
        self._task = pyrock.nameservice.get(self.name)

        self.subscriptions = deque()
        self.ports = {}

        if self.is_connected():
            desc = self._task.ports().getPortDescriptions()
            self.ports = {p.name: Port(self, p.name, p.type_name, p.type) for p in desc}


    def subscripe(self, portname, callback, policy=pyrock.create_default_policy()):
        # assert portname in self.output_ports.keys()
        channel, policy = self._task.ports().buildChannelInput(
            portname, policy)
        sub = Subscription(
            portname, callback, self.ports[portname], channel, policy)
        self.subscriptions.append(sub)

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
        sub = self.subscriptions.popleft()
        new, res = sub.channel.read(False)
        if new is pyrock.RTT.corba.CNewData:  # new data
            msg = res.value()
            sub.callback(msg)
        self.subscriptions.append(sub)  # reschedule

    def spin(self):
        try:
            while True:
                self.spin_once()

        except KeyboardInterrupt:
            self._teardown()
            sys.exit()

    def _teardown(self):
        map(lambda sub: sub.channel.disconnect(), self.subscriptions)


class Subscription:

    def __init__(self, portname, callback, type_name, channel, policy):
        self.portname = portname
        self.callback = callback
        self.type_name = type_name
        self.channel = channel
        self.policy = policy

    def __repr__(self):
        return 'Subscription \'%s\' (%s) -> %s' % (self.portname,
                                                   self.type_name,
                                                   self.callback.__name__)
