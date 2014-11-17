#!/usr/bin/env python3

""" This module is used as client for the control channel of detours. """

import sys
from pydetours.comm import DefaultChannel


keep_going = True


def status(channel):
    header = {'action': 'status'}
    channel.send([header])
    try:
        response = channel.recv(20*1000)  # 5 secs form timeout
    except Exception as e:
        print("Unknown status: {}".format(str(e)))
    else:
        response_header = response[0]
        print(response_header)
        status_dict = response_header['return']
        for elm, status in status_dict.items():
            print("### {} --> {}".format(elm, status))


def terminate(channel):
    header = {'action': 'terminate'}
    channel.send([header])
    try:
        response = channel.recv(5*1000)  # 5 secs form timeout
    except Exception as e:
        print("Unreached server: {}".format(str(e)))
    else:
        response_header = response[0]
        print("{}\n".format(response_header['return']))


def quit(channel):
    print("Leaving client...\n")
    global keep_going
    keep_going = False
    sys.exit(0)


def unkown_command():
    print("Unknown command. Valid commands are: %s\n".format(commands.keys))


commands = {'status': status,
            'terminate': terminate,
            'quit': quit
            }


def start_service(endpoint):
    control = DefaultChannel(endpoint)
    control.connect()

    global keep_going
    while keep_going:
        command = input('>')
        command_ftn = commands.get(command, unkown_command)
        command_ftn(control)
        print()


if __name__ == '__main__':
    try:
        endpoint = sys.argv[1]
    except Exception:
        print("Usage: control_service <endpoint>")
        sys.exit(2)
    else:

        start_service(endpoint)
