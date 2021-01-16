# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from threading import Lock, Condition
from datetime import datetime, timedelta
from typing import ( # pylint: disable=unused-import
    cast,
    Tuple,
)
import six
from msrest.serialization import TZ_UTC
from .utils import create_access_token

class CommunicationTokenRefreshOptions(object):

    def __init__(self, # type: str
        token_refresher,
        refresh_proactively,
        token = None,
    ):
        self._token = token
        self._token_refresher = token_refresher
        self._refresh_proactively = refresh_proactively
    
    def get_token(self):
        return self._token

    def get_token_refresher(self):
        return self._token_refresher

    def get_refresh_proactively(self):
        return self._refresh_proactively