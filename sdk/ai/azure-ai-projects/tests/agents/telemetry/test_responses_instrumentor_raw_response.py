# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Tests for with_raw_response + stream=True when ResponsesInstrumentor is active.

Verifies that:
1. The raw response interface (.parse(), .headers) is preserved
2. The parsed stream is iterable and yields events
3. Telemetry spans are produced with correct attributes
"""

import asyncio
import os
from typing import Any

import pytest
import httpx2
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.trace import StatusCode
from memory_trace_exporter import MemoryTraceExporter  # pylint: disable=import-error
from azure.core.settings import settings
from azure.core.tracing.ext.opentelemetry_span import OpenTelemetrySpan
from azure.ai.projects.telemetry import AIProjectInstrumentor
from openai import AsyncOpenAI, AsyncStream, OpenAI, Stream

CONTENT_TRACING_ENV_VARIABLE = "OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"
EXPERIMENTAL_ENABLE_GENAI_TRACING_ENV_VARIABLE = "AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING"

# Fake SSE payload with a text delta and DONE marker
SSE_PAYLOAD = (
    'data: {"type":"response.output_text.delta","delta":"Hello","item_id":"m1",'
    '"output_index":0,"content_index":0,"sequence_number":1,"logprobs":[]}\n\n'
    "data: [DONE]\n\n"
)


class CustomAsyncStream(AsyncStream[Any]):
    def custom_method(self):
        return "custom async stream"


class CustomStream(Stream[Any]):
    def custom_method(self):
        return "custom stream"


def _make_mock_transport():
    """Create an httpx2 MockTransport that returns a fake SSE streaming response."""
    return httpx2.MockTransport(
        lambda r: httpx2.Response(
            200,
            headers={"content-type": "text/event-stream"},
            content=SSE_PAYLOAD.encode(),
        )
    )


class TestRawResponseStreaming:
    """Tests for with_raw_response streaming with instrumentor active."""

    def setup_method(self):
        os.environ[EXPERIMENTAL_ENABLE_GENAI_TRACING_ENV_VARIABLE] = "true"
        os.environ[CONTENT_TRACING_ENV_VARIABLE] = "True"
        settings.tracing_implementation = OpenTelemetrySpan
        self.tracer_provider = TracerProvider()
        trace._TRACER_PROVIDER = self.tracer_provider
        self.exporter = MemoryTraceExporter()
        span_processor = SimpleSpanProcessor(self.exporter)
        self.tracer_provider.add_span_processor(span_processor)
        AIProjectInstrumentor().instrument()

    def teardown_method(self):
        self.exporter.shutdown()
        AIProjectInstrumentor().uninstrument()
        trace._TRACER_PROVIDER = None
        os.environ.pop(CONTENT_TRACING_ENV_VARIABLE, None)
        os.environ.pop(EXPERIMENTAL_ENABLE_GENAI_TRACING_ENV_VARIABLE, None)

    # ─── Async tests ───────────────────────────────────────────────

    def test_async_raw_response_parse_preserves_custom_stream_type(self):
        """Async raw response parsing should preserve custom stream methods via delegation."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

            stream = raw.parse(to=CustomAsyncStream)

            # Custom methods remain accessible through the telemetry wrapper
            assert stream.custom_method() == "custom async stream"
            await stream.close()
            assert stream.response.is_closed

        asyncio.run(_run())

    def test_async_parse_cache_returns_default_after_custom(self):
        """parse() should always return the default stream even after parse(to=X)."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

            default = raw.parse()
            custom = raw.parse(to=CustomAsyncStream)
            assert raw.parse() is default, "parse() must return default stream after custom parse"
            assert raw.parse(to=CustomAsyncStream) is custom, "repeated parse(to=X) must return cached wrapper"
            await default.close()

        asyncio.run(_run())

    def test_async_with_raw_response_streaming_preserves_interface(self):
        """with_raw_response.create(stream=True) should preserve .parse() and .headers."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

            # Raw response interface must be preserved
            assert hasattr(raw, "parse"), "Result should have .parse() method"
            assert hasattr(raw, "headers"), "Result should have .headers attribute"

            # parse() is sync (matches OpenAI's LegacyAPIResponse contract)
            stream = raw.parse()

            assert hasattr(stream, "__aiter__"), "Parsed stream should be async iterable"

            # Consuming the stream should yield at least one event
            events = []
            async for event in stream:
                events.append(event)
            assert len(events) >= 1, "Stream should yield at least one event"

        asyncio.run(_run())

    def test_async_with_raw_response_streaming_produces_telemetry(self):
        """with_raw_response streaming should produce telemetry spans."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

            stream = raw.parse()

            async for _ in stream:
                pass

        asyncio.run(_run())

        # Verify spans were captured
        spans = self.exporter.get_spans()
        assert len(spans) >= 1, f"Expected at least 1 span, got {len(spans)}"

        # The instrumentor names spans like 'chat <model>'
        span = spans[0]
        assert span.status.status_code == StatusCode.OK, f"Span status should be OK, got {span.status.status_code}"
        assert span.attributes.get("gen_ai.request.model") == "gpt-4o"

    def test_async_with_raw_response_repeated_parse_is_exhausted(self):
        """Parsing an async raw stream twice should not replay events or create another span."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

            first_stream = raw.parse()
            first_events = [event async for event in first_stream]

            second_stream = raw.parse()
            second_events = [event async for event in second_stream]

            assert first_events
            assert second_events == []

        asyncio.run(_run())

        assert len(self.exporter.get_spans()) == 1

    def test_async_with_raw_response_close_finalizes_unconsumed_stream(self):
        """Closing an unconsumed async raw response should finalize its telemetry span."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

            await raw.close()  # pyright: ignore[reportAttributeAccessIssue]

        asyncio.run(_run())

        assert len(self.exporter.get_spans()) == 1

    def test_async_with_raw_response_close_finalizes_partially_consumed_stream(self):
        """Closing a partially consumed async raw response should finalize its telemetry span."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)
            stream = raw.parse()

            await stream.__anext__()
            await raw.close()  # pyright: ignore[reportAttributeAccessIssue]

        asyncio.run(_run())

        assert len(self.exporter.get_spans()) == 1

    def test_async_parsed_stream_context_closes_partially_consumed_stream(self):
        """Exiting a parsed async stream should close its HTTP response and finalize telemetry."""

        async def _run():
            client = AsyncOpenAI(
                api_key="fake-key",
                http_client=httpx2.AsyncClient(transport=_make_mock_transport()),
            )
            raw = await client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)
            stream = raw.parse()

            async with stream:
                await stream.__anext__()

            assert stream.response.is_closed

        asyncio.run(_run())

        assert len(self.exporter.get_spans()) == 1

    # ─── Sync tests ────────────────────────────────────────────────

    def test_sync_raw_response_parse_preserves_custom_stream_type(self):
        """Sync raw response parsing should preserve custom stream methods via delegation."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

        stream = raw.parse(to=CustomStream)

        # Custom methods remain accessible through the telemetry wrapper
        assert stream.custom_method() == "custom stream"
        stream.close()
        assert stream.response.is_closed

    def test_sync_parse_cache_returns_default_after_custom(self):
        """parse() should always return the default stream even after parse(to=X)."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

        default = raw.parse()
        custom = raw.parse(to=CustomStream)
        assert raw.parse() is default, "parse() must return default stream after custom parse"
        assert raw.parse(to=CustomStream) is custom, "repeated parse(to=X) must return cached wrapper"
        default.close()

    def test_sync_with_raw_response_streaming_preserves_interface(self):
        """Sync with_raw_response.create(stream=True) should preserve .parse() and .headers."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

        # Raw response interface must be preserved
        assert hasattr(raw, "parse"), "Result should have .parse() method"
        assert hasattr(raw, "headers"), "Result should have .headers attribute"

        # Parsing should yield an iterable stream
        stream = raw.parse()
        assert hasattr(stream, "__iter__"), "Parsed stream should be iterable"

        # Consuming the stream should yield at least one event
        events = list(stream)
        assert len(events) >= 1, "Stream should yield at least one event"

    def test_sync_with_raw_response_streaming_produces_telemetry(self):
        """Sync with_raw_response streaming should produce telemetry spans."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

        stream = raw.parse()
        for _ in stream:
            pass

        # Verify spans were captured
        spans = self.exporter.get_spans()
        assert len(spans) >= 1, f"Expected at least 1 span, got {len(spans)}"

        # The instrumentor names spans like 'chat <model>'
        span = spans[0]
        assert span.status.status_code == StatusCode.OK, f"Span status should be OK, got {span.status.status_code}"
        assert span.attributes.get("gen_ai.request.model") == "gpt-4o"

    def test_sync_with_raw_response_repeated_parse_is_exhausted(self):
        """Parsing a sync raw stream twice should not replay events or create another span."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

        first_events = list(raw.parse())
        second_events = list(raw.parse())

        assert first_events
        assert second_events == []
        assert len(self.exporter.get_spans()) == 1

    def test_sync_with_raw_response_close_finalizes_unconsumed_stream(self):
        """Closing an unconsumed sync raw response should finalize its telemetry span."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)

        raw.close()  # pyright: ignore[reportAttributeAccessIssue]

        assert len(self.exporter.get_spans()) == 1

    def test_sync_with_raw_response_close_finalizes_partially_consumed_stream(self):
        """Closing a partially consumed sync raw response should finalize its telemetry span."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)
        stream = raw.parse()

        next(stream)
        raw.close()  # pyright: ignore[reportAttributeAccessIssue]

        assert len(self.exporter.get_spans()) == 1

    def test_sync_parsed_stream_context_closes_partially_consumed_stream(self):
        """Exiting a parsed sync stream should close its HTTP response and finalize telemetry."""
        client = OpenAI(
            api_key="fake-key",
            http_client=httpx2.Client(transport=_make_mock_transport()),
        )
        raw = client.responses.with_raw_response.create(model="gpt-4o", input="hi", stream=True)
        stream = raw.parse()

        with stream:
            next(stream)

        assert stream.response.is_closed
        assert len(self.exporter.get_spans()) == 1
