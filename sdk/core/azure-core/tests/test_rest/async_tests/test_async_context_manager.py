# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.exceptions import HttpResponseError
import pytest
from azure.core.rest import HttpRequest, ResponseNotReadError

@pytest.mark.asyncio
async def test_normal_call(client):
    async def _raise_and_get_text(response):
        response.raise_for_status()
        await response.read()
        assert response.text == "Hello, world!"
        assert response.is_closed
    request = HttpRequest("GET", url="http://127.0.0.1:5000/basic/string")
    response = await client.send_request(request)
    await _raise_and_get_text(response)
    assert response.is_closed

    async with client.send_request(request) as response:
        await _raise_and_get_text(response)

    response = client.send_request(request)
    async with response as response:
        await _raise_and_get_text(response)

@pytest.mark.asyncio
async def test_stream_call(client):
    async def _raise_and_get_text(response):
        response.raise_for_status()
        assert not response.is_closed
        await response.read()
        assert response.text == "Hello, world!"
        assert response.is_closed
    request = HttpRequest("GET", url="http://127.0.0.1:5000/streams/basic")
    response = await client.send_request(request, stream=True)
    await _raise_and_get_text(response)
    assert response.is_closed

    async with client.send_request(request) as response:
        await _raise_and_get_text(response)
    assert response.is_closed

    response = client.send_request(request)
    async with response as response:
        await _raise_and_get_text(response)

@pytest.mark.asyncio
async def test_stream_with_error(client):
    request = HttpRequest("GET", url="http://127.0.0.1:5000/streams/error")
    async with client.send_request(request, stream=True) as response:
        assert not response.is_closed
        with pytest.raises(HttpResponseError) as e:
            response.raise_for_status()
        error = e.value
        assert error.status_code == 400
        assert error.reason == "BAD REQUEST"
        assert "Operation returned an invalid status 'BAD REQUEST'" in str(error)
        with pytest.raises(ResponseNotReadError):
            error.error
        with pytest.raises(ResponseNotReadError):
            error.model
        with pytest.raises(ResponseNotReadError):
            response.json()
        with pytest.raises(ResponseNotReadError):
            response.content

        # NOW WE READ THE RESPONSE
        await response.read()
        assert error.status_code == 400
        assert error.reason == "BAD REQUEST"
        assert error.error.code == "BadRequest"
        assert error.error.message == "You made a bad request"
        assert error.model.code == "BadRequest"
        assert error.error.message == "You made a bad request"




# # @pytest.mark.asyncio
# # async def test_stream_context_manager_error(client):
# #     request = HttpRequest(method="GET", url="https://httpbin.org/status/404")
# #     async with client.send_request(request, stream_response=True) as r:
# #         with pytest.raises(HttpResponseError) as e:
# #             r.raise_for_status()
# #         assert error.status_code == 404
# #         assert error.reason == "NOT FOUND"
# #         with pytest.raises(ResponseNotReadError):
# #             str(error)
# #         with pytest.raises(ResponseNotReadError):
# #             r.json()
# #         with pytest.raises(ResponseNotReadError):
# #             r.content
# #         await r.read()
# #         assert str(error) == "Operation returned an invalid status 'NOT FOUND'"
# #         assert r.content == b''
# #     assert r.is_closed
# #     assert r.is_stream_consumed

# a = "b"
        # assert len(transport.method_calls) == 1
        # method_call = transport.method_calls[0]
        # assert method_call[0] == 'send'  # check method call name

        # assert len(method_call[1])  # assert args
        # arg = method_call[1][0]
        # assert arg.url == "https://httpbin.org/get"
        # assert arg.method == "GET"

        # assert method_call[2] == {"stream": True}  # check kwargs

    # assert actual response from requests etc is closed
    # internal_response_mock_calls = response._internal_response.internal_response.mock_calls
    # assert len(internal_response_mock_calls) == 1
    # assert internal_response_mock_calls[0][0] == '__aexit__'  # assert exit was called
