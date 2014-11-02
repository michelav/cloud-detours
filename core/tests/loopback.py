#!/usr/bin/env python3

import zmq
import sys
import json

# from zhelpers import dump


def loopback(header_dict, zmq_message):
    """
    """
    msg_list = []
    resp_dict = {"control": "back"}
    next_pos = 0
    json_header = json.dumps(resp_dict)
    msg_list.insert(next_pos, json_header.encode())
    next_pos += 1

    if 'True' == header_dict.get('payload', 'False'):
        msg_list.insert(next_pos, zmq_message[1])
        next_pos += 1
        pass
    msg_list.insert(2, '[END]'.encode())
    next_pos += 1
    print("Looping Back...")
    return msg_list


def ping(header_dict, zmq_message):
    """
    """
    msg_list = []
    resp_dict = {"control": "pong"}
    next_pos = 0
    json_header = json.dumps(resp_dict)
    msg_list.insert(next_pos, json_header.encode())
    next_pos += 1

    if 'True' == header_dict.get('payload', 'False'):
        msg_list.insert(next_pos, zmq_message[1])
        next_pos += 1
        pass
    msg_list.insert(2, '[END]'.encode())
    next_pos += 1
    print("Pinging...")
    return msg_list


def handle_message(zmq_message):
    evt_dict = json.loads(zmq_message[0].decode())
    dispatcher_ftn = control_dict[evt_dict['control']]
    evt_response = dispatcher_ftn(evt_dict, zmq_message)
    return evt_response


def terminate(zmq_message):
    if not zmq_message:
        return True
    evt_dict = json.loads(zmq_message[0].decode())
    return 'terminate' == evt_dict['control']

control_dict = {'loop': loopback,
                'ping': ping,
                'terminate': terminate
                }


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('I: Syntax: %s <endpoint>' % sys.argv[0])
        sys.exit(0)

    endpoint = sys.argv[1]
    context = zmq.Context()
    server = context.socket(zmq.REP)
    server.bind(endpoint)

    print('I: Echo service is ready at %s' % endpoint)
    while True:
        msg = server.recv_multipart()
        if terminate(msg):
            print("Terminating...")
            break  # Interrupted
        msg_list = handle_message(msg)
  #      dump(msg_list)
        server.send_multipart(msg_list)

    server.setsockopt(zmq.LINGER, 0)  # Terminate immediately
