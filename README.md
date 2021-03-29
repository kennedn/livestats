# livestats

Uses Flask-SocketIO to provide live server statistics via websocket to all connected clients

Currently provides:
| name     | description             |
|----------|-------------------------|
| cpu      | float between 0 & 1     |
| memory   | float between 0 & 1     |
| download | float between 0 & 1     |
| upload   | float between 0 & 1     |
| cpu_h    | human readable cpu str  |
| memory_h | human readable mem str  |
| download_h| human readable rx str  |
| upload_h | human readable tx str   |
| uptime   | time since boot         |

Floats can be used quite easily to create percentage bars, human readable variants can then be used to supplement the data so it has context. For example [kennedn.com](https://kennedn.com) uses the data like so on its 'About this website' tile:

![](images/example.gif)

## Pre-requisites 

- Python >=3.7
	- Flask, Flask-SocketIO, psutil, eventlet

e.g
`python3.7 -m pip install flask flask-socketio psutil eventlet`

## Client setup

To keep the server alive and sending data, it must receive ping emits periodically, otherwise it will time out and go dormant until a ping is recieved.

To kick this off an initial ping should be emitted by the client:
`socket.emit('ping')`

This will wake the server up if you are the first client or will reset an internal counter otherwise.


A callback can then be set up to receive data from the server on the `response` emit, a ping should be sent in every response callback too:
```
socket.on('response', msg => {
	socket.emit('ping')
	...
	console.log('msg.cpu_h')
}
```

The server currently emits a response every `1s` in an awakened state, and will timeout if no pings are recieved for `10s`.