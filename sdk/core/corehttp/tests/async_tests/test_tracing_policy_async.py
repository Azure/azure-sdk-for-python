# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Tests for the distributed tracing policy."""
import pytest

from corehttp.rest import HttpRequest
from corehttp.runtime.policies import (
    DistributedHttpTracingPolicy,
    AsyncRetryPolicy,
)
from corehttp.runtime.pipeline import AsyncPipeline
from corehttp.transport import AsyncHttpTransport

from utils import HTTP_RESPONSES, create_http_response


@pytest.mark.asyncio
@pytest.mark.parametrize("http_response", HTTP_RESPONSES)
async def test_span_retry_attributes(tracing_helper, http_response):
    """Test that the retry count is added to the span attributes."""

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
            response = create_http_response(http_response, request, None, status_code=429)
            return response

    http_request = HttpRequest("GET", "http://localhost/")
    retry_policy = AsyncRetryPolicy(retry_total=2)
    distributed_tracing_policy = DistributedHttpTracingPolicy()
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
