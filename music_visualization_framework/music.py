#! /usr/bin/python3
import argparse
import json
import socket
import sys

# This module interacts with the music daemon

def add_listener(c, args):
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect('/tmp/musicd')
        command = {'type': 'command', 'command': c, 'args': args}
        s.sendall(json.dumps(command).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    return res

def query(query):
    s = None
    try:
        s = socket.socket(socket.AF_UNIX)
        s.connect('/tmp/litd')
        msg = {'type': 'query', 'query': query}
        s.sendall(json.dumps(msg).encode())
    except Exception as e:
        s.close()
        raise conn_error(e)

    res = get_response(s)
    s.close()
    return res

def get_response(s):
    response = ''
    try:
        #First 32 bytes are a string representation of the message length
        expected = int(s.recv(32).decode())
        received = 0
        while received < expected:
            msg = s.recv(1024).decode()
            received += 1024
            response += msg
    except Exception as e:
        raise conn_error(e)
    return json.loads(response)

def add_beat_listener(beat, func):
    add_listener('add_beat_listener', (beat, func))

def add_total_level_beat_listener(beat, func):
    add_listener('add_total_level_beat_listener', (func,))

def add_threshold_change_listener(func):
    add_listener('add_threshold_change_listener', (func,))

def add_level_change_listener(beat, func):
    add_listener('add_level_change_listener', (func,))

def conn_error(e):
    return Exception('Music Visualization Daemon error: {}'.format(e))

def response_error(res):
    return Exception('Daemon returned a non-zero response code(rc={}). Error={}'.format(res.get('rc', None), res.get('result', 'No message')))

if __name__ == '__main__':
    print('This is a library that must be imported to be used')
 
