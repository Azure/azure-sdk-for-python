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
from opentelemetry.trace import SpanKind as OTelSpanKind
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from azure.core.settings import settings
from azure.servicebus._transport._pyamqp_transport import PyamqpTransport
from azure.servicebus.aio._transport._pyamqp_transport_async import PyamqpTransportAsync

try:
    from azure.servicebus._transport._uamqp_transport import UamqpTransport
    from azure.servicebus.aio._transport._uamqp_transport_async import UamqpTransportAsync

    uamqp_installed = True
except ImportError:
    UamqpTransport = None
    UamqpTransportAsync = None
    uamqp_installed = False

sync_transports = [PyamqpTransport]
async_transports = [PyamqpTransportAsync]
if uamqp_installed:
    sync_transports.append(UamqpTransport)
    async_transports.append(UamqpTransportAsync)


@pytest.fixture(scope="module", autouse=True)
def span_exporter():
    # A recording provider is required; suppression is skipped for NonRecordingSpans.
    # An in-memory exporter lets the tests assert the receive span is still emitted.
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)
    exporter = InMemorySpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    return exporter


@pytest.fixture
def enable_otel_tracing(span_exporter):
    settings.tracing_implementation = "opentelemetry"
    assert settings.tracing_implementation() is not None
    span_exporter.clear()
    yield span_exporter
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


@pytest.mark.parametrize("transport", sync_transports)
def test_receive_iter_no_http_suppression(enable_otel_tracing, transport):
    """Messages are yielded outside the receive span, so HTTP instrumentation is not suppressed in user code."""
    span_exporter = enable_otel_tracing
    receiver = MockReceiver(message_count=2)

    yielded = 0
    for _ in transport.iter_contextual_wrapper(receiver):
        yielded += 1
        # User code scope: suppression must not be active.
        assert get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY) is not True

    assert yielded == 2

    # The receive span should still be emitted (same name and kind) even though it no
    # longer encloses the user's message processing.
    receive_spans = [s for s in span_exporter.get_finished_spans() if s.name == "ServiceBus.receive"]
    assert len(receive_spans) == 2
    assert all(s.kind == OTelSpanKind.CLIENT for s in receive_spans)


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", async_transports)
async def test_receive_iter_no_http_suppression_async(enable_otel_tracing, transport):
    """Async counterpart of the sync suppression-scope test."""
    span_exporter = enable_otel_tracing
    receiver = MockReceiver(message_count=2)

    yielded = 0
    async for _ in transport.iter_contextual_wrapper_async(receiver):
        yielded += 1
        assert get_value(_SUPPRESS_HTTP_INSTRUMENTATION_KEY) is not True

    assert yielded == 2

    receive_spans = [s for s in span_exporter.get_finished_spans() if s.name == "ServiceBus.receive"]
    assert len(receive_spans) == 2
    assert all(s.kind == OTelSpanKind.CLIENT for s in receive_spans)
