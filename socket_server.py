#!/usr/bin/env python3
from flask import Flask
from flask_socketio import SocketIO
from threading import Thread, Event
from util import kube

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["*"])
thread = Thread()
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
                       'download': last_data['network']['download']['float'],
                       'download_h': last_data['network']['download']['str'],
                       'upload': last_data['network']['upload']['float'],
                       'upload_h':last_data['network']['upload']['str']
                       }

#        net_stats = network.get(net_stats[0], net_stats[1])
#
#        cpu_data = cpu.get()
#        mem_data = memory.get()
#
#        status_data = {'cpu': cpu_data[0],
#                       'cpu_h': cpu_data[1],
#                       'memory': mem_data[0],
#                       'memory_h': mem_data[1],
#                       'uptime': uptime.get(),
#                       'download': net_stats[2],
#                       'download_h': net_stats[4],
#                       'upload': net_stats[3],
#                       'upload_h': net_stats[5]}

        socketio.emit('response', status_data, broadcast=True)
        countdown -= delay
        runtime += delay
        socketio.sleep(delay)


@socketio.on('ping')
def reset_timer():
    global thread
    if thread.is_alive():
        thread_reset_timeout_event.set()
    else:
        print("Starting response thread")
        thread = socketio.start_background_task(count_until_timeout)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0')
