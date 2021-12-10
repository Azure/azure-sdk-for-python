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

@pytest.fixture
async def client(port):
    async with AsyncioRequestsTransport() as transport:
        async with AsyncTestRestClient(port, transport=transport) as client:
            yield client

@pytest.mark.asyncio
async def test_async_gen_data(port, client):
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

    request = HttpRequest('GET', 'http://localhost:{}/basic/anything'.format(port), content=AsyncGen())
    response = await client.send_request(request)
    assert response.json()['data'] == "azerty"

@pytest.mark.asyncio
async def test_send_data(port, client):
    request = HttpRequest('PUT', 'http://localhost:{}/basic/anything'.format(port), content=b"azerty")
    response = await client.send_request(request)

    assert response.json()['data'] == "azerty"

@pytest.mark.asyncio
async def test_readonly(client):
    """Make sure everything that is readonly is readonly"""
    response = await client.send_request(HttpRequest("GET", "/health"))
    response.raise_for_status()

    assert isinstance(response, RestAsyncioRequestsTransportResponse)
    from azure.core.pipeline.transport import AsyncioRequestsTransportResponse
    readonly_checks(response, old_response_class=AsyncioRequestsTransportResponse)

@pytest.mark.asyncio
async def test_decompress_compressed_header(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = await client.send_request(request)
    content = await response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"

@pytest.mark.asyncio
async def test_decompress_compressed_header_stream(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = await client.send_request(request, stream=True)
    content = await response.read()
    assert content == b"hello world"
    assert response.content == content
    assert response.text() == "hello world"

@pytest.mark.asyncio
async def test_decompress_compressed_header_stream_body_content(client):
    # expect plain text
    request = HttpRequest("GET", "/encoding/gzip")
    response = await client.send_request(request, stream=True)
    await response.read()
    content = response.content
    assert content == response.body()
