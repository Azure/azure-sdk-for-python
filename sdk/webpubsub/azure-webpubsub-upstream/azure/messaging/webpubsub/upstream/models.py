# coding=utf-8
# --------------------------------------------------------------------------
# Created on Thu Sep 23 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-argument

__all__ = [
    "ConnectionContext",
    "ServiceRequest",
	"ConnectEventRequest",
	"ConnectedEventRequest",
	"DisconnectedEventRequest",
	"MessageEventRequest",
    "ServiceResponse",
    "ServiceErrorResponse",
    "ConnectEventResponse",
    "MessageEventResponse"
]

import base64
import json

from http import HTTPStatus

from typing import (
    Any,
    Dict,
    List
)

from .context import ConnectionContext

from .headers import (
    CE_CONNECTION_STATE,
)

from .exceptions import (
    InvalidConnectRequestError,
)


_HTTPHeaders = Dict[str, str]


class ClientCertificateInfo:

    def __init__(self, thumbprint: str):
        self.thumbprint = thumbprint


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
        try:
            self._message = json.loads(raw_data)
        except json.decoder.JSONDecodeError as exc:
            raise InvalidConnectRequestError(context) from exc
        super().__init__(context, raw_data)


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
        try:
            self._message = json.loads(raw_data)
        except json.decoder.JSONDecodeError as exc:
            raise InvalidConnectRequestError(context) from exc
        super().__init__(context, raw_data)


class ServiceResponse(Model):

    @property
    def status(self) -> HTTPStatus:
        return HTTPStatus.OK

    @property
    def headers(self):
        return self._headers

    @property
    def payload(self):
        return self._payload

    def __init__(self, raw_data: str, headers: _HTTPHeaders = None):
        self._payload = raw_data
        self._headers = headers or {}


class BlockingServiceResponse(ServiceResponse):

    @property
    def connection_state(self):
        return base64.b64encode(json.dumps(self._state).encode('utf-8')).decode('ascii')

    @property
    def headers(self):
        return {
            CE_CONNECTION_STATE: self.connection_state
        }

    def __init__(self, context: ConnectionContext, raw_data: str, connection_state: Dict[str, str]):
        self._context = context
        self._state = connection_state
        super().__init__(raw_data)

    def set_state(self, key: str, value: str, **kwargs: Any) -> None:
        self._state[key] = value

    def del_state(self, key: str, **kwargs: Any) -> None:
        if key in self._state:
            del self._state[key]

    def clear_states(self, **kwargs: Any) -> None:
        self._state.clear()


class ServiceErrorResponse(ServiceResponse):

    @property
    def status(self) -> HTTPStatus:
        return self._status

    def __init__(self, exception: Exception, status: HTTPStatus = HTTPStatus.BAD_REQUEST):
        self._exception = exception
        self._status = status
        super().__init__("", {})


class ConnectEventResponse(BlockingServiceResponse):

    def __init__(self, request: ConnectEventRequest, raw_data: str):
        super().__init__(
            request.context, raw_data, request.connection_state)


class MessageEventResponse(BlockingServiceResponse):

    def __init__(self, request: MessageEventRequest, raw_data: str):
        super().__init__(
            request.context, raw_data, request.connection_state)
