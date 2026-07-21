# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Unit tests for Service Bus receiver tracing behavior.

Verifies that the receive span's automatic HTTP instrumentation suppression does
not leak into user code while iterating over received messages.
"""

import pytest

from opentelemetry import trace
from opentelemetry.context import get_value, _SUPPRESS_HTTP_INSTRUMENTATION_KEY
from opentelemetry.sdk.trace import TracerProvider

from azure.core.settings import settings
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.aio._transport._pyamqp_transport_async import PyamqpTransportAsync


@pytest.fixture(scope="module", autouse=True)
def tracer_provider():
    # A recording provider is required; suppression is skipped for NonRecordingSpans.
    provider = TracerProvider()
    trace.set_tracer_provider(provider)


@pytest.fixture
def enable_otel_tracing():
    settings.tracing_implementation = "opentelemetry"
    yield
    settings.tracing_implementation = None


class MockReceivedMessage:
    application_properties = None


class MockReceiver:
    # Attributes read by add_span_attributes for a RECEIVE operation.
    _entity_name = "test-entity"
    fully_qualified_namespace = "test-namespace.servicebus.windows.net"

    def __init__(self, message_count):
        self._remaining = message_count

    def _inner_next(self, wait_time=None):
        if self._remaining <= 0:
            raise StopIteration
        self._remaining -= 1
        return MockReceivedMessage()

    async def _inner_anext(self, wait_time=None):
        if self._remaining <= 0:
            raise StopAsyncIteration
        self._remaining -= 1
        return MockReceivedMessage()


def test_receive_iter_no_http_suppression(enable_otel_tracing):
    """Messages are yielded outside the receive span, so HTTP instrumentation is not suppressed in user code."""
    receiver = MockReceiver(message_count=2)

    yielded = 0
    for _ in PyamqpTransport.iter_contextual_wrapper(receiver):
        yielded += 1
        # User code scope: suppression must not be active.
        assert get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY) is not True

    assert yielded == 2


@pytest.mark.asyncio
async def test_receive_iter_no_http_suppression_async(enable_otel_tracing):
    """Async counterpart of the sync suppression-scope test."""
    receiver = MockReceiver(message_count=2)

    yielded = 0
    async for _ in PyamqpTransportAsync.iter_contextual_wrapper_async(receiver):
        yielded += 1
        assert get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY) is not True

    assert yielded == 2
