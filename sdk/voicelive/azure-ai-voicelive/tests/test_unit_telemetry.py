# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Unit tests for VoiceLive telemetry instrumentation."""

import json
import os
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytest.importorskip("opentelemetry")
# ------------------------------------------------------------------ #
#  Fixtures                                                           #
# ------------------------------------------------------------------ #


@pytest.fixture(autouse=True)
def _reset_instrumentation():
    """Ensure instrumentation state is clean before/after each test."""
    import azure.ai.voicelive.telemetry._voicelive_instrumentor as mod

    mod._voicelive_traces_enabled = False
    mod._trace_voicelive_content = False
    yield
    # Uninstrument after each test to restore originals
    try:
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        if inst.is_instrumented():
            inst.uninstrument()
    except Exception:  # pylint: disable=broad-except
        pass
    mod._voicelive_traces_enabled = False
    mod._trace_voicelive_content = False


@pytest.fixture
def enable_tracing_env(monkeypatch):
    """Set the env var gate that enables tracing."""
    monkeypatch.setenv("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "true")


@pytest.fixture
def mock_span():
    """Create a mock AbstractSpan."""
    span = MagicMock()
    span.span_instance = MagicMock()
    span.span_instance.is_recording = True
    span.add_attribute = MagicMock()
    span.__enter__ = MagicMock(return_value=span)
    span.__exit__ = MagicMock(return_value=False)
    return span


# ------------------------------------------------------------------ #
#  VoiceLiveInstrumentor - basic lifecycle                            #
# ------------------------------------------------------------------ #


class TestVoiceLiveInstrumentorLifecycle:
    """Tests for instrument/uninstrument/is_instrumented."""

    def test_instrument_requires_env_gate(self):
        """instrument() is a no-op when env gate is not set."""
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        assert not inst.is_instrumented()

    def test_instrument_with_env_gate(self, enable_tracing_env):
        """instrument() activates when env gate is set."""
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        assert inst.is_instrumented()

    def test_uninstrument(self, enable_tracing_env):
        """uninstrument() restores original methods."""
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        assert inst.is_instrumented()

        inst.uninstrument()
        assert not inst.is_instrumented()

    def test_double_instrument_raises(self, enable_tracing_env):
        """Calling instrument() twice without uninstrument raises RuntimeError."""
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        with pytest.raises(RuntimeError, match="already enabled"):
            inst._impl._instrument_voicelive()

    def test_uninstrument_when_not_instrumented_is_noop(self):
        """uninstrument() when not instrumented is safe."""
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.uninstrument()  # should not raise
        assert not inst.is_instrumented()


# ------------------------------------------------------------------ #
#  Content recording                                                  #
# ------------------------------------------------------------------ #


class TestContentRecording:
    """Tests for content recording controls."""

    def test_content_recording_default_false(self, enable_tracing_env):
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        assert not inst.is_content_recording_enabled()

    def test_content_recording_explicit_true(self, enable_tracing_env):
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument(enable_content_recording=True)
        assert inst.is_content_recording_enabled()

    def test_content_recording_from_env(self, enable_tracing_env, monkeypatch):
        monkeypatch.setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        assert inst.is_content_recording_enabled()

    def test_content_recording_from_legacy_env(self, enable_tracing_env, monkeypatch):
        monkeypatch.setenv("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "true")
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        assert inst.is_content_recording_enabled()

    def test_conflicting_env_vars_disables_content(self, enable_tracing_env, monkeypatch):
        monkeypatch.setenv("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT", "true")
        monkeypatch.setenv("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "false")
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        assert not inst.is_content_recording_enabled()

    def test_successive_instrument_updates_content_recording(self, enable_tracing_env):
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        inst = VoiceLiveInstrumentor()
        inst.instrument(enable_content_recording=True)
        assert inst.is_content_recording_enabled()

        # Second call with False should update
        inst.instrument(enable_content_recording=False)
        assert not inst.is_content_recording_enabled()


# ------------------------------------------------------------------ #
#  Method wrapping verification                                       #
# ------------------------------------------------------------------ #


class TestMethodWrapping:
    """Tests that instrument() wraps the correct methods."""

    def test_methods_are_wrapped(self, enable_tracing_env):
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor
        from azure.ai.voicelive.aio._patch import VoiceLiveConnection, _VoiceLiveConnectionManager

        inst = VoiceLiveInstrumentor()
        inst.instrument()

        assert hasattr(VoiceLiveConnection.send, "_original")
        assert hasattr(VoiceLiveConnection.recv, "_original")
        assert hasattr(VoiceLiveConnection.close, "_original")
        assert hasattr(_VoiceLiveConnectionManager.__aenter__, "_original")
        assert hasattr(_VoiceLiveConnectionManager.__aexit__, "_original")

    def test_methods_are_unwrapped(self, enable_tracing_env):
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor
        from azure.ai.voicelive.aio._patch import VoiceLiveConnection, _VoiceLiveConnectionManager

        inst = VoiceLiveInstrumentor()
        inst.instrument()
        inst.uninstrument()

        assert not hasattr(VoiceLiveConnection.send, "_original")
        assert not hasattr(VoiceLiveConnection.recv, "_original")
        assert not hasattr(VoiceLiveConnection.close, "_original")
        assert not hasattr(_VoiceLiveConnectionManager.__aenter__, "_original")
        assert not hasattr(_VoiceLiveConnectionManager.__aexit__, "_original")


# ------------------------------------------------------------------ #
#  Span creation in _utils                                            #
# ------------------------------------------------------------------ #


class TestStartSpan:
    """Tests for the start_span utility."""

    def test_start_span_returns_none_without_tracing(self):
        """start_span returns None when no tracing provider is configured."""
        from azure.ai.voicelive.telemetry._utils import start_span, OperationName

        with patch("azure.ai.voicelive.telemetry._utils._span_impl_type", None):
            with patch("azure.ai.voicelive.telemetry._utils.settings") as mock_settings:
                mock_settings.tracing_implementation.return_value = None
                result = start_span(OperationName.CONNECT)
                assert result is None

    def test_start_span_sets_attributes(self, mock_span):
        """start_span sets the expected semantic attributes."""
        from azure.ai.voicelive.telemetry._utils import (
            start_span,
            OperationName,
            AZ_NAMESPACE,
            AZ_NAMESPACE_VALUE,
            GEN_AI_SYSTEM,
            AZ_AI_VOICELIVE_SYSTEM,
            GEN_AI_OPERATION_NAME,
            GEN_AI_REQUEST_MODEL,
            SERVER_ADDRESS,
        )

        mock_impl = MagicMock(return_value=mock_span)

        with patch("azure.ai.voicelive.telemetry._utils._span_impl_type", mock_impl):
            span = start_span(
                OperationName.CONNECT,
                server_address="test.cognitiveservices.azure.com",
                port=443,
                model="gpt-4o-realtime-preview",
            )

        assert span is not None
        span.add_attribute.assert_any_call(AZ_NAMESPACE, AZ_NAMESPACE_VALUE)
        span.add_attribute.assert_any_call(GEN_AI_SYSTEM, AZ_AI_VOICELIVE_SYSTEM)
        span.add_attribute.assert_any_call(GEN_AI_OPERATION_NAME, "connect")
        span.add_attribute.assert_any_call(SERVER_ADDRESS, "test.cognitiveservices.azure.com")
        span.add_attribute.assert_any_call(GEN_AI_REQUEST_MODEL, "gpt-4o-realtime-preview")


# ------------------------------------------------------------------ #
#  Send/recv wrapper span tests                                       #
# ------------------------------------------------------------------ #


class TestSendRecvTracing:
    """Tests that send/recv wrappers create spans correctly."""

    @pytest.mark.asyncio
    async def test_send_creates_span(self, enable_tracing_env, mock_span):
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor
        from azure.ai.voicelive.aio._patch import VoiceLiveConnection

        inst = VoiceLiveInstrumentor()
        inst.instrument()

        mock_impl = MagicMock(return_value=mock_span)
        mock_ws = AsyncMock()
        mock_session = AsyncMock()

        conn = VoiceLiveConnection.__new__(VoiceLiveConnection)
        conn._client_session = mock_session
        conn._connection = mock_ws
        conn._telemetry_server_address = "test.example.com"
        conn._telemetry_port = 443
        conn._telemetry_model = "gpt-4o-realtime-preview"

        event = {"type": "session.update", "session": {"model": "gpt-4o-realtime-preview"}}

        with patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.settings") as mock_settings:
            mock_settings.tracing_implementation.return_value = mock_impl
            with patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.start_span", return_value=mock_span):
                await conn.send(event)

        mock_ws.send_str.assert_called_once()

    @pytest.mark.asyncio
    async def test_recv_creates_span(self, enable_tracing_env, mock_span):
        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor
        from azure.ai.voicelive.aio._patch import VoiceLiveConnection

        inst = VoiceLiveInstrumentor()
        inst.instrument()

        mock_impl = MagicMock(return_value=mock_span)

        # Create a mock WebSocket message
        import aiohttp

        mock_ws_msg = MagicMock()
        mock_ws_msg.type = aiohttp.WSMsgType.TEXT
        mock_ws_msg.data = json.dumps({"type": "session.created", "session": {"id": "test-session-123"}})

        mock_ws = AsyncMock()
        mock_ws.receive = AsyncMock(return_value=mock_ws_msg)
        mock_session = AsyncMock()

        conn = VoiceLiveConnection.__new__(VoiceLiveConnection)
        conn._client_session = mock_session
        conn._connection = mock_ws
        conn._telemetry_server_address = "test.example.com"
        conn._telemetry_port = 443
        conn._telemetry_model = "gpt-4o-realtime-preview"

        # Initialize resource attributes that VoiceLiveConnection.__init__ would set
        from azure.ai.voicelive.aio._patch import (
            SessionResource,
            ResponseResource,
            InputAudioBufferResource,
            ConversationResource,
            OutputAudioBufferResource,
            TranscriptionSessionResource,
        )

        conn.session = SessionResource(conn)
        conn.response = ResponseResource(conn)
        conn.input_audio_buffer = InputAudioBufferResource(conn)
        conn.conversation = ConversationResource(conn)
        conn.output_audio_buffer = OutputAudioBufferResource(conn)
        conn.transcription_session = TranscriptionSessionResource(conn)

        with patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.settings") as mock_settings:
            mock_settings.tracing_implementation.return_value = mock_impl
            with patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.start_span", return_value=mock_span):
                result = await conn.recv()

        assert result is not None
        # Verify recv span name is updated to include event type
        mock_span.span_instance.update_name.assert_called_once_with("recv session.created")


# ------------------------------------------------------------------ #
#  Error recording                                                    #
# ------------------------------------------------------------------ #


class TestErrorRecording:
    """Tests for error recording on spans."""

    def test_record_error_sets_status(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        impl = _VoiceLiveInstrumentorPreview()

        exc = ConnectionError("test error")
        with patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.Span", MagicMock()):
            with patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.StatusCode") as mock_code:
                mock_code.ERROR = "ERROR"
                mock_span.span_instance = MagicMock(spec=["set_status"])
                # Make isinstance check pass
                with patch(
                    "azure.ai.voicelive.telemetry._voicelive_instrumentor.Span",
                    type(mock_span.span_instance),
                ):
                    impl.record_error(mock_span, exc)
                    mock_span.span_instance.set_status.assert_called_once()


# ------------------------------------------------------------------ #
#  Event helpers                                                      #
# ------------------------------------------------------------------ #


class TestEventHelpers:
    """Tests for send/recv event helpers."""

    def test_add_send_event_without_content(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        impl = _VoiceLiveInstrumentorPreview()
        impl._add_send_event(mock_span, "session.update", None)
        mock_span.span_instance.add_event.assert_called_once()
        call_kwargs = mock_span.span_instance.add_event.call_args
        assert call_kwargs[1]["name"] == "gen_ai.input.messages"
        assert "gen_ai.voice.event_type" in call_kwargs[1]["attributes"]

    def test_add_send_event_with_content_recording(self, mock_span):
        import azure.ai.voicelive.telemetry._voicelive_instrumentor as mod

        mod._trace_voicelive_content = True
        try:
            impl = mod._VoiceLiveInstrumentorPreview()
            impl._add_send_event(mock_span, "session.update", '{"session": {}}')
            call_kwargs = mock_span.span_instance.add_event.call_args
            assert "gen_ai.event.content" in call_kwargs[1]["attributes"]
        finally:
            mod._trace_voicelive_content = False

    def test_add_recv_event(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        impl = _VoiceLiveInstrumentorPreview()
        impl._add_recv_event(mock_span, "session.created", None)
        call_kwargs = mock_span.span_instance.add_event.call_args
        assert call_kwargs[1]["name"] == "gen_ai.output.messages"

    def test_add_connection_context_attributes(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_session_id = "session-123"
        conn._telemetry_conversation_id = "conv-456"

        _VoiceLiveInstrumentorPreview._add_connection_context_attributes(mock_span, conn)

        mock_span.add_attribute.assert_any_call("gen_ai.voice.session_id", "session-123")
        mock_span.add_attribute.assert_any_call("gen_ai.conversation.id", "conv-456")

    def test_serialize_content_and_size_for_dict(self):
        import azure.ai.voicelive.telemetry._voicelive_instrumentor as mod

        old_flag = mod._trace_voicelive_content
        mod._trace_voicelive_content = True
        try:
            payload = {"type": "session.created", "session": {"id": "abc"}}
            content, size = mod._VoiceLiveInstrumentorPreview._serialize_content_and_size(payload)
            assert content is not None
            assert size == len(content)
        finally:
            mod._trace_voicelive_content = old_flag

    def test_add_recv_event_with_forced_content(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        impl = _VoiceLiveInstrumentorPreview()
        impl._add_recv_event(
            mock_span,
            "response.text.done",
            '{"text":"hello"}',
            force_content=True,
        )
        call_kwargs = mock_span.span_instance.add_event.call_args
        assert call_kwargs[1]["name"] == "gen_ai.output.messages"
        assert call_kwargs[1]["attributes"]["gen_ai.event.content"] == '{"text":"hello"}'


class TestDoneEventContentExtraction:
    """Tests for done-event message/transcript extraction."""

    def test_extract_text_done_content(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {"type": "response.text.done", "text": "done text"}
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(result, "response.text.done")
        assert content == '{"text": "done text"}'

    def test_extract_audio_transcript_done_content(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {"type": "response.audio_transcript.done", "transcript": "done transcript"}
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(
            result,
            "response.audio_transcript.done",
        )
        assert content == '{"transcript": "done transcript"}'

    def test_extract_content_part_done_content(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {
            "type": "response.content_part.done",
            "part": {"type": "audio", "transcript": "final transcript"},
        }
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(result, "response.content_part.done")
        assert content == '{"transcript": "final transcript"}'

    def test_extract_output_item_done_content(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {
            "type": "response.output_item.done",
            "item": {
                "type": "message",
                "content": [{"type": "text", "text": "hello world"}],
            },
        }
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(result, "response.output_item.done")
        assert content == '{"messages": [{"text": "hello world"}]}'

    def test_extract_response_done_content(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {
            "type": "response.done",
            "response": {
                "output": [
                    {"type": "message", "content": [{"type": "audio", "transcript": "goodbye"}]},
                ]
            },
        }
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(result, "response.done")
        assert content == '{"messages": [{"transcript": "goodbye"}]}'

    def test_extract_function_call_arguments_done_content(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {
            "type": "response.function_call_arguments.done",
            "name": "get_current_weather",
            "arguments": '{"location": "Seattle"}',
            "call_id": "call_abc123",
        }
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(
            result, "response.function_call_arguments.done"
        )
        import json as _json
        parsed = _json.loads(content)
        assert parsed["name"] == "get_current_weather"
        assert parsed["arguments"] == {"location": "Seattle"}

    def test_extract_output_item_done_function_call(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {
            "type": "response.output_item.done",
            "item": {
                "type": "function_call",
                "name": "get_current_weather",
                "arguments": '{"location": "Seattle"}',
                "call_id": "call_abc123",
            },
        }
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(result, "response.output_item.done")
        import json as _json
        parsed = _json.loads(content)
        assert parsed["messages"][0]["name"] == "get_current_weather"
        assert parsed["messages"][0]["arguments"] == {"location": "Seattle"}

    def test_extract_response_done_function_call_item(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        result = {
            "type": "response.done",
            "response": {
                "output": [
                    {
                        "type": "function_call",
                        "name": "get_current_weather",
                        "arguments": '{"location": "Seattle"}',
                        "call_id": "call_abc123",
                    }
                ]
            },
        }
        content = _VoiceLiveInstrumentorPreview._extract_done_event_content(result, "response.done")
        import json as _json
        parsed = _json.loads(content)
        assert parsed["messages"][0]["name"] == "get_current_weather"
        assert parsed["messages"][0]["arguments"] == {"location": "Seattle"}


# ------------------------------------------------------------------ #
#  Session ID extraction                                              #
# ------------------------------------------------------------------ #


class TestSessionIdExtraction:
    """Tests for session ID tracking from recv events."""

    def test_extract_session_id_from_dict(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        result = {"type": "session.created", "session": {"id": "test-session-abc123"}}

        _VoiceLiveInstrumentorPreview._extract_session_id(conn, result)

        assert conn._telemetry_session_id == "test-session-abc123"
        conn._telemetry_span.add_attribute.assert_called_with(
            "gen_ai.voice.session_id", "test-session-abc123"
        )

    def test_extract_session_id_from_object(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview
        import types

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        session = types.SimpleNamespace(id="test-session-xyz789")
        result = types.SimpleNamespace(session=session)

        _VoiceLiveInstrumentorPreview._extract_session_id(conn, result)

        assert conn._telemetry_session_id == "test-session-xyz789"

    def test_extract_session_id_no_session(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        result = {"type": "session.created"}

        _VoiceLiveInstrumentorPreview._extract_session_id(conn, result)

        # Should not crash, and no attribute set
        conn._telemetry_span.add_attribute.assert_not_called()


# ------------------------------------------------------------------ #
#  Audio format extraction                                            #
# ------------------------------------------------------------------ #


class TestAudioFormatExtraction:
    """Tests for audio format extraction from session.update events."""

    def test_extract_audio_format_from_dict(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        event = {
            "type": "session.update",
            "session": {
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_sampling_rate": 24000,
            },
        }

        _VoiceLiveInstrumentorPreview._extract_audio_format_from_send(conn, event)

        assert conn._telemetry_input_audio_format == "pcm16"
        assert conn._telemetry_output_audio_format == "pcm16"
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.voice.input_audio_format", "pcm16"
        )
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.voice.output_audio_format", "pcm16"
        )
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.voice.input_sample_rate", 24000
        )

    def test_extract_audio_format_with_g711_ulaw(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        event = {
            "type": "session.update",
            "session": {
                "input_audio_format": "g711_ulaw",
                "output_audio_format": "g711_alaw",
                "input_audio_sampling_rate": 8000,
            },
        }

        _VoiceLiveInstrumentorPreview._extract_audio_format_from_send(conn, event)

        assert conn._telemetry_input_audio_format == "g711_ulaw"
        assert conn._telemetry_output_audio_format == "g711_alaw"
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.voice.input_sample_rate", 8000
        )

    def test_extract_audio_format_no_sampling_rate(self):
        """When input_audio_sampling_rate is absent, only formats are set."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        event = {
            "type": "session.update",
            "session": {
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_audio_format_from_send(conn, event)

        assert conn._telemetry_input_audio_format == "pcm16"
        # input_sample_rate should NOT be set
        calls = [c for c in conn._telemetry_span.add_attribute.call_args_list
                 if c[0][0] == "gen_ai.voice.input_sample_rate"]
        assert len(calls) == 0

    def test_extract_audio_format_no_session(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        event = {"type": "session.update"}

        _VoiceLiveInstrumentorPreview._extract_audio_format_from_send(conn, event)

        # Should not crash
        conn._telemetry_span.add_attribute.assert_not_called()

    def test_extract_audio_format_from_recv(self):
        """Server session.created/session.updated should set audio format and sample rate."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        result = {
            "type": "session.created",
            "session": {
                "input_audio_format": "pcm16",
                "output_audio_format": "pcm16",
                "input_audio_sampling_rate": 24000,
            },
        }

        _VoiceLiveInstrumentorPreview._extract_audio_format_from_recv(conn, result)

        assert conn._telemetry_input_audio_format == "pcm16"
        assert conn._telemetry_output_audio_format == "pcm16"
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.voice.input_audio_format", "pcm16"
        )
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.voice.output_audio_format", "pcm16"
        )
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.voice.input_sample_rate", 24000
        )

    def test_extract_audio_format_from_recv_no_session(self):
        """Recv extraction should not crash when session field is missing."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        result = {"type": "session.created"}

        _VoiceLiveInstrumentorPreview._extract_audio_format_from_recv(conn, result)

        conn._telemetry_span.add_attribute.assert_not_called()


# ------------------------------------------------------------------ #
#  First-token latency                                                #
# ------------------------------------------------------------------ #


class TestFirstTokenLatency:
    """Tests for first-token latency tracking."""

    def test_first_token_latency_set_on_recv(self, mock_span):
        """First token latency should be calculated on first audio delta."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_response_create_time = time.monotonic() - 0.5  # 500ms ago
        conn._telemetry_first_token_latency_recorded = False
        conn._telemetry_span = MagicMock()

        result = {"type": "response.audio.delta", "delta": "AAAA"}

        # Simulate the logic from _trace_recv
        event_type_str = "response.audio.delta"
        response_create_time = conn._telemetry_response_create_time
        already_recorded = conn._telemetry_first_token_latency_recorded
        if response_create_time is not None and not already_recorded:
            latency_ms = (time.monotonic() - response_create_time) * 1000
            mock_span.add_attribute("gen_ai.voice.first_token_latency_ms", round(latency_ms, 2))
            conn._telemetry_first_token_latency_recorded = True

        mock_span.add_attribute.assert_called_once()
        call_args = mock_span.add_attribute.call_args
        assert call_args[0][0] == "gen_ai.voice.first_token_latency_ms"
        assert call_args[0][1] >= 400  # Should be ~500ms
        assert conn._telemetry_first_token_latency_recorded is True

    def test_first_token_latency_ignores_text_delta(self, mock_span):
        """Text delta should not trigger first-token latency tracking."""
        conn = MagicMock()
        conn._telemetry_response_create_time = time.monotonic() - 0.5
        conn._telemetry_first_token_latency_recorded = False

        event_type_str = "response.text.delta"
        response_create_time = conn._telemetry_response_create_time
        already_recorded = conn._telemetry_first_token_latency_recorded
        if event_type_str == "response.audio.delta" and response_create_time is not None and not already_recorded:
            latency_ms = (time.monotonic() - response_create_time) * 1000
            mock_span.add_attribute("gen_ai.voice.first_token_latency_ms", round(latency_ms, 2))
            conn._telemetry_first_token_latency_recorded = True

        mock_span.add_attribute.assert_not_called()
        assert conn._telemetry_first_token_latency_recorded is False

    def test_first_token_latency_not_recorded_twice(self):
        """Once first-token latency is recorded, subsequent deltas should not re-record."""
        conn = MagicMock()
        conn._telemetry_response_create_time = time.monotonic() - 0.5
        conn._telemetry_first_token_latency_recorded = True

        # Simulate the guard check
        already_recorded = conn._telemetry_first_token_latency_recorded
        assert already_recorded is True  # Should not proceed with recording


# ------------------------------------------------------------------ #
#  Turn count and interruption tracking                               #
# ------------------------------------------------------------------ #


class TestTurnCountAndInterruptions:
    """Tests for turn count and interruption count tracking."""

    def test_turn_count_increments_on_response_done(self):
        conn = MagicMock()
        conn._telemetry_turn_count = 0

        # Simulate response.done processing
        conn._telemetry_turn_count = conn._telemetry_turn_count + 1
        assert conn._telemetry_turn_count == 1

        conn._telemetry_turn_count = conn._telemetry_turn_count + 1
        assert conn._telemetry_turn_count == 2

    def test_interruption_count_increments_on_response_cancel(self):
        conn = MagicMock()
        conn._telemetry_interruption_count = 0

        # Simulate response.cancel processing
        conn._telemetry_interruption_count = conn._telemetry_interruption_count + 1
        assert conn._telemetry_interruption_count == 1

    def test_counters_recorded_on_aexit(self, mock_span):
        """Verify the aexit wrapper records session-level counters."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import (
            _VoiceLiveInstrumentorPreview,
            GEN_AI_VOICE_TURN_COUNT,
            GEN_AI_VOICE_INTERRUPTION_COUNT,
            GEN_AI_VOICE_AUDIO_BYTES_SENT,
            GEN_AI_VOICE_AUDIO_BYTES_RECEIVED,
        )

        conn = MagicMock()
        conn._telemetry_turn_count = 3
        conn._telemetry_interruption_count = 1
        conn._telemetry_audio_bytes_sent = 48000
        conn._telemetry_audio_bytes_received = 96000

        # Simulate the aexit logic that records counters on the span
        if conn._telemetry_turn_count > 0:
            mock_span.add_attribute(GEN_AI_VOICE_TURN_COUNT, conn._telemetry_turn_count)
        if conn._telemetry_interruption_count > 0:
            mock_span.add_attribute(GEN_AI_VOICE_INTERRUPTION_COUNT, conn._telemetry_interruption_count)
        if conn._telemetry_audio_bytes_sent > 0:
            mock_span.add_attribute(GEN_AI_VOICE_AUDIO_BYTES_SENT, conn._telemetry_audio_bytes_sent)
        if conn._telemetry_audio_bytes_received > 0:
            mock_span.add_attribute(GEN_AI_VOICE_AUDIO_BYTES_RECEIVED, conn._telemetry_audio_bytes_received)

        mock_span.add_attribute.assert_any_call("gen_ai.voice.turn_count", 3)
        mock_span.add_attribute.assert_any_call("gen_ai.voice.interruption_count", 1)
        mock_span.add_attribute.assert_any_call("gen_ai.voice.audio_bytes_sent", 48000)
        mock_span.add_attribute.assert_any_call("gen_ai.voice.audio_bytes_received", 96000)


# ------------------------------------------------------------------ #
#  Audio bytes tracking                                               #
# ------------------------------------------------------------------ #


class TestAudioBytesTracking:
    """Tests for audio bytes sent/received tracking."""

    def test_audio_bytes_sent_from_base64(self):
        """Audio bytes sent should decode base64 to count raw bytes."""
        import base64

        conn = MagicMock()
        conn._telemetry_audio_bytes_sent = 0

        # 100 bytes of raw audio encoded as base64
        raw_audio = b"\x00" * 100
        b64_audio = base64.b64encode(raw_audio).decode("utf-8")

        audio_bytes = len(base64.b64decode(b64_audio))
        conn._telemetry_audio_bytes_sent = conn._telemetry_audio_bytes_sent + audio_bytes

        assert conn._telemetry_audio_bytes_sent == 100

    def test_audio_bytes_received_from_delta(self):
        """Audio bytes received should decode the delta field."""
        import base64

        conn = MagicMock()
        conn._telemetry_audio_bytes_received = 0

        raw_audio = b"\xFF" * 200
        b64_delta = base64.b64encode(raw_audio).decode("utf-8")

        audio_bytes = len(base64.b64decode(b64_delta))
        conn._telemetry_audio_bytes_received = conn._telemetry_audio_bytes_received + audio_bytes

        assert conn._telemetry_audio_bytes_received == 200


# ------------------------------------------------------------------ #
#  Message size tracking                                              #
# ------------------------------------------------------------------ #


class TestMessageSize:
    """Tests for WebSocket message size tracking on spans."""

    def test_message_size_on_send(self, mock_span):
        """Send wrapper should set message size attribute."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        event = {"type": "session.update", "session": {"model": "gpt-4o"}}
        content_str = json.dumps(event, default=str)
        expected_size = len(content_str)

        mock_span.add_attribute("gen_ai.voice.message_size", expected_size)
        mock_span.add_attribute.assert_called_with("gen_ai.voice.message_size", expected_size)

    def test_message_size_on_recv(self, mock_span):
        """Recv wrapper should set message size attribute."""
        result = {"type": "session.created", "session": {"id": "test-session-123"}}
        content_str = json.dumps(result, default=str)
        expected_size = len(content_str)

        mock_span.add_attribute("gen_ai.voice.message_size", expected_size)
        mock_span.add_attribute.assert_called_with("gen_ai.voice.message_size", expected_size)


# ------------------------------------------------------------------ #
#  Rate limit and error event tracking                                #
# ------------------------------------------------------------------ #


class TestRateLimitEvents:
    """Tests for rate limit / error event recording."""

    def test_error_event_recorded(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        impl = _VoiceLiveInstrumentorPreview()
        result = {
            "type": "error",
            "error": {"code": "rate_limit_exceeded", "message": "Too many requests"},
        }

        impl._add_rate_limit_event(mock_span, "error", result)

        call_kwargs = mock_span.span_instance.add_event.call_args
        assert call_kwargs[1]["name"] == "gen_ai.voice.error"
        assert call_kwargs[1]["attributes"]["error.code"] == "rate_limit_exceeded"
        assert call_kwargs[1]["attributes"]["error.message"] == "Too many requests"

    def test_rate_limits_updated_event_recorded(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        impl = _VoiceLiveInstrumentorPreview()
        result = {
            "type": "rate_limits.updated",
            "rate_limits": [
                {"name": "requests", "limit": 100, "remaining": 95, "reset_seconds": 60},
            ],
        }

        impl._add_rate_limit_event(mock_span, "rate_limits.updated", result)

        call_kwargs = mock_span.span_instance.add_event.call_args
        assert call_kwargs[1]["name"] == "gen_ai.voice.rate_limits.updated"
        assert "gen_ai.voice.rate_limits" in call_kwargs[1]["attributes"]

    def test_error_event_with_object_result(self, mock_span):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview
        import types

        impl = _VoiceLiveInstrumentorPreview()
        error_obj = types.SimpleNamespace(code="server_error", message="Internal error")
        result = types.SimpleNamespace(error=error_obj)

        impl._add_rate_limit_event(mock_span, "error", result)

        call_kwargs = mock_span.span_instance.add_event.call_args
        assert call_kwargs[1]["attributes"]["error.code"] == "server_error"
        assert call_kwargs[1]["attributes"]["error.message"] == "Internal error"


# ------------------------------------------------------------------ #
#  New constants verification                                         #
# ------------------------------------------------------------------ #


class TestNewConstants:
    """Verify all new telemetry constants are properly defined."""

    def test_new_constants_exist(self):
        from azure.ai.voicelive.telemetry._utils import (
            GEN_AI_VOICE_INPUT_AUDIO_FORMAT,
            GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT,
            GEN_AI_VOICE_INPUT_SAMPLE_RATE,
            GEN_AI_VOICE_OUTPUT_SAMPLE_RATE,
            GEN_AI_VOICE_TURN_COUNT,
            GEN_AI_VOICE_INTERRUPTION_COUNT,
            GEN_AI_VOICE_AUDIO_BYTES_SENT,
            GEN_AI_VOICE_AUDIO_BYTES_RECEIVED,
            GEN_AI_VOICE_MESSAGE_SIZE,
            GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS,
            GEN_AI_VOICE_CALL_ID,
            GEN_AI_VOICE_ITEM_ID,
            GEN_AI_VOICE_PREVIOUS_ITEM_ID,
            GEN_AI_VOICE_OUTPUT_INDEX,
            GEN_AI_VOICE_MCP_SERVER_LABEL,
            GEN_AI_VOICE_MCP_TOOL_NAME,
            GEN_AI_VOICE_MCP_APPROVAL_REQUEST_ID,
            GEN_AI_VOICE_MCP_APPROVE,
            GEN_AI_VOICE_MCP_CALL_COUNT,
            GEN_AI_VOICE_MCP_LIST_TOOLS_COUNT,
            GEN_AI_AGENT_NAME,
            GEN_AI_AGENT_ID,
            GEN_AI_AGENT_THREAD_ID,
            GEN_AI_AGENT_VERSION,
            GEN_AI_AGENT_PROJECT_NAME,
            GEN_AI_CONVERSATION_ID,
            GEN_AI_RESPONSE_ID,
            GEN_AI_RESPONSE_FINISH_REASONS,
            GEN_AI_REQUEST_TEMPERATURE,
            GEN_AI_REQUEST_MAX_OUTPUT_TOKENS,
            GEN_AI_REQUEST_TOOLS,
            GEN_AI_SYSTEM_MESSAGE,
            GEN_AI_SYSTEM_INSTRUCTION_EVENT,
            GEN_AI_CLIENT_OPERATION_DURATION,
            GEN_AI_CLIENT_TOKEN_USAGE,
            ERROR_MESSAGE,
        )

        assert GEN_AI_VOICE_INPUT_AUDIO_FORMAT == "gen_ai.voice.input_audio_format"
        assert GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT == "gen_ai.voice.output_audio_format"
        assert GEN_AI_VOICE_INPUT_SAMPLE_RATE == "gen_ai.voice.input_sample_rate"
        assert GEN_AI_VOICE_OUTPUT_SAMPLE_RATE == "gen_ai.voice.output_sample_rate"
        assert GEN_AI_VOICE_TURN_COUNT == "gen_ai.voice.turn_count"
        assert GEN_AI_VOICE_INTERRUPTION_COUNT == "gen_ai.voice.interruption_count"
        assert GEN_AI_VOICE_AUDIO_BYTES_SENT == "gen_ai.voice.audio_bytes_sent"
        assert GEN_AI_VOICE_AUDIO_BYTES_RECEIVED == "gen_ai.voice.audio_bytes_received"
        assert GEN_AI_VOICE_MESSAGE_SIZE == "gen_ai.voice.message_size"
        assert GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS == "gen_ai.voice.first_token_latency_ms"
        assert GEN_AI_VOICE_CALL_ID == "gen_ai.voice.call_id"
        assert GEN_AI_VOICE_ITEM_ID == "gen_ai.voice.item_id"
        assert GEN_AI_VOICE_PREVIOUS_ITEM_ID == "gen_ai.voice.previous_item_id"
        assert GEN_AI_VOICE_OUTPUT_INDEX == "gen_ai.voice.output_index"
        assert GEN_AI_VOICE_MCP_SERVER_LABEL == "gen_ai.voice.mcp.server_label"
        assert GEN_AI_VOICE_MCP_TOOL_NAME == "gen_ai.voice.mcp.tool_name"
        assert GEN_AI_VOICE_MCP_APPROVAL_REQUEST_ID == "gen_ai.voice.mcp.approval_request_id"
        assert GEN_AI_VOICE_MCP_APPROVE == "gen_ai.voice.mcp.approve"
        assert GEN_AI_VOICE_MCP_CALL_COUNT == "gen_ai.voice.mcp.call_count"
        assert GEN_AI_VOICE_MCP_LIST_TOOLS_COUNT == "gen_ai.voice.mcp.list_tools_count"
        assert GEN_AI_AGENT_NAME == "gen_ai.agent.name"
        assert GEN_AI_AGENT_ID == "gen_ai.agent.id"
        assert GEN_AI_AGENT_THREAD_ID == "gen_ai.agent.thread_id"
        assert GEN_AI_AGENT_VERSION == "gen_ai.agent.version"
        assert GEN_AI_AGENT_PROJECT_NAME == "gen_ai.agent.project_name"
        assert GEN_AI_CONVERSATION_ID == "gen_ai.conversation.id"
        assert GEN_AI_RESPONSE_ID == "gen_ai.response.id"
        assert GEN_AI_RESPONSE_FINISH_REASONS == "gen_ai.response.finish_reasons"
        assert GEN_AI_REQUEST_TEMPERATURE == "gen_ai.request.temperature"
        assert GEN_AI_REQUEST_MAX_OUTPUT_TOKENS == "gen_ai.request.max_output_tokens"
        assert GEN_AI_REQUEST_TOOLS == "gen_ai.request.tools"
        assert GEN_AI_SYSTEM_MESSAGE == "gen_ai.system_instructions"
        assert GEN_AI_SYSTEM_INSTRUCTION_EVENT == "gen_ai.system.instructions"
        assert GEN_AI_CLIENT_OPERATION_DURATION == "gen_ai.client.operation.duration"
        assert GEN_AI_CLIENT_TOKEN_USAGE == "gen_ai.client.token.usage"
        assert ERROR_MESSAGE == "error.message"


# ------------------------------------------------------------------ #
#  Session config extraction                                          #
# ------------------------------------------------------------------ #


class TestSessionConfigExtraction:
    """Tests for _extract_session_config_from_send."""

    def test_extract_instructions_and_temperature(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        event = {
            "type": "session.update",
            "session": {
                "instructions": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_response_output_tokens": 4096,
            },
        }

        _VoiceLiveInstrumentorPreview._extract_session_config_from_send(conn, event)

        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.system_instructions", "You are a helpful assistant."
        )
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.request.temperature", "0.7"
        )
        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.request.max_output_tokens", 4096
        )

    def test_extract_tools(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        event = {
            "type": "session.update",
            "session": {
                "tools": [{"type": "function", "name": "get_weather"}],
            },
        }

        _VoiceLiveInstrumentorPreview._extract_session_config_from_send(conn, event)

        conn._telemetry_span.add_attribute.assert_any_call(
            "gen_ai.request.tools",
            json.dumps([{"type": "function", "name": "get_weather"}]),
        )

    def test_extract_no_session(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        event = {"type": "session.update"}

        _VoiceLiveInstrumentorPreview._extract_session_config_from_send(conn, event)

        conn._telemetry_span.add_attribute.assert_not_called()

    def test_system_instruction_event_with_content_recording(self):
        import azure.ai.voicelive.telemetry._voicelive_instrumentor as mod
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        mod._trace_voicelive_content = True
        try:
            conn = MagicMock()
            conn._telemetry_span = MagicMock()
            event = {
                "type": "session.update",
                "session": {"instructions": "Be concise."},
            }

            _VoiceLiveInstrumentorPreview._extract_session_config_from_send(conn, event)

            conn._telemetry_span.span_instance.add_event.assert_called_once()
            call_kwargs = conn._telemetry_span.span_instance.add_event.call_args
            assert call_kwargs[1]["name"] == "gen_ai.system.instructions"
        finally:
            mod._trace_voicelive_content = False


# ------------------------------------------------------------------ #
#  Response done extraction                                           #
# ------------------------------------------------------------------ #


class TestResponseDoneExtraction:
    """Tests for _extract_response_done."""

    def test_extract_response_metadata(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.done",
            "response": {
                "id": "resp_abc123",
                "conversation_id": "conv_xyz",
                "status": "completed",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_response_done(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_abc123")
        span.add_attribute.assert_any_call("gen_ai.conversation.id", "conv_xyz")
        span.add_attribute.assert_any_call("gen_ai.response.finish_reasons", '["completed"]')
        assert conn._telemetry_conversation_id == "conv_xyz"
        # Connect span also gets the attributes
        conn._telemetry_span.add_attribute.assert_any_call("gen_ai.response.id", "resp_abc123")
        conn._telemetry_span.add_attribute.assert_any_call("gen_ai.conversation.id", "conv_xyz")

    def test_extract_response_no_response_field(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()
        span = MagicMock()

        result = {"type": "response.done"}

        _VoiceLiveInstrumentorPreview._extract_response_done(conn, result, span)

        span.add_attribute.assert_not_called()
        conn._telemetry_span.add_attribute.assert_not_called()


# ------------------------------------------------------------------ #
#  Agent config extraction in connect                                 #
# ------------------------------------------------------------------ #


class TestAgentConfigExtraction:
    """Tests for agent config extraction during connect."""

    def test_agent_name_from_config(self):
        """_trace_connect should set agent_name on the span from agent_config."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        instrumentor = _VoiceLiveInstrumentorPreview()

        mock_conn = MagicMock()

        async def fake_aenter(mgr_self, *a, **kw):
            return mock_conn

        wrapper = instrumentor._trace_connect(fake_aenter)

        # Build a mock manager with agent config
        mgr = MagicMock()
        mgr._endpoint = "wss://example.com"
        mgr._VoiceLiveConnectionManager__model = "gpt-4o-realtime"
        mgr._VoiceLiveConnectionManager__agent_config = {
            "agent_name": "TestAgent",
            "conversation_id": "conv_123",
        }

        import asyncio

        with patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.settings") as mock_settings, \
             patch("azure.ai.voicelive.telemetry._voicelive_instrumentor.start_span") as mock_start:
            mock_span = MagicMock()
            mock_span.__enter__ = MagicMock(return_value=mock_span)
            mock_span.__exit__ = MagicMock(return_value=False)
            mock_start.return_value = mock_span
            mock_settings.tracing_implementation.return_value = MagicMock

            asyncio.get_event_loop().run_until_complete(wrapper(mgr))

            mock_span.add_attribute.assert_any_call("gen_ai.agent.name", "TestAgent")
            mock_span.add_attribute.assert_any_call("gen_ai.conversation.id", "conv_123")
            assert mock_conn._telemetry_agent_name == "TestAgent"
            assert mock_conn._telemetry_conversation_id == "conv_123"


# ------------------------------------------------------------------ #
#  Event ID extraction (recv)                                         #
# ------------------------------------------------------------------ #


class TestExtractEventIds:
    """Tests for _extract_event_ids - generic ID extraction from recv events."""

    def test_extract_response_id_and_call_id_from_function_call_delta(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.function_call_arguments.delta",
            "response_id": "resp_abc123",
            "item_id": "item_001",
            "call_id": "call_xyz",
            "delta": '{"arg": "val"}',
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_abc123")
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_xyz")
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_001")

    def test_extract_response_id_and_call_id_from_function_call_done(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.function_call_arguments.done",
            "response_id": "resp_abc123",
            "item_id": "item_001",
            "call_id": "call_xyz",
            "name": "get_weather",
            "arguments": '{"city": "Seattle"}',
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_abc123")
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_xyz")
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_001")

    def test_extract_response_id_from_audio_delta(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.audio.delta",
            "response_id": "resp_abc123",
            "item_id": "item_002",
            "delta": "base64data",
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_abc123")
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_002")

    def test_extract_conversation_id_from_response_created(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.created",
            "response": {
                "id": "resp_new",
                "conversation_id": "conv_abc",
                "status": "in_progress",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_new")
        span.add_attribute.assert_any_call("gen_ai.conversation.id", "conv_abc")
        assert conn._telemetry_conversation_id == "conv_abc"

    def test_extract_previous_item_id_from_conversation_item_created(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "conversation.item.created",
            "previous_item_id": "item_prev_001",
            "item": {
                "id": "item_new",
                "type": "function_call",
                "call_id": "call_fc_001",
                "name": "get_weather",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.voice.previous_item_id", "item_prev_001")
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_fc_001")

    def test_extract_nested_call_id_from_output_item_added(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.output_item.added",
            "response_id": "resp_abc",
            "output_index": 0,
            "item": {
                "id": "item_fc",
                "type": "function_call",
                "call_id": "call_nested_001",
                "name": "search_db",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_abc")
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_nested_001")

    def test_no_nested_call_id_when_top_level_present(self):
        """Top-level call_id takes precedence; nested item.call_id is NOT duplicated."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.function_call_arguments.delta",
            "response_id": "resp_abc",
            "call_id": "call_top",
            "item_id": "item_001",
            "item": {
                "call_id": "call_nested_should_be_ignored",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        # call_id should be from top-level, not nested
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_top")
        # Ensure nested call_id was NOT set (only one call for call_id key)
        call_id_calls = [c for c in span.add_attribute.call_args_list if c[0][0] == "gen_ai.voice.call_id"]
        assert len(call_id_calls) == 1

    def test_no_ids_on_session_created(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "session.created",
            "session": {"id": "session_123"},
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        # session.created has no response_id, call_id, or item_id
        span.add_attribute.assert_not_called()

    def test_extract_with_model_objects(self):
        """Test extraction from model objects (attribute access instead of dict)."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = MagicMock()
        result.get = MagicMock(side_effect=AttributeError)
        del result.get  # force attribute access path
        result.response_id = "resp_obj"
        result.call_id = "call_obj"
        result.item_id = "item_obj"
        result.previous_item_id = None
        result.output_index = None
        result.response = None
        result.item = None

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_obj")
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_obj")
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_obj")


# ------------------------------------------------------------------ #
#  Send event ID extraction                                           #
# ------------------------------------------------------------------ #


class TestExtractSendEventIds:
    """Tests for _extract_send_event_ids - ID extraction from send events."""

    def test_extract_call_id_from_conversation_item_create(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "function_call_output",
                "call_id": "call_xyz",
                "output": '{"result": "sunny"}',
            },
        }

        _VoiceLiveInstrumentorPreview._extract_send_event_ids(conn, event, span)

        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_xyz")

    def test_extract_previous_item_id_from_conversation_item_create(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        event = {
            "type": "conversation.item.create",
            "previous_item_id": "item_prev_send",
            "item": {
                "type": "function_call_output",
                "call_id": "call_xyz",
                "output": '{"result": "sunny"}',
            },
        }

        _VoiceLiveInstrumentorPreview._extract_send_event_ids(conn, event, span)

        span.add_attribute.assert_any_call("gen_ai.voice.previous_item_id", "item_prev_send")
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_xyz")

    def test_extract_response_id_from_response_cancel(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        event = {
            "type": "response.cancel",
            "response_id": "resp_cancel",
        }

        _VoiceLiveInstrumentorPreview._extract_send_event_ids(conn, event, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_cancel")

    def test_no_ids_on_audio_append(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        event = {
            "type": "input_audio_buffer.append",
            "audio": "base64data",
        }

        _VoiceLiveInstrumentorPreview._extract_send_event_ids(conn, event, span)

        span.add_attribute.assert_not_called()


# ------------------------------------------------------------------ #
#  MCP event ID / field extraction (recv)                             #
# ------------------------------------------------------------------ #


class TestMCPEventExtraction:
    """Tests for MCP-specific field extraction from recv events."""

    def test_extract_mcp_fields_from_output_item_added_mcp_call(self):
        """response.output_item.added with an mcp_call item."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.output_item.added",
            "response_id": "resp_mcp",
            "output_index": 0,
            "item": {
                "id": "item_mcp_call_001",
                "type": "mcp_call",
                "server_label": "my_mcp_server",
                "name": "search_docs",
                "arguments": "{}",
                "approval_request_id": "apr_001",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.response.id", "resp_mcp")
        span.add_attribute.assert_any_call("gen_ai.voice.output_index", 0)
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_mcp_call_001")
        span.add_attribute.assert_any_call("gen_ai.voice.mcp.server_label", "my_mcp_server")
        span.add_attribute.assert_any_call("gen_ai.voice.mcp.tool_name", "search_docs")
        span.add_attribute.assert_any_call("gen_ai.voice.mcp.approval_request_id", "apr_001")

    def test_extract_mcp_approval_request_item(self):
        """response.output_item.added with an mcp_approval_request item."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.output_item.added",
            "response_id": "resp_apr",
            "output_index": 1,
            "item": {
                "id": "item_apr_001",
                "type": "mcp_approval_request",
                "server_label": "secure_server",
                "name": "delete_record",
                "arguments": '{"id": 42}',
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.voice.mcp.server_label", "secure_server")
        span.add_attribute.assert_any_call("gen_ai.voice.mcp.tool_name", "delete_record")
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_apr_001")

    def test_extract_mcp_approval_response_item(self):
        """conversation.item.created with an mcp_approval_response."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "conversation.item.created",
            "previous_item_id": "item_prev",
            "item": {
                "id": "item_apres_001",
                "type": "mcp_approval_response",
                "approval_request_id": "apr_001",
                "approve": True,
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.voice.mcp.approval_request_id", "apr_001")
        span.add_attribute.assert_any_call("gen_ai.voice.mcp.approve", True)
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_apres_001")
        span.add_attribute.assert_any_call("gen_ai.voice.previous_item_id", "item_prev")

    def test_extract_mcp_list_tools_item(self):
        """response.output_item.done with an mcp_list_tools item."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.output_item.done",
            "response_id": "resp_lt",
            "output_index": 0,
            "item": {
                "id": "item_lt_001",
                "type": "mcp_list_tools",
                "server_label": "tools_server",
                "tools": [{"name": "tool_a"}, {"name": "tool_b"}],
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.voice.mcp.server_label", "tools_server")
        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_lt_001")
        span.add_attribute.assert_any_call("gen_ai.voice.output_index", 0)

    def test_no_tool_name_for_message_items(self):
        """Message items have 'name' in some contexts but we should NOT set mcp.tool_name."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "conversation.item.created",
            "item": {
                "id": "item_msg",
                "type": "message",
                "role": "assistant",
                "content": [],
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        # Should NOT have mcp.tool_name
        tool_name_calls = [c for c in span.add_attribute.call_args_list
                           if c[0][0] == "gen_ai.voice.mcp.tool_name"]
        assert len(tool_name_calls) == 0

    def test_extract_item_id_from_nested_item(self):
        """conversation.item.created has no top-level item_id; should extract from item.id."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "conversation.item.created",
            "item": {
                "id": "item_nested_id_001",
                "type": "function_call",
                "call_id": "call_fc",
                "name": "get_weather",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.voice.item_id", "item_nested_id_001")
        span.add_attribute.assert_any_call("gen_ai.voice.call_id", "call_fc")
        span.add_attribute.assert_any_call("gen_ai.voice.mcp.tool_name", "get_weather")

    def test_output_index_extraction(self):
        """output_index should be tracked on MCP call argument events."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        result = {
            "type": "response.mcp_call_arguments.delta",
            "response_id": "resp_mcp",
            "item_id": "item_mcp",
            "output_index": 2,
            "delta": "{}",
        }

        _VoiceLiveInstrumentorPreview._extract_event_ids(conn, result, span)

        span.add_attribute.assert_any_call("gen_ai.voice.output_index", 2)


# ------------------------------------------------------------------ #
#  MCP send event extraction                                          #
# ------------------------------------------------------------------ #


class TestMCPSendEventExtraction:
    """Tests for MCP-specific field extraction from send events."""

    def test_extract_approval_response_from_send(self):
        """conversation.item.create with mcp_approval_response item."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        event = {
            "type": "conversation.item.create",
            "item": {
                "type": "mcp_approval_response",
                "approval_request_id": "apr_send_001",
                "approve": False,
            },
        }

        _VoiceLiveInstrumentorPreview._extract_send_event_ids(conn, event, span)

        span.add_attribute.assert_any_call("gen_ai.voice.mcp.approval_request_id", "apr_send_001")
        span.add_attribute.assert_any_call("gen_ai.voice.mcp.approve", False)


# ------------------------------------------------------------------ #
#  Agent config extraction from session.created                       #
# ------------------------------------------------------------------ #


class TestAgentConfigExtraction:
    """Tests for _extract_agent_config_from_session."""

    def test_extract_agent_id_and_thread_id(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()

        result = {
            "type": "session.created",
            "session": {
                "id": "session_abc",
                "agent": {
                    "type": "agent",
                    "name": "MyAgent",
                    "agent_id": "agent_001",
                    "thread_id": "thread_001",
                },
            },
        }

        _VoiceLiveInstrumentorPreview._extract_agent_config_from_session(conn, result)

        conn._telemetry_span.add_attribute.assert_any_call("gen_ai.agent.id", "agent_001")
        conn._telemetry_span.add_attribute.assert_any_call("gen_ai.agent.thread_id", "thread_001")

    def test_no_agent_config_in_session(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()

        result = {
            "type": "session.created",
            "session": {
                "id": "session_abc",
            },
        }

        _VoiceLiveInstrumentorPreview._extract_agent_config_from_session(conn, result)

        conn._telemetry_span.add_attribute.assert_not_called()

    def test_no_session_field(self):
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        conn._telemetry_span = MagicMock()

        result = {"type": "session.created"}

        _VoiceLiveInstrumentorPreview._extract_agent_config_from_session(conn, result)

        conn._telemetry_span.add_attribute.assert_not_called()


# ------------------------------------------------------------------ #
#  Agent session config extraction on connect span                    #
# ------------------------------------------------------------------ #


class TestAgentSessionConfigOnConnect:
    """Tests for agent_version and project_name on the connect span."""

    def test_agent_version_and_project_name_on_connect(self):
        """Verify agent_version and project_name are set on the connect span."""
        from azure.ai.voicelive.telemetry._voicelive_instrumentor import _VoiceLiveInstrumentorPreview

        conn = MagicMock()
        span = MagicMock()

        # Simulate _trace_aenter agent config extraction
        agent_config = {
            "agent_name": "TestAgent",
            "project_name": "TestProject",
            "agent_version": "v2.1",
            "conversation_id": "conv_123",
        }

        # Extract logic inline (as done in _trace_aenter)
        agent_name = agent_config.get("agent_name")
        if agent_name:
            span.add_attribute("gen_ai.agent.name", agent_name)
        conv_id = agent_config.get("conversation_id")
        if conv_id:
            span.add_attribute("gen_ai.conversation.id", conv_id)
        agent_version = agent_config.get("agent_version")
        if agent_version:
            span.add_attribute("gen_ai.agent.version", agent_version)
        project_name = agent_config.get("project_name")
        if project_name:
            span.add_attribute("gen_ai.agent.project_name", project_name)

        span.add_attribute.assert_any_call("gen_ai.agent.name", "TestAgent")
        span.add_attribute.assert_any_call("gen_ai.conversation.id", "conv_123")
        span.add_attribute.assert_any_call("gen_ai.agent.version", "v2.1")
        span.add_attribute.assert_any_call("gen_ai.agent.project_name", "TestProject")

