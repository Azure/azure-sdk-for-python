# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import sys

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
from corehttp.exceptions import BaseError
import aiohttp
import pytest

from utils import HTTP_REQUESTS


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_sans_io_exception(http_request):
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

    req = http_request("GET", "/")
    with pytest.raises(ValueError):
        await pipeline.run(req)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_basic_aiohttp(port, http_request):

    request = http_request("GET", "http://localhost:{}/basic/string".format(port))
    policies = [UserAgentPolicy("myusergant"), AsyncRetryPolicy()]
    async with AsyncPipeline(AioHttpTransport(), policies=policies) as pipeline:
        response = await pipeline.run(request)

    assert pipeline._transport.session is None
    # all we need to check is if we are able to make the call
    assert isinstance(response.http_response.status_code, int)


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_basic_aiohttp_separate_session(port, http_request):

    session = aiohttp.ClientSession()
    request = http_request("GET", "http://localhost:{}/basic/string".format(port))
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
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_retry_without_http_response(http_request):
    class NaughtyPolicy(AsyncHTTPPolicy):
        def send(*args):
            raise BaseError("boo")

    policies = [AsyncRetryPolicy(), NaughtyPolicy()]
    pipeline = AsyncPipeline(policies=policies, transport=None)
    with pytest.raises(BaseError):
        await pipeline.run(http_request("GET", url="https://foo.bar"))


@pytest.mark.asyncio
async def test_add_custom_policy():
    class BooPolicy(AsyncHTTPPolicy):
        def send(*args):
            raise BaseError("boo")

    class FooPolicy(AsyncHTTPPolicy):
        def send(*args):
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
