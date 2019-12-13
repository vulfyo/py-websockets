# -*- coding: utf-8 -*-

import json


class Connection:
    """ Class for work with websocket """

    # Dict with info about active users
    # Format {agency_id: {user_id: [ws1, ws2], user_id: [ws1, ws2]}, ...}
    connected = {}

    @staticmethod
    async def register(websocket, auth_data):
        """ Save websocket and user in connected dict """
        auth_data = {'agency_id': auth_data['agency_id'], 'user_id': auth_data['user_id'], 'ws': websocket}
        if auth_data['agency_id'] not in Connection.connected:
            # new agency
            Connection.connected.update({auth_data['agency_id']: {auth_data['user_id']: [auth_data['ws']]}})
        elif auth_data['user_id'] not in Connection.connected[auth_data['agency_id']]:
            # new user
            Connection.connected[auth_data['agency_id']][auth_data['user_id']] = [auth_data['ws']]
        elif websocket not in Connection.connected[auth_data['agency_id']][auth_data['user_id']]:
            # new token
            Connection.connected[auth_data['agency_id']][auth_data['user_id']].append(websocket)

    @staticmethod
    async def unregister(websocket):
        """ Remove websocket and user from connected dict """
        for users_key, users_value in Connection.connected.copy().items():
            for user_data_key, user_data_value in users_value.items():
                # if user have only one token
                if len(user_data_value) == 1:
                    if user_data_value[0] == websocket:
                        if len(users_value) == 1:
                            # if was only one user in agency - remove all agency dict
                            del Connection.connected[users_key]
                        else:
                            # if were many users
                            del users_value[user_data_key]
                        break
                else:
                    # if many tokens are - remove needed if exists
                    ws_to_remove = [x for x in user_data_value if x == websocket]
                    if len(ws_to_remove):
                        user_data_value.remove(websocket)
                        break

    @staticmethod
    async def user_info_get_by_ws(websocket):
        """ Get agency_id and user_id by websocket for certain user """
        for agency_id, users_value in Connection.connected.items():
            for user_id, user_data_value in users_value.items():
                # if found token
                if [x for x in user_data_value if x == websocket]:
                    return agency_id, user_id

    @staticmethod
    async def user_ws_get(agency_id, user_id):
        """ Get certain user websocket """
        if agency_id not in Connection.connected:
            return False
        ws_list = [v for k, v in Connection.connected[agency_id].items() if k == user_id]
        if ws_list:
            return ws_list[0]
        else:
            return False

    @staticmethod
    async def all_users_in_agency_ws_get(agency_id):
        """ Get all user`s websockets for agency """
        if agency_id not in Connection.connected:
            return False
        ws_list = [val for sublist in Connection.connected[agency_id].values() for val in sublist]
        if ws_list:
            return ws_list
        else:
            return False

    @staticmethod
    async def particular_users_in_agency_ws_get(agency_id, users_list):
        """ Get all websockets for agency for certain users list """
        if agency_id not in Connection.connected:
            return False
        ws_list = [v for k, v in Connection.connected[agency_id].items() if k in users_list]
        # make 1 dimension of list
        ws_list = [val for sublist in ws_list for val in sublist]
        if ws_list:
            return ws_list
        else:
            return False

    @staticmethod
    async def agencies_list_get():
        if Connection.connected:
            return [agency_id for agency_id, y in Connection.connected.items()]
        else:
            return False

    @staticmethod
    async def users_list_get():
        if Connection.connected:
            return [x for users in Connection.connected.values() for x in [x for x in users]]
        else:
            return False

    @staticmethod
    async def connections_to_string():
        """ replace websocket info for string representation """
        result = {agency_id:
                      {user_id:
                           [str(webcocket) for webcocket in user_data]
                       for user_id, user_data in users.items()}
                  for agency_id, users in Connection.connected.items()}
        return json.dumps(result)
