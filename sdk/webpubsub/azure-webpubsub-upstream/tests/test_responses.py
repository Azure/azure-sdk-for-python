# coding=utf-8
# --------------------------------------------------------------------------
# Created on Thu Sep 23 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------
import json

from guid import guid

from azure.messaging.webpubsub.upstream import (
    EventHandler,
    ServiceResponse,
    ConnectEventResponse,
    MessageEventResponse,
)

from azure.messaging.webpubsub.upstream.headers import (
    CE_CONNECTION_ID,
    CE_HUB,
    CE_TYPE,
    CE_EVENT_NAME,
    CE_CONNECTION_STATE,
    WEBHOOK_REQUEST_ORIGIN,
)

from .test_utils import (
    build_connection_state,
)

protocol1 = "protocol1"
protocol2 = "protocol2"


def mock_handler(req):
    return {}


def test_handle_connect():

    groups = ["foo", "bar"]
    userId = "tefa"
    roles = ["webpubsub.sendToGroup"]
    subprotocol = protocol1

    def handle_connect(request):
        return {
            "groups": groups,
            "userId": userId,
            "roles": roles,
            "subprotocol": subprotocol,
        }

    helper = EventHandler(handle_connect=handle_connect)

    ce_connection_id = str(guid.uuid4())
    ce_hub = "foo"
    ce_type = "azure.webpubsub.sys.connect"
    ce_event_name = "connect"
    ce_connection_state = build_connection_state()
    origin = "foo.webpubsub.azure.com"

    headers = {
        CE_CONNECTION_ID: ce_connection_id,
        CE_HUB: ce_hub,
        CE_TYPE: ce_type,
        CE_EVENT_NAME: ce_event_name,
        CE_CONNECTION_STATE: ce_connection_state,
        WEBHOOK_REQUEST_ORIGIN: origin,
    }

    body = json.dumps({
        "claims": {},
        "query": {},
        "subprotocols": [],
        "clientCertificates": []
    })

    response = helper.handle(headers, body)
    assert isinstance(response, ConnectEventResponse)
    assert response.status.value == 200

    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({})
    response.set_state("key", "next_state")
    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({"key": "next_state"})
    response.clear_states()
    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({})

    assert response.payload == json.dumps({
        "groups": groups,
        "userId": userId,
        "roles": roles,
        "subprotocol": subprotocol,
    })


def test_handle_connected():

    a = []

    def handle_connected(req):
        a.append(1)

    ce_connection_id = str(guid.uuid4())
    ce_hub = "foo"
    ce_type = "azure.webpubsub.sys.connected"
    ce_event_name = "connect"
    ce_connection_state = build_connection_state()
    origin = "foo.webpubsub.azure.com"

    headers = {
        CE_CONNECTION_ID: ce_connection_id,
        CE_HUB: ce_hub,
        CE_TYPE: ce_type,
        CE_EVENT_NAME: ce_event_name,
        CE_CONNECTION_STATE: ce_connection_state,
        WEBHOOK_REQUEST_ORIGIN: origin,
    }

    body = json.dumps({})

    helper = EventHandler(handle_connect=mock_handler, handle_connected=handle_connected)
    response = helper.handle(headers, body)

    assert isinstance(response, ServiceResponse)
    assert response.status.value == 200
    assert response.headers == {}
    assert response.payload == ""
    assert len(a) == 1


def test_handle_disconnected():
    a = []

    def handle_disconnected(req):
        a.append(1)

    ce_connection_id = str(guid.uuid4())
    ce_hub = "foo"
    ce_type = "azure.webpubsub.sys.disconnected"
    ce_event_name = "disconnect"
    ce_connection_state = build_connection_state()
    origin = "foo.webpubsub.azure.com"

    headers = {
        CE_CONNECTION_ID: ce_connection_id,
        CE_HUB: ce_hub,
        CE_TYPE: ce_type,
        CE_EVENT_NAME: ce_event_name,
        CE_CONNECTION_STATE: ce_connection_state,
        WEBHOOK_REQUEST_ORIGIN: origin,
    }

    body = json.dumps({})

    helper = EventHandler(handle_connect=mock_handler, handle_disconnected=handle_disconnected)
    response = helper.handle(headers, body)

    assert isinstance(response, ServiceResponse)
    assert response.status.value == 200
    assert response.headers == {}
    assert response.payload == ""
    assert len(a) == 1


def test_handle_user_message():

    customized_request = "this is a customized request"
    customized_response = "this is a customized response"

    def handle_user_message(req):
        assert req.payload == customized_request
        return customized_response

    ce_connection_id = str(guid.uuid4())
    ce_hub = "foo"
    ce_type = "azure.webpubsub.user.message"
    ce_event_name = "message"
    ce_connection_state = build_connection_state({"foo": "bar"})
    origin = "foo.webpubsub.azure.com"

    headers = {
        CE_CONNECTION_ID: ce_connection_id,
        CE_HUB: ce_hub,
        CE_TYPE: ce_type,
        CE_EVENT_NAME: ce_event_name,
        CE_CONNECTION_STATE: ce_connection_state,
        WEBHOOK_REQUEST_ORIGIN: origin,
    }

    helper = EventHandler(handle_connect=mock_handler, handle_user_message=handle_user_message)
    response = helper.handle(headers, customized_request)

    assert isinstance(response, MessageEventResponse)
    assert response.status.value == 200

    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({"foo": "bar"})
    response.clear_states()
    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({})

    assert response.payload == customized_response


def test_update_connection_state():
    ce_connection_id = str(guid.uuid4())
    ce_hub = "foo"
    ce_type = "azure.webpubsub.user.message"
    ce_event_name = "message"
    ce_connection_state = build_connection_state({"foo": "bar"})
    origin = "foo.webpubsub.azure.com"

    headers = {
        CE_CONNECTION_ID: ce_connection_id,
        CE_HUB: ce_hub,
        CE_TYPE: ce_type,
        CE_EVENT_NAME: ce_event_name,
        CE_CONNECTION_STATE: ce_connection_state,
        WEBHOOK_REQUEST_ORIGIN: origin,
    }

    helper = EventHandler(handle_connect=lambda x: {})
    response = helper.handle(headers, "")

    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({"foo": "bar"})
    response.set_state("foo", "far")
    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({"foo": "far"})
    response.set_state("far", "foo")
    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({"foo": "far", "far": "foo"})
    response.del_state("foo")
    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({"far": "foo"})
    response.clear_states()
    assert response.headers[CE_CONNECTION_STATE] == build_connection_state({})