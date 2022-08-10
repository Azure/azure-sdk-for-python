# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from azure.core.pipeline.transport import AsyncioRequestsTransport
from utils import HTTP_REQUESTS
from azure.core.pipeline._tools import is_rest
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_async_gen_data(port, http_request):
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
        req = http_request('GET', 'http://localhost:{}/basic/anything'.format(port), data=AsyncGen())
        response = await transport.send(req)
        if is_rest(http_request):
            assert is_rest(response)
        assert json.loads(response.text())['data'] == "azerty"

@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_send_data(port, http_request):
    async with AsyncioRequestsTransport() as transport:
        req = http_request('PUT', 'http://localhost:{}/basic/anything'.format(port), data=b"azerty")
        response = await transport.send(req)
        if is_rest(http_request):
            assert is_rest(response)
        assert json.loads(response.text())['data'] == "azerty"

def test_open_closed_asyncio_transport():
    transport = AsyncioRequestsTransport()
    transport.close()
    transport.open()
    assert not transport.session
