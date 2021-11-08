# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from azure.core.rest import HttpRequest
from azure.core.exceptions import ResponseNotReadError

def test_normal_call(client, port):
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

# TODO: commenting until https://github.com/Azure/azure-sdk-for-python/issues/18086 is fixed

# def test_stream_with_error(client):
#     request = HttpRequest("GET", url="/streams/error")
#     with client.send_request(request, stream=True) as response:
#         assert not response.is_closed
#         with pytest.raises(HttpResponseError) as e:
#             response.raise_for_status()
#         error = e.value
#         assert error.status_code == 400
#         assert error.reason == "BAD REQUEST"
#         assert "Operation returned an invalid status 'BAD REQUEST'" in str(error)
#         with pytest.raises(ResponseNotReadError):
#             error.error
#         with pytest.raises(ResponseNotReadError):
#             error.model
#         with pytest.raises(ResponseNotReadError):
#             response.json()
#         with pytest.raises(ResponseNotReadError):
#             response.content

#         # NOW WE READ THE RESPONSE
#         response.read()
#         assert error.status_code == 400
#         assert error.reason == "BAD REQUEST"
#         assert error.error.code == "BadRequest"
#         assert error.error.message == "You made a bad request"
#         assert error.model.code == "BadRequest"
#         assert error.error.message == "You made a bad request"
