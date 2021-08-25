# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from azure.core.pipeline.transport import TrioRequestsTransport, HttpRequest

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
        req = HttpRequest('GET', 'http://localhost:{}/basic/anything'.format(port), data=AsyncGen())
        response = await transport.send(req)
        assert json.loads(response.text())['data'] == "azerty"

@pytest.mark.trio
async def test_send_data(port):
    async with TrioRequestsTransport() as transport:
        req = HttpRequest('PUT', 'http://localhost:{}/basic/anything'.format(port), data=b"azerty")
        response = await transport.send(req)

        assert json.loads(response.text())['data'] == "azerty"