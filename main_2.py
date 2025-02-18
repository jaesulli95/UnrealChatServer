from Core.Data.QueueGroup import PhoenixQueueGroup
from Core.Data.PlayerInQueue import *
from aiohttp import web
import QueueConstants as QC
import pandas as pd
import socketio
import uuid
import subprocess
import random


server_io = socketio.AsyncServer()
app = web.Application()
server_io.attach(app)


#Variables for the Queue System
playerConnections = []
playersInQueue = []
queue_groups = {}


#Dungeon Data
dungeon_data = pd.read_csv('Data/dungeons.csv', encoding='utf-16')
result = dungeon_data.loc[dungeon_data["id"] == 1000]


@server_io.event
def connect(sid, socket):
    playerConnections.append(sid)


# Triggered when a client disconnects from our socket
@server_io.event
def disconnect(sid):
    playerConnections.remove(sid)


@server_io.event()
async def queue_add(sid, data):
    #This code is neeeded
    '''dungeon_to_play = dungeon_data.loc[dungeon_data["id"] == int(random.choice(data["dungeonIds"]))]
    command = f'F:\\UE_5.1\\Engine\\Binaries\\Win64\\UnrealEditor.exe {QC.UPROJECT_LOCATION} {dungeon_to_play["map_name"].iloc[0]} -server -log -port=7777'
    subprocess.Popen(command)'''
    #await server_io.emit('queue_pop', data={"ip_address": "192.168.1.31", "port": 7777}, to=sid)
    _tmpPlayersInQueue = [x for x in playersInQueue if x.QueueStatus == 0 and x.SocketId == sid]
    if len(_tmpPlayersInQueue) == 0:
        playersInQueue.append(PlayerInQueue(sid, data["dungeonIds"]))
        await server_io.emit('queue_modified', data={"queued": True}, to=sid)
        await how_many_queued(sid)
    else:
        print(f'Player is already in the Queue')


@server_io.event()
async def queue_remove(sid, data):
    print(f'{sid}')
    _tmpSids = [x for x in playersInQueue if x.SocketId == sid]
    print(_tmpSids)
    if len(_tmpSids):
        playersInQueue.remove(_tmpSids[0])
        print(f'Removing Player from Queue')
        await server_io.emit('queue_modified', data={"queued": False}, to=sid)


@server_io.event()
async def queue_accepted(sid, data):
    pqg = PhoenixQueueGroup([], 0)
    if data['group_id'] in queue_groups:
        pqg = queue_groups[data['group_id']]
        pqg.set_player_queue_result(sid, True)

    if pqg.queue_group_accepted():
        command = f'F:\\UE_5.1\\Engine\\Binaries\\Win64\\UnrealEditor.exe {QC.UPROJECT_LOCATION} FrozenCove -server -log -port=7777'
        subprocess.Popen(command)
        for x in pqg.get_players_in_queue():
            await server_io.emit('queue_load', data={"ip_address": "192.168.1.31", "port": 7777}, to=x.SocketId)
    ## delete the queue group and remove them from the queue!!!
    ## and remove them from the queue group!!


@server_io.event()
async def queue_declined(sid, data):
    print(f'Group Id {data["group_id"]}')
    if data['group_id'] in queue_groups:
        _tmpSids = [x for x in playersInQueue if x.SocketId == sid]
        playersInQueue.remove(_tmpSids[0])
        for x in queue_groups[data['group_id']]:
            print(x.SocketId)
            if sid == x.SocketId:
                await server_io.emit('queue_ack', data={"user_declined": True}, to=x.SocketId)
            else:
                x.set_queue_status(QueueType.Queued)
                await server_io.emit('queue_ack', data={"user_declined": False}, to=x.SocketId)
        del queue_groups[data["group_id"]]


async def how_many_queued(sid):
    ## Rework algorithm here too see what i can for specific dungeons
    _tmpPlayersInQueue = [x for x in playersInQueue if x.QueueStatus == QueueType.Queued]
    if len(_tmpPlayersInQueue) >= 2:
        _tmpPlayers = _tmpPlayersInQueue[0:2]
        _newUUID = uuid.uuid4().hex
        for x in _tmpPlayers:
            x.QueueStatus = 1  # Set it to Queue Pending
            await server_io.emit('queue_pop', data={"group_id": _newUUID}, to=x.SocketId)
        queue_groups[_newUUID] = PhoenixQueueGroup(_tmpPlayers, 2)

if __name__ == '__main__':
    web.run_app(app, host="127.0.0.1", port=5279)