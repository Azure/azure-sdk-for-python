
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import sys
import pytest
from copy import deepcopy
from azure.core.pipeline import policies
from azure.core.pipeline.transport import RequestsTransport
from azure.core.rest import AsyncHttpResponse, _AsyncStreamContextManager
from azure.core import AsyncPipelineClient
from azure.core.configuration import Configuration
from async_generator import yield_, async_generator



# Ignore async tests for Python < 3.5
collect_ignore_glob = []
if sys.version_info < (3, 5):
    collect_ignore_glob.append("async_tests")

class TestRestClientConfiguration(Configuration):
    def __init__(
        self, **kwargs
    ):
        # type: (...) -> None
        super(TestRestClientConfiguration, self).__init__(**kwargs)

        kwargs.setdefault("sdk_moniker", "autorestswaggerbatfileservice/1.0.0b1")
        self._configure(**kwargs)

    def _configure(self, **kwargs) -> None:
        self.user_agent_policy = kwargs.get("user_agent_policy") or policies.UserAgentPolicy(**kwargs)
        self.headers_policy = kwargs.get("headers_policy") or policies.HeadersPolicy(**kwargs)
        self.proxy_policy = kwargs.get("proxy_policy") or policies.ProxyPolicy(**kwargs)
        self.logging_policy = kwargs.get("logging_policy") or policies.NetworkTraceLoggingPolicy(**kwargs)
        self.http_logging_policy = kwargs.get("http_logging_policy") or policies.HttpLoggingPolicy(**kwargs)
        self.retry_policy = kwargs.get("retry_policy") or policies.AsyncRetryPolicy(**kwargs)
        self.custom_hook_policy = kwargs.get("custom_hook_policy") or policies.CustomHookPolicy(**kwargs)
        self.redirect_policy = kwargs.get("redirect_policy") or policies.AsyncRedirectPolicy(**kwargs)
        self.authentication_policy = kwargs.get("authentication_policy")


class AsyncTestRestClient(object):

    def __init__(self, **kwargs):
        self._config = TestRestClientConfiguration(**kwargs)
        self._client = AsyncPipelineClient(
            base_url="http://localhost:3000",
            config=self._config,
            **kwargs
        )

    async def send_request(self, http_request, **kwargs):
        request_copy = deepcopy(http_request)
        http_request.url = self._client.format_url(http_request.url)
        if kwargs.pop("stream_response", False):
            return _AsyncStreamContextManager(
                client=self._client,
                request=request_copy,
            )
        pipeline_response = await self._client._pipeline.run(request_copy._internal_request, **kwargs)
        return AsyncHttpResponse(
            status_code=pipeline_response.http_response.status_code,
            request=request_copy,
            _internal_response=pipeline_response.http_response,
        )

    async def close(self) -> None:
        await self._client.close()

    async def __aenter__(self):
        await self._client.__aenter__()
        return self

    async def __aexit__(self, *exc_details) -> None:
        await self._client.__aexit__(*exc_details)

@pytest.fixture
@async_generator
async def client():
    async with AsyncTestRestClient() as client:
        await yield_(client)
