# -*- coding: utf-8 -*-

import sys
import aiohttp
import asyncio
import json
import logging
from logging.handlers import RotatingFileHandler
from aiohttp import web
from http.cookies import SimpleCookie

from config import configs
from app.connection.models import Connection


async def http_request_token_check(token):
    """ check is token valid """
    if configs.HTTP_INCOMING_REQUEST_TOKEN == token:
        return True
    else:
        # init error logger
        error_logger = Logger('ws_server_errors')
        await error_logger.prepare_and_save_record(
            level=Logger.ERROR,
            message='Got wrong token "{}"'.format(token))
        return False


async def http_async_get_json(url):
    # init error logger
    listeners_error_logger = Logger('ws_server_errors')

    """ Send http request and return json"""
    data = None
    try:
        timeout = aiohttp.ClientTimeout(total=configs.HTTP_ASYNC_REQUEST_TIMEOUT)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request('GET', url) as response:
                if response.status != 200:
                    await listeners_error_logger.prepare_and_save_record(
                        level=Logger.ERROR,
                        message='Got error HTTP status {} for "{}"'.format(response.status, url))
                else:
                    data = await response.json()
    except (web.HTTPException,
            aiohttp.client_exceptions.ClientError,
            aiohttp.client_exceptions.ClientConnectorError,
            json.decoder.JSONDecodeError,
            asyncio.TimeoutError) as e:
        await listeners_error_logger.prepare_and_save_record(
            level=Logger.ERROR,
            message='Got exception for "{}"'.format(url),
            exc_info=True)
    finally:
        return data


async def cookies_to_dict(cookies_string):
    """ get raw string of cookies to dictionary """
    if not cookies_string:
        return False

    cookie = SimpleCookie()
    cookie.load(cookies_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


class Logger:
    logger = None
    formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s')
    level = logging.DEBUG if configs.DEBUG else logging.INFO
    stream = None
    max_bytes = 104857600
    backup_count = 20

    # error states
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    method_mapper = {
        logging.INFO: logging.info
    }

    @staticmethod
    class HandlerTypes():
        StreamConsoleHandler = {'name': 'StreamConsoleHandler', 'value': logging.StreamHandler}
        # StreamMemoryHandler = {'name': 'StreamMemoryHandler', 'value': logging.StreamHandler}
        RotatingFileHandler = {'name': 'RotatingFileHandler', 'value': RotatingFileHandler}

    @staticmethod
    async def loggers_init():
        """ Initialize loggers """
        ws_logger = Logger('websockets')
        requests_http_logger = Logger('requests_http')
        requests_ws_logger = Logger('requests_ws')
        error_logger = Logger('ws_server_errors')
        listeners_error_logger = Logger('listeners_error_logger')
        if configs.DEBUG:
            # add console write handlers
            await ws_logger.handler_add(handler=Logger.HandlerTypes.StreamConsoleHandler['name'])
            ws_logger.level = Logger.INFO  # DEBUG mode is too detailed
            await requests_http_logger.handler_add(handler=Logger.HandlerTypes.StreamConsoleHandler['name'])
            await requests_ws_logger.handler_add(handler=Logger.HandlerTypes.StreamConsoleHandler['name'])
            await error_logger.handler_add(handler=Logger.HandlerTypes.StreamConsoleHandler['name'])
            await listeners_error_logger.handler_add(handler=Logger.HandlerTypes.StreamConsoleHandler['name'])
        await ws_logger.handler_add(handler=Logger.HandlerTypes.RotatingFileHandler['name'],
                                    logger_path='{}/websockets.log'.format(configs.LOGS_PATH_FOLDER))
        await requests_http_logger.handler_add(handler=Logger.HandlerTypes.RotatingFileHandler['name'],
                                               logger_path='{}/requests_http.log'.format(configs.LOGS_PATH_FOLDER))
        await requests_ws_logger.handler_add(handler=Logger.HandlerTypes.RotatingFileHandler['name'],
                                             logger_path='{}/requests_ws.log'.format(configs.LOGS_PATH_FOLDER))
        await error_logger.handler_add(handler=Logger.HandlerTypes.RotatingFileHandler['name'],
                                       logger_path='{}/ws_server_errors.log'.format(configs.LOGS_PATH_FOLDER))
        await listeners_error_logger.handler_add(handler=Logger.HandlerTypes.RotatingFileHandler['name'],
                                                 logger_path='{}/listeners_error.log'.format(configs.LOGS_PATH_FOLDER))


    def __init__(self, logger_name):
        """ Init logger """
        self.logger = logging.getLogger(logger_name)
        # self.handlers_clear()

    async def handler_add(self, handler, **kwargs):
        """Add new handler"""
        if handler == self.HandlerTypes.RotatingFileHandler['name']:
            hdlr = self.HandlerTypes.RotatingFileHandler['value'](kwargs['logger_path'],
                                                                  maxBytes=self.max_bytes,
                                                                  backupCount=self.backup_count,
                                                                  encoding='UTF-8')
        elif handler == self.HandlerTypes.StreamConsoleHandler['name']:
            hdlr = self.HandlerTypes.StreamConsoleHandler['value'](sys.stdout)
        # elif handler == self.HandlerTypes.StreamMemoryHandler['name']:
        #     self.stream = StringIO.StringIO()
        #     hdlr = self.HandlerTypes.StreamMemoryHandler['value'](self.stream)
        hdlr.setFormatter(self.formatter)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(self.level)

    def handler_pop(self):
        """Remove last added handler"""
        self.logger.handlers.pop()

    def handlers_clear(self):
        """Remove all added handlers"""
        if self.logger.handlers:
            [handler.close() for handler in self.logger.handlers]
            self.logger.handlers = []

    async def prepare_and_save_record(self, level, message, ws=None, exc_info=False):
        """ add to log message additional info """

        result = str(message)

        if ws:
            result += '\nws info: user-agent="{}", origin="{}", cookies="{}"'.format(
                ws.request_headers.get("user-agent", None),
                ws.request_headers.get("origin", None),
                ws.request_headers.get("cookie", None))

            if Connection.connected:
                answered_agency_id, answered_user_id = await Connection.user_info_get_by_ws(ws)
                if answered_agency_id and answered_user_id:
                    result += '\nConnection info: agency_id="{}", user_id="{}"'.format(answered_agency_id, answered_user_id)

        if level == Logger.DEBUG:
            self.logger.debug(result, exc_info=exc_info)
        elif level == Logger.INFO:
            self.logger.info(result, exc_info=exc_info)
        elif level == Logger.WARNING:
            self.logger.warning(result, exc_info=exc_info)
        elif level == Logger.ERROR:
            self.logger.error(result, exc_info=exc_info)
        elif level == Logger.CRITICAL:
            self.logger.critical(result, exc_info=exc_info)
        return result
