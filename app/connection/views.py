# -*- coding: utf-8 -*-

import json
from random import randrange

from app.connection.models import Connection
from helpers import http_async_get_json, cookies_to_dict, Logger


async def auth_check(service, websocket):
    """ check rights for work with server """

    # init error logger
    error_logger = Logger('ws_server_errors')

    cookies_string = websocket.request_headers.get("Cookie", None)
    cookies = await cookies_to_dict(cookies_string)
    if not cookies:
        await error_logger.prepare_and_save_record(Logger.ERROR, 'Websocket without cookie', websocket)
        return False, None

    ci_session = cookies.get('ci_session', None)
    if not ci_session:
        await error_logger.prepare_and_save_record(Logger.ERROR, 'Websocket without ci_session cookie', websocket)
        return False, None

    service['url'] = 'http://127.0.0.1:8000/blog/123/vote/'
    service['url'] = ''.join([service['url'], '?session_id', ci_session])

    response = await http_async_get_json(service['url'])
    response = True
    if response:
        id = randrange(1, 4)
        if id == 1:
            response = json.loads('{{"agency_id": {0}, "user_id": {1}}}'.format(1, 100))
        elif id == 2:
             response = json.loads('{{"agency_id": {0}, "user_id": {1}}}'.format(2, 200))
        else:
            response = json.loads('{{"agency_id": {0}, "user_id": {1}}}'.format(1, 101))
        return True, response
    else:
        await error_logger.prepare_and_save_record(Logger.ERROR, 'Websocket with wrong ci_session cookie', websocket)
        return False, None
