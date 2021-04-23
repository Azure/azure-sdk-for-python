# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from mock import AsyncMock
import sys
from azure.core.exceptions import HttpResponseError
from azure.core.rest import HttpRequest, ResponseNotReadError
from azure.core.rest._rest_py3 import _AsyncStreamContextManager

from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import AioHttpTransport

@pytest.mark.asyncio
async def test_stream_context_manager():
    async def monkey_patch_magic_mock():
        pass
    transport = AsyncMock()
    async with AsyncPipeline(transport=transport) as pipeline:
        async with _AsyncStreamContextManager(pipeline=pipeline, request=HttpRequest(method="GET", url="https://httpbin.org/get")) as r:
            response = r

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
    assert internal_response_mock_calls[0][0] == 'close'  # assert exit was called

@pytest.mark.asyncio
async def test_stream_context_manager_error():
    async with AsyncPipeline(transport=AioHttpTransport()) as pipeline:
        async with _AsyncStreamContextManager(pipeline=pipeline, request=HttpRequest(method="GET", url="https://httpbin.org/status/404")) as r:
            with pytest.raises(HttpResponseError) as e:
                r.raise_for_status()
            assert e.value.status_code == 404
            assert e.value.reason == "NOT FOUND"
            with pytest.raises(ResponseNotReadError):
                str(e.value)
            with pytest.raises(ResponseNotReadError):
                r.json()
            with pytest.raises(ResponseNotReadError):
                r.content
            await r.read()
            assert str(e.value) == "HttpResponseError: 404 NOT FOUND"
            assert r.content == b''
    assert r.is_closed
    assert r.is_stream_consumed