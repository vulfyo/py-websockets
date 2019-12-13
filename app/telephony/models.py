# -*- coding: utf-8 -*-

import json
from time import time

from config import configs


class Telephony:
    """ Class for work with telephony """

    # Dict with info about active users
    # Format {{call_uid: [user_id, user_id, ...]}}, ... }
    incoming_callings = {}
    # ttl for each incoming call
    # Format {ttl:uid, ...}
    incoming_callings_ttl = {}

    @staticmethod
    async def incoming_call_register(users_list, call_uid):
        """ Save call_uid and connected with call users to incoming_callings dict """
        Telephony.incoming_callings.update({call_uid: users_list})
        Telephony.incoming_callings_ttl.update({int(time() + configs.INCOMING_CALL_TTL): call_uid})
        return call_uid

    @staticmethod
    async def incoming_call_unregister(call_uid):
        """ Remove call from incoming_callings dict """
        del Telephony.incoming_callings[call_uid]

    @staticmethod
    async def recipients_about_answer_get(call_uid, answered_user_id):
        """ get list of recipients for notify about call """
        if call_uid in Telephony.incoming_callings:
            return [x for x in Telephony.incoming_callings[call_uid] if x != answered_user_id]

    @staticmethod
    async def incoming_call_cancel(call_uid):
        """ remove call from dict """
        Telephony.incoming_callings.pop(call_uid, None)


    @staticmethod
    async def incoming_callings_to_string():
        """ replace websocket info for string representation """
        return json.dumps(Telephony.incoming_callings)
