# -*- coding: utf-8 -*-

import asyncio
import json
import websockets

import routers
from config import configs
from helpers import Logger
from app.connection.views import auth_check
from app.connection.models import Connection
from app.telephony.views import old_incoming_calls_remove
from app.listeners.views import balance_check, online_users_get, notifications_get, selections_get


async def event_loop(websocket, path):
    # if authorised
    is_authorised, auth_data = await auth_check(service=configs.HOMECRM_SERVICES['auth_check'],
                                                websocket=websocket)
    if is_authorised and auth_data:
        await Connection.register(websocket, auth_data)
        try:
            await websocket.send((json.dumps({"type": "auth_data", "data": json.dumps(auth_data)})))
            async for message in websocket:
                await routers.ws_router(json.loads(message), websocket)
        finally:
            await Connection.unregister(websocket)
    else:
        await websocket.send(json.dumps({"type": "auth", "value": False}))

start_server = websockets.serve(event_loop,
                                configs.WS_SERVER['url'],
                                configs.WS_SERVER['port'],
                                process_request=routers.http_router)

ioloop = asyncio.get_event_loop()

# create tasks for async running
ioloop.create_task(online_users_get(configs.HOMECRM_SERVICES['online_users_get']))
ioloop.create_task(selections_get(configs.HOMECRM_SERVICES['selections_get']))
ioloop.create_task(notifications_get(configs.HOMECRM_SERVICES['notifications_get']))
ioloop.create_task(balance_check(configs.HOMECRM_SERVICES['balance_check']))

# inner tasks
ioloop.create_task(old_incoming_calls_remove())

ioloop.run_until_complete(Logger.loggers_init())
ioloop.run_until_complete(start_server)
ioloop.run_forever()

# server side
# todo limitation for ome user connections
# todo wss https://websockets.readthedocs.io/en/stable/intro.html#secure-server-example
# install pip install aiohttp[speedups] and add it to requirements.txt

# deploy side
# todo proxy ws requests via nginx

# crm side
# todo make methods for listeners
# todo make methods for auth
# todo install supervisord

# client side
# todo when smb calling while active call
# todo test on mobiles
