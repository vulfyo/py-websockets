# -*- coding: utf-8 -*-

import asyncio
import json
from time import time

from app.connection.models import Connection
from app.telephony.models import Telephony
from config import configs


async def incoming_call_begin(recipients, call_uid):
    """ incoming call started. Send info about it to connected users (recipients) """
    await Telephony.incoming_call_register(recipients['users_ids'], call_uid)

    ws_list = await Connection.particular_users_in_agency_ws_get(recipients['agency_id'], recipients['users_ids'])
    if ws_list:
        await asyncio.wait([ws.send(json.dumps({"type": "incoming_call_begin",
                                                "data": {"info": "incoming_call from Client",
                                                         "call_uid": call_uid}})) for ws in ws_list])
    return True


async def incoming_call_cancel(recipients, call_uid):
    """ incoming call started. Send info about it to connected users (recipients) """
    users_in_call = [{users_list for users_list in users} for uid, users in Telephony.incoming_callings.items() if uid == call_uid]
    await Telephony.incoming_call_cancel(call_uid)
    if users_in_call:
        ws_list = await Connection.particular_users_in_agency_ws_get(recipients['agency_id'], users_in_call[0])
        if ws_list:
            await asyncio.wait([ws.send(json.dumps({"type": "incoming_call_cancel",
                                                    "data": {"info": "incoming_call_cancelled from Client",
                                                             "call_uid": call_uid}})) for ws in ws_list])
    return True


async def incoming_call_answered(data, answered_user_websocket):
    """ incoming call was answered by user. Send others about it and synchronize answered user interfaces """
    if 'call_uid' not in data or not data['call_uid']:
        return

    # if call not exists
    if not data['call_uid'] in Telephony.incoming_callings:
        return

    # get answered user info
    answered_agency_id, answered_user_id = await Connection.user_info_get_by_ws(answered_user_websocket)

    # send info to user who answered
    ws_list = await Connection.user_ws_get(answered_agency_id, answered_user_id)
    if ws_list:
        await asyncio.wait([ws.send(json.dumps({"type": "incoming_call_answered", "data": json.dumps('you answered')}))
                            for ws in ws_list])

    # send to others that call answered
    recipients = await Telephony.recipients_about_answer_get(call_uid=data['call_uid'],
                                                             answered_user_id=answered_user_id)

    ws_list = await Connection.particular_users_in_agency_ws_get(answered_agency_id, recipients)
    if ws_list:
        await asyncio.wait(
            [ws.send(json.dumps({"type": "incoming_call_answered", "data": "already answered by other user"}))
             for ws in ws_list])

    from helpers import Logger
    listeners_error_logger = Logger('ws_server_errors')

    # unregister
    await Telephony.incoming_call_unregister(data['call_uid'])


async def old_incoming_calls_remove():
    """ Check for old incoming calls and remove they """
    while True:
        if Telephony.incoming_callings_ttl:
            callings_to_remove = {ttl: call_uid for ttl, call_uid in Telephony.incoming_callings_ttl.items() if
                                  ttl < int(time())}

            for ttl, call_uid in callings_to_remove.items():
                # safe remove from incoming_callings
                Telephony.incoming_callings.pop(call_uid, None)
                # remove from incoming_callings_ttl
                del Telephony.incoming_callings_ttl[ttl]
            # print('incoming_calls_old_remove')
        await asyncio.sleep(configs.INCOMING_CALL_DELAY)
