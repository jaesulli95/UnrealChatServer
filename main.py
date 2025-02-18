import aiohttp
import socketio

sio =socketio.AsyncServer()
app = aiohttp.web.Application()
sio.attach(app)

@sio.event
def connect(sid, socket):
    print('User Connected')

@sio.event
def disconnect(sid, socket):
    print('User Disconnected')



if __name__ == '__main__':
    aiohttp.web.run_app(app, host="0.0.0.0", port=5275)
