# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from azure.core.pipeline.transport import AsyncioRequestsTransport, HttpRequest as PipelineTransportHttpRequest
from azure.core.rest import HttpRequest as RestHttpRequest

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_async_gen_data(http_request):
    class AsyncGen:
        def __init__(self):
            self._range = iter([b"azerty"])

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self._range)
            except StopIteration:
                raise StopAsyncIteration

    async with AsyncioRequestsTransport() as transport:
        req = http_request('GET', 'http://httpbin.org/anything', data=AsyncGen())
        response = await transport.send(req)
        assert json.loads(response.text())['data'] == "azerty"

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_send_data(http_request):
    async with AsyncioRequestsTransport() as transport:
        req = http_request('PUT', 'http://httpbin.org/anything', data=b"azerty")
        response = await transport.send(req)

        assert json.loads(response.text())['data'] == "azerty"