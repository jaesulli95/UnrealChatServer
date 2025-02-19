import aiohttp
import socketio

sio =socketio.AsyncServer()
app = aiohttp.web.Application()
sio.attach(app)

clients = []

@sio.on('connect')
def connect(sid, socket):
    print('Client connected', sid)
    clients.append(sid)

@sio.on('disconnect')
def disconnect(sid, socket):
    print('Client disconnected', sid)
    clients.remove(sid)

@sio.event
async def on_message(sid, data):
    print(data['message'])
    await sio.emit('OnMessageReceived', data['message'], to=sid)

if __name__ == '__main__':
    aiohttp.web.run_app(app, host="0.0.0.0", port=5275)
