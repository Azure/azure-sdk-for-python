# coding=utf-8
# --------------------------------------------------------------------------
# Created on Thu Oct 28 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

# pylint: disable=unused-argument

import json
import pytest

from azure.messaging.webpubsub.upstream import (
    EventHandler,
    ConnectionContext,
)

from azure.messaging.webpubsub.upstream.headers import (
    CE_CONNECTION_ID,
    CE_CONNECTION_STATE,
    CE_EVENT_NAME,
    CE_HUB,
    CE_SIGNATURE,
    CE_SUBPROTOCOL,
    CE_TYPE,
    CE_USER_ID,
    EVENT_SYS_CONNECT,
    EVENT_SYS_CONNECTED,
    EVENT_SYS_DISCONNECTED,
    EVENT_USER_MESSAGE,
    WEBHOOK_REQUEST_ORIGIN,
)

from http import HTTPStatus

from typing import (
    Callable,
    Dict,
    List,
    Tuple,
)

from azure.messaging.webpubsub.upstream.helper import AccessKeyValidator
from azure.messaging.webpubsub.upstream.models import ConnectEventRequest, DisconnectedEventRequest, MessageEventRequest
from tests.test_utils import build_connection_state

ORIGIN = b'Hello world!'


def _build_http_status(status: HTTPStatus):
    return "{} {}".format(status.value, status.phrase)


def _set_payload(environ: Dict[str, str], payload: str):

    class Buffer(object):
        def __init__(self, payload):
            self._payload = payload

        def read(self, length):
            return self._payload[:length]

    environ['CONTENT_LENGTH'] = len(payload)
    environ['wsgi.input'] = Buffer(payload)


class TestDispatcher(object):

    status = ""
    headers = []

    def start_response(self, status: str, headers: List[Tuple[str, str]]) -> None:
        self.status = status
        self.headers = headers


def default_app(environ, start_response):
    start_response(_build_http_status(HTTPStatus.OK), [])
    return [ORIGIN]


def test_skip_middleware():
    handler = EventHandler(handle_connect=lambda x: {})
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    actual = app({}, dispatcher.start_response)
    assert [ORIGIN] == actual
    assert _build_http_status(HTTPStatus.OK) == dispatcher.status


def test_skip_when_path_mismatch():
    handler = EventHandler(handle_connect=lambda x: {})
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    actual = app({
        'HTTP_CE_AWPSVERSION': '1.0',
        'PATH_INFO': '/',
    }, dispatcher.start_response)
    assert [b''] == actual
    assert _build_http_status(HTTPStatus.NOT_FOUND) == dispatcher.status


def test_preflight_missing_origin():
    handler = EventHandler(handle_connect=lambda x: {})
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    actual = app({
        'HTTP_CE_AWPSVERSION': '1.0',
        'PATH_INFO': '/upstream',
    }, dispatcher.start_response)
    assert [b'Missing webhook request origin.'] == actual
    assert _build_http_status(HTTPStatus.BAD_REQUEST) == dispatcher.status


@pytest.mark.parametrize(
    "http_method",
    [
        pytest.param(""),
        pytest.param("GET"),
        pytest.param("PUT"),
        pytest.param("DELETE"),
        pytest.param("INVALID"),
    ]
)
def test_not_allowed_http_methods(http_method):
    handler = EventHandler(handle_connect=lambda x: {})
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    actual = app({
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
        "REQUEST_METHOD": http_method,
    }, dispatcher.start_response)
    assert [b''] == actual
    assert _build_http_status(
        HTTPStatus.METHOD_NOT_ALLOWED) == dispatcher.status


def test_preflight_failed():
    handler = EventHandler(
        handle_connect=lambda x: {},
        request_validator=AccessKeyValidator("Endpoint=foo.bar;AccessKey=aaa"),
    )

    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    actual = app({
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo',
        'PATH_INFO': '/upstream',
        "REQUEST_METHOD": "OPTIONS",
    }, dispatcher.start_response)
    assert [b'Abuse protection validation failed.'] == actual
    assert _build_http_status(HTTPStatus.BAD_REQUEST) == dispatcher.status


def test_preflight_passed():
    handler = EventHandler(handle_connect=lambda x: {})
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    actual = app({
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
        "REQUEST_METHOD": "OPTIONS",
    }, dispatcher.start_response)
    assert [b''] == actual
    assert _build_http_status(HTTPStatus.OK) == dispatcher.status

    headers = {k: v for (k, v) in dispatcher.headers}
    assert "*" == headers[WEBHOOK_REQUEST_ORIGIN]


@pytest.mark.parametrize(
    "header_key,required",
    [
        pytest.param(CE_CONNECTION_ID, True),
        pytest.param(CE_CONNECTION_STATE, True),
        pytest.param(CE_EVENT_NAME, True),
        pytest.param(CE_HUB, True),
        pytest.param(CE_SUBPROTOCOL, False),
        pytest.param(CE_TYPE, True),
        pytest.param(CE_USER_ID, False),
    ]
)
def test_missing_required_headers(header_key: str, required: bool):
    handler = EventHandler(handle_connect=lambda x: {})
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    headers = {
        "REQUEST_METHOD": "POST",
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_CE_CONNECTIONID': 'abcdefg',
        'HTTP_CE_CONNECTIONSTATE': build_connection_state(),
        'HTTP_CE_EVENTNAME': 'connect',
        'HTTP_CE_HUB': 'chat',
        'HTTP_CE_SUBPROTOCOL': 'primary',
        'HTTP_CE_TYPE': EVENT_SYS_CONNECTED,
        'HTTP_CE_USERID': 'tefa',
        'HTTP_CE_SIGNATURE': 'abc',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
    }

    del headers["HTTP_" + header_key.upper().replace('-', '_')]

    actual = app(headers, dispatcher.start_response)

    if required:
        assert [b''] == actual
        assert _build_http_status(HTTPStatus.BAD_REQUEST) == dispatcher.status
    else:
        assert _build_http_status(HTTPStatus.OK) == dispatcher.status


@pytest.mark.parametrize(
    "signature,success",
    [
        pytest.param(None, False),
        pytest.param("abc", True),
    ]
)
def test_signature_validation_failed(signature: str, success: bool):
    handler = EventHandler(
        handle_connect=lambda x: {},
        request_validator=AccessKeyValidator("Endpoint=foo.bar;AccessKey=aaa"),
    )
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    headers = {
        "REQUEST_METHOD": "POST",
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_CE_CONNECTIONID': 'abcdefg',
        'HTTP_CE_CONNECTIONSTATE': build_connection_state(),
        'HTTP_CE_EVENTNAME': 'connect',
        'HTTP_CE_HUB': 'chat',
        'HTTP_CE_SIGNATURE': signature,
        'HTTP_CE_SUBPROTOCOL': 'primary',
        'HTTP_CE_TYPE': EVENT_SYS_CONNECTED,
        'HTTP_CE_USERID': 'tefa',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
    }

    actual = app(headers, dispatcher.start_response)

    if success:
        assert _build_http_status(HTTPStatus.OK) == dispatcher.status
    else:
        assert _build_http_status(HTTPStatus.UNAUTHORIZED) == dispatcher.status
    assert [b''] == actual


@pytest.mark.parametrize(
    "event_type,exists",
    [
        pytest.param(EVENT_SYS_CONNECTED, True),
        pytest.param(EVENT_USER_MESSAGE, True),
        pytest.param("", False),
        pytest.param("foo.bar", False),
        pytest.param("azure.sys.message", False),
    ]
)
def test_invalid_event_type(event_type: str, exists: bool):
    handler = EventHandler(handle_connect=lambda x: {})
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    headers = {
        "REQUEST_METHOD": "POST",
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_CE_CONNECTIONID': 'abcdefg',
        'HTTP_CE_CONNECTIONSTATE': build_connection_state(),
        'HTTP_CE_EVENTNAME': 'connect',
        'HTTP_CE_HUB': 'chat',
        'HTTP_CE_SUBPROTOCOL': 'primary',
        'HTTP_CE_TYPE': event_type,
        'HTTP_CE_USERID': 'tefa',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
    }

    actual = app(headers, dispatcher.start_response)

    if exists:
        assert _build_http_status(HTTPStatus.OK) == dispatcher.status
    else:
        assert _build_http_status(HTTPStatus.BAD_REQUEST) == dispatcher.status
    assert [b''] == actual


@pytest.mark.parametrize(
    "with_handler",
    [
        pytest.param(True),
        pytest.param(False),
    ]
)
def test_disconnected(with_handler: bool):

    called = [False]

    def handle_disconnected(req: DisconnectedEventRequest):
        called[0] = True
        assert req.reason == "foobar"

    handler = EventHandler(
        handle_connect=lambda x: {},
        handle_disconnected=handle_disconnected if with_handler else None,
    )
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    environ = {
        "REQUEST_METHOD": "POST",
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_CE_CONNECTIONID': 'abcdefg',
        'HTTP_CE_CONNECTIONSTATE': build_connection_state(),
        'HTTP_CE_EVENTNAME': 'disconnected',
        'HTTP_CE_HUB': 'chat',
        'HTTP_CE_SIGNATURE': "abc",
        'HTTP_CE_SUBPROTOCOL': 'primary',
        'HTTP_CE_TYPE': EVENT_SYS_DISCONNECTED,
        'HTTP_CE_USERID': 'tefa',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
    }
    _set_payload(environ, json.dumps({'reason': 'foobar'}))

    actual = app(environ, dispatcher.start_response)

    assert _build_http_status(HTTPStatus.OK) == dispatcher.status
    assert [b''] == actual
    assert called[0] == with_handler


@pytest.mark.parametrize(
    "with_handler",
    [
        pytest.param(True),
        pytest.param(False),
    ]
)
def test_user_message(with_handler: bool):
    called = [False]

    def handle_user_message(req: MessageEventRequest):
        called[0] = True
        assert req.hub == "chat"
        assert req.payload == "Customized payload"
        return 'Customized response'

    handler = EventHandler(
        handle_connect=lambda x: {},
        handle_user_message=handle_user_message if with_handler else None
    )
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    environ = {
        "REQUEST_METHOD": "POST",
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_CE_CONNECTIONID': 'abcdefg',
        'HTTP_CE_CONNECTIONSTATE': build_connection_state(),
        'HTTP_CE_EVENTNAME': 'message',
        'HTTP_CE_HUB': 'chat',
        'HTTP_CE_SIGNATURE': "abc",
        'HTTP_CE_SUBPROTOCOL': 'primary',
        'HTTP_CE_TYPE': EVENT_USER_MESSAGE,
        'HTTP_CE_USERID': 'tefa',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
    }
    _set_payload(environ, "Customized payload")

    actual = app(environ, dispatcher.start_response)

    assert _build_http_status(HTTPStatus.OK) == dispatcher.status
    assert [b'Customized response'] if with_handler else [b''] == actual
    assert called[0] == with_handler


def test_connect():
    called = [False]

    claims = {
        "iat": ["1632476178"],
        "nbf": ["1632476178"],
        "exp": ["1632476178"],
    }

    query = {
        "access_token": "ABC.DEF.GHI"
    }

    subprotocols = ["protocol1", "protocol2"]

    client_certificates = [{
        "thumbprint": "ABC"
    }]

    def handle_connect(req: ConnectEventRequest):
        called[0] = True
        assert req.hub == "chat"
        assert claims == req.claims
        assert query == req.query
        assert subprotocols == req.subprotocols
        assert client_certificates == req.client_certificates
        return {
            "foo": "bar"
        }

    handler = EventHandler(
        handle_connect=handle_connect,
    )
    app = handler.wrap(default_app, '/upstream')
    dispatcher = TestDispatcher()
    environ = {
        "REQUEST_METHOD": "POST",
        'HTTP_CE_AWPSVERSION': '1.0',
        'HTTP_CE_CONNECTIONID': 'abcdefg',
        'HTTP_CE_CONNECTIONSTATE': build_connection_state(),
        'HTTP_CE_EVENTNAME': 'connect',
        'HTTP_CE_HUB': 'chat',
        'HTTP_CE_SIGNATURE': "abc",
        'HTTP_CE_SUBPROTOCOL': 'primary',
        'HTTP_CE_TYPE': EVENT_SYS_CONNECT,
        'HTTP_CE_USERID': 'tefa',
        'HTTP_WEBHOOK_REQUEST_ORIGIN': 'foo.bar',
        'PATH_INFO': '/upstream',
    }

    data = {
        "claims": claims,
        "query": query,
        "subprotocols": subprotocols,
        "clientCertificates": client_certificates
    }
    _set_payload(environ, json.dumps(data))

    actual = app(environ, dispatcher.start_response)

    assert _build_http_status(HTTPStatus.OK) == dispatcher.status
    assert [bytes(json.dumps({"foo": "bar"}), 'utf-8')] == actual
    assert called[0]


if __name__ == '__main__':
    test_skip_when_path_mismatch()
