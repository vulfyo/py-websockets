# -*- coding: utf-8 -*-


class Configs():
    DEBUG = True
    LOGS_PATH_FOLDER = 'logs'

    HTTP_INCOMING_REQUEST_TOKEN = '74a17b7f-7e19-41f4-aee4-95b52d899c0d'
    CRM_REQUEST_TOKEN = '9d48ff6d-2965-4710-8ac1-53eeadd2bcf4'

    # server credentials
    WS_SERVER = {
        'url': "localhost",
        "port": 6789
    }

    # time for waiting fot request
    HTTP_ASYNC_REQUEST_TIMEOUT = 15.9

    # time for live (in sec)
    INCOMING_CALL_TTL = 120
    INCOMING_CALL_DELAY = 30

    # TODO
    HOMECRM_URL = 'https://test.ru'
    HOMECRM_SERVICES = {
        'online_users_get': {'url': '{}/api/1.0/online_users_get?token={}'.format(HOMECRM_URL, CRM_REQUEST_TOKEN),
                             'delay': 1},
        'selections_get': {'url': '{}/api/1.0/selections_get?token={}'.format(HOMECRM_URL, CRM_REQUEST_TOKEN),
                           'delay': 2},
        'notifications_get': {'url': '{}/api/1.0/notifications_get?token={}'.format(HOMECRM_URL, CRM_REQUEST_TOKEN),
                              'delay': 3},
        'balance_check': {'url': '{}/api/1.0/balance_check?token={}'.format(HOMECRM_URL, CRM_REQUEST_TOKEN),
                          'delay': 4},
        'auth_check': {'url': '{}/api/1.0/auth_check?token={}'.format(HOMECRM_URL, CRM_REQUEST_TOKEN)},
    }
