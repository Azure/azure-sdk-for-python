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

from azure.ai.agentserver.server import AgentServer
from azure.ai.agentserver.server._tracing import _TracingHelper


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
    """Return the module-level exporter with a clean slate for each test.

    Patches ``_setup_azure_monitor`` so that an ``APPLICATIONINSIGHTS_CONNECTION_STRING``
    env var in the CI environment doesn't replace the test TracerProvider.
    """
    _MODULE_EXPORTER._spans.clear()
    # Ensure the module-level provider is active (a prior test may have replaced it).
    trace.set_tracer_provider(_MODULE_PROVIDER)
    with patch.object(_TracingHelper, "_setup_azure_monitor"):
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
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
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
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
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
    # Default returns 501 — but span should still exist
    assert resp.status_code == 501

    spans = span_exporter.get_finished_spans()
    get_spans = [s for s in spans if "get_invocation" in s.name]
    assert len(get_spans) == 1
    assert dict(get_spans[0].attributes)["invocation.id"] == "test-id-123"


@pytest.mark.asyncio
async def test_tracing_cancel_invocation_creates_span(span_exporter):
    """POST /invocations/{id}/cancel with tracing creates a span."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post("/invocations/test-cancel-456/cancel")
    assert resp.status_code == 501

    spans = span_exporter.get_finished_spans()
    cancel_spans = [s for s in spans if "cancel_invocation" in s.name]
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
    assert any("execute_agent" in s.name for s in spans)


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
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
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
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
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
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
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
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
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
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
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
    """Tests for _TracingHelper._setup_azure_monitor (mocked exporter imports)."""

    def test_setup_configures_tracer_provider(self):
        """_setup_azure_monitor sets a global TracerProvider with exporter."""
        from azure.ai.agentserver.server._tracing import _TracingHelper

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
            _TracingHelper._setup_azure_monitor("InstrumentationKey=test")

            mock_exporter_cls.assert_called_once_with(
                connection_string="InstrumentationKey=test"
            )
            mock_set_provider.assert_called_once()

    def test_setup_logs_warning_when_packages_missing(self, caplog):
        """Warns gracefully when azure-monitor exporter is not installed."""
        import builtins
        from azure.ai.agentserver.server._tracing import _TracingHelper

        real_import = builtins.__import__

        def _block_monitor(name, *args, **kwargs):
            if "azure.monitor" in name:
                raise ImportError("no monitor")
            return real_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=_block_monitor):
            import logging

            with caplog.at_level(logging.WARNING, logger="azure.ai.agentserver"):
                _TracingHelper._setup_azure_monitor("InstrumentationKey=test")

        assert "Traces will not be forwarded" in caplog.text

    def test_constructor_passes_connection_string(self, monkeypatch):
        """AgentServer passes resolved connection string to _TracingHelper."""
        monkeypatch.delenv("APPLICATIONINSIGHTS_CONNECTION_STRING", raising=False)

        with patch(
            "azure.ai.agentserver.server._tracing._TracingHelper._setup_azure_monitor"
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
            "azure.ai.agentserver.server._tracing._TracingHelper._setup_azure_monitor"
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
            "azure.ai.agentserver.server._tracing._TracingHelper._setup_azure_monitor"
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


# ---------------------------------------------------------------------------
# Tests: span naming with agent name and version
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_span_name_includes_agent_label(monkeypatch, span_exporter):
    """Span name includes agent_name:agent_version when env vars are set."""
    monkeypatch.setenv("AGENT_NAME", "my-agent")
    monkeypatch.setenv("AGENT_VERSION", "2.1")
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{}')

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "execute_agent my-agent:2.1"]
    assert len(invoke_spans) == 1


@pytest.mark.asyncio
async def test_span_name_without_agent_label(span_exporter, monkeypatch):
    """Span name is just the operation when AGENT_NAME is not set."""
    monkeypatch.delenv("AGENT_NAME", raising=False)
    monkeypatch.delenv("AGENT_VERSION", raising=False)
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{}')

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if s.name == "execute_agent"]
    assert len(invoke_spans) == 1


@pytest.mark.asyncio
async def test_get_invocation_span_name_with_label(monkeypatch, span_exporter):
    """GET /invocations/{id} span includes agent label."""
    monkeypatch.setenv("AGENT_NAME", "agent-x")
    monkeypatch.setenv("AGENT_VERSION", "0.5")
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.get("/invocations/test-id")

    spans = span_exporter.get_finished_spans()
    get_spans = [s for s in spans if s.name == "get_invocation agent-x:0.5"]
    assert len(get_spans) == 1


@pytest.mark.asyncio
async def test_cancel_invocation_span_name_with_label(monkeypatch, span_exporter):
    """POST /invocations/{id}/cancel span includes agent label."""
    monkeypatch.setenv("AGENT_NAME", "agent-x")
    monkeypatch.setenv("AGENT_VERSION", "0.5")
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations/test-id/cancel")

    spans = span_exporter.get_finished_spans()
    cancel_spans = [s for s in spans if s.name == "cancel_invocation agent-x:0.5"]
    assert len(cancel_spans) == 1


# ---------------------------------------------------------------------------
# Tests: GenAI semantic convention attributes
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_genai_attributes_on_invoke_span(span_exporter, monkeypatch):
    """Invoke span has GenAI semantic convention attributes."""
    monkeypatch.setenv("AGENT_NAME", "test-agent")
    monkeypatch.setenv("AGENT_VERSION", "1.0")
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{}')

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    attrs = dict(invoke_spans[0].attributes)
    assert attrs["gen_ai.operation.name"] == "invoke_agent"
    assert attrs["gen_ai.agent.id"] == "test-agent:1.0"
    assert attrs["gen_ai.provider.name"] == "microsoft.foundry"
    assert "gen_ai.response.id" in attrs  # UUID invocation ID


@pytest.mark.asyncio
async def test_genai_conversation_id_from_session_header(span_exporter, monkeypatch):
    """gen_ai.conversation.id is set from agent_session_id query parameter."""
    monkeypatch.delenv("AGENT_NAME", raising=False)
    monkeypatch.delenv("AGENT_VERSION", raising=False)
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post(
            "/invocations",
            content=b'{}',
            params={"agent_session_id": "session-abc-123"},
        )

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    attrs = dict(invoke_spans[0].attributes)
    assert attrs["gen_ai.conversation.id"] == "session-abc-123"


@pytest.mark.asyncio
async def test_genai_conversation_id_absent_when_no_header(span_exporter, monkeypatch):
    """gen_ai.conversation.id is NOT set when agent_session_id query parameter is absent."""
    monkeypatch.delenv("AGENT_NAME", raising=False)
    monkeypatch.delenv("AGENT_VERSION", raising=False)
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{}')

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    attrs = dict(invoke_spans[0].attributes)
    assert "gen_ai.conversation.id" not in attrs


@pytest.mark.asyncio
async def test_genai_attributes_on_get_invocation_span(span_exporter, monkeypatch):
    """GET /invocations/{id} span has GenAI attributes (minus operation.name)."""
    monkeypatch.setenv("AGENT_NAME", "test-agent")
    monkeypatch.setenv("AGENT_VERSION", "1.0")
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.get(
            "/invocations/inv-42",
            params={"agent_session_id": "sess-99"},
        )

    spans = span_exporter.get_finished_spans()
    get_spans = [s for s in spans if "get_invocation" in s.name]
    assert len(get_spans) == 1

    attrs = dict(get_spans[0].attributes)
    assert attrs["gen_ai.agent.id"] == "test-agent:1.0"
    assert attrs["gen_ai.provider.name"] == "microsoft.foundry"
    assert attrs["gen_ai.response.id"] == "inv-42"
    assert attrs["gen_ai.conversation.id"] == "sess-99"
    assert attrs["invocation.id"] == "inv-42"


# ---------------------------------------------------------------------------
# Tests: baggage extraction and leaf_customer_span_id
# ---------------------------------------------------------------------------


class TestBaggageParsing:
    """Unit tests for _parse_baggage_key."""

    def test_single_key(self):
        from azure.ai.agentserver.server._tracing import _parse_baggage_key
        assert _parse_baggage_key("leaf_customer_span_id=abc123", "leaf_customer_span_id") == "abc123"

    def test_multiple_keys(self):
        from azure.ai.agentserver.server._tracing import _parse_baggage_key
        baggage = "foo=bar,leaf_customer_span_id=deadbeef01234567,baz=qux"
        assert _parse_baggage_key(baggage, "leaf_customer_span_id") == "deadbeef01234567"

    def test_key_not_present(self):
        from azure.ai.agentserver.server._tracing import _parse_baggage_key
        assert _parse_baggage_key("foo=bar,baz=qux", "leaf_customer_span_id") is None

    def test_empty_baggage(self):
        from azure.ai.agentserver.server._tracing import _parse_baggage_key
        assert _parse_baggage_key("", "leaf_customer_span_id") is None

    def test_key_with_properties(self):
        from azure.ai.agentserver.server._tracing import _parse_baggage_key
        baggage = "leaf_customer_span_id=abc123;property1=val1,other=2"
        assert _parse_baggage_key(baggage, "leaf_customer_span_id") == "abc123"

    def test_whitespace_handling(self):
        from azure.ai.agentserver.server._tracing import _parse_baggage_key
        baggage = " leaf_customer_span_id = abc123 , other = val "
        assert _parse_baggage_key(baggage, "leaf_customer_span_id") == "abc123"


@pytest.mark.asyncio
async def test_baggage_leaf_customer_span_id_overrides_parent(span_exporter):
    """When baggage contains leaf_customer_span_id, the span's parent span ID
    is overridden to match, while the trace ID stays the same as traceparent."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)

    trace_id_hex = "0af7651916cd43dd8448eb211c80319c"
    original_parent_hex = "b7ad6b7169203331"
    leaf_span_hex = "00f067aa0ba902b7"

    traceparent = f"00-{trace_id_hex}-{original_parent_hex}-01"
    baggage = f"leaf_customer_span_id={leaf_span_hex},other=val"

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b'{"data": 1}',
            headers={"traceparent": traceparent, "baggage": baggage},
        )
    assert resp.status_code == 200

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    span = invoke_spans[0]
    # Trace ID should match traceparent
    expected_trace_id = int(trace_id_hex, 16)
    assert span.context.trace_id == expected_trace_id

    # Parent span ID should be the leaf_customer_span_id, not the original
    expected_parent_span_id = int(leaf_span_hex, 16)
    assert span.parent.span_id == expected_parent_span_id


@pytest.mark.asyncio
async def test_baggage_without_leaf_uses_traceparent_parent(span_exporter):
    """When baggage is present but does NOT contain leaf_customer_span_id,
    the parent span ID comes from traceparent as usual."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)

    trace_id_hex = "0af7651916cd43dd8448eb211c80319c"
    parent_hex = "b7ad6b7169203331"
    traceparent = f"00-{trace_id_hex}-{parent_hex}-01"
    baggage = "some_other_key=value"

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b'{}',
            headers={"traceparent": traceparent, "baggage": baggage},
        )
    assert resp.status_code == 200

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    span = invoke_spans[0]
    expected_parent_span_id = int(parent_hex, 16)
    assert span.parent.span_id == expected_parent_span_id


@pytest.mark.asyncio
async def test_baggage_no_traceparent_no_crash(span_exporter):
    """When baggage is present but no traceparent, no crash occurs."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b'{}',
            headers={"baggage": "leaf_customer_span_id=00f067aa0ba902b7"},
        )
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_baggage_invalid_leaf_span_id_falls_back(span_exporter):
    """Invalid hex in leaf_customer_span_id falls back to traceparent parent."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)

    trace_id_hex = "0af7651916cd43dd8448eb211c80319c"
    parent_hex = "b7ad6b7169203331"
    traceparent = f"00-{trace_id_hex}-{parent_hex}-01"
    baggage = "leaf_customer_span_id=not_valid_hex"

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        resp = await client.post(
            "/invocations",
            content=b'{}',
            headers={"traceparent": traceparent, "baggage": baggage},
        )
    assert resp.status_code == 200

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    span = invoke_spans[0]
    # Should fall back to traceparent's parent span ID
    expected_parent = int(parent_hex, 16)
    assert span.parent.span_id == expected_parent


@pytest.mark.asyncio
async def test_baggage_leaf_on_get_invocation(span_exporter):
    """Baggage leaf_customer_span_id also works on GET /invocations/{id}."""
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)

    trace_id_hex = "0af7651916cd43dd8448eb211c80319c"
    original_parent_hex = "b7ad6b7169203331"
    leaf_span_hex = "00f067aa0ba902b7"

    traceparent = f"00-{trace_id_hex}-{original_parent_hex}-01"
    baggage = f"leaf_customer_span_id={leaf_span_hex}"

    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.get(
            "/invocations/test-id",
            headers={"traceparent": traceparent, "baggage": baggage},
        )

    spans = span_exporter.get_finished_spans()
    get_spans = [s for s in spans if "get_invocation" in s.name]
    assert len(get_spans) == 1

    expected_trace_id = int(trace_id_hex, 16)
    expected_parent = int(leaf_span_hex, 16)
    assert get_spans[0].context.trace_id == expected_trace_id
    assert get_spans[0].parent.span_id == expected_parent


# ---------------------------------------------------------------------------
# Tests: agent name / version resolution
# ---------------------------------------------------------------------------


class TestAgentNameVersionResolution:
    """Tests for resolve_agent_name and resolve_agent_version."""

    def test_agent_name_from_env(self, monkeypatch):
        from azure.ai.agentserver.server._config import resolve_agent_name
        monkeypatch.setenv("AGENT_NAME", "my-agent")
        assert resolve_agent_name() == "my-agent"

    def test_agent_name_default_empty(self, monkeypatch):
        from azure.ai.agentserver.server._config import resolve_agent_name
        monkeypatch.delenv("AGENT_NAME", raising=False)
        assert resolve_agent_name() == ""

    def test_agent_version_from_env(self, monkeypatch):
        from azure.ai.agentserver.server._config import resolve_agent_version
        monkeypatch.setenv("AGENT_VERSION", "3.0.1")
        assert resolve_agent_version() == "3.0.1"

    def test_agent_version_default_empty(self, monkeypatch):
        from azure.ai.agentserver.server._config import resolve_agent_version
        monkeypatch.delenv("AGENT_VERSION", raising=False)
        assert resolve_agent_version() == ""


# ---------------------------------------------------------------------------
# Tests: project ID resolution and tracing attribute
# ---------------------------------------------------------------------------


class TestProjectIdResolution:
    """Tests for resolve_project_id and microsoft.foundry.project.id span attribute."""

    def test_project_id_from_env(self, monkeypatch):
        from azure.ai.agentserver.server._config import resolve_project_id
        monkeypatch.setenv("AGENT_PROJECT_NAME", "proj-abc-123")
        assert resolve_project_id() == "proj-abc-123"

    def test_project_id_default_empty(self, monkeypatch):
        from azure.ai.agentserver.server._config import resolve_project_id
        monkeypatch.delenv("AGENT_PROJECT_NAME", raising=False)
        assert resolve_project_id() == ""


@pytest.mark.asyncio
async def test_project_id_attribute_on_invoke_span(monkeypatch, span_exporter):
    """microsoft.foundry.project.id is set on invoke span when AGENT_PROJECT_NAME is set."""
    monkeypatch.setenv("AGENT_PROJECT_NAME", "proj-xyz-789")
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{}')

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    attrs = dict(invoke_spans[0].attributes)
    assert attrs["microsoft.foundry.project.id"] == "proj-xyz-789"


@pytest.mark.asyncio
async def test_project_id_attribute_absent_when_not_set(monkeypatch, span_exporter):
    """microsoft.foundry.project.id is NOT set when AGENT_PROJECT_NAME env var is absent."""
    monkeypatch.delenv("AGENT_PROJECT_NAME", raising=False)
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.post("/invocations", content=b'{}')

    spans = span_exporter.get_finished_spans()
    invoke_spans = [s for s in spans if "execute_agent" in s.name]
    assert len(invoke_spans) == 1

    attrs = dict(invoke_spans[0].attributes)
    assert "microsoft.foundry.project.id" not in attrs


@pytest.mark.asyncio
async def test_project_id_attribute_on_get_invocation_span(monkeypatch, span_exporter):
    """microsoft.foundry.project.id is set on get_invocation span too."""
    monkeypatch.setenv("AGENT_PROJECT_NAME", "proj-get-456")
    agent = _make_echo_traced_agent(enable_tracing=True)
    transport = httpx.ASGITransport(app=agent.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        await client.get("/invocations/test-id")

    spans = span_exporter.get_finished_spans()
    get_spans = [s for s in spans if "get_invocation" in s.name]
    assert len(get_spans) == 1

    attrs = dict(get_spans[0].attributes)
    assert attrs["microsoft.foundry.project.id"] == "proj-get-456"
