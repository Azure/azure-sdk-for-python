# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for optional OpenTelemetry tracing."""
import asyncio
import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor, SpanExporter, SpanExportResult

from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse

from azure.ai.agentserver import AgentServer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _InMemoryExporter(SpanExporter):
    """Minimal in-memory span exporter for tests."""

    def __init__(self):
        self._spans: list = []

    def export(self, spans):  # type: ignore[override]
        self._spans.extend(spans)
        return SpanExportResult.SUCCESS

    def get_finished_spans(self):
        return list(self._spans)

    def shutdown(self):
        self._spans.clear()


def _make_echo_traced_agent(**kwargs) -> AgentServer:
    """Create a simple agent for tracing tests."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        body = await request.body()
        return Response(content=body, media_type="application/octet-stream")

    return server


def _make_failing_traced_agent(**kwargs) -> AgentServer:
    """Create an agent whose invoke raises — so the span records the error."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        raise RuntimeError("trace-this-error")

    return server


@pytest.fixture()
def span_exporter():
    """Return the module-level exporter with a clean slate for each test."""
    _MODULE_EXPORTER._spans.clear()
    yield _MODULE_EXPORTER


# Module-level OTel setup — set once to avoid
# "Overriding of current TracerProvider is not allowed" warnings.
_MODULE_EXPORTER = _InMemoryExporter()
_MODULE_PROVIDER = TracerProvider()
_MODULE_PROVIDER.add_span_processor(SimpleSpanProcessor(_MODULE_EXPORTER))
trace.set_tracer_provider(_MODULE_PROVIDER)


# ---------------------------------------------------------------------------
# Tests: tracing disabled (default)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tracing_disabled_by_default():
    """Agent created without enable_tracing has tracing off."""
    agent = _make_echo_traced_agent()
    assert agent._tracing is None  # noqa: SLF001


@pytest.mark.asyncio
async def test_tracing_disabled_no_spans(span_exporter):
    """When tracing is disabled, no spans are produced."""
    agent = _make_echo_traced_agent()  # default: tracing off
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{"hi": "there"}')

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


# ---------------------------------------------------------------------------
# Tests: tracing enabled via constructor
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tracing_enabled_creates_invoke_span(span_exporter):
    """POST /invocations with tracing enabled creates a span."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b'{"data": 1}')
    assert resp.status_code == 200

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "AgentServer.invoke"]
    assert len(invoke_spans) == 1

    span = invoke_spans[0]
    assert "invocation.id" in dict(span.attributes)
    assert span.status.status_code == trace.StatusCode.UNSET  # success


@pytest.mark.asyncio
async def test_tracing_invoke_error_records_exception(span_exporter):
    """When invoke() raises, the span records the error status and exception."""
    agent = _make_failing_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b'{}')
    assert resp.status_code == 500

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "AgentServer.invoke"]
    assert len(invoke_spans) == 1

    span = invoke_spans[0]
    assert span.status.status_code == trace.StatusCode.ERROR
    # Exception should be recorded in events
    events = span.events
    assert any("trace-this-error" in str(e.attributes) for e in events)


@pytest.mark.asyncio
async def test_tracing_get_invocation_creates_span(span_exporter):
    """GET /invocations/{id} with tracing creates a span."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.get("/invocations/test-id-123")
    # Default returns 404 — but span should still exist
    assert resp.status_code == 404

    spans = span_exporter.get_finished_spans()
    get_spans = [s for s in spans if s.name == "AgentServer.get_invocation"]
    assert len(get_spans) == 1
    assert dict(get_spans[0].attributes)["invocation.id"] == "test-id-123"


@pytest.mark.asyncio
async def test_tracing_cancel_invocation_creates_span(span_exporter):
    """POST /invocations/{id}/cancel with tracing creates a span."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/test-cancel-456/cancel")
    assert resp.status_code == 404

    spans = span_exporter.get_finished_spans()
    cancel_spans = [s for s in spans if s.name == "AgentServer.cancel_invocation"]
    assert len(cancel_spans) == 1
    assert dict(cancel_spans[0].attributes)["invocation.id"] == "test-cancel-456"


# ---------------------------------------------------------------------------
# Tests: tracing enabled via env var
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_tracing_enabled_via_env_var(monkeypatch, span_exporter):
    """AGENT_ENABLE_TRACING=true activates tracing."""
    monkeypatch.setenv("AGENT_ENABLE_TRACING", "true")
    agent = _make_echo_traced_agent()
    assert agent._tracing is not None  # noqa: SLF001

    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{}')

    spans = span_exporter.get_finished_spans()
    assert any(s.name == "AgentServer.invoke" for s in spans)


@pytest.mark.asyncio
async def test_tracing_constructor_overrides_env_var(monkeypatch, span_exporter):
    """Constructor enable_tracing=False overrides AGENT_ENABLE_TRACING=true."""
    monkeypatch.setenv("AGENT_ENABLE_TRACING", "true")
    agent = _make_echo_traced_agent(enable_tracing=False)
    assert agent._tracing is None  # noqa: SLF001


@pytest.mark.asyncio
async def test_tracing_propagates_traceparent(span_exporter):
    """Incoming traceparent header is extracted as parent context."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    # Valid W3C traceparent — version-trace-id-parent-id-flags
    traceparent = "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b'{"hello": "world"}',
            headers={"traceparent": traceparent},
        )
    assert resp.status_code == 200

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "AgentServer.invoke"]
    assert len(invoke_spans) == 1
    span = invoke_spans[0]
    # The span's trace ID should match the traceparent's trace ID
    expected_trace_id = int("0af7651916cd43dd8448eb211c80319c", 16)
    assert span.context.trace_id == expected_trace_id


# ---------------------------------------------------------------------------
# Tests: streaming response tracing
# ---------------------------------------------------------------------------


def _make_streaming_traced_agent(**kwargs) -> AgentServer:
    """Create an agent that returns a StreamingResponse."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        async def _generate():
            for i in range(5):
                yield f"chunk-{i}\n".encode()

        return StreamingResponse(_generate(), media_type="application/octet-stream")

    return server


def _make_slow_streaming_agent(**kwargs) -> AgentServer:
    """Create an agent that streams with deliberate delays per chunk."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        async def _generate():
            for i in range(3):
                await asyncio.sleep(0.05)
                yield f"slow-{i}\n".encode()

        return StreamingResponse(_generate(), media_type="text/plain")

    return server


def _make_failing_stream_agent(**kwargs) -> AgentServer:
    """Create an agent whose streaming body raises mid-stream."""
    server = AgentServer(**kwargs)

    @server.invoke_handler
    async def handle(request: Request) -> Response:
        async def _generate():
            yield b"ok-chunk\n"
            raise RuntimeError("stream-exploded")

        return StreamingResponse(_generate(), media_type="text/plain")

    return server


@pytest.mark.asyncio
async def test_streaming_response_creates_span(span_exporter):
    """Streaming response still produces a span."""
    agent = _make_streaming_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b'{}')
    assert resp.status_code == 200

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "AgentServer.invoke"]
    assert len(invoke_spans) == 1
    assert invoke_spans[0].status.status_code == trace.StatusCode.UNSET


@pytest.mark.asyncio
async def test_streaming_span_covers_full_body(span_exporter):
    """Span for streaming response covers the full streaming duration,
    not just the invoke() call that creates the StreamingResponse."""
    agent = _make_slow_streaming_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b'{}')
    assert resp.status_code == 200
    # All chunks received
    assert b"slow-0" in resp.content
    assert b"slow-2" in resp.content

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "AgentServer.invoke"]
    assert len(invoke_spans) == 1
    span = invoke_spans[0]

    # Span duration should cover the streaming time (~150ms for 3×50ms),
    # not just the instant invoke() returns the StreamingResponse object.
    duration_ns = span.end_time - span.start_time
    # At minimum 100ms (conservative) — would be <1ms without the fix.
    assert duration_ns > 50_000_000, f"Span duration {duration_ns}ns is too short for streaming"


@pytest.mark.asyncio
async def test_streaming_body_fully_received(span_exporter):
    """All chunks from a streaming response are delivered to the client."""
    agent = _make_streaming_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b'{}')
    assert resp.status_code == 200
    body = resp.content.decode()
    for i in range(5):
        assert f"chunk-{i}" in body


@pytest.mark.asyncio
async def test_streaming_error_recorded_in_span(span_exporter):
    """Errors during streaming are recorded on the span."""
    agent = _make_failing_stream_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        # The server will encounter a mid-stream error; httpx may raise or
        # return a partial response depending on ASGI transport behaviour.
        try:
            await client.post("/invocations", content=b'{}')
        except Exception:
            pass  # connection reset / partial read is acceptable

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "AgentServer.invoke"]
    assert len(invoke_spans) == 1

    span = invoke_spans[0]
    assert span.status.status_code == trace.StatusCode.ERROR
    events = span.events
    assert any("stream-exploded" in str(e.attributes) for e in events)


@pytest.mark.asyncio
async def test_streaming_tracing_disabled_no_span(span_exporter):
    """When tracing is disabled, streaming responses produce no spans."""
    agent = _make_streaming_traced_agent()  # tracing off (default)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations", content=b'{}')
    assert resp.status_code == 200
    body = resp.content.decode()
    assert "chunk-0" in body  # body still delivered

    spans = span_exporter.get_finished_spans()
    assert len(spans) == 0


@pytest.mark.asyncio
async def test_streaming_propagates_traceparent(span_exporter):
    """Incoming traceparent header is propagated for streaming responses."""
    agent = _make_streaming_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    traceparent = "00-0af7651916cd43dd8448eb211c80319c-b7ad6b7169203331-01"
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b'{}',
            headers={"traceparent": traceparent},
        )
    assert resp.status_code == 200

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "AgentServer.invoke"]
    assert len(invoke_spans) == 1
    expected_trace_id = int("0af7651916cd43dd8448eb211c80319c", 16)
    assert invoke_spans[0].context.trace_id == expected_trace_id


# ---------------------------------------------------------------------------
# Tests: Application Insights connection string resolution
# ---------------------------------------------------------------------------


class TestAppInsightsConnectionStringResolution:
    """Tests for resolve_appinsights_connection_string and constructor wiring."""

    def test_explicit_param_takes_priority(self, monkeypatch):
        """Constructor param beats env var."""
        from azure.ai.agentserver.server._config import resolve_appinsights_connection_string

        monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "env-standard")
        result = resolve_appinsights_connection_string("explicit-value")
        assert result == "explicit-value"

    def test_standard_env_var_fallback(self, monkeypatch):
        """Falls back to APPLICATIONINSIGHTS_CONNECTION_STRING."""
        from azure.ai.agentserver.server._config import resolve_appinsights_connection_string

        monkeypatch.setenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "env-standard")
        result = resolve_appinsights_connection_string(None)
        assert result == "env-standard"

    def test_no_connection_string_returns_none(self, monkeypatch):
        """Returns None when no source provides a connection string."""
        from azure.ai.agentserver.server._config import resolve_appinsights_connection_string

        monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)
        result = resolve_appinsights_connection_string(None)
        assert result is None


# ---------------------------------------------------------------------------
# Tests: _setup_azure_monitor
# ---------------------------------------------------------------------------


class TestSetupAzureMonitor:
    """Tests for TracingHelper._setup_azure_monitor (mocked exporter imports)."""

    def test_setup_configures_tracer_provider(self):
        """_setup_azure_monitor sets a global TracerProvider with exporter."""
        from azure.ai.agentserver._tracing import TracingHelper

        mock_exporter = MagicMock()
        mock_exporter_cls = MagicMock(return_value=mock_exporter)

        with patch.dict(
            "sys.modules",
            {
                "azure.monitor.opentelemetry.exporter": MagicMock(
                    AzureMonitorTraceExporter=mock_exporter_cls,
                    AzureMonitorLogExporter=MagicMock(return_value=MagicMock()),
                ),
            },
        ), patch("opentelemetry.trace.set_tracer_provider") as mock_set_provider:
            TracingHelper._setup_azure_monitor("InstrumentationKey=test")

            mock_exporter_cls.assert_called_once_with(
                connection_string="InstrumentationKey=test"
            )
            mock_set_provider.assert_called_once()

    def test_setup_logs_warning_when_packages_missing(self, caplog):
        """Warns gracefully when azure-monitor exporter is not installed."""
        import builtins
        from azure.ai.agentserver._tracing import TracingHelper

        real_import = builtins.__import__

        def _block_monitor(name, *args, **kwargs):
            if "azure.monitor" in name:
                raise ImportError("no monitor")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_block_monitor):
            import logging

            with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
                TracingHelper._setup_azure_monitor("InstrumentationKey=test")

        assert "required packages are not installed" in caplog.text

    def test_constructor_passes_connection_string(self, monkeypatch):
        """AgentServer passes resolved connection string to TracingHelper."""
        monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)

        with patch(
            "azure.ai.agentserver._tracing.TracingHelper._setup_azure_monitor"
        ) as mock_setup:
            _make_echo_traced_agent(
                enable_tracing=True,
                application_insights_connection_string="InstrumentationKey=from-param",
            )
            mock_setup.assert_called_once_with("InstrumentationKey=from-param")

    def test_constructor_no_connection_string_skips_setup(self, monkeypatch):
        """When no connection string is available, _setup_azure_monitor is not called."""
        monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)

        with patch(
            "azure.ai.agentserver._tracing.TracingHelper._setup_azure_monitor"
        ) as mock_setup:
            _make_echo_traced_agent(enable_tracing=True)
            mock_setup.assert_not_called()

    def test_constructor_env_var_connection_string(self, monkeypatch):
        """Connection string from env var is passed to _setup_azure_monitor."""
        monkeypatch.setenv(
            "APPLICATIONINSIGHTS_CONNECTION_STRING",
            "InstrumentationKey=from-env",
        )

        with patch(
            "azure.ai.agentserver._tracing.TracingHelper._setup_azure_monitor"
        ) as mock_setup:
            _make_echo_traced_agent(enable_tracing=True)
            mock_setup.assert_called_once_with("InstrumentationKey=from-env")

    def test_tracing_disabled_skips_connection_string_resolution(self, monkeypatch):
        """When tracing is disabled, connection string is not resolved."""
        monkeypatch.setenv(
            "APPLICATIONINSIGHTS_CONNECTION_STRING",
            "InstrumentationKey=should-not-use",
        )

        agent = _make_echo_traced_agent(enable_tracing=False)
        assert agent._tracing is None  # noqa: SLF001
