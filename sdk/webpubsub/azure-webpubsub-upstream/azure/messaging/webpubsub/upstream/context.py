# coding=utf-8
# --------------------------------------------------------------------------
# Created on Thu Oct 28 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

__all__ = ["ConnectionContext"]

import base64
import json

from typing import Dict

from .exceptions import HeaderNotFoundError

from .headers import (
    CE_CONNECTION_ID,
    CE_CONNECTION_STATE,
    CE_EVENT_NAME,
    CE_HUB,
    CE_SIGNATURE,
    CE_SUBPROTOCOL,
    CE_TYPE,
    CE_USER_ID,
    WEBHOOK_REQUEST_ORIGIN
)

_HTTPHeaders = Dict[str, str]


def _get_first_header_value(headers, key, optional=False):
    # type: (_HTTPHeaders, str, bool) -> str
    value = headers.get(key.lower())
    if value is None:
        if optional:
            return None
        raise HeaderNotFoundError(key)
    return value.split(",")[0]


class ConnectionContext(object):

    @property
    def headers(self):
        # type: (ConnectionContext) -> _HTTPHeaders
        return self._headers

    @property
    def connection_state(self):
        # type: (ConnectionContext) -> dict
        return json.loads(self._decoded_state)

    @property
    def signature(self):
        return self._signature

    def __init__(self, headers):
        # type: (ConnectionContext, _HTTPHeaders) -> None

        self.user_id = _get_first_header_value(headers, CE_USER_ID, True)
        self.hub = _get_first_header_value(headers, CE_HUB)
        self.connection_id = _get_first_header_value(
            headers, CE_CONNECTION_ID)
        self.event_type = _get_first_header_value(headers, CE_TYPE).lower()
        self.event_name = _get_first_header_value(
            headers, CE_EVENT_NAME).lower()
        self.origin = _get_first_header_value(
            headers, WEBHOOK_REQUEST_ORIGIN)
        self.subprotocol = _get_first_header_value(
            headers, CE_SUBPROTOCOL, True)

        # private properties
        self._headers = {k.lower(): v for (k, v) in headers.items()}
        self._signature = _get_first_header_value(
            headers, CE_SIGNATURE, True)

        # connection state
        encoded_state = _get_first_header_value(headers, CE_CONNECTION_STATE)
        self._decoded_state = base64.b64decode(encoded_state).decode('utf-8')
