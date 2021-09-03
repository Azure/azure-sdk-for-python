# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.core.pipeline.transport import TrioRequestsTransport
from azure.core.rest import HttpRequest
from rest_client_async import AsyncTestRestClient

import pytest


@pytest.mark.trio
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

    async with TrioRequestsTransport() as transport:
        client = AsyncTestRestClient(port, transport=transport)
        request = HttpRequest('GET', 'http://localhost:{}/basic/anything'.format(port), content=AsyncGen())
        response = await client.send_request(request)
        assert response.json()['data'] == "azerty"

@pytest.mark.trio
async def test_send_data(port):
    async with TrioRequestsTransport() as transport:
        request = HttpRequest('PUT', 'http://localhost:{}/basic/anything'.format(port), content=b"azerty")
        client = AsyncTestRestClient(port, transport=transport)
        response = await client.send_request(request)

        assert response.json()['data'] == "azerty"
