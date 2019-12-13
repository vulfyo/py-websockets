# -*- coding: utf-8 -*-

import asyncio
import json
from random import randrange

from app.connection.models import Connection
from helpers import http_async_get_json


async def online_users_get(service):
    while True:
        service['url'] = 'http://127.0.0.1:8000/blog/123/vote/'

        if Connection.connected:
            # get info for agency not separated users
            agencies_list = await Connection.agencies_list_get()
            if not agencies_list:
                continue

            url = "{}?agencies={}".format(service['url'], json.dumps(agencies_list))
            response = await http_async_get_json(url)
            if response:
                response = json.loads('[{{"agency_id": 1, "data": "notifications_data_AGENCY_100_{}"}},'
                                      '{{"agency_id": 2, "data": "notifications_data_AGENCY_200_{}"}},'
                                      '{{"agency_id": 3, "data": "notifications_data_AGENCY_300"}}'
                                      ']'.format(randrange(1, 9),
                                                 randrange(10, 19),
                                                 randrange(20, 29)))

                for user in response:
                    ws_list = None
                    if 'agency_id' in user:
                        ws_list = await Connection.all_users_in_agency_ws_get(user['agency_id'])
                    if ws_list:
                        await asyncio.wait(
                            [ws.send(json.dumps({"type": "online_users", "data": user['data']})) for ws in ws_list])
            # print('online_users_get')
        await asyncio.sleep(service['delay'])


async def selections_get(service):
    while True:
        service['url'] = 'http://127.0.0.1:8000/blog/123/vote/'

        if Connection.connected:
            # get info about online for separated users
            users_list = await Connection.users_list_get()
            if not users_list:
                continue

            url = "{}?users={}".format(service['url'], json.dumps(users_list))
            response = await http_async_get_json(url)
            if response:
                response = json.loads('[{{"agency_id": 1, "user_id": 100, "data": "selection_data_user_100_{}"}},'
                                      '{{"agency_id": 1, "user_id": 101, "data": "selection_data_user_101_{}"}},'
                                      '{{"agency_id": 2, "user_id": 200, "data": "selection_data_user_200_{}"}},'
                                      '{{"agency_id": 3, "user_id": 300, "data": "selection_data_user_300"}},'
                                      '{{"agency_id": 1, "user_id": 104, "data": "selection_data_user_104"}}'
                                      ']'.format(randrange(1, 9),
                                                 randrange(10, 19),
                                                 randrange(20, 29)))
                for user in response:
                    # find users ws and send to certain users or on agency
                    ws_list = None
                    if 'user_id' in user and 'agency_id' in user:
                        ws_list = await Connection.user_ws_get(agency_id=user['agency_id'], user_id=user['user_id'])
                    if ws_list:
                        await asyncio.wait([ws.send(json.dumps({"type": "selections", "data": user['data']}))
                                            for ws in ws_list])
                # print('selections_get')
        await asyncio.sleep(service['delay'])


async def notifications_get(service):
    while True:
        service['url'] = 'http://127.0.0.1:8000/blog/123/vote/'

        if Connection.connected:
            # get info about online for separated users
            users_list = await Connection.users_list_get()
            if not users_list:
                continue

            url = "{}?users={}".format(service['url'], json.dumps(users_list))
            response = await http_async_get_json(url)
            if response:
                response = json.loads('[{{"agency_id": 1, "data": "notifications_data_AGENCY_100_{}"}},'
                                      '{{"agency_id": 2, "user_id": 200, "data": "notifications_data_user_200_{}"}},'
                                      '{{"agency_id": 3, "user_id": 300, "data": "notifications_data_user_300"}}'
                                      ']'.format(randrange(1, 9),
                                                 randrange(10, 19),
                                                 randrange(20, 29)))

                for user in response:
                    # find users ws and send to certain users or on agency
                    if 'user_id' in user and 'agency_id' in user:
                        ws_list = await Connection.user_ws_get(agency_id=user['agency_id'], user_id=user['user_id'])
                        if ws_list:
                            await asyncio.wait([ws.send(json.dumps({"type": "notifications", "data": user['data']}))
                                                for ws in ws_list])
                    if 'user_id' not in user and 'agency_id' in user:
                        ws_list = await Connection.all_users_in_agency_ws_get(user['agency_id'])
                        if ws_list:
                            await asyncio.wait([ws.send(json.dumps({"type": "notifications", "data": user['data']}))
                                                for ws in ws_list])
                # print('notifications_get')
        await asyncio.sleep(service['delay'])


async def balance_check(service):
    while True:
        service['url'] = 'http://127.0.0.1:8000/blog/123/vote/'

        if Connection.connected:
            # get info for agency not separated users
            agencies_list = await Connection.agencies_list_get()
            if not agencies_list:
                continue

            url = "{}?agencies={}".format(service['url'], json.dumps(agencies_list))
            response = await http_async_get_json(url)
            if response:
                response = json.loads('[{{"agency_id": 1, "data": "notifications_data_AGENCY_100_{}"}},'
                                      '{{"agency_id": 2, "user_id": 200, "data": "notifications_data_user_200_{}"}},'
                                      '{{"agency_id": 3, "user_id": 300, "data": "notifications_data_user_300"}},'
                                      '{{"agency_id": 1, "user_id": 104, "data": "notifications_data_user_104"}}'
                                      ']'.format(randrange(1, 9),
                                                 randrange(10, 19),
                                                 randrange(20, 29)))

                for user in response:
                    # find users ws and send to certain users or on agency
                    if 'user_id' in user:
                        ws_list = await Connection.user_ws_get(agency_id=user['agency_id'], user_id=user['user_id'])
                    elif 'agency_id' in user:
                        ws_list = await Connection.all_users_in_agency_ws_get(user['agency_id'])
                    if ws_list:
                        await asyncio.wait([ws.send(json.dumps({"type": "balance", "data": user['data']}))
                                            for ws in ws_list])

                # print('balance_check')
        await asyncio.sleep(service['delay'])
