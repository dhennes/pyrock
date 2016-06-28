import argparse

import pyrock


def ports2str(ports):
    return '\n  - '.join([''] + ['%s [%s]' % (n, t) for n, t in ports.iteritems()])


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


def cmd_info(taskname):
    task = pyrock.TaskProxy(taskname)
    print("""Task [%s]

State: %s

Input ports:%s

Output ports:%s
""" % (task.name, task.state(), ports2str(task.input_ports), ports2str(task.output_ports)))


def main():
    parser = argparse.ArgumentParser(description='rocktask is a commandline tool for printing information about Rock tasks.')
    subparsers = parser.add_subparsers(help='Commands', dest='command')

    # list
    list_parser = subparsers.add_parser('list', help='list all tasks')
    list_parser.add_argument('-s', '--state', dest='print_state', const=True, default=False, action='store_const', help='print state')

    # info
    subparsers.add_parser('info', help='print information about task').add_argument('taskname', help='taskname')

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
        if args.command in ['start', 'stop', 'cleanup', 'configure']:
            cmd_call(args.taskname, args.command)
            

    except Exception as e:
        print('Ups! Something went wrong!\n' + e)
        sys.exit(1)
