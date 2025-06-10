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

from tracing_common import FakeSpan
from utils import HTTP_REQUESTS


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


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_span_retry_attributes_plugin_tracing(tracing_implementation, http_request):
    """Test that the retry count is added to the span attributes with plugin tracing."""

    http_request = http_request("GET", "http://localhost/")
    retry_policy = AsyncRetryPolicy(retry_total=2)
    distributed_tracing_policy = DistributedTracingPolicy()
    transport = MockTransport()

    with FakeSpan(name="parent") as root_span:
        pipeline = AsyncPipeline(transport, [retry_policy, distributed_tracing_policy])
        await pipeline.run(http_request)

    assert transport._count == 3
    assert len(root_span.children) == 3
    assert root_span.children[0].attributes.get("http.request.resend_count") is None
    assert root_span.children[1].attributes.get("http.request.resend_count") == 1
    assert root_span.children[2].attributes.get("http.request.resend_count") == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("http_request", HTTP_REQUESTS)
async def test_span_retry_attributes_native_tracing(tracing_helper, http_request):
    """Test that the retry count is added to the span attributes with native tracing."""
    http_request = http_request("GET", "http://localhost/")
    retry_policy = AsyncRetryPolicy(retry_total=2)
    distributed_tracing_policy = DistributedTracingPolicy()
    transport = MockTransport()

    with tracing_helper.tracer.start_as_current_span("Root") as root_span:
        policies = [retry_policy, distributed_tracing_policy]
        pipeline = AsyncPipeline(transport, policies=policies)
        await pipeline.run(http_request)

    assert transport._count == 3

    finished_spans = tracing_helper.exporter.get_finished_spans()
    parent_context = root_span.get_span_context()
    assert len(finished_spans) == 4
    assert finished_spans[0].parent == parent_context
    assert finished_spans[0].attributes.get(distributed_tracing_policy._HTTP_RESEND_COUNT) is None
    assert finished_spans[0].attributes.get(distributed_tracing_policy._URL_FULL) == "http://localhost/"

    assert finished_spans[1].parent == parent_context
    assert finished_spans[1].attributes.get(distributed_tracing_policy._HTTP_RESEND_COUNT) == 1
    assert finished_spans[1].attributes.get(distributed_tracing_policy._URL_FULL) == "http://localhost/"

    assert finished_spans[2].parent == parent_context
    assert finished_spans[2].attributes.get(distributed_tracing_policy._HTTP_RESEND_COUNT) == 2
    assert finished_spans[2].attributes.get(distributed_tracing_policy._URL_FULL) == "http://localhost/"
