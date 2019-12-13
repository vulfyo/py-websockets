# -*- coding: utf-8 -*-

import json
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

from helpers import http_request_token_check, Logger
from app.telephony.views import incoming_call_answered, incoming_call_begin, incoming_call_cancel
from app.connection.models import Connection
from app.telephony.models import Telephony


async def telephony_router(method, call_uid, recipients):
    if method == 'begin':
        return await incoming_call_begin(recipients=recipients, call_uid=call_uid)
    elif method == 'cancel':
        return await incoming_call_cancel(recipients=recipients, call_uid=call_uid)
