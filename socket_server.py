#!/usr/bin/env python3
from flask import Flask
from flask_socketio import SocketIO
from threading import Thread, Event
from util import kube
import logging

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
socketio = SocketIO(app, cors_allowed_origins="*")
thread = None
thread_reset_timeout_event = Event()


def count_until_timeout(timeout=10, delay=1):
    runtime = 0
    countdown = timeout
    last_data = None
    while True:
        if thread_reset_timeout_event.is_set():
            thread_reset_timeout_event.clear()
            countdown = timeout
        if countdown == 0:
            print("Stopping response thread (Ran for {}s)".format(runtime))
            return
        last_data = kube.get_node_stats(last_data=last_data)

        status_data = {'cpu': last_data['cpu']['float'],
                       'cpu_h': last_data['cpu']['str'],
                       'memory': last_data['memory']['float'],
                       'memory_h': last_data['memory']['str'],
                       'uptime': last_data['uptime']['str'],
                       'pods': last_data['pods']['str'],
                       'download': last_data['network']['download']['float'],
                       'download_h': last_data['network']['download']['str'],
                       'upload': last_data['network']['upload']['float'],
                       'upload_h':last_data['network']['upload']['str']
                       }


        socketio.emit('response', status_data, broadcast=True)
        countdown -= delay
        runtime += delay
        socketio.sleep(delay)


@socketio.on('ping')
def reset_timer():
    global thread
    if thread is not None and not thread.ready():
        thread_reset_timeout_event.set()
    else:
        print("Starting response thread")
        thread = socketio.start_background_task(count_until_timeout)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
