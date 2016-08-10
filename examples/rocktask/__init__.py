from __future__ import print_function
import sys
import argparse
import json

import pyrock


class DictEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def ports2str(ports):
    return '\n  - '.join([''] + ['%s [%s]' % (p.name, p.type_name) for p in ports])


def cmd_call(taskname, command):
    task = pyrock.TaskProxy(taskname)
    getattr(task, command)()


def cmd_list(state=False):
    names = pyrock.nameservice.names()
    if not names:
        return
    if state:
        print('\n'.join(['%s [%s]' % (name, pyrock.TaskProxy(name).state()) for name in names]))
    else:
        print('\n'.join(names))


def cmd_ports(taskname, porttype):
    task = pyrock.TaskProxy(taskname)
    portnames = [p.name for p in task.ports(port_type=porttype).values()]
    if not portnames:
        return
    print('\n'.join(portnames))


def cmd_info(taskname):
    task = pyrock.TaskProxy(taskname)
    print("""Task [%s]

State: %s

Input ports:%s

Output ports:%s
""" % (task.name, task.state(),
       ports2str([p for p in task.ports(port_type=pyrock.Port.CInput).values()]),
       ports2str([p for p in task.ports(port_type=pyrock.Port.COutput).values()])))


def cmd_echo(taskname, portname, indent=None):
    proxy = pyrock.TaskProxy(taskname)
    proxy.subscriber(portname, lambda msg: print(json.dumps(msg, cls=DictEncoder, indent=indent)))
    proxy.spin()


def main():
    parser = argparse.ArgumentParser(description='rocktask is a commandline tool for printing information about Rock tasks.')
    subparsers = parser.add_subparsers(help='Commands', dest='command')

    # list
    list_parser = subparsers.add_parser('list', help='list all tasks')
    list_parser.add_argument('-s', '--state', dest='print_state', const=True, default=False, action='store_const', help='print state')

    # info
    subparsers.add_parser('info', help='print information about task').add_argument('taskname', help='taskname')

    # ports
    subparsers.add_parser('out', help='list all output ports').add_argument('taskname', help='taskname')
    subparsers.add_parser('in', help='list all input ports').add_argument('taskname', help='taskname')
    echo_parser = subparsers.add_parser('echo', help='print messages to screen')
    echo_parser.add_argument('taskname', help='taskname')
    echo_parser.add_argument('portname', help='portname')
    echo_parser.add_argument('-p', '--pretty', dest='indent', const=4, default=None, action='store_const', help='pretty output')

    # start/stop/cleanup/configure
    subparsers.add_parser('start', help='start the task').add_argument('taskname', help='taskname')
    subparsers.add_parser('stop', help='stop the task').add_argument('taskname', help='taskname')
    subparsers.add_parser('cleanup', help='cleanup the task').add_argument('taskname', help='taskname')
    subparsers.add_parser('configure', help='configure the task').add_argument('taskname', help='taskname')

    args = parser.parse_args()

    try:

        if args.command == 'list':
            cmd_list(args.print_state)
        if args.command == 'info':
            cmd_info(args.taskname)
        if args.command == 'out':
            cmd_ports(args.taskname, pyrock.Port.COutput)
        if args.command == 'in':
            cmd_ports(args.taskname, pyrock.Port.CInput)
        if args.command == 'echo':
            cmd_echo(args.taskname, args.portname, indent=args.indent)
        if args.command in ['start', 'stop', 'cleanup', 'configure']:
            cmd_call(args.taskname, args.command)


    except Exception as e:
        sys.stderr.write('Ups! Something went wrong!\n' + str(e) + '\n')
        sys.exit(1)
