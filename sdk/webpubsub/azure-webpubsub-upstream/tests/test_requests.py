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
    ConnectEventRequest,
    ConnectedEventRequest,
    DisconnectedEventRequest,
    MessageEventRequest,
)

from azure.messaging.webpubsub.upstream.headers import (
    CE_CONNECTION_ID,
    CE_CONNECTION_STATE,
    CE_HUB,
    CE_TYPE,
    CE_EVENT_NAME,
    WEBHOOK_REQUEST_ORIGIN,
)

from .test_utils import (
    build_connection_state,
    parse_connection_state,
)


def handle_connect():
    return {
        "user_id": "foo"
    }


helper = EventHandler(handle_connect=handle_connect)


def test_connect_event_request():
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

    body = json.dumps({
        "claims": claims,
        "query": query,
        "subprotocols": subprotocols,
        "clientCertificates": client_certificates
    })

    event = helper.from_http(headers, body)
    assert isinstance(event, ConnectEventRequest)
    assert event.connection_id == ce_connection_id
    assert event.connection_state == parse_connection_state(
        ce_connection_state)
    assert event.hub == ce_hub
    assert event.webhook_request_origin == origin
    assert event.is_blocking

    assert event.claims == claims
    assert event.query == query
    assert event.subprotocols == subprotocols
    assert event.client_certificates == client_certificates


def test_connected_event_request():
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

    event = helper.from_http(headers, body)
    assert isinstance(event, ConnectedEventRequest)
    assert event.connection_id == ce_connection_id
    assert event.connection_state == parse_connection_state(
        ce_connection_state)
    assert event.hub == ce_hub
    assert event.webhook_request_origin == origin
    assert not event.is_blocking


def test_disconnected_event_request():
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

    event = helper.from_http(headers, body)
    assert isinstance(event, DisconnectedEventRequest)
    assert event.connection_id == ce_connection_id
    assert event.connection_state == parse_connection_state(
        ce_connection_state)
    assert event.hub == ce_hub
    assert event.webhook_request_origin == origin
    assert not event.is_blocking


def test_user_message_event_request():
    ce_connection_id = str(guid.uuid4())
    ce_hub = "foo"
    ce_type = "azure.webpubsub.user.message"
    ce_event_name = "message"
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

    body = "user customized data"

    event = helper.from_http(headers, body)
    assert isinstance(event, MessageEventRequest)
    assert event.connection_id == ce_connection_id
    assert event.connection_state == parse_connection_state(
        ce_connection_state)
    assert event.hub == ce_hub
    assert event.webhook_request_origin == origin
    assert event.payload == body
    assert event.is_blocking


if __name__ == "__main__":
    test_connect_event_request()
