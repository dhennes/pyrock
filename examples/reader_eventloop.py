import time
import sys


import omniORB.any as _any
import omniORB.CORBA as CORBA
import pyrock

from collections import deque


class TaskProxy:

    def __init__(self, taskname):
        self._task = pyrock.nameservice.get(taskname)
        desc = self._task.ports().getPortDescriptions()
        self.output_ports = {
            p.name: p.type_name for p in desc if p.type is pyrock.RTT.corba.COutput}
        self.input_ports = {
            p.name: p.type_name for p in desc if p.type is pyrock.RTT.corba.CInput}
        self.subscriptions = deque()

    def subscripe(self, portname, callback, policy=pyrock.create_default_policy()):
        assert portname in self.output_ports.keys()
        channel, policy = self._task.ports().buildChannelInput(
            portname, policy)
        sub = Subscription(
            portname, callback, self.output_ports[portname], channel, policy)
        self.subscriptions.append(sub)

    def configure(self):
        self._task.configure()

    def start(self):
        self._task.configure()

    def stop(self):
        self._task.configure()

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
            self.teardown()
            sys.exit()

    def teardown(self):
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


def message_callback(msg):
    print('[%d] %s' % (msg.time.microseconds, msg.content))


def state_callback(state):
    print('state: %d' % state)


task = TaskProxy('orogen_default_message_producer__Task')
task.subscripe('messages', message_callback)
task.subscripe('state', state_callback)


task.configure()
task.start()

task.spin()
