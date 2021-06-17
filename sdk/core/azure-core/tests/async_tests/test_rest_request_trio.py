# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json

from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.transport import TrioRequestsTransport
from azure.core.rest import HttpRequest, ResponseNotReadError, StreamConsumedError

import pytest


@pytest.mark.trio
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

    async with TrioRequestsTransport() as transport:
        pipeline = AsyncPipeline(transport=transport)
        req = HttpRequest('GET', 'http://httpbin.org/anything', data=AsyncGen())
        response = await pipeline.run(req)
        assert response.http_response.json()['data'] == "azerty"

@pytest.mark.trio
async def test_send_data():
    async with TrioRequestsTransport() as transport:
        pipeline = AsyncPipeline(transport=transport)
        req = HttpRequest('PUT', 'http://httpbin.org/anything', data=b"azerty")
        response = await pipeline.run(req)

        assert response.http_response.json()['data'] == "azerty"


@pytest.mark.trio
async def test_iter_read_back_and_forth():
    # thanks to McCoy Patiño for this test!

    # while this test may look like it's exposing buggy behavior, this is httpx's behavior
    # the reason why the code flow is like this, is because the 'iter_x' functions don't
    # actually read the contents into the response, the output them. Once they're yielded,
    # the stream is closed, so you have to catch the output when you iterate through it
    request = HttpRequest("GET", "http://localhost:5000/basic/lines")

    async with TrioRequestsTransport() as transport:
        pipeline = AsyncPipeline(transport=transport)
        req = HttpRequest("GET", "http://localhost:5000/basic/lines")
        response = (await pipeline.run(req, stream=True)).http_response
        async for line in response.iter_lines():
            assert line
        with pytest.raises(ResponseNotReadError):
            response.text
        with pytest.raises(StreamConsumedError):
            await response.read()
        with pytest.raises(ResponseNotReadError):
            response.text
