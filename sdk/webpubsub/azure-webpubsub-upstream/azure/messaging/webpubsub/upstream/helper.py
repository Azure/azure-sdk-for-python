# coding=utf-8
# --------------------------------------------------------------------------
# Created on Sun Sep 26 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-argument

import http
import json

from abc import ABC, abstractmethod

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Union,
)

from .exceptions import (
    BaseError,
    HandlerNotFoundError,
    InvalidEventTypeError,
    ValidationFailedError,
)

from .models import (
    ConnectEventRequest,
    ConnectEventResponse,
    ConnectedEventRequest,
    ConnectionContext,
    DisconnectedEventRequest,
    MessageEventRequest,
    MessageEventResponse,
    ServiceErrorResponse,
    ServiceRequest,
    ServiceResponse,
)

from .utils import (
    parse_connection_string,
    iterate_headers,
    build_status,
)

from .headers import (
    AWPS_SPEC_VERSION,
    EVENT_SYS_CONNECT,
    EVENT_SYS_CONNECTED,
    EVENT_SYS_DISCONNECTED,
    EVENT_USER_MESSAGE,
    WEBHOOK_REQUEST_ORIGIN,
)

HEADER_SPEC_VERSION = "HTTP_" + AWPS_SPEC_VERSION.upper().replace('-', '_')
HEADER_WEBHOOK_REQUEST_ORIGIN = "HTTP_" + \
    WEBHOOK_REQUEST_ORIGIN.upper().replace('-', '_')

_HTTPHeaders = Dict[str, str]
_WSGIApplication = Callable[[Any, Any], Callable[[str, List], None]]

OK = build_status(http.HTTPStatus.OK)
NOT_FOUND = build_status(http.HTTPStatus.NOT_FOUND)
BAD_REQUEST = build_status(http.HTTPStatus.BAD_REQUEST)
METHOD_NOT_ALLOWED = build_status(http.HTTPStatus.METHOD_NOT_ALLOWED)

class RequestValidator(ABC):

    @abstractmethod
    def validate(self, context: ConnectionContext):
        '''
        Try authenticating the request via signature or bearer token
        '''

    @abstractmethod
    def contains(self, host: str):
        '''
        See if the request was coming from preserved hostnames
        '''


class AccessKeyValidator(RequestValidator):

    def __init__(self, conn_str: Union[str, List[str]]):
        self._mapping = {}
        for c in [conn_str] if isinstance(conn_str, str) else conn_str:
            data = parse_connection_string(c)
            endpoint = data['endpoint']
            accesskey = data['accesskey']
            self._mapping[endpoint] = accesskey
        print(self._mapping)

    def validate(self, context: ConnectionContext, **kwargs: Any) -> bool:
        '''
        TODO validate signature
        '''
        return context.signature is not None

    def contains(self, host: str, **kwargs: Any) -> bool:
        return host in self._mapping


class EventHandler:

    _validator = None  # type: RequestValidator

    def __init__(self,
                 request_validator: RequestValidator = None,
                 handle_connect: Callable[[ConnectEventRequest], Dict[str, str]] = None,
                 handle_connected: Callable[[ConnectedEventRequest], None] = None,
                 handle_disconnected: Callable[[DisconnectedEventRequest], None] = None,
                 handle_user_message: Callable[[MessageEventRequest], Any] = None,
                 handle_exception: Callable[[BaseError], int] = None,
                 ):
        self._validator = request_validator
        if handle_connect is None:
            raise HandlerNotFoundError()
        self._handle_connect = handle_connect
        self._handle_connected = handle_connected
        self._handle_disconnected = handle_disconnected
        self._handle_user_message = handle_user_message
        self._handle_exception = handle_exception

    def __handle_connect(self, request: ConnectEventRequest) -> ConnectEventResponse:
        if self._handle_connect is None:
            raise HandlerNotFoundError()
        data = self._handle_connect(request)
        payload = json.dumps(data)
        response = ConnectEventResponse(request, payload)
        return response

    def __handle_connected(self, request: ConnectedEventRequest) -> None:
        if self._handle_connected is not None:
            self._handle_connected(request)

    def __handle_disconnected(self, request: DisconnectedEventRequest) -> None:
        if self._handle_disconnected is not None:
            self._handle_disconnected(request)

    def __handle_user_message(self, request: MessageEventRequest) -> MessageEventResponse:
        if self._handle_user_message is None:
            payload = ""
        else:
            payload = self._handle_user_message(request)
        response = MessageEventResponse(request, payload)
        return response

    def __handle_exception(self, exception: BaseError) -> ServiceErrorResponse:
        status = exception.status
        if self._handle_exception is not None:
            new_status = self._handle_exception(exception)
            if new_status is not None:
                status = new_status
        return ServiceErrorResponse(exception, status)

    def __validate_context(self, context: ConnectionContext) -> bool:
        '''
        validate if the http context passing the authentication.
        '''
        if self._validator is not None:
            return self._validator.validate(context)
        return True

    def from_http(self, headers, raw_data) -> ConnectionContext:
        context = ConnectionContext(headers)
        event_type = context.event_type

        if not self.__validate_context(context):
            raise ValidationFailedError(context)

        if event_type == EVENT_USER_MESSAGE:
            return MessageEventRequest(context, raw_data)
        if event_type == EVENT_SYS_CONNECT:
            return ConnectEventRequest(context, raw_data)
        if event_type == EVENT_SYS_CONNECTED:
            return ConnectedEventRequest(context, raw_data)
        if event_type == EVENT_SYS_DISCONNECTED:
            return DisconnectedEventRequest(context, raw_data)
        raise InvalidEventTypeError(context)

    def preflight(self, headers: _HTTPHeaders, **kwargs: Any) -> bool:
        '''
        validate if the request coming from preserved hostnames.
        '''
        if self._validator is None:
            return True

        request_hosts = headers.get(WEBHOOK_REQUEST_ORIGIN, "").split(",")
        for host in request_hosts:
            if self._validator.contains(host):
                return True
        return False

    def handle(self,
               headers_or_request: Union[_HTTPHeaders, ServiceRequest],
               raw_data: str = "",
               **kwargs
               ) -> ServiceResponse:
        try:
            if isinstance(headers_or_request, ServiceRequest):
                req = headers_or_request
            else:
                req = self.from_http(headers_or_request, raw_data)

            if isinstance(req, ConnectEventRequest):
                return self.__handle_connect(req)
            if isinstance(req, MessageEventRequest):
                return self.__handle_user_message(req)
            if isinstance(req, ConnectedEventRequest):
                self.__handle_connected(req)
            elif isinstance(req, DisconnectedEventRequest):
                self.__handle_disconnected(req)
            return ServiceResponse("")
        except BaseError as exc:
            return self.__handle_exception(exc)

    def wrap(self, app: _WSGIApplication, path: str = "") -> _WSGIApplication:
        '''
        Wrap a wsgi app to handle azure web pubsub cloud events
        '''
        return WSGIMiddleware(app, self, path=path)


class WSGIMiddleware(object):
    '''
    WSGI Middleware for handling azure web pubsub cloud events.
    '''

    def __init__(self, app: _WSGIApplication, handler: EventHandler, path=""):
        self.app = app
        self.handler = handler
        self._path = path

    def _preflight(self, environ, start_response):
        if HEADER_WEBHOOK_REQUEST_ORIGIN not in environ:
            start_response(BAD_REQUEST, [])
            return [b'Missing webhook request origin.']

        origin = environ[HEADER_WEBHOOK_REQUEST_ORIGIN]
        if not self.handler.preflight({WEBHOOK_REQUEST_ORIGIN: origin}):
            start_response(BAD_REQUEST, [])
            return [b'Abuse protection validation failed.']

        start_response(OK, [(WEBHOOK_REQUEST_ORIGIN, "*")])
        return [b'']

    def _handle_cloud_event(self, environ, start_response):
        req_headers = {
            WEBHOOK_REQUEST_ORIGIN: environ[HEADER_WEBHOOK_REQUEST_ORIGIN]
        }
        for key, value in iterate_headers(environ):
            if key.startswith("ce"):
                req_headers[key] = value

        raw_body = ""
        try:
            length = int(environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            length = 0
        if length != 0:
            raw_body = environ['wsgi.input'].read(length)
        response = self.handler.handle(req_headers, raw_body)

        res_headers = list(response.headers.items())
        start_response(build_status(response.status), res_headers)
        return [bytes(response.payload, encoding='utf-8')]

    def __call__(self, environ, start_response):
        if environ.get(HEADER_SPEC_VERSION) != "1.0":
            return self.app(environ, start_response)

        path = environ["PATH_INFO"]
        if path != self._path:
            start_response(NOT_FOUND, [])
            return [b'']

        if HEADER_WEBHOOK_REQUEST_ORIGIN not in environ:
            start_response(BAD_REQUEST, [])
            return [b'Missing webhook request origin.']

        method = environ['REQUEST_METHOD']
        if method == "OPTIONS":
            return self._preflight(environ, start_response)
        if method == "POST":
            return self._handle_cloud_event(environ, start_response)
        start_response(METHOD_NOT_ALLOWED, [])
        return [b'']


__all__ = ['EventHandler']
