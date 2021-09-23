# coding=utf-8
# --------------------------------------------------------------------------
# Created on Thu Sep 23 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

import base64
import json
import re

from typing import Dict, List

from .headers import (
    CE_CONNECTION_ID,
    CE_EVENT_NAME,
    CE_HUB,
    CE_SIGNATURE,
    CE_SUBPROTOCOL,
    CE_TYPE,
    CE_USER_ID,
    CE_CONNECTION_STATE,
    WEBHOOK_REQUEST_ORIGIN
)

from .exceptions import (
    HeaderNotFoundError,
)


def _get_first_header_value(headers, key, optional=False):
    value = headers.get(key)
    if value is None:
        if optional:
            return None
        raise HeaderNotFoundError(key)
    return value.split(",")[0]


_pattern = re.compile(r'(?<!^)(?=[A-Z])')


class ConnectionContext(object):

    @property
    def headers(self):
        return self._headers

    @property
    def connection_state(self):
        return json.loads(self._decoded_state)

    @property
    def signature(self):
        return self._signature

    def __init__(self, headers: dict[str, str]):

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
        self._encoded_state = _get_first_header_value(
            headers, CE_CONNECTION_STATE)
        self._decoded_state = base64.b64decode(
            self._encoded_state).decode('utf-8')
        self._signature = _get_first_header_value(
            headers, CE_SIGNATURE, True)
        self._headers = {k.lower(): v for (k, v) in headers.items()}
        # TODO
        # user id

        # user id is optional
        self.user_id = headers.get(CE_USER_ID)


class Model:
    pass


class ServiceRequest(Model):

    @property
    def is_blocking(self):
        return True

    @property
    def connection_id(self):
        return self._context.connection_id

    @property
    def connection_state(self):
        return self._context.connection_state

    @property
    def context(self):
        return self._context

    @property
    def hub(self):
        return self._context.hub

    @property
    def webhook_request_origin(self):
        return self._context.origin

    @property
    def headers(self):
        return self._context.headers

    @property
    def payload(self):
        return self._payload

    def __init__(self, context: ConnectionContext, raw_data: str):
        self._context = context
        self._payload = raw_data
        super().__init__()


class NonBlockingServiceRequest(ServiceRequest):

    @property
    def is_blocking(self):
        return False

    def __init__(self, context: ConnectionContext, raw_data: str):
        super().__init__(context, raw_data)


class ServiceResponse(Model):

    @property
    def status_code(self):
        return 200

    @property
    def headers(self):
        return {}

    @property
    def payload(self):
        return self._payload

    def __init__(self, context: ConnectionContext, raw_data: str):
        self._context = context
        self._payload = raw_data


class BlockingServiceResponse(ServiceResponse):

    @property
    def connection_state(self):
        return base64.b64encode(json.dumps(self._state).encode('utf-8')).decode('ascii')

    @property
    def headers(self):
        return {
            CE_CONNECTION_STATE: self.connection_state
        }

    def __init__(self, context: ConnectionContext, raw_data: str, connection_state: dict[str, str]):
        self._state = connection_state
        super().__init__(context, raw_data)

    def set_state(self, key: str, value: str):
        self._state[key] = value

    def del_state(self, key: str):
        if key in self._state:
            del self._state[key]

    def clear_states(self):
        self._state.clear()


class ClientCertificateInfo:

    def __init__(self, thumbprint: str):
        self.thumbprint = thumbprint


class ConnectEventRequest(ServiceRequest):

    @property
    def claims(self) -> Dict[str, List[str]]:
        return self._message.get('claims', {})

    @property
    def query(self) -> Dict[str, List[str]]:
        return self._message.get('query', [])

    @property
    def subprotocols(self) -> List[str]:
        return self._message.get('subprotocols', [])

    @property
    def client_certificates(self) -> Dict[str, List[ClientCertificateInfo]]:
        return self._message.get('clientCertificates', {})

    def __init__(
        self,
        context: ConnectionContext,
        raw_data: str,
    ):
        super().__init__(context, raw_data)

        # TODO object_hook to do validation
        self._message = json.loads(raw_data)


class MessageEventRequest(ServiceRequest):
    pass


class ConnectedEventRequest(NonBlockingServiceRequest):
    pass


class DisconnectedEventRequest(NonBlockingServiceRequest):

    @property
    def reason(self):
        return self._message.get("reason", "")

    def __init__(
        self,
        context: ConnectionContext,
        raw_data: str,
    ):
        super().__init__(context, raw_data)

        # TODO object_hook to do validation
        self._message = json.loads(raw_data)


class ServiceErrorResponse(ServiceResponse):

    @property
    def status_code(self):
        return self._status_code

    def __init__(self, exception: Exception, status_code: int = None):
        self._status_code = status_code


class ConnectEventResponse(BlockingServiceResponse):

    def __init__(self, request: ConnectEventRequest, raw_data: str):
        super().__init__(
            request.context, raw_data, request.connection_state)


class MessageEventResponse(BlockingServiceResponse):

    def __init__(self, request: MessageEventRequest, raw_data: str):
        super().__init__(
            request.context, raw_data, request.connection_state)
