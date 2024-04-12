# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from typing import cast
from unittest.mock import AsyncMock, PropertyMock, Mock

from corehttp.rest import HttpRequest
from corehttp.runtime import AsyncPipelineClient
from corehttp.runtime.pipeline import AsyncPipeline
from corehttp.runtime.policies import (
    SansIOHTTPPolicy,
    UserAgentPolicy,
    AsyncRetryPolicy,
    AsyncHTTPPolicy,
)
from corehttp.transport import AsyncHttpTransport
from corehttp.transport.aiohttp import AioHttpTransport
from corehttp.transport.httpx import AsyncHttpXTransport
from corehttp.exceptions import BaseError
import aiohttp
import httpx
import pytest

from utils import ASYNC_TRANSPORTS


@pytest.mark.asyncio
async def test_sans_io_exception():
    class BrokenSender(AsyncHttpTransport):
        async def send(self, request, **config):
            raise ValueError("Broken")

        async def open(self):
            self.session = aiohttp.ClientSession()

        async def close(self):
            await self.session.close()

        async def __aexit__(self, exc_type, exc_value, traceback):
            """Raise any exception triggered within the runtime context."""
            return self.close()

    pipeline = AsyncPipeline(BrokenSender(), [SansIOHTTPPolicy()])

    req = HttpRequest("GET", "/")
    with pytest.raises(ValueError):
        await pipeline.run(req)


def test_invalid_policy_error():
    # non-HTTPPolicy/non-SansIOHTTPPolicy should raise an error
    class FooPolicy:
        pass

    # sync send method should raise an error
    class SyncSendPolicy:
        def send(self, request):
            pass

    # only on_request should raise an error
    class OnlyOnRequestPolicy:
        def on_request(self, request):
            pass

    # only on_response should raise an error
    class OnlyOnResponsePolicy:
        def on_response(self, request, response):
            pass

    with pytest.raises(AttributeError):
        pipeline = AsyncPipeline(transport=Mock(), policies=[FooPolicy()])

    with pytest.raises(AttributeError):
        pipeline = AsyncPipeline(transport=Mock(), policies=[SyncSendPolicy()])

    with pytest.raises(AttributeError):
        pipeline = AsyncPipeline(transport=Mock(), policies=[OnlyOnRequestPolicy()])

    with pytest.raises(AttributeError):
        pipeline = AsyncPipeline(transport=Mock(), policies=[OnlyOnResponsePolicy()])


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ASYNC_TRANSPORTS)
async def test_transport_socket_timeout(transport):
    request = HttpRequest("GET", "https://bing.com")
    policies = [UserAgentPolicy("myusergant")]
    # Sometimes this will raise a read timeout, sometimes a socket timeout depending on timing.
    # Either way, the error should always be wrapped as an BaseError to ensure it's caught
    # by the retry policy.
    with pytest.raises(BaseError):
        async with AsyncPipeline(transport(), policies=policies) as pipeline:
            response = await pipeline.run(request, connection_timeout=0.000001, read_timeout=0.000001)


@pytest.mark.asyncio
async def test_basic_aiohttp(port):

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant"), AsyncRetryPolicy()]
    async with AsyncPipeline(AioHttpTransport(), policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert cast(AioHttpTransport, pipeline._transport).session is None
    # all we need to check is if we are able to make the call
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.asyncio
async def test_basic_aiohttp_separate_session(port):

    session = aiohttp.ClientSession()
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant"), AsyncRetryPolicy()]
    transport = AioHttpTransport(session=session, session_owner=False)
    async with AsyncPipeline(transport, policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert transport.session
    assert isinstance(response.http_response.status_code, int)
    await transport.close()
    assert transport.session
    await transport.session.close()


@pytest.mark.asyncio
async def test_retry_without_http_response():
    class NaughtyPolicy(AsyncHTTPPolicy):
        async def send(*args):
            raise BaseError("boo")

    policies = [AsyncRetryPolicy(), NaughtyPolicy()]
    pipeline = AsyncPipeline(policies=policies, transport=None)
    with pytest.raises(BaseError):
        await pipeline.run(HttpRequest("GET", url="https://foo.bar"))


@pytest.mark.asyncio
async def test_add_custom_policy():
    class BooPolicy(AsyncHTTPPolicy):
        async def send(*args):
            raise BaseError("boo")

    class FooPolicy(AsyncHTTPPolicy):
        async def send(*args):
            raise BaseError("boo")

    retry_policy = AsyncRetryPolicy()
    boo_policy = BooPolicy()
    foo_policy = FooPolicy()
    client = AsyncPipelineClient(endpoint="test", policies=[retry_policy], per_call_policies=boo_policy)
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry

    client = AsyncPipelineClient(endpoint="test", policies=[retry_policy], per_call_policies=[boo_policy])
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry

    client = AsyncPipelineClient(endpoint="test", policies=[retry_policy], per_retry_policies=boo_policy)
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo > pos_retry

    client = AsyncPipelineClient(endpoint="test", policies=[retry_policy], per_retry_policies=[boo_policy])
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo > pos_retry

    client = AsyncPipelineClient(
        endpoint="test", policies=[retry_policy], per_call_policies=boo_policy, per_retry_policies=foo_policy
    )
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    assert foo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_foo = policies.index(foo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry
    assert pos_foo > pos_retry

    client = AsyncPipelineClient(
        endpoint="test", policies=[retry_policy], per_call_policies=[boo_policy], per_retry_policies=[foo_policy]
    )
    policies = client.pipeline._impl_policies
    assert boo_policy in policies
    assert foo_policy in policies
    pos_boo = policies.index(boo_policy)
    pos_foo = policies.index(foo_policy)
    pos_retry = policies.index(retry_policy)
    assert pos_boo < pos_retry
    assert pos_foo > pos_retry

    policies = [UserAgentPolicy(), AsyncRetryPolicy()]
    client = AsyncPipelineClient(endpoint="test", policies=policies, per_call_policies=boo_policy)
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    client = AsyncPipelineClient(endpoint="test", policies=policies, per_call_policies=[boo_policy])
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]

    client = AsyncPipelineClient(endpoint="test", policies=policies, per_retry_policies=foo_policy)
    actual_policies = client.pipeline._impl_policies
    assert foo_policy == actual_policies[2]
    client = AsyncPipelineClient(endpoint="test", policies=policies, per_retry_policies=[foo_policy])
    actual_policies = client.pipeline._impl_policies
    assert foo_policy == actual_policies[2]

    client = AsyncPipelineClient(
        endpoint="test", policies=policies, per_call_policies=boo_policy, per_retry_policies=[foo_policy]
    )
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    assert foo_policy == actual_policies[3]
    client = AsyncPipelineClient(
        endpoint="test", policies=policies, per_call_policies=[boo_policy], per_retry_policies=[foo_policy]
    )
    actual_policies = client.pipeline._impl_policies
    assert boo_policy == actual_policies[0]
    assert foo_policy == actual_policies[3]

    policies = [UserAgentPolicy()]
    with pytest.raises(ValueError):
        client = AsyncPipelineClient(endpoint="test", policies=policies, per_retry_policies=foo_policy)
    with pytest.raises(ValueError):
        client = AsyncPipelineClient(endpoint="test", policies=policies, per_retry_policies=[foo_policy])


@pytest.mark.asyncio
async def test_basic_httpx(port):

    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant"), AsyncRetryPolicy()]
    transport = AsyncHttpXTransport()
    async with AsyncPipeline(AsyncHttpXTransport(), policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert cast(AsyncHttpXTransport, pipeline._transport).client is None
    # all we need to check is if we are able to make the call
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.asyncio
async def test_basic_httpx_separate_session(port):

    client = httpx.AsyncClient()
    request = HttpRequest("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant"), AsyncRetryPolicy()]
    transport = AsyncHttpXTransport(client=client, client_owner=False)
    async with AsyncPipeline(transport, policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert transport.client
    assert isinstance(response.http_response.status_code, int)
    await transport.close()
    assert transport.client
    await transport.client.aclose()


@pytest.mark.asyncio
async def test_aiohttp_default_ssl_context():
    class MockAiohttpSession:
        async def __aenter__(self):
            pass

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def close(self):
            pass

        async def open(self):
            pass

        async def request(self, method: str, url: str, **kwargs):
            assert "ssl" not in kwargs
            mock_response = AsyncMock(spec=aiohttp.ClientResponse)
            type(mock_response).status = PropertyMock(return_value=200)
            return mock_response

    transport = AioHttpTransport(session=MockAiohttpSession(), session_owner=False)
    pipeline = AsyncPipeline(transport=transport)

    req = HttpRequest("GET", "https://bing.com")
    await pipeline.run(req)
