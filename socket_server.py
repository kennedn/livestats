#!/usr/bin/env python3
from flask import Flask
from flask_socketio import SocketIO
from threading import Thread, Event
from util import cpu, memory, uptime, network

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins=["https://kennedn.com", "https://kennedn.root.sx", "http://thinboy.int", "http://127.0.0.1"])
thread = Thread()
thread_reset_timeout_event = Event()


def count_until_timeout(timeout=10, delay=1):
    runtime = 0
    countdown = timeout
    net_stats = (0, 0, 0, 0)
    while True:
        if thread_reset_timeout_event.is_set():
            thread_reset_timeout_event.clear()
            countdown = timeout
        if countdown == 0:
            print("Stopping response thread (Ran for {}s)".format(runtime))
            return
        net_stats = network.get(net_stats[0], net_stats[1])

        cpu_data = cpu.get()
        mem_data = memory.get()

        status_data = {'cpu': cpu_data[0],
                       'cpu_h': cpu_data[1],
                       'memory': mem_data[0],
                       'memory_h': mem_data[1],
                       'uptime': uptime.get(),
                       'download': net_stats[2],
                       'download_h': net_stats[4],
                       'upload': net_stats[3],
                       'upload_h': net_stats[5]}

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
    socketio.run(app)
