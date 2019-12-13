# -*- coding: utf-8 -*-

import os
from enum import Enum


class environments(Enum):
    """ Available environments """
    DEVELOPMENT = 'DEV'
    TESTING = 'TEST'
    PRODUCTION = 'PROD'


environment = os.environ.get('ENVIRONMENT')
if environment == environments.PRODUCTION.value:
    from configs.production import Configs
elif environment == environments.TESTING.value:
    from configs.testing import Configs
else:
    from configs.development import Configs

configs = Configs()
