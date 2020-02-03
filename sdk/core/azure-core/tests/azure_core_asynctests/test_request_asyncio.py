# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from azure.core.pipeline.transport import AsyncioRequestsTransport, HttpRequest

import pytest


@pytest.mark.asyncio
async def test_async_gen_data():
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
        req = HttpRequest('GET', 'http://httpbin.org/post', data=AsyncGen())
        await transport.send(req)

@pytest.mark.asyncio
async def test_send_data():
    async with AsyncioRequestsTransport() as transport:
        req = HttpRequest('PUT', 'http://httpbin.org/anything', data=b"azerty")
        response = await transport.send(req)

        assert json.loads(response.text())['data'] == "azerty"