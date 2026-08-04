# pylint: disable=line-too-long,useless-suppression
# LIVE async telemetry tests using azure.ai.voicelive.aio (no mocks).
# Verifies that real OpenTelemetry spans are emitted for the `connect`
# operation and for the received `session.updated` event over a live session.

import pytest

pytest.importorskip(
    "aiohttp",
    reason="Skipping aio tests: aiohttp not installed (whl_no_aio).",
)
pytest.importorskip(
    "opentelemetry.sdk",
    reason="Skipping telemetry tests: opentelemetry-sdk not installed.",
)

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from azure.core.settings import settings
from azure.core.credentials import AzureKeyCredential
from azure.ai.voicelive.aio import connect
from azure.ai.voicelive.models import (
    Modality,
    RequestSession,
    ServerEventType,
)
from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor
from azure.ai.voicelive.telemetry import _utils as telemetry_utils

from devtools_testutils import AzureRecordedTestCase
from .voicelive_preparer import VoiceLivePreparer
from ._live_helpers import _wait_for_event


# Span / attribute names mirror the GenAI semantic conventions used by the
# instrumentor (see azure.ai.voicelive.telemetry._utils).
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
SERVER_ADDRESS = "server.address"
SERVER_PORT = "server.port"
GEN_AI_EVENT_CONTENT = "gen_ai.event.content"


def _find_span(spans, name):
    for s in spans:
        if s.name == name:
            return s
    return None


@pytest.fixture
def in_memory_span_exporter(request, monkeypatch):
    """Wire up OpenTelemetry with an in-memory exporter and enable VoiceLive tracing.

    Yields the exporter so the test can inspect the emitted spans, and tears
    instrumentation down afterwards to keep global state clean. Content recording
    can be toggled via indirect parametrization (``request.param``); defaults off.
    """
    enable_content_recording = getattr(request, "param", False)

    monkeypatch.setenv("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")
    monkeypatch.setattr(telemetry_utils, "_span_impl_type", None)
    settings.tracing_implementation = "opentelemetry"

    # Reuse a real SDK TracerProvider if one is already installed globally
    # (set_tracer_provider can only take effect once per process); otherwise
    # install one so the azure-core OpenTelemetry bridge has somewhere to emit.
    provider = trace.get_tracer_provider()
    if not isinstance(provider, TracerProvider):
        provider = TracerProvider()
        trace.set_tracer_provider(provider)

    exporter = InMemorySpanExporter()
    processor = SimpleSpanProcessor(exporter)
    provider.add_span_processor(processor)

    instrumentor = VoiceLiveInstrumentor()
    instrumentor.instrument(enable_content_recording=enable_content_recording)

    try:
        yield exporter
    finally:
        if instrumentor.is_instrumented():
            instrumentor.uninstrument()
        processor.shutdown()
        settings.tracing_implementation.unset_value()


class TestRealtimeServiceTelemetry(AzureRecordedTestCase):

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    async def test_telemetry_traces_connect_and_session_updated(
        self, in_memory_span_exporter: InMemorySpanExporter, model: str, **kwargs
    ):
        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")

        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
        ) as conn:
            session = RequestSession(modalities=[Modality.TEXT, Modality.AUDIO])
            await conn.session.update(session=session)

            await _wait_for_event(conn, {ServerEventType.SESSION_CREATED}, 15)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 15)

        # The connect span closes only when the context manager exits, so it is
        # the last span to finish. Collect everything after the block.
        spans = in_memory_span_exporter.get_finished_spans()
        span_names = [s.name for s in spans]

        connect_span = _find_span(spans, "connect")
        recv_span = _find_span(spans, "recv session.updated")
        send_span = _find_span(spans, "send session.update")

        # --- Spans exist ---
        assert connect_span is not None, f"expected a 'connect' span, got: {span_names}"
        assert recv_span is not None, f"expected 'recv session.updated', got: {span_names}"
        assert send_span is not None, f"expected 'send session.update', got: {span_names}"

        # --- Connect span attributes ---
        attrs = connect_span.attributes or {}
        assert attrs.get(GEN_AI_OPERATION_NAME) == "connect"
        assert attrs.get(GEN_AI_REQUEST_MODEL) == model
        assert attrs.get(SERVER_ADDRESS), f"missing server.address: {dict(attrs)}"
        assert attrs.get(SERVER_PORT), f"missing server.port: {dict(attrs)}"

        # --- Parent/child nesting: connect wraps the whole trace ---
        connect_span_id = connect_span.context.span_id
        assert recv_span.parent is not None, "recv span should have a parent"
        assert recv_span.parent.span_id == connect_span_id, "recv span should be a child of connect"
        assert send_span.parent is not None, "send span should have a parent"
        assert send_span.parent.span_id == connect_span_id, "send span should be a child of connect"

    @pytest.mark.live_test_only
    @VoiceLivePreparer()
    @pytest.mark.flaky(reruns=3, reruns_delay=2)
    @pytest.mark.parametrize("model", ["gpt-realtime"])
    @pytest.mark.parametrize("in_memory_span_exporter", [True, False], indirect=True)
    async def test_telemetry_content_recording_gate(
        self, in_memory_span_exporter: InMemorySpanExporter, model: str, **kwargs
    ):
        """The send span carries message content only when content recording is on."""
        content_recording_enabled = VoiceLiveInstrumentor().is_content_recording_enabled()

        voicelive_openai_endpoint = kwargs.pop("voicelive_openai_endpoint")
        voicelive_openai_api_key = kwargs.pop("voicelive_openai_api_key")

        async with connect(
            endpoint=voicelive_openai_endpoint,
            credential=AzureKeyCredential(voicelive_openai_api_key),
            model=model,
        ) as conn:
            session = RequestSession(modalities=[Modality.TEXT, Modality.AUDIO])
            await conn.session.update(session=session)
            await _wait_for_event(conn, {ServerEventType.SESSION_UPDATED}, 15)

        spans = in_memory_span_exporter.get_finished_spans()
        send_span = _find_span(spans, "send session.update")
        assert send_span is not None, "expected 'send session.update' span"

        # Content is attached as a span event attribute (gen_ai.input.messages event).
        content_values = [
            ev.attributes.get(GEN_AI_EVENT_CONTENT)
            for ev in send_span.events
            if ev.attributes and GEN_AI_EVENT_CONTENT in ev.attributes
        ]
        has_content = any(content_values)

        if content_recording_enabled:
            assert has_content, "content recording enabled but no message content captured"
        else:
            assert not has_content, "content recording disabled but message content was captured"
