# coding=utf-8
# --------------------------------------------------------------------------
# Created on Sun Sep 26 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

import http
import json

from .exceptions import (
    BaseError,
    ContextBasedError,
    HandlerNotFoundError,
    InvalidEventTypeError,
    ValidationFailedError,
)

from .models import (
    ConnectionContext,
    ServiceRequest,
    ConnectEventRequest,
    ConnectedEventRequest,
    DisconnectedEventRequest,
    MessageEventRequest,
    ServiceResponse,
    ServiceErrorResponse,
    ConnectEventResponse,
    MessageEventResponse,
)

from .utils import (
    parse_connection_string,
)

from .headers import (
    EVENT_USER_MESSAGE,
    EVENT_SYS_CONNECT,
    EVENT_SYS_CONNECTED,
    EVENT_SYS_DISCONNECTED,
)


class AccessKeyValidator(object):

    def __init__(self, conn_str):
        self._kwargs = parse_connection_string(conn_str)

    def validate(self, context: ConnectionContext):
        '''
        TODO validate signature
        '''
        return context.signature is not None


class EventHandler:

    def __init__(self,
                 request_validator=None,
                 handle_connect=None,
                 handle_connected=None,
                 handle_disconnected=None,
                 handle_user_message=None,
                 handle_exception=None,
                 **kwargs):
        self._validator = request_validator
        if handle_connect is None:
            raise HandlerNotFoundError()
        self._handle_connect = handle_connect
        self._handle_connected = handle_connected
        self._handle_disconnected = handle_disconnected
        self._handle_user_message = handle_user_message
        self._handle_exception = handle_exception

    def handle_connect(self, request: ConnectEventRequest):
        if self._handle_connect is None:
            raise HandlerNotFoundError()
        data = self._handle_connect(request)
        payload = json.dumps(data)
        response = ConnectEventResponse(request, payload)
        return response

    def handle_connected(self, request: ConnectedEventRequest):
        if self._handle_connected is not None:
            self._handle_connected(request)

    def handle_disconnected(self, request: DisconnectedEventRequest):
        if self._handle_disconnected is not None:
            self._handle_disconnected(request)

    def handle_user_message(self, request: MessageEventRequest):
        if self._handle_user_message is None:
            data = {}
        else:
            data = self._handle_user_message(request)
        payload = data
        response = MessageEventResponse(request, payload)
        return response

    def handle_exception(self, exception: ContextBasedError):
        status_code = exception.status_code
        if self._handle_exception is not None:
            status_code = self._handle_exception(exception)
        return ServiceErrorResponse(exception, status_code)

    def _validate_context(self, context: ConnectionContext) -> bool:
        if self._validator is not None:
            return self._validator.validate(context)
        return True

    def from_http(self, headers, raw_data) -> ConnectionContext:
        context = ConnectionContext(headers)
        event_type = context.event_type

        if not self._validate_context(context):
            raise ValidationFailedError(context)
        elif event_type == EVENT_USER_MESSAGE:
            return MessageEventRequest(context, raw_data)
        elif event_type == EVENT_SYS_CONNECT:
            return ConnectEventRequest(context, raw_data)
        elif event_type == EVENT_SYS_CONNECTED:
            return ConnectedEventRequest(context, raw_data)
        elif event_type == EVENT_SYS_DISCONNECTED:
            return DisconnectedEventRequest(context, raw_data)
        raise InvalidEventTypeError(context)

    def handle(self, headers_or_request, raw_data="") -> ServiceResponse:
        try:
            if isinstance(headers_or_request, ServiceRequest):
                req = headers_or_request
            else:
                req = self.from_http(headers_or_request, raw_data)
            if isinstance(req, ConnectEventRequest):
                return self.handle_connect(req)
            elif isinstance(req, MessageEventRequest):
                return self.handle_user_message(req)
            elif isinstance(req, ConnectedEventRequest):
                self.handle_connected(req)
            elif isinstance(req, DisconnectedEventRequest):
                self.handle_disconnected(req)
            return ServiceResponse(req.context, "")
        except ContextBasedError as e:
            return self.handle_exception(e)


__all__ = ['EventHandler']
