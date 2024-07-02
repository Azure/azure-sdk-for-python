# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for the distributed tracing policy in an async pipeline."""

import pytest


from azure.core.pipeline import AsyncPipeline
from azure.core.pipeline.policies import AsyncRetryPolicy, DistributedTracingPolicy
from azure.core.pipeline.transport import (
    HttpResponse,
    AsyncHttpTransport,
)
from azure.core.settings import settings

from tracing_common import FakeSpan
from utils import HTTP_REQUESTS


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_span_retry_attributes(http_request):
    class MockTransport(AsyncHttpTransport):
        def __init__(self):
            self._count = 0

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

        async def close(self):
            pass

        async def open(self):
            pass

        async def send(self, request, **kwargs):
            self._count += 1
            response = HttpResponse(request, None)
            response.status_code = 429
            return response

    http_request = http_request("GET", "http://localhost/")
    retry_policy = AsyncRetryPolicy(retry_total=2)
    distributed_tracing_policy = DistributedTracingPolicy()
    transport = MockTransport()

    settings.tracing_implementation.set_value(FakeSpan)
    with FakeSpan(name="parent") as root_span:
        pipeline = AsyncPipeline(transport, [retry_policy, distributed_tracing_policy])
        await pipeline.run(http_request)

    assert transport._count == 3
    assert len(root_span.children) == 3
    assert root_span.children[0].attributes.get("http.request.resend_count") is None
    assert root_span.children[1].attributes.get("http.request.resend_count") == 1
    assert root_span.children[2].attributes.get("http.request.resend_count") == 2
