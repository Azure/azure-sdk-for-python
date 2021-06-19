# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from azure.core.pipeline.transport import AsyncioRequestsTransport, HttpRequest as PipelineTransportHttpRequest
from azure.core.pipeline.transport._requests_asyncio import RestAsyncioRequestsTransportResponse
from azure.core.rest import HttpRequest as RestHttpRequest

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_async_gen_data(request_type):
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
        if hasattr(request_type, "content"):
            # only pipeline transport requests actually go into the transport code
            req = request_type('GET', 'http://httpbin.org/post', content=AsyncGen())._to_pipeline_transport_request()
        else:
            req = request_type('GET', 'http://httpbin.org/post', data=AsyncGen())
        await transport.send(req)

@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [PipelineTransportHttpRequest, RestHttpRequest])
async def test_send_data(request_type):
    async with AsyncioRequestsTransport() as transport:
        if hasattr(request_type, "content"):
            # only pipeline transport requests actually go into the transport code
            req = request_type('PUT', 'http://httpbin.org/anything', content=b"azerty")._to_pipeline_transport_request()
        else:
            req = request_type('PUT', 'http://httpbin.org/anything', data=b"azerty")
        response = await transport.send(req)

        assert json.loads(response.text())['data'] == "azerty"