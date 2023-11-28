# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from corehttp.rest import HttpRequest
from corehttp.exceptions import ResponseNotReadError


def test_normal_call(client):
    def _raise_and_get_text(response):
        response.raise_for_status()
        assert response.text() == "Hello, world!"
        assert response.is_closed

    request = HttpRequest("GET", url="/basic/string")
    response = client.send_request(request)
    _raise_and_get_text(response)
    assert response.is_closed

    with client.send_request(request) as response:
        _raise_and_get_text(response)

    response = client.send_request(request)
    with response as response:
        _raise_and_get_text(response)


def test_stream_call(client):
    def _raise_and_get_text(response):
        response.raise_for_status()
        assert not response.is_closed
        with pytest.raises(ResponseNotReadError):
            response.text()
        response.read()
        assert response.text() == "Hello, world!"
        assert response.is_closed

    request = HttpRequest("GET", url="/streams/basic")
    response = client.send_request(request, stream=True)
    _raise_and_get_text(response)
    assert response.is_closed

    with client.send_request(request, stream=True) as response:
        _raise_and_get_text(response)
    assert response.is_closed

    response = client.send_request(request, stream=True)
    with response as response:
        _raise_and_get_text(response)
