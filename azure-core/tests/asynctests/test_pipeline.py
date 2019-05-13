#--------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
#--------------------------------------------------------------------------
import sys

from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import SansIOHTTPPolicy, UserAgentPolicy, AsyncRedirectPolicy
from azure.core.pipeline.transport import (
    AsyncHttpTransport,
    HttpRequest,
    AsyncioRequestsTransport,
    TrioRequestsTransport,
    AioHttpTransport
)

import trio

import pytest


@pytest.mark.asyncio
async def test_sans_io_exception():
    class BrokenSender(AsyncHttpTransport):
        async def send(self, request, **config):
            raise ValueError("Broken")

        async def __aexit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return None

    pipeline = AsyncPipeline(BrokenSender(), [SansIOHTTPPolicy()])

    req = HttpRequest('GET', '/')
    with pytest.raises(ValueError):
        await pipeline.run(req)

    class SwapExec(SansIOHTTPPolicy):
        def on_exception(self, requests, **kwargs):
            exc_type, exc_value, exc_traceback = sys.exc_info()
            raise NotImplementedError(exc_value)

    pipeline = AsyncPipeline(BrokenSender(), [SwapExec()])
    with pytest.raises(NotImplementedError):
        await pipeline.run(req)


@pytest.mark.asyncio
async def test_basic_aiohttp():

    conf = Configuration()
    request = HttpRequest("GET", "https://bing.com")
    policies = [
        UserAgentPolicy("myusergant"),
        AsyncRedirectPolicy()
    ]
    async with AsyncPipeline(AioHttpTransport(conf), policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert pipeline._transport.session is None
    assert response.http_response.status_code == 200

@pytest.mark.asyncio
async def test_basic_async_requests():

    request = HttpRequest("GET", "https://bing.com")
    policies = [
        UserAgentPolicy("myusergant"),
        AsyncRedirectPolicy()
    ]
    async with AsyncPipeline(AsyncioRequestsTransport(), policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert response.http_response.status_code == 200

@pytest.mark.asyncio
async def test_conf_async_requests():

    conf = Configuration()
    request = HttpRequest("GET", "https://bing.com/")
    policies = [
        UserAgentPolicy("myusergant"),
        AsyncRedirectPolicy()
    ]
    async with AsyncPipeline(AsyncioRequestsTransport(conf), policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert response.http_response.status_code == 200

def test_conf_async_trio_requests():

    async def do():
        conf = Configuration()
        request = HttpRequest("GET", "https://bing.com/")
        policies = [
            UserAgentPolicy("myusergant"),
            AsyncRedirectPolicy()
        ]
        async with AsyncPipeline(TrioRequestsTransport(conf), policies=policies) as pipeline:
            return await pipeline.run(request)

    response = trio.run(do)
    assert response.http_response.status_code == 200