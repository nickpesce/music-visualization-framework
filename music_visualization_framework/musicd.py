#! /usr/bin/python3
import argparse
import json
import logging
import os
import operator
import socket
import threading

from music_visualization_framework import music_analyzer

MAX_CONNECTIONS = 5
socket_path = '/tmp/musicd'
queries = {}
commands = {}
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(name)s:(%(lineno)d):%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

def setup():
    logger.info('setting up')

    parser = argparse.ArgumentParser(description='Start the music analyzer daemon')
    parser.add_argument('--device', '-d', dest='dev', type=str, default='/dev/ttyACM0',
                                help='The device path of the music serial source')
    args = parser.parse_args()
    app = music_analyzer.Analyzer(args.dev)
    app.start()
    queries.update({
            'num_bands': lambda _: app.num_bands,
            'bands': lambda _: app.bands,
            'thresholds': lambda _:app.thresholds,
            'beats': lambda _: app.beats,
            'time_since_last_beat': lambda _: app.time_since_last_beat,
            'total_volume': lambda _: app.total_volume,
            'time_since_last_total_volume_beat': lambda _: app.time_since_last_total_volume_beat,
            'error': error
    })
    commands.update({
            'add_beat_listener': (lambda b, f: app.beat_listeners[b].append(f)),
            'add_total_level_beat_listener': app.total_beat_listeners.append,
            'add_level_change_listener': app.level_change_listeners.append,
            'add_threshold_change_listener': app.threshold_change_listeners.append,
            'error': error
    })

def start():
    setup()
    logger.info('Starting music analyzer daemon')
    running = True
    serv = socket.socket(socket.AF_UNIX)
    try:
        os.remove(socket_path)
    except OSError as e:
        logger.warning('Got "{}" when trying to remove {}'.format(e, socket_path))
    try:
        # Allow created socket to have non-root read and write permissions
        os.umask(0o1)
        serv.bind(socket_path)
        serv.listen(MAX_CONNECTIONS)
        logger.info('Listening on {}'.format(socket_path))
        while running:
           conn, address = serv.accept()
           start_conn_thread(conn)
    except Exception as e:
        logger.error('musicd socket error: {}'.format(e))

def start_conn_thread(conn):
    def listener():
        while True:
            try:
                data = conn.recv(4096)
                if not data: break
                msg = data.decode()
                logger.info('received command: {}'.format(msg))
                resp = handle_command(msg).encode()
                logger.debug('responding: {}'.format(resp))
                # First 32 bytes is message length
                conn.send(str(len(resp)).zfill(32).encode())
                conn.send(resp)
            except Exception as e:
                logger.error('musicd connection error: {}'.format(e))

    thread = threading.Thread(target=listener)
    thread.start()

def handle_command(data):
    msg = json.loads(data)
    type_error = error('type must be specified as "command" or "query"')
    if not 'type' in msg:
        return type_error
    msg_type = msg['type']
    if msg_type == 'command':
        return command(msg)
    elif msg_type == 'query':
        return query(msg)
    else:
        return type_error

def error(msg):
    return json.dumps({'result': 'ERROR: {}'.format(msg)})

def result(data):
    data['rc'] = 0
    return json.dumps(data)

def command(msg):
    ret = commands[msg.get('command', 'error')](*msg.get('args', []))
    return json.dumps({'result': ret})

def query(msg):
    return queries[msg.get('query', 'error')]

if __name__ == '__main__':
    logger.info('This module must be started by calling importing and calling start()')
