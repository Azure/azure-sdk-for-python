# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest
from mock import AsyncMock
import sys
from azure.core.rest import HttpRequest
from azure.core.rest._rest_py3 import _AsyncStreamContextManager

from azure.core._pipeline_client_async import AsyncPipelineClient

@pytest.mark.asyncio
async def test_rest_stream_context_manager():
    async def monkey_patch_magic_mock():
        pass
    transport = AsyncMock()
    client = AsyncPipelineClient(base_url="", transport=transport)
    async with _AsyncStreamContextManager(client=client, request=HttpRequest(method="GET", url="https://httpbin.org/get")) as r:
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
    assert internal_response_mock_calls[0][0] == '__aexit__'  # assert exit was called
