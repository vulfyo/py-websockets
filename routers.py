# -*- coding: utf-8 -*-

import json
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

from helpers import http_request_token_check, Logger
from app.telephony.views import incoming_call_answered, incoming_call_begin
from app.telephony.routers import telephony_router
from app.connection.models import Connection
from app.telephony.models import Telephony


async def http_router(path, request_headers):
    """ router for http responses """
    # if it is ws request
    if path == '/':
        return

    # init error logger
    error_logger = Logger('ws_server_errors')
    # init router logger
    requests_http_logger = Logger('requests_http')
    await requests_http_logger.prepare_and_save_record(
        level=Logger.INFO,
        message='path: "{}"'.format(path))

    if path.startswith('/health'):
        """ 
        get status of ws server
        sample http://127.0.0.1:6789/health
        """
        return HTTPStatus.OK, [], b'{"status": "ok"}\n'
    elif path.startswith('/telephony_incoming'):
        """ 
        when incoming call are
        sample http://127.0.0.1:6789/telephony_incoming?token=74a17b7f-7e19-41f4-aee4-95b52d899c0d&method=begin&call_uid=123-123-123&recipients={"agency_id":1,"users_ids":[101,102,100]}
        sample http://127.0.0.1:6789/telephony_incoming?token=74a17b7f-7e19-41f4-aee4-95b52d899c0d&method=cancel&call_uid=123-123-123&recipients={"agency_id":1}
        """
        parsed = urlparse(path)
        if parsed.query and \
                'recipients' in parse_qs(parsed.query) and \
                'token' in parse_qs(parsed.query) and \
                'method' in parse_qs(parsed.query) and \
                'call_uid' in parse_qs(parsed.query) and \
                await http_request_token_check(parse_qs(parsed.query)['token'][0]) and \
                await telephony_router(method=parse_qs(parsed.query)['method'][0],
                                       call_uid=parse_qs(parsed.query)['call_uid'][0],
                                       recipients=json.loads(parse_qs(parsed.query)['recipients'][0])):
            return HTTPStatus.OK, [], b'{"status": "success"}\n'
        else:
            await error_logger.prepare_and_save_record(level=Logger.ERROR,
                                                       message='HTTP router error "{}"'.format(path))
            return HTTPStatus.OK, [], b'{"status": "error"}\n'
    elif path.startswith('/active_connections_get'):
        """
        get active connections from ws server memory
        sample http://127.0.0.1:6789/active_connections_get?token=74a17b7f-7e19-41f4-aee4-95b52d899c0d
        """
        parsed = urlparse(path)
        if parsed.query and \
                'token' in parse_qs(parsed.query) and \
                await http_request_token_check(parse_qs(parsed.query)['token'][0]):
            return HTTPStatus.OK, [], bytes('{{"status": "success", "result": {0}}}\n'.format(
                await Connection.connections_to_string()), 'utf-8')
        else:
            await error_logger.prepare_and_save_record(level=Logger.ERROR,
                                                       message='HTTP router error "{}"'.format(path))
            return HTTPStatus.OK, [], b'{"status": "error"}\n'
    elif path.startswith('/incoming_callings_get'):
        """
        get active incoming callings from ws server memory
        sample http://127.0.0.1:6789/incoming_callings_get?token=74a17b7f-7e19-41f4-aee4-95b52d899c0d
        """
        parsed = urlparse(path)
        if parsed.query and \
                'token' in parse_qs(parsed.query) and \
                await http_request_token_check(parse_qs(parsed.query)['token'][0]):
            return HTTPStatus.OK, [], bytes('{{"status": "success", "result": {0}}}\n'.format(
                await Telephony.incoming_callings_to_string()), 'utf-8')
            return HTTPStatus.OK, [], bytes('{}\n'.format(await Telephony.incoming_callings_to_string()), 'utf-8')
        else:
            await error_logger.prepare_and_save_record(level=Logger.ERROR,
                                                       message='HTTP router error "{}"'.format(path))
            return HTTPStatus.OK, [], b'{"status": "error"}\n'


async def ws_router(request, ws):
    """ router for websocket responses """
    action = request.get('action', None)
    data = request.get('data', None)

    if not action:
        return

    # init router logger
    requests_ws_logger = Logger('requests_ws')
    await requests_ws_logger.prepare_and_save_record(
        level=Logger.INFO,
        message='action: "{}", data: "{}"'.format(action, data if data else '-'),
        ws=ws)

    if action == 'incoming_call_answered':
        await incoming_call_answered(data, ws)
    elif action == 'destroy_session':
        await ws.close()
