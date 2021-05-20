# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from async_generator import yield_, async_generator
import pytest
from mock import AsyncMock
from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpRequest, ResponseNotReadError

@pytest.mark.asyncio
async def test_stream_context_manager(client):
    request = HttpRequest(method="GET", url="https://httpbin.org/get")
    async with client.send_request(request, stream_response=True) as response:

        assert len(transport.method_calls) == 1
        method_call = transport.method_calls[0]
        assert method_call[0] == 'send'  # check method call name

        assert len(method_call[1])  # assert args
        arg = method_call[1][0]
        assert arg.url == "https://httpbin.org/get"
        assert arg.method == "GET"

        assert method_call[2] == {"stream": True}  # check kwargs

    # assert actual response from requests etc is closed
    internal_response_mock_calls = response._internal_response.internal_response.mock_calls
    assert len(internal_response_mock_calls) == 1
    assert internal_response_mock_calls[0][0] == '__aexit__'  # assert exit was called

# @pytest.mark.asyncio
# async def test_stream_context_manager_error(client):
#     request = HttpRequest(method="GET", url="https://httpbin.org/status/404")
#     async with client.send_request(request, stream_response=True) as r:
#         with pytest.raises(HttpResponseError) as e:
#             r.raise_for_status()
#         assert e.value.status_code == 404
#         assert e.value.reason == "NOT FOUND"
#         with pytest.raises(ResponseNotReadError):
#             str(e.value)
#         with pytest.raises(ResponseNotReadError):
#             r.json()
#         with pytest.raises(ResponseNotReadError):
#             r.content
#         await r.read()
#         assert str(e.value) == "Operation returned an invalid status 'NOT FOUND'"
#         assert r.content == b''
#     assert r.is_closed
#     assert r.is_stream_consumed