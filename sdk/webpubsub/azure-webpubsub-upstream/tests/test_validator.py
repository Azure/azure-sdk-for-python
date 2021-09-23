# coding=utf-8
# --------------------------------------------------------------------------
# Created on Tue Oct 19 2021
#
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root
# for license information.
# --------------------------------------------------------------------------

import pytest

from guid import guid

from http import HTTPStatus

from azure.messaging.webpubsub.upstream import (
    EventHandler,
    AccessKeyValidator,
)

from azure.messaging.webpubsub.upstream.headers import (
    CE_CONNECTION_ID,
    CE_CONNECTION_STATE,
    CE_HUB,
    CE_SIGNATURE,
    CE_TYPE,
    CE_EVENT_NAME,
    WEBHOOK_REQUEST_ORIGIN,
)

from azure.messaging.webpubsub.upstream.exceptions import (
    ValidationFailedError
)

from .test_utils import build_connection_state

ACCESS_KEY = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


@pytest.mark.parametrize(
    "conn_str,host,expected",
    [
        pytest.param("Endpoint=foo.bar;AccessKey=aaa", "foo.bar", True),
        pytest.param("Endpoint=foo.bar;AccessKey=aaa", "bar.foo", False),
        pytest.param("Endpoint=foo.bar;AccessKey=aaa", "", False),
        pytest.param(["Endpoint=foo.bar;AccessKey=aaa",
                     "Endpoint=bar.foo;AccessKey=aaa"], "foo.bar", True),
        pytest.param(["Endpoint=foo.bar;AccessKey=aaa",
                     "Endpoint=bar.foo;AccessKey=aaa"], "bar.foo", True),
        pytest.param(["Endpoint=foo.bar;AccessKey=aaa",
                     "Endpoint=bar.foo;AccessKey=aaa"], "", False),
    ]
)
def test_validator_contains(conn_str, host, expected):
    validator = AccessKeyValidator(conn_str)
    assert validator.contains(host) == expected


@pytest.mark.parametrize(
    "conn_str,origin,expected",
    [
        pytest.param("Endpoint=foo.bar;AccessKey=aaa", None, False),
        pytest.param("Endpoint=foo.bar;AccessKey=aaa", "", False),
        pytest.param("Endpoint=foo.bar;AccessKey=aaa", "foo.bar", True),
        pytest.param("Endpoint=foo.bar;AccessKey=aaa", "bar.foo", False),
        pytest.param(["Endpoint=foo.bar;AccessKey=aaa",
                     "Endpoint=bar.foo;AccessKey=aaa"], None, False),
        pytest.param(["Endpoint=foo.bar;AccessKey=aaa",
                     "Endpoint=bar.foo;AccessKey=aaa"], "", False),
        pytest.param(["Endpoint=foo.bar;AccessKey=aaa",
                     "Endpoint=bar.foo;AccessKey=aaa"], "foo.bar", True),
        pytest.param(["Endpoint=foo.bar;AccessKey=aaa",
                     "Endpoint=bar.foo;AccessKey=aaa"], "bar.foo", True),
    ]
)
def test_preflight(conn_str, origin, expected):
    validator = AccessKeyValidator(conn_str)
    helper = EventHandler(request_validator=validator,
                          handle_connect=lambda x: None)
    headers = {WEBHOOK_REQUEST_ORIGIN: origin} if origin is not None else {}
    assert helper.preflight(headers) == expected


def test_access_key_validator():
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

    validator = AccessKeyValidator(
        "Endpoint=foo.bar;AccessKey={}".format(ACCESS_KEY))
    helper = EventHandler(request_validator=validator,
                          handle_connect=lambda x: {})
    response = helper.handle(headers, "{}")
    assert response.status.value == HTTPStatus.UNAUTHORIZED.value

    headers[CE_SIGNATURE] = "abc"
    response = helper.handle(headers, "{}")
    assert response.status.value == HTTPStatus.OK.value


if __name__ == '__init__':
    test_access_key_validator()
