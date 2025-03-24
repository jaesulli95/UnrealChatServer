import Constants.EventNames as UCSEvents
import socketio
import aiohttp

sio =socketio.AsyncServer()
app = aiohttp.web.Application()
sio.attach(app)

clients = []
channels = {"GENERAL": [],
            "SERVICES": []}

@sio.on(UCSEvents.CONNECT)
async def connect(sid, socket):
    await sio.emit(UCSEvents.CONNECT, {}, to=sid)
    clients.append(sid)
    channels["GENERAL"].append(sid)
    channels["SERVICES"].append(sid)

@sio.on(UCSEvents.DISCONNECT)
def disconnect(sid, socket):
    clients.remove(sid)
    channels["GENERAL"].remove(sid)
    channels["SERVICES"].remove(sid)

@sio.on(UCSEvents.ON_MESSAGE)
async def on_message(sid, data):
    for client in clients:
        await sio.emit(UCSEvents.ON_MESSAGE_RECEIVED, data, to=client)

if __name__ == '__main__':
    aiohttp.web.run_app(app, host="0.0.0.0", port=5275)
