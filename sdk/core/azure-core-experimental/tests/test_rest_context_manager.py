# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from itertools import product

from azure.core.exceptions import ResponseNotReadError

from utils import SYNC_TRANSPORTS, HTTP_REQUESTS, create_http_request
from rest_client import MockRestClient


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_normal_call(port, transport, requesttype):
    def _raise_and_get_text(response):
        response.raise_for_status()
        assert response.text() == "Hello, world!"
        assert response.is_closed

    request = create_http_request(requesttype, "GET", "/basic/string")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request)
    _raise_and_get_text(response)

    with client.send_request(request) as response:
        _raise_and_get_text(response)

    response = client.send_request(request)
    with response as response:
        _raise_and_get_text(response)


@pytest.mark.parametrize("transport,requesttype", product(SYNC_TRANSPORTS, HTTP_REQUESTS))
def test_stream_call(port, transport, requesttype):
    def _raise_and_get_text(response):
        response.raise_for_status()
        assert not response.is_closed
        with pytest.raises(ResponseNotReadError):
            response.text()
        response.read()
        assert response.text() == "Hello, world!"
        assert response.is_closed

    request = create_http_request(requesttype, "GET", "/streams/basic")
    client = MockRestClient(port, transport=transport())
    response = client.send_request(request, stream=True)
    _raise_and_get_text(response)

    with client.send_request(request, stream=True) as response:
        _raise_and_get_text(response)

    response = client.send_request(request, stream=True)
    with response as response:
        _raise_and_get_text(response)
