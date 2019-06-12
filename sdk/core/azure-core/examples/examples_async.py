# --------------------------------------------------------------------------
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
# --------------------------------------------------------------------------

import pytest
from azure.core.configuration import Configuration
from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline_client_async import AsyncPipelineClient
from azure.core.pipeline.policies import SansIOHTTPPolicy, UserAgentPolicy, AsyncRedirectPolicy, AsyncRetryPolicy
from azure.core.pipeline.transport import (
    AsyncHttpTransport,
    HttpRequest,
    AsyncioRequestsTransport
)


@pytest.mark.asyncio
async def test_example_async_pipeline_client():

    conf = Configuration()
    request = HttpRequest("GET", "https://bing.com")
    conf.user_agent_policy = UserAgentPolicy("myusergant")
    conf.redirect_policy = AsyncRedirectPolicy()

    # [START build_async_pipeline_client]
    async with AsyncPipelineClient(base_url="https://bing.com", config=conf) as client:
        response = await client._pipeline.run(request)
    # [END build_async_pipeline_client]

    assert client._pipeline._transport.session is None
    assert response.http_response.status_code == 200


@pytest.mark.asyncio
async def test_example_async_redirect_policy():
    url = "https://bing.com"
    request = HttpRequest("GET", "https://bing.com")

    # [START async_redirect_policy]
    config = Configuration()
    config.redirect_policy = AsyncRedirectPolicy()

    # Client allows redirects. Defaults to True.
    config.redirect_policy.allow = True

    # The maximum allowed redirects. The default value is 30
    config.redirect_policy.max_redirects = 10

    # Alternatively you can disable redirects entirely
    config.redirect_policy = AsyncRedirectPolicy.no_redirects()

    # It can also be overridden per operation.
    async with AsyncPipelineClient(base_url=url, config=config) as client:
        response = await client._pipeline.run(request, permit_redirects=True, redirect_max=5)

    # [END async_redirect_policy]

    assert client._pipeline._transport.session is None
    assert response.http_response.status_code == 200

@pytest.mark.asyncio
async def test_example_async_retry_policy():
    url = "https://bing.com"
    request = HttpRequest("GET", "https://bing.com")
    config = Configuration()
    config.user_agent_policy = UserAgentPolicy("myusergant")
    config.redirect_policy = AsyncRedirectPolicy()

    # [START async_retry_policy]
    config.retry_policy = AsyncRetryPolicy()

    # Total number of retries to allow. Takes precedence over other counts.
    # Default value is 10.
    config.retry_policy.total_retries = 5

    # How many connection-related errors to retry on.
    # These are errors raised before the request is sent to the remote server,
    # which we assume has not triggered the server to process the request. Default value is 3
    config.retry_policy.connect_retries = 2

    # How many times to retry on read errors.
    # These errors are raised after the request was sent to the server, so the
    # request may have side-effects. Default value is 3.
    config.retry_policy.read_retries = 4

    # How many times to retry on bad status codes. Default value is 3.
    config.retry_policy.status_retries = 3

    # A backoff factor to apply between attempts after the second try
    # (most errors are resolved immediately by a second try without a delay).
    # Retry policy will sleep for:
    #    {backoff factor} * (2 ** ({number of total retries} - 1))
    # seconds. If the backoff_factor is 0.1, then the retry will sleep
    # for [0.0s, 0.2s, 0.4s, ...] between retries.
    # The default value is 0.8.
    config.retry_policy.backoff_factor = 0.5

    # The maximum back off time. Default value is 120 seconds (2 minutes).
    config.retry_policy.backoff_max = 120

    # Alternatively you can disable redirects entirely
    config.retry_policy = AsyncRetryPolicy.no_retries()

    # All of these settings can also be configured per operation.
    async with AsyncPipelineClient(base_url=url, config=config) as client:
        response = await client._pipeline.run(
            request,
            retry_total=10,
            retry_connect=1,
            retry_read=1,
            retry_status=5,
            retry_backoff_factor=0.5,
            retry_backoff_max=60,
            retry_on_methods=['GET']
        )
    # [END async_retry_policy]

    assert client._pipeline._transport.session is None
    assert response.http_response.status_code == 200
