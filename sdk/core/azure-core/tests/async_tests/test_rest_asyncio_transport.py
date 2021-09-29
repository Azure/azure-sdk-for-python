# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline.transport import AsyncioRequestsTransport
from azure.core.rest import HttpRequest
from azure.core.rest._requests_asyncio import RestAsyncioRequestsTransportResponse
from rest_client_async import AsyncTestRestClient

import pytest
from utils import readonly_checks

@pytest.mark.asyncio
async def test_async_gen_data(port):
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
        client = AsyncTestRestClient(port, transport=transport)
        request = HttpRequest('GET', 'http://localhost:{}/basic/anything'.format(port), content=AsyncGen())
        response = await client.send_request(request)
        assert response.json()['data'] == "azerty"

@pytest.mark.asyncio
async def test_send_data(port):
    async with AsyncioRequestsTransport() as transport:
        client = AsyncTestRestClient(port, transport=transport)
        request = HttpRequest('PUT', 'http://localhost:{}/basic/anything'.format(port), content=b"azerty")
        response = await client.send_request(request)

        assert response.json()['data'] == "azerty"

@pytest.mark.asyncio
async def test_readonly(port):
    """Make sure everything that is readonly is readonly"""
    async with AsyncioRequestsTransport() as transport:
        client = AsyncTestRestClient(port, transport=transport)
        response = await client.send_request(HttpRequest("GET", "/health"))
        response.raise_for_status()

    assert isinstance(response, RestAsyncioRequestsTransportResponse)
    from azure.core.pipeline.transport import AsyncioRequestsTransportResponse
    readonly_checks(response, old_response_class=AsyncioRequestsTransportResponse)
