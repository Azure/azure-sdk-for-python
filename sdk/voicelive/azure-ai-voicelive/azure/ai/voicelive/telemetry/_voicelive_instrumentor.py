# pylint: disable=line-too-long,useless-suppression,protected-access,too-many-statements,too-many-lines,invalid-name,import-outside-toplevel
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""VoiceLive telemetry instrumentor for OpenTelemetry-based tracing."""

import base64
import functools
import importlib
import json
import logging
import os
import time
from typing import Any, Callable, Dict, Optional, Tuple

from azure.core.settings import settings
from azure.core.tracing import AbstractSpan

from ..models._enums import ClientEventType, ServerEventType
from ._utils import (
    AZ_AI_VOICELIVE_SYSTEM,
    ERROR_MESSAGE,
    ERROR_TYPE,
    GEN_AI_AGENT_ID,
    GEN_AI_AGENT_NAME,
    GEN_AI_AGENT_PROJECT_NAME,
    GEN_AI_AGENT_THREAD_ID,
    GEN_AI_AGENT_VERSION,
    GEN_AI_CLIENT_OPERATION_DURATION,
    GEN_AI_CLIENT_TOKEN_USAGE,
    GEN_AI_CONVERSATION_ID,
    GEN_AI_EVENT_CONTENT,
    GEN_AI_OPERATION_NAME,
    GEN_AI_PROVIDER_NAME,
    GEN_AI_PROVIDER_VALUE,
    GEN_AI_REQUEST_MAX_OUTPUT_TOKENS,
    GEN_AI_REQUEST_MODEL,
    GEN_AI_REQUEST_TEMPERATURE,
    GEN_AI_REQUEST_TOOLS,
    GEN_AI_RESPONSE_FINISH_REASONS,
    GEN_AI_RESPONSE_ID,
    GEN_AI_SYSTEM,
    GEN_AI_SYSTEM_INSTRUCTION_EVENT,
    GEN_AI_SYSTEM_MESSAGE,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    GEN_AI_VOICE_AUDIO_BYTES_RECEIVED,
    GEN_AI_VOICE_AUDIO_BYTES_SENT,
    GEN_AI_VOICE_CALL_ID,
    GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS,
    GEN_AI_VOICE_ITEM_ID,
    GEN_AI_VOICE_INPUT_AUDIO_FORMAT,
    GEN_AI_VOICE_INPUT_SAMPLE_RATE,
    GEN_AI_VOICE_INTERRUPTION_COUNT,
    GEN_AI_VOICE_MCP_APPROVAL_REQUEST_ID,
    GEN_AI_VOICE_MCP_APPROVE,
    GEN_AI_VOICE_MCP_CALL_COUNT,
    GEN_AI_VOICE_MCP_LIST_TOOLS_COUNT,
    GEN_AI_VOICE_MCP_SERVER_LABEL,
    GEN_AI_VOICE_MCP_TOOL_NAME,
    GEN_AI_VOICE_MESSAGE_SIZE,
    GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT,
    GEN_AI_VOICE_OUTPUT_INDEX,
    GEN_AI_VOICE_PREVIOUS_ITEM_ID,
    GEN_AI_VOICE_SESSION_ID,
    GEN_AI_VOICE_TURN_COUNT,
    SERVER_ADDRESS,
    SERVER_PORT,
    OperationName,
    start_span,
)

logger = logging.getLogger(__name__)

try:
    from opentelemetry import context as otel_context
    from opentelemetry.trace import Span, StatusCode, set_span_in_context
    from opentelemetry.metrics import get_meter

    _tracing_library_available = True
except ModuleNotFoundError:
    otel_context = None  # type: ignore[assignment]
    set_span_in_context = None  # type: ignore[assignment]
    Span = None  # type: ignore[assignment,misc]
    StatusCode = None  # type: ignore[assignment,misc]
    get_meter = None  # type: ignore[assignment]
    _tracing_library_available = False

__all__ = ["VoiceLiveInstrumentor"]

_voicelive_traces_enabled: bool = False
_trace_voicelive_content: bool = False

_ITEM_BEARING_EVENTS = frozenset(
    {
        ServerEventType.CONVERSATION_ITEM_CREATED,
        ServerEventType.CONVERSATION_ITEM_RETRIEVED,
        ServerEventType.RESPONSE_OUTPUT_ITEM_ADDED,
        ServerEventType.RESPONSE_OUTPUT_ITEM_DONE,
    }
)

_SESSION_EVENT_TYPES = frozenset(
    {
        ServerEventType.SESSION_CREATED,
        ServerEventType.SESSION_UPDATED,
    }
)

_DELTA_SKIP_EVENT_TYPES = frozenset(
    {
        ServerEventType.RESPONSE_TEXT_DELTA,
        ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DELTA,
    }
)

_MCP_CALL_EVENT_TYPES = frozenset(
    {
        ServerEventType.RESPONSE_MCP_CALL_COMPLETED,
        ServerEventType.RESPONSE_MCP_CALL_FAILED,
    }
)

_MCP_LIST_TOOLS_EVENT_TYPES = frozenset(
    {
        ServerEventType.MCP_LIST_TOOLS_COMPLETED,
        ServerEventType.MCP_LIST_TOOLS_FAILED,
    }
)

# Metrics instruments
_operation_duration_histogram = None
_token_usage_histogram = None


class VoiceLiveInstrumentor:
    """Manages OpenTelemetry trace instrumentation for VoiceLive.

    This class enables or disables tracing for the VoiceLive SDK.
    Instrumentation is opt-in and controlled via the
    ``AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING`` environment variable,
    which must be set to ``"true"`` for ``.instrument()`` to take effect.

    Example usage::

        from azure.ai.voicelive.telemetry import VoiceLiveInstrumentor

        VoiceLiveInstrumentor().instrument()

    """

    def __init__(self) -> None:
        if not _tracing_library_available:
            raise ModuleNotFoundError(
                "OpenTelemetry is not installed. "
                "Please install it using 'pip install azure-core-tracing-opentelemetry'"
            )
        self._impl = _VoiceLiveInstrumentorPreview()

    def instrument(self, enable_content_recording: Optional[bool] = None) -> None:
        """Enable trace instrumentation for VoiceLive.

        Tracing is gated behind the ``AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING``
        environment variable. If it is not set to ``"true"``, this method is a no-op.

        :param enable_content_recording: Whether to record message content in spans.
            If ``None``, the value is read from
            ``OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT`` (preferred) or
            ``AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED`` (legacy).
            Defaults to ``False`` if neither is set.
        :type enable_content_recording: bool or None
        """
        env_gate = os.environ.get("AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING", "").lower()
        if env_gate != "true":
            logger.debug(
                "VoiceLive tracing not enabled. Set AZURE_EXPERIMENTAL_ENABLE_GENAI_TRACING=true to enable."
            )
            return
        self._impl.instrument(enable_content_recording)

    def uninstrument(self) -> None:
        """Remove trace instrumentation for VoiceLive."""
        self._impl.uninstrument()

    def is_instrumented(self) -> bool:
        """Check whether VoiceLive tracing is currently active.

        :return: ``True`` if instrumentation is active.
        :rtype: bool
        """
        return self._impl.is_instrumented()

    def is_content_recording_enabled(self) -> bool:
        """Check whether message content recording is enabled.

        :return: ``True`` if content recording is enabled.
        :rtype: bool
        """
        return self._impl.is_content_recording_enabled()


class _VoiceLiveInstrumentorPreview:
    """Internal implementation of VoiceLive instrumentation.

    Applies monkey-patching to ``_VoiceLiveConnectionManager`` and
    ``VoiceLiveConnection`` methods to inject OpenTelemetry spans around
    connection lifecycle and message send/receive operations.
    """

    @staticmethod
    def _str_to_bool(s: Optional[str]) -> bool:
        """Convert a string value to a boolean.

        :param s: The string to convert. Returns ``False`` for ``None``.
        :type s: str or None
        :return: ``True`` if *s* is the case-insensitive string ``"true"``.
        :rtype: bool
        """
        if s is None:
            return False
        return str(s).lower() == "true"

    def instrument(self, enable_content_recording: Optional[bool] = None) -> None:
        """Enable tracing by monkey-patching VoiceLive connection classes.

        :param enable_content_recording: Whether to capture full message payloads
            in span events. If ``None``, the value is resolved from environment
            variables.
        :type enable_content_recording: bool or None
        """
        if enable_content_recording is None:
            var_value_new = os.environ.get("OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT")
            var_value_old = os.environ.get("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED")
            var_value: Optional[str] = None

            if var_value_new and var_value_old and var_value_new != var_value_old:
                logger.error(
                    "Environment variables OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT "
                    "and AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED are both set and differ. "
                    "Content recording will be disabled. "
                    "Please set OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT only."
                )
                var_value = None
            elif var_value_new:
                var_value = var_value_new
            elif var_value_old:
                var_value = var_value_old

            enable_content_recording = self._str_to_bool(var_value)

        if not self.is_instrumented():
            self._instrument_voicelive(enable_content_recording)
        else:
            self._set_enable_content_recording(enable_content_recording)

    def uninstrument(self) -> None:
        """Remove tracing by restoring original methods on VoiceLive classes."""
        if self.is_instrumented():
            self._uninstrument_voicelive()

    def is_instrumented(self) -> bool:
        """Return ``True`` if VoiceLive tracing is currently active.

        :return: ``True`` if instrumentation is active.
        :rtype: bool
        """
        return _voicelive_traces_enabled

    def is_content_recording_enabled(self) -> bool:
        """Return ``True`` if message content recording is enabled.

        :return: ``True`` if content recording is enabled.
        :rtype: bool
        """
        return _trace_voicelive_content

    # ------------------------------------------------------------------ #
    #  Attribute / event helpers                                          #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _set_attributes(span: "AbstractSpan", *attrs: Tuple[str, Any]) -> None:
        """Set one or more key-value attributes on a span, skipping ``None`` values.

        :param span: The span to annotate.
        :type span: ~azure.core.tracing.AbstractSpan
        :param attrs: Attribute ``(key, value)`` tuples.
        :type attrs: tuple[str, Any]
        """
        for key, value in attrs:
            if value is not None:
                span.add_attribute(key, value)

    def record_error(self, span: "AbstractSpan", exc: BaseException) -> None:
        """Record an error on the span.

        Sets the span status to ``ERROR`` and adds the ``error.type`` attribute
        with the fully-qualified exception class name.

        :param span: The span to record the error on.
        :type span: ~azure.core.tracing.AbstractSpan
        :param exc: The exception that occurred.
        :type exc: BaseException
        """
        if isinstance(span.span_instance, Span):  # pyright: ignore[reportArgumentType]
            span.span_instance.set_status(
                StatusCode.ERROR,  # pyright: ignore[reportOptionalMemberAccess]
                description=str(exc),
            )
        module = getattr(exc, "__module__", "")
        module = module if module != "builtins" else ""
        error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
        self._set_attributes(span, (ERROR_TYPE, error_type), (ERROR_MESSAGE, str(exc)))

    @staticmethod
    def _start_connection_child_span(
        conn_self: Any,
        operation_name: OperationName,
        span_name: Optional[str] = None,
    ) -> Optional["AbstractSpan"]:
        """Start a child span under the connection span context when available.

        :param conn_self: The active ``VoiceLiveConnection`` instance.
        :type conn_self: any
        :param operation_name: Logical operation name for span attributes.
        :type operation_name: ~azure.ai.voicelive.telemetry._utils.OperationName
        :param span_name: Optional explicit span name override.
        :type span_name: str or None
        :return: The started span, or ``None`` if tracing is unavailable.
        :rtype: ~azure.core.tracing.AbstractSpan or None
        """
        parent_span = getattr(conn_self, "_telemetry_span", None)
        parent_token = None
        if parent_span is not None and set_span_in_context is not None and otel_context is not None:
            parent_ctx = set_span_in_context(parent_span.span_instance)
            parent_token = otel_context.attach(parent_ctx)

        try:
            return start_span(
                operation_name,
                server_address=getattr(conn_self, "_telemetry_server_address", None),
                port=getattr(conn_self, "_telemetry_port", None),
                model=getattr(conn_self, "_telemetry_model", None),
                span_name=span_name,
            )
        finally:
            if parent_token is not None:
                otel_context.detach(parent_token)  # pyright: ignore[reportOptionalMemberAccess]

    @staticmethod
    def _add_connection_context_attributes(span: "AbstractSpan", conn_self: Any) -> None:
        """Add common connection attributes present on send/recv/close spans.

        :param span: The active child span.
        :type span: ~azure.core.tracing.AbstractSpan
        :param conn_self: The active ``VoiceLiveConnection`` instance.
        :type conn_self: any
        """
        session_id = getattr(conn_self, "_telemetry_session_id", None)
        if session_id:
            span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)

        conv_id = getattr(conn_self, "_telemetry_conversation_id", None)
        if conv_id:
            span.add_attribute(GEN_AI_CONVERSATION_ID, conv_id)

    @staticmethod
    def _serialize_content_and_size(payload: Any) -> Tuple[Optional[str], Optional[int]]:
        """Serialize payload content and compute payload size.

        When content recording is disabled, content may be ``None`` while size is
        still computed from the serializable payload.

        :param payload: Event payload (dict or model instance).
        :type payload: any
        :return: A tuple ``(content_str, message_size)``.
        :rtype: tuple[str or None, int or None]
        """
        content_str = None
        if _trace_voicelive_content:
            try:
                if hasattr(payload, "as_dict"):
                    content_str = json.dumps(payload.as_dict(), default=str)
                elif isinstance(payload, dict):
                    content_str = json.dumps(payload, default=str)
            except (TypeError, ValueError):
                pass

        message_size = len(content_str) if content_str else None
        if message_size is None:
            try:
                if isinstance(payload, dict):
                    message_size = len(json.dumps(payload, default=str))
                elif hasattr(payload, "as_dict"):
                    message_size = len(json.dumps(payload.as_dict(), default=str))
            except (TypeError, ValueError):
                pass

        return content_str, message_size

    @staticmethod
    def _extract_session_audio_attributes(conn_self: Any, session: Any) -> None:
        """Extract input/output audio format and sampling rate from a session object.

        :param conn_self: The active ``VoiceLiveConnection`` instance.
        :type conn_self: any
        :param session: Session payload object from send/recv events.
        :type session: any
        """
        get = _VoiceLiveInstrumentorPreview._get_field
        connect_span = getattr(conn_self, "_telemetry_span", None)

        input_audio_format = get(session, "input_audio_format")
        if input_audio_format:
            input_fmt_str = str(input_audio_format)
            conn_self._telemetry_input_audio_format = input_fmt_str  # pylint: disable=protected-access
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_INPUT_AUDIO_FORMAT, input_fmt_str)

        input_sampling_rate = get(session, "input_audio_sampling_rate")
        if input_sampling_rate is not None and connect_span is not None:
            connect_span.add_attribute(GEN_AI_VOICE_INPUT_SAMPLE_RATE, input_sampling_rate)

        output_audio_format = get(session, "output_audio_format")
        if output_audio_format:
            output_fmt_str = str(output_audio_format)
            conn_self._telemetry_output_audio_format = output_fmt_str  # pylint: disable=protected-access
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT, output_fmt_str)

    def _add_send_event(
        self,
        span: "AbstractSpan",
        event_type: Optional[str],
        content: Optional[str],
    ) -> None:
        """Add a ``gen_ai.input.messages`` event to the span.

        :param span: The active span.
        :type span: ~azure.core.tracing.AbstractSpan
        :param event_type: The VoiceLive event type (e.g. ``"session.update"``).
        :type event_type: str or None
        :param content: Serialized event payload. Only attached when content
            recording is enabled.
        :type content: str or None
        """
        attrs: Dict[str, Any] = {GEN_AI_SYSTEM: AZ_AI_VOICELIVE_SYSTEM}
        if event_type:
            attrs["gen_ai.voice.event_type"] = event_type
        if _trace_voicelive_content and content:
            attrs[GEN_AI_EVENT_CONTENT] = content
        span.span_instance.add_event(name="gen_ai.input.messages", attributes=attrs)

    def _add_recv_event(
        self,
        span: "AbstractSpan",
        event_type: Optional[str],
        content: Optional[str],
        force_content: bool = False,
    ) -> None:
        """Add a ``gen_ai.output.messages`` event to the span.

        :param span: The active span.
        :type span: ~azure.core.tracing.AbstractSpan
        :param event_type: The VoiceLive event type (e.g. ``"response.done"``).
        :type event_type: str or None
        :param content: Serialized event payload. Only attached when content
            recording is enabled.
        :type content: str or None
        :param force_content: Whether to include content even when content
            recording is disabled.
        :type force_content: bool
        """
        attrs: Dict[str, Any] = {GEN_AI_SYSTEM: AZ_AI_VOICELIVE_SYSTEM}
        if event_type:
            attrs["gen_ai.voice.event_type"] = event_type
        if (_trace_voicelive_content or force_content) and content:
            attrs[GEN_AI_EVENT_CONTENT] = content
        span.span_instance.add_event(name="gen_ai.output.messages", attributes=attrs)

    @staticmethod
    def _extract_done_event_content(result: Any, event_type: str) -> Optional[str]:
        """Extract text/transcript payload from selected ``response.*.done`` events.

        Returns a compact JSON string suitable for ``gen_ai.event.content`` or
        ``None`` if no message/transcript content is available.

        :param result: The received server event.
        :type result: any
        :param event_type: The resolved event type string.
        :type event_type: str
        :return: JSON-serialized done content, if available.
        :rtype: str or None
        """
        get = _VoiceLiveInstrumentorPreview._get_field

        def _collect_text_or_transcript_from_item(item_obj: Any) -> list[Dict[str, Any]]:
            contents: list[Dict[str, Any]] = []
            if item_obj is None:
                return contents
            # function_call items carry payload in name/arguments, not content parts
            item_type = get(item_obj, "type")
            if item_type == "function_call":
                name = get(item_obj, "name")
                arguments = get(item_obj, "arguments")
                fc_payload: Dict[str, Any] = {}
                if name:
                    fc_payload["name"] = str(name)
                if arguments:
                    try:
                        fc_payload["arguments"] = json.loads(arguments)
                    except (ValueError, TypeError):
                        fc_payload["arguments"] = str(arguments)
                if fc_payload:
                    contents.append(fc_payload)
                return contents
            content_parts = get(item_obj, "content")
            if not content_parts:
                return contents
            for part in content_parts:
                text = get(part, "text")
                transcript = get(part, "transcript")
                part_payload: Dict[str, str] = {}
                if text:
                    part_payload["text"] = str(text)
                if transcript:
                    part_payload["transcript"] = str(transcript)
                if part_payload:
                    contents.append(part_payload)
            return contents

        done_content: Optional[str] = None

        if event_type == ServerEventType.RESPONSE_FUNCTION_CALL_ARGUMENTS_DONE:
            name = get(result, "name")
            arguments = get(result, "arguments")
            fc_payload: Dict[str, Any] = {}
            if name:
                fc_payload["name"] = str(name)
            if arguments:
                try:
                    fc_payload["arguments"] = json.loads(arguments)
                except (ValueError, TypeError):
                    fc_payload["arguments"] = str(arguments)
            if fc_payload:
                done_content = json.dumps(fc_payload, ensure_ascii=False)

        elif event_type == ServerEventType.RESPONSE_TEXT_DONE:
            text = get(result, "text")
            if text:
                done_content = json.dumps({"text": text}, ensure_ascii=False)

        elif event_type == ServerEventType.RESPONSE_AUDIO_TRANSCRIPT_DONE:
            transcript = get(result, "transcript")
            if transcript:
                done_content = json.dumps({"transcript": transcript}, ensure_ascii=False)

        elif event_type == ServerEventType.RESPONSE_CONTENT_PART_DONE:
            part = get(result, "part")
            if part:
                text = get(part, "text")
                transcript = get(part, "transcript")
                payload: Dict[str, Any] = {}
                if text:
                    payload["text"] = text
                if transcript:
                    payload["transcript"] = transcript
                if payload:
                    done_content = json.dumps(payload, ensure_ascii=False)

        elif event_type == ServerEventType.RESPONSE_OUTPUT_ITEM_DONE:
            item = get(result, "item")
            item_contents = _collect_text_or_transcript_from_item(item)
            if item_contents:
                done_content = json.dumps({"messages": item_contents}, ensure_ascii=False)

        elif event_type == ServerEventType.RESPONSE_DONE:
            response = get(result, "response")
            output_items = get(response, "output") if response is not None else None
            if output_items:
                messages: list[Dict[str, Any]] = []
                for output_item in output_items:
                    messages.extend(_collect_text_or_transcript_from_item(output_item))
                if messages:
                    done_content = json.dumps({"messages": messages}, ensure_ascii=False)

        return done_content

    # ------------------------------------------------------------------ #
    #  Tracing wrappers for connection lifecycle                          #
    # ------------------------------------------------------------------ #

    def _trace_connect(self, original_aenter: Callable) -> Callable:
        """Wrap ``_VoiceLiveConnectionManager.__aenter__``.

        :param original_aenter: The original ``__aenter__`` method to wrap.
        :type original_aenter: Callable
        :return: The wrapped method.
        :rtype: Callable
        """
        instrumentor = self

        @functools.wraps(original_aenter)
        async def wrapper(mgr_self, *args, **kwargs):  # pylint: disable=protected-access,too-many-locals
            span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
            if span_impl_type is None:
                return await original_aenter(mgr_self, *args, **kwargs)

            from urllib.parse import urlparse

            parsed = urlparse(mgr_self._endpoint)
            server_address = parsed.hostname
            port = parsed.port
            if port is None:
                scheme = (parsed.scheme or "").lower()
                if scheme in ("https", "wss"):
                    port = 443
                elif scheme in ("http", "ws"):
                    port = 80

            span = start_span(
                OperationName.CONNECT,
                server_address=server_address,
                port=port,
                model=getattr(mgr_self, "_VoiceLiveConnectionManager__model", None),
            )
            if span is None:
                return await original_aenter(mgr_self, *args, **kwargs)

            try:
                result = await original_aenter(mgr_self, *args, **kwargs)
                # Store span reference on the connection for later use
                result._telemetry_span = span
                result._telemetry_server_address = server_address
                result._telemetry_port = port
                result._telemetry_model = getattr(mgr_self, "_VoiceLiveConnectionManager__model", None)
                # Session-level telemetry counters
                result._telemetry_turn_count = 0
                result._telemetry_interruption_count = 0
                result._telemetry_audio_bytes_sent = 0
                result._telemetry_audio_bytes_received = 0
                result._telemetry_response_create_time = None
                result._telemetry_first_token_latency_recorded = False
                result._telemetry_connect_start_time = time.monotonic()

                # Extract agent config for agent attributes
                agent_config = getattr(mgr_self, "_VoiceLiveConnectionManager__agent_config", None)
                if agent_config:
                    agent_name = agent_config.get("agent_name")
                    if agent_name:
                        result._telemetry_agent_name = agent_name
                        span.add_attribute(GEN_AI_AGENT_NAME, agent_name)
                    conv_id = agent_config.get("conversation_id")
                    if conv_id:
                        result._telemetry_conversation_id = conv_id
                        span.add_attribute(GEN_AI_CONVERSATION_ID, conv_id)
                    agent_version = agent_config.get("agent_version")
                    if agent_version:
                        span.add_attribute(GEN_AI_AGENT_VERSION, agent_version)
                    project_name = agent_config.get("project_name")
                    if project_name:
                        span.add_attribute(GEN_AI_AGENT_PROJECT_NAME, project_name)

                return result
            except Exception as exc:
                instrumentor.record_error(span, exc)
                span.__exit__(type(exc), exc, exc.__traceback__)  # pyright: ignore[reportArgumentType]
                raise

        wrapper._original = original_aenter  # type: ignore[attr-defined]
        return wrapper

    def _trace_aexit(self, original_aexit: Callable) -> Callable:
        """Wrap ``_VoiceLiveConnectionManager.__aexit__``.

        :param original_aexit: The original ``__aexit__`` method to wrap.
        :type original_aexit: Callable
        :return: The wrapped method.
        :rtype: Callable
        """
        instrumentor = self

        @functools.wraps(original_aexit)
        async def wrapper(mgr_self, exc_type, exc, exc_tb):
            conn = getattr(mgr_self, "_VoiceLiveConnectionManager__connection", None)
            span = getattr(conn, "_telemetry_span", None) if conn else None

            await original_aexit(mgr_self, exc_type, exc, exc_tb)

            if span is not None:
                # Record session-level counters on the connect span
                turn_count = getattr(conn, "_telemetry_turn_count", 0)
                interruption_count = getattr(conn, "_telemetry_interruption_count", 0)
                audio_bytes_sent = getattr(conn, "_telemetry_audio_bytes_sent", 0)
                audio_bytes_received = getattr(conn, "_telemetry_audio_bytes_received", 0)
                if turn_count > 0:
                    span.add_attribute(GEN_AI_VOICE_TURN_COUNT, turn_count)
                if interruption_count > 0:
                    span.add_attribute(GEN_AI_VOICE_INTERRUPTION_COUNT, interruption_count)
                if audio_bytes_sent > 0:
                    span.add_attribute(GEN_AI_VOICE_AUDIO_BYTES_SENT, audio_bytes_sent)
                if audio_bytes_received > 0:
                    span.add_attribute(GEN_AI_VOICE_AUDIO_BYTES_RECEIVED, audio_bytes_received)

                # MCP session-level counters
                mcp_call_count = getattr(conn, "_telemetry_mcp_call_count", 0)
                mcp_list_tools_count = getattr(conn, "_telemetry_mcp_list_tools_count", 0)
                if mcp_call_count > 0:
                    span.add_attribute(GEN_AI_VOICE_MCP_CALL_COUNT, mcp_call_count)
                if mcp_list_tools_count > 0:
                    span.add_attribute(GEN_AI_VOICE_MCP_LIST_TOOLS_COUNT, mcp_list_tools_count)

                # Record duration metric
                connect_start = getattr(conn, "_telemetry_connect_start_time", None)
                if connect_start is not None:
                    duration = time.monotonic() - connect_start
                    instrumentor._record_operation_duration(
                        duration,
                        "connect",
                        server_address=getattr(conn, "_telemetry_server_address", None),
                        port=getattr(conn, "_telemetry_port", None),
                        model=getattr(conn, "_telemetry_model", None),
                        error_type=type(exc).__name__ if exc else None,
                    )

                if exc is not None:
                    instrumentor.record_error(span, exc)
                try:
                    span.__exit__(exc_type, exc, exc_tb)
                except Exception:  # pylint: disable=broad-except
                    pass

        wrapper._original = original_aexit  # type: ignore[attr-defined]
        return wrapper

    # ------------------------------------------------------------------ #
    #  Tracing wrappers for send / recv                                   #
    # ------------------------------------------------------------------ #

    def _trace_send(self, original_send: Callable) -> Callable:  # pylint: disable=too-many-statements
        """Wrap ``VoiceLiveConnection.send``.

        :param original_send: The original ``send`` method to wrap.
        :type original_send: Callable
        :return: The wrapped method.
        :rtype: Callable
        """
        instrumentor = self

        @functools.wraps(original_send)
        async def wrapper(conn_self, event, *args, **kwargs):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements,protected-access
            span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
            if span_impl_type is None:
                return await original_send(conn_self, event, *args, **kwargs)

            # Determine event type string
            event_type = None
            event_type = instrumentor._get_field(event, "type")
            content_str, message_size = instrumentor._serialize_content_and_size(event)

            # Track audio bytes for input_audio_buffer.append
            event_type_str = str(event_type) if event_type else ""
            if ClientEventType.INPUT_AUDIO_BUFFER_APPEND in event_type_str:
                audio_data = None
                if hasattr(event, "get"):
                    audio_data = event.get("audio")
                elif hasattr(event, "audio"):
                    audio_data = getattr(event, "audio", None)
                if audio_data and isinstance(audio_data, str):
                    try:
                        audio_bytes = len(base64.b64decode(audio_data))
                    except Exception:  # pylint: disable=broad-except
                        audio_bytes = len(audio_data)
                    current = getattr(conn_self, "_telemetry_audio_bytes_sent", 0)
                    conn_self._telemetry_audio_bytes_sent = current + audio_bytes

            # Track response.cancel for interruption count
            if ClientEventType.RESPONSE_CANCEL in event_type_str:
                current = getattr(conn_self, "_telemetry_interruption_count", 0)
                conn_self._telemetry_interruption_count = current + 1

            # Track response.create timestamp for first-token latency
            if ClientEventType.RESPONSE_CREATE in event_type_str:
                conn_self._telemetry_response_create_time = time.monotonic()
                conn_self._telemetry_first_token_latency_recorded = False

            # Extract audio format from session.update
            if ClientEventType.SESSION_UPDATE in event_type_str:
                instrumentor._extract_audio_format_from_send(conn_self, event)
                instrumentor._extract_session_config_from_send(conn_self, event)

            op_name = OperationName.SEND
            span_name = f"send {event_type}" if event_type else "send"

            # Ensure the send span is parented under the connect span,
            # even when called from a different asyncio task.
            span = instrumentor._start_connection_child_span(conn_self, op_name, span_name)

            if span is None:
                return await original_send(conn_self, event, *args, **kwargs)

            try:
                with span:
                    instrumentor._add_connection_context_attributes(span, conn_self)
                    if event_type:
                        span.add_attribute("gen_ai.voice.event_type", event_type)
                    if message_size is not None:
                        span.add_attribute(GEN_AI_VOICE_MESSAGE_SIZE, message_size)
                    # Extract call_id from send events (e.g. conversation.item.create with function_call_output)
                    instrumentor._extract_send_event_ids(conn_self, event, span)
                    instrumentor._add_send_event(span, event_type, content_str)
                    return await original_send(conn_self, event, *args, **kwargs)
            except Exception as exc:
                instrumentor.record_error(span, exc)
                raise

        wrapper._original = original_send  # type: ignore[attr-defined]
        return wrapper

    def _trace_recv(self, original_recv: Callable) -> Callable:  # pylint: disable=too-many-statements
        """Wrap ``VoiceLiveConnection.recv``.

        :param original_recv: The original ``recv`` method to wrap.
        :type original_recv: Callable
        :return: The wrapped method.
        :rtype: Callable
        """
        instrumentor = self

        @functools.wraps(original_recv)
        async def wrapper(conn_self, *args, **kwargs):  # pylint: disable=too-many-branches,too-many-locals,too-many-statements,protected-access
            span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
            if span_impl_type is None:
                return await original_recv(conn_self, *args, **kwargs)

            # Ensure the recv span is parented under the connect span,
            # even when called from a different asyncio task.
            span = instrumentor._start_connection_child_span(conn_self, OperationName.RECV)

            if span is None:
                return await original_recv(conn_self, *args, **kwargs)

            try:
                with span:
                    instrumentor._add_connection_context_attributes(span, conn_self)

                    result = await original_recv(conn_self, *args, **kwargs)
                    # Extract event type from the result
                    event_type = instrumentor._get_field(result, "type")
                    content_str, message_size = instrumentor._serialize_content_and_size(result)

                    event_type_str = str(event_type) if event_type else ""

                    # --- First-token latency ---
                    if event_type_str in (ServerEventType.RESPONSE_AUDIO_DELTA, ServerEventType.RESPONSE_TEXT_DELTA):
                        response_create_time = getattr(conn_self, "_telemetry_response_create_time", None)
                        already_recorded = getattr(conn_self, "_telemetry_first_token_latency_recorded", True)
                        if response_create_time is not None and not already_recorded:
                            latency_ms = (time.monotonic() - response_create_time) * 1000
                            span.add_attribute(GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS, round(latency_ms, 2))
                            # Also record on the parent connect span
                            connect_span = getattr(conn_self, "_telemetry_span", None)
                            if connect_span is not None:
                                connect_span.add_attribute(GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS, round(latency_ms, 2))
                            conn_self._telemetry_first_token_latency_recorded = True

                    # We intentionally do not track text/audio-transcript delta as
                    # normal recv events to keep telemetry volume lower, while still
                    # allowing text delta to set first-token latency above.
                    if event_type_str in _DELTA_SKIP_EVENT_TYPES:
                        return result

                    if event_type:
                        span.add_attribute("gen_ai.voice.event_type", event_type_str)
                        # Update span name to include event type (e.g. "recv session.created")
                        span.span_instance.update_name(f"recv {event_type_str}")

                    if message_size is not None:
                        span.add_attribute(GEN_AI_VOICE_MESSAGE_SIZE, message_size)

                    done_content = instrumentor._extract_done_event_content(result, event_type_str)
                    instrumentor._add_recv_event(
                        span,
                        event_type_str if event_type else None,
                        content_str or done_content,
                        force_content=done_content is not None,
                    )

                    # --- Extract response_id, call_id, conversation_id from top-level fields ---
                    instrumentor._extract_event_ids(conn_self, result, span)

                    # --- Session ID and audio format tracking ---
                    if event_type_str in _SESSION_EVENT_TYPES:
                        instrumentor._extract_session_id(conn_self, result)
                        instrumentor._extract_audio_format_from_recv(conn_self, result)
                        instrumentor._extract_agent_config_from_session(conn_self, result)

                    # --- Audio bytes received ---
                    if event_type_str == ServerEventType.RESPONSE_AUDIO_DELTA:
                        delta = None
                        if hasattr(result, "get"):
                            delta = result.get("delta")
                        elif hasattr(result, "delta"):
                            delta = getattr(result, "delta", None)
                        if delta and isinstance(delta, str):
                            try:
                                audio_bytes = len(base64.b64decode(delta))
                            except Exception:  # pylint: disable=broad-except
                                audio_bytes = len(delta)
                            current = getattr(conn_self, "_telemetry_audio_bytes_received", 0)
                            conn_self._telemetry_audio_bytes_received = current + audio_bytes

                    # --- Turn count ---
                    if event_type_str == ServerEventType.RESPONSE_DONE:
                        current = getattr(conn_self, "_telemetry_turn_count", 0)
                        conn_self._telemetry_turn_count = current + 1
                        # Extract response metadata
                        instrumentor._extract_response_done(conn_self, result, span)

                    # --- Rate limit / error events ---
                    if event_type_str in (ServerEventType.ERROR, "rate_limits.updated"):
                        instrumentor._add_rate_limit_event(span, event_type_str, result)

                    # --- MCP call count ---
                    if event_type_str in _MCP_CALL_EVENT_TYPES:
                        current = getattr(conn_self, "_telemetry_mcp_call_count", 0)
                        conn_self._telemetry_mcp_call_count = current + 1

                    # --- MCP list tools count ---
                    if event_type_str in _MCP_LIST_TOOLS_EVENT_TYPES:
                        current = getattr(conn_self, "_telemetry_mcp_list_tools_count", 0)
                        conn_self._telemetry_mcp_list_tools_count = current + 1

                    # Capture token usage if present on the event
                    usage = instrumentor._get_field(result, "usage")

                    if usage:
                        input_tokens = getattr(usage, "input_tokens", None) or (
                            usage.get("input_tokens") if isinstance(usage, dict) else None
                        )
                        output_tokens = getattr(usage, "output_tokens", None) or (
                            usage.get("output_tokens") if isinstance(usage, dict) else None
                        )
                        if input_tokens is not None:
                            span.add_attribute(GEN_AI_USAGE_INPUT_TOKENS, input_tokens)
                            instrumentor._record_token_usage(
                                input_tokens, "input", "recv",
                                server_address=getattr(conn_self, "_telemetry_server_address", None),
                                model=getattr(conn_self, "_telemetry_model", None),
                            )
                        if output_tokens is not None:
                            span.add_attribute(GEN_AI_USAGE_OUTPUT_TOKENS, output_tokens)
                            instrumentor._record_token_usage(
                                output_tokens, "output", "recv",
                                server_address=getattr(conn_self, "_telemetry_server_address", None),
                                model=getattr(conn_self, "_telemetry_model", None),
                            )

                    return result
            except Exception as exc:
                instrumentor.record_error(span, exc)
                raise

        wrapper._original = original_recv  # type: ignore[attr-defined]
        return wrapper

    def _trace_close(self, original_close: Callable) -> Callable:
        """Wrap ``VoiceLiveConnection.close``.

        :param original_close: The original ``close`` method to wrap.
        :type original_close: Callable
        :return: The wrapped method.
        :rtype: Callable
        """
        instrumentor = self

        @functools.wraps(original_close)
        async def wrapper(conn_self, *args, **kwargs):
            span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
            if span_impl_type is None:
                return await original_close(conn_self, *args, **kwargs)

            # Ensure the close span is parented under the connect span,
            # even when called from a different asyncio task.
            span = instrumentor._start_connection_child_span(conn_self, OperationName.CLOSE)

            if span is None:
                return await original_close(conn_self, *args, **kwargs)

            try:
                with span:
                    instrumentor._add_connection_context_attributes(span, conn_self)
                    return await original_close(conn_self, *args, **kwargs)
            except Exception as exc:
                instrumentor.record_error(span, exc)
                raise

        wrapper._original = original_close  # type: ignore[attr-defined]
        return wrapper

    # ------------------------------------------------------------------ #
    #  Session metadata extraction helpers                                #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_session_id(conn_self: Any, result: Any) -> None:
        """Extract session ID from a session.created/session.updated event and
        store it on the connection object. Also sets it on the parent connect span.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param result: The received event object.
        :type result: any
        """
        get = _VoiceLiveInstrumentorPreview._get_field
        session = get(result, "session")

        if session is not None:
            session_id = get(session, "id")

            if session_id:
                conn_self._telemetry_session_id = session_id  # pylint: disable=protected-access
                connect_span = getattr(conn_self, "_telemetry_span", None)
                if connect_span is not None:
                    connect_span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)

    @staticmethod
    def _extract_agent_config_from_session(conn_self: Any, result: Any) -> None:
        """Extract agent_id and thread_id from the ``session.agent`` field in
        a ``session.created`` / ``session.updated`` event.

        The server-side ``AgentConfig`` object lives inside ``session.agent``
        and carries ``agent_id`` and ``thread_id``.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param result: The received event object.
        :type result: any
        """
        get = _VoiceLiveInstrumentorPreview._get_field
        session = get(result, "session")
        if session is None:
            return

        agent = get(session, "agent")
        if agent is None:
            return

        connect_span = getattr(conn_self, "_telemetry_span", None)

        agent_id = get(agent, "agent_id")
        if agent_id and connect_span is not None:
            connect_span.add_attribute(GEN_AI_AGENT_ID, agent_id)

        thread_id = get(agent, "thread_id")
        if thread_id and connect_span is not None:
            connect_span.add_attribute(GEN_AI_AGENT_THREAD_ID, thread_id)

    @staticmethod
    def _extract_audio_format_from_send(conn_self: Any, event: Any) -> None:  # pylint: disable=too-many-branches
        """Extract audio format, codec, and sample rate from a session.update
        send event and store on the connection. Also sets on the parent connect span.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param event: The event being sent.
        :type event: any
        """
        session = _VoiceLiveInstrumentorPreview._get_field(event, "session")

        if session is None:
            return
        _VoiceLiveInstrumentorPreview._extract_session_audio_attributes(conn_self, session)

    @staticmethod
    def _extract_audio_format_from_recv(conn_self: Any, result: Any) -> None:  # pylint: disable=too-many-branches
        """Extract audio format and sample rate from a session.created or
        session.updated server event. The server response is authoritative and
        may include values the client did not explicitly set (e.g. defaults).

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param result: The received server event.
        :type result: any
        """
        session = _VoiceLiveInstrumentorPreview._get_field(result, "session")

        if session is None:
            return
        _VoiceLiveInstrumentorPreview._extract_session_audio_attributes(conn_self, session)

    @staticmethod
    def _extract_session_config_from_send(conn_self: Any, event: Any) -> None:  # pylint: disable=too-many-branches
        """Extract system instructions, tools, temperature, and max_output_tokens
        from a session.update event and set on the connect span.

        Also emits a ``gen_ai.system.instructions`` span event when content
        recording is enabled and instructions are present.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param event: The session.update event being sent.
        :type event: any
        """
        get = _VoiceLiveInstrumentorPreview._get_field
        session = get(event, "session")

        if session is None:
            return

        connect_span = getattr(conn_self, "_telemetry_span", None)

        # System instructions
        instructions = get(session, "instructions")
        if instructions and connect_span is not None:
            connect_span.add_attribute(GEN_AI_SYSTEM_MESSAGE, instructions)
            # Emit system instructions event when content recording is enabled
            if _trace_voicelive_content:
                event_attrs: Dict[str, Any] = {GEN_AI_PROVIDER_NAME: GEN_AI_PROVIDER_VALUE}
                event_attrs[GEN_AI_EVENT_CONTENT] = json.dumps(
                    [{"role": "system", "content": instructions}], ensure_ascii=False
                )
                connect_span.span_instance.add_event(
                    name=GEN_AI_SYSTEM_INSTRUCTION_EVENT, attributes=event_attrs
                )

        # Temperature
        temperature = get(session, "temperature")
        if temperature is not None and connect_span is not None:
            connect_span.add_attribute(GEN_AI_REQUEST_TEMPERATURE, str(temperature))

        # Max output tokens
        max_output_tokens = get(session, "max_response_output_tokens")
        if max_output_tokens is not None and connect_span is not None:
            connect_span.add_attribute(GEN_AI_REQUEST_MAX_OUTPUT_TOKENS, max_output_tokens)

        # Tools
        tools = get(session, "tools")
        if tools and connect_span is not None:
            try:
                if isinstance(tools, list):
                    tools_json = json.dumps(
                        [t if isinstance(t, dict) else (t.as_dict() if hasattr(t, "as_dict") else str(t))
                         for t in tools],
                        default=str, ensure_ascii=False,
                    )
                else:
                    tools_json = str(tools)
                connect_span.add_attribute(GEN_AI_REQUEST_TOOLS, tools_json)
            except (TypeError, ValueError):
                pass

    @staticmethod
    def _get_field(obj: Any, field: str) -> Any:
        """Get a field from an object or dict.

        :param obj: The object or dict.
        :type obj: any
        :param field: The field name.
        :type field: str
        :return: The field value, or None.
        :rtype: any
        """
        if hasattr(obj, "get"):
            return obj.get(field)
        return getattr(obj, field, None)

    @staticmethod
    def _extract_event_ids(conn_self: Any, result: Any, span: "AbstractSpan") -> None:  # pylint: disable=too-many-branches,too-many-locals
        """Extract IDs, MCP fields, and agent fields from any recv event.

        Extracts ``response_id``, ``call_id``, ``item_id``, ``previous_item_id``,
        ``output_index`` from top-level fields, and ``conversation_id``,
        ``call_id``, ``server_label``, ``name``, ``approval_request_id``,
        ``approve``, and ``id`` from nested ``response`` / ``item`` objects.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param result: The received event object.
        :type result: any
        :param span: The current recv span.
        :type span: ~azure.core.tracing.AbstractSpan
        """
        get = _VoiceLiveInstrumentorPreview._get_field

        # response_id – present on most response.* events at the top level
        response_id = get(result, "response_id")
        if response_id:
            span.add_attribute(GEN_AI_RESPONSE_ID, response_id)

        # call_id – present on function_call_arguments.delta/done, mcp_call events
        call_id = get(result, "call_id")
        if call_id:
            span.add_attribute(GEN_AI_VOICE_CALL_ID, call_id)

        # item_id – present on output_item, content_part, function_call events
        item_id = get(result, "item_id")
        if item_id:
            span.add_attribute(GEN_AI_VOICE_ITEM_ID, item_id)

        # previous_item_id – present on conversation.item.created
        previous_item_id = get(result, "previous_item_id")
        if previous_item_id:
            span.add_attribute(GEN_AI_VOICE_PREVIOUS_ITEM_ID, previous_item_id)

        # output_index – present on MCP call events and response output/content events
        output_index = get(result, "output_index")
        if output_index is not None:
            span.add_attribute(GEN_AI_VOICE_OUTPUT_INDEX, output_index)

        # conversation_id is NOT a top-level field on most events; it lives
        # inside the nested ``response`` object on response.done/created events.
        response_obj = get(result, "response")
        if response_obj:
            if not response_id:
                nested_resp_id = get(response_obj, "id")
                if nested_resp_id:
                    span.add_attribute(GEN_AI_RESPONSE_ID, nested_resp_id)
            nested_conv_id = get(response_obj, "conversation_id")
            if nested_conv_id:
                conn_self._telemetry_conversation_id = nested_conv_id  # pylint: disable=protected-access
                span.add_attribute(GEN_AI_CONVERSATION_ID, nested_conv_id)

        # Nested item – only extract from events known to carry a ResponseItem.
        # This guards against future events reusing the ``item`` field name
        # for something semantically different.
        event_type = str(get(result, "type") or "")
        if event_type in _ITEM_BEARING_EVENTS:
            item_obj = get(result, "item")
            if item_obj:
                # item.id → item_id (if not already set from top-level)
                if not item_id:
                    nested_item_id = get(item_obj, "id")
                    if nested_item_id:
                        span.add_attribute(GEN_AI_VOICE_ITEM_ID, nested_item_id)

                # item.call_id → call_id (function_call / function_call_output)
                if not call_id:
                    nested_call_id = get(item_obj, "call_id")
                    if nested_call_id:
                        span.add_attribute(GEN_AI_VOICE_CALL_ID, nested_call_id)

                # MCP fields from nested item (ResponseMCPCallItem, ResponseMCPApprovalRequestItem, etc.)
                server_label = get(item_obj, "server_label")
                if server_label:
                    span.add_attribute(GEN_AI_VOICE_MCP_SERVER_LABEL, server_label)

                tool_name = get(item_obj, "name")
                item_type = get(item_obj, "type")
                # Only set tool_name for MCP/function_call item types (not message items)
                if tool_name and item_type and str(item_type) not in ("message",):
                    span.add_attribute(GEN_AI_VOICE_MCP_TOOL_NAME, tool_name)

                approval_request_id = get(item_obj, "approval_request_id")
                if approval_request_id:
                    span.add_attribute(GEN_AI_VOICE_MCP_APPROVAL_REQUEST_ID, approval_request_id)

                approve = get(item_obj, "approve")
                if approve is not None:
                    span.add_attribute(GEN_AI_VOICE_MCP_APPROVE, approve)

    @staticmethod
    def _extract_send_event_ids(conn_self: Any, event: Any, span: "AbstractSpan") -> None:  # pylint: disable=unused-argument
        """Extract call_id and response_id from send events.

        For ``conversation.item.create`` events, the nested ``item`` may carry
        a ``call_id`` (for function_call_output items). For ``response.cancel``
        events, ``response_id`` may be present.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param event: The client event being sent.
        :type event: any
        :param span: The current send span.
        :type span: ~azure.core.tracing.AbstractSpan
        """
        get = _VoiceLiveInstrumentorPreview._get_field

        # response_id on response.cancel
        response_id = get(event, "response_id")
        if response_id:
            span.add_attribute(GEN_AI_RESPONSE_ID, response_id)

        # call_id from nested item (conversation.item.create with function_call_output)
        item = get(event, "item")
        if item:
            call_id = get(item, "call_id")
            if call_id:
                span.add_attribute(GEN_AI_VOICE_CALL_ID, call_id)

            # MCP approval response: approval_request_id and approve
            approval_request_id = get(item, "approval_request_id")
            if approval_request_id:
                span.add_attribute(GEN_AI_VOICE_MCP_APPROVAL_REQUEST_ID, approval_request_id)
            approve = get(item, "approve")
            if approve is not None:
                span.add_attribute(GEN_AI_VOICE_MCP_APPROVE, approve)

        # previous_item_id on conversation.item.create
        previous_item_id = get(event, "previous_item_id")
        if previous_item_id:
            span.add_attribute(GEN_AI_VOICE_PREVIOUS_ITEM_ID, previous_item_id)

    @staticmethod
    def _extract_response_done(conn_self: Any, result: Any, span: "AbstractSpan") -> None:  # pylint: disable=too-many-branches
        """Extract response metadata from a response.done event.

        Sets ``gen_ai.response.id``, ``gen_ai.conversation.id``, and
        ``gen_ai.response.finish_reasons`` on both the recv span and the
        parent connect span.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param result: The received response.done event object.
        :type result: any
        :param span: The current recv span.
        :type span: ~azure.core.tracing.AbstractSpan
        """
        response = None
        if hasattr(result, "get"):
            response = result.get("response")
        elif hasattr(result, "response"):
            response = getattr(result, "response", None)

        if response is None:
            return

        connect_span = getattr(conn_self, "_telemetry_span", None)

        # Response ID
        response_id = None
        if hasattr(response, "get"):
            response_id = response.get("id")
        elif hasattr(response, "id"):
            response_id = getattr(response, "id", None)
        if response_id:
            span.add_attribute(GEN_AI_RESPONSE_ID, response_id)
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_RESPONSE_ID, response_id)

        # Conversation ID from response
        conv_id = None
        if hasattr(response, "get"):
            conv_id = response.get("conversation_id")
        elif hasattr(response, "conversation_id"):
            conv_id = getattr(response, "conversation_id", None)
        if conv_id:
            conn_self._telemetry_conversation_id = conv_id  # pylint: disable=protected-access
            span.add_attribute(GEN_AI_CONVERSATION_ID, conv_id)
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_CONVERSATION_ID, conv_id)

        # Finish reason / status
        status = None
        if hasattr(response, "get"):
            status = response.get("status")
        elif hasattr(response, "status"):
            status = getattr(response, "status", None)
        if status:
            status_str = str(status)
            span.add_attribute(GEN_AI_RESPONSE_FINISH_REASONS, json.dumps([status_str]))
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_RESPONSE_FINISH_REASONS, json.dumps([status_str]))

    # ------------------------------------------------------------------ #
    #  Metrics helpers                                                    #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _initialize_metrics() -> None:
        """Initialize OpenTelemetry metrics instruments."""
        global _operation_duration_histogram, _token_usage_histogram  # pylint: disable=global-statement
        if not _tracing_library_available or get_meter is None:
            return
        try:
            meter = get_meter(__name__)
            _operation_duration_histogram = meter.create_histogram(
                name=GEN_AI_CLIENT_OPERATION_DURATION,
                description="Duration of GenAI VoiceLive operations",
                unit="s",
            )
            _token_usage_histogram = meter.create_histogram(
                name=GEN_AI_CLIENT_TOKEN_USAGE,
                description="Token usage for GenAI VoiceLive operations",
                unit="token",
            )
        except Exception:  # pylint: disable=broad-except
            logger.debug("Failed to initialize VoiceLive metrics", exc_info=True)

    @staticmethod
    def _record_operation_duration(  # pylint: disable=too-many-arguments
        duration: float,
        operation_name: str,
        server_address: Optional[str] = None,
        port: Optional[int] = None,
        model: Optional[str] = None,
        error_type: Optional[str] = None,
    ) -> None:
        """Record an operation duration metric.

        :param duration: Duration in seconds.
        :type duration: float
        :param operation_name: The operation name.
        :type operation_name: str
        :param server_address: Server hostname.
        :type server_address: str or None
        :param port: Server port.
        :type port: int or None
        :param model: Model identifier.
        :type model: str or None
        :param error_type: Error type if the operation failed.
        :type error_type: str or None
        """
        if not _operation_duration_histogram:
            return
        attributes: Dict[str, Any] = {
            GEN_AI_OPERATION_NAME: operation_name,
            GEN_AI_PROVIDER_NAME: GEN_AI_PROVIDER_VALUE,
        }
        if server_address:
            attributes[SERVER_ADDRESS] = server_address
        if port is not None:
            attributes[SERVER_PORT] = str(port)
        if model:
            attributes[GEN_AI_REQUEST_MODEL] = model
        if error_type:
            attributes[ERROR_TYPE] = error_type
        try:
            _operation_duration_histogram.record(duration, attributes)
        except Exception:  # pylint: disable=broad-except
            logger.debug("Failed to record operation duration", exc_info=True)

    @staticmethod
    def _record_token_usage(
        token_count: int,
        token_type: str,
        operation_name: str,
        server_address: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        """Record a token usage metric.

        :param token_count: Number of tokens.
        :type token_count: int
        :param token_type: Token type (``"input"`` or ``"output"``).
        :type token_type: str
        :param operation_name: The operation name.
        :type operation_name: str
        :param server_address: Server hostname.
        :type server_address: str or None
        :param model: Model identifier.
        :type model: str or None
        """
        if not _token_usage_histogram:
            return
        attributes: Dict[str, Any] = {
            GEN_AI_OPERATION_NAME: operation_name,
            GEN_AI_PROVIDER_NAME: GEN_AI_PROVIDER_VALUE,
            "gen_ai.token.type": token_type,
        }
        if server_address:
            attributes[SERVER_ADDRESS] = server_address
        if model:
            attributes[GEN_AI_REQUEST_MODEL] = model
        try:
            _token_usage_histogram.record(token_count, attributes)
        except Exception:  # pylint: disable=broad-except
            logger.debug("Failed to record token usage", exc_info=True)

    @staticmethod
    def _add_rate_limit_event(span: "AbstractSpan", event_type: str, result: Any) -> None:  # pylint: disable=too-many-branches
        """Add a span event for rate limit or error events from the server.

        :param span: The active span.
        :type span: ~azure.core.tracing.AbstractSpan
        :param event_type: The event type string (``"error"`` or ``"rate_limits.updated"``).
        :type event_type: str
        :param result: The received event object.
        :type result: any
        """
        attrs: Dict[str, Any] = {GEN_AI_SYSTEM: AZ_AI_VOICELIVE_SYSTEM, "gen_ai.voice.event_type": event_type}

        if event_type == "error":
            error_msg = None
            error_code = None
            error_obj = None

            if hasattr(result, "get"):
                error_obj = result.get("error")
            elif hasattr(result, "error"):
                error_obj = getattr(result, "error", None)

            if error_obj:
                if hasattr(error_obj, "get"):
                    error_msg = error_obj.get("message")
                    error_code = error_obj.get("code")
                elif hasattr(error_obj, "message"):
                    error_msg = getattr(error_obj, "message", None)
                    error_code = getattr(error_obj, "code", None)

            if error_code:
                attrs["error.code"] = str(error_code)
            if error_msg:
                attrs["error.message"] = str(error_msg)

        elif event_type == "rate_limits.updated":
            rate_limits = None
            if hasattr(result, "get"):
                rate_limits = result.get("rate_limits")
            elif hasattr(result, "rate_limits"):
                rate_limits = getattr(result, "rate_limits", None)

            if rate_limits:
                try:
                    if isinstance(rate_limits, (list, tuple)):
                        attrs["gen_ai.voice.rate_limits"] = json.dumps(
                            [rl if isinstance(rl, dict) else (rl.as_dict() if hasattr(rl, "as_dict") else str(rl))
                             for rl in rate_limits],
                            default=str,
                        )
                    else:
                        attrs["gen_ai.voice.rate_limits"] = str(rate_limits)
                except (TypeError, ValueError):
                    pass

        span.span_instance.add_event(name=f"gen_ai.voice.{event_type}", attributes=attrs)

    # ------------------------------------------------------------------ #
    #  Instrument / Uninstrument core logic                               #
    # ------------------------------------------------------------------ #

    def _voicelive_apis(self):
        """Return the list of (module, class, method, wrapper_factory) tuples to instrument.

        :return: A list of four-element tuples ``(module_name, class_name,
            method_name, wrapper_factory)`` describing each method to monkey-patch.
        :rtype: list[tuple[str, str, str, Callable]]
        """
        return [
            (
                "azure.ai.voicelive.aio._patch",
                "_VoiceLiveConnectionManager",
                "__aenter__",
                self._trace_connect,
            ),
            (
                "azure.ai.voicelive.aio._patch",
                "_VoiceLiveConnectionManager",
                "__aexit__",
                self._trace_aexit,
            ),
            (
                "azure.ai.voicelive.aio._patch",
                "VoiceLiveConnection",
                "send",
                self._trace_send,
            ),
            (
                "azure.ai.voicelive.aio._patch",
                "VoiceLiveConnection",
                "recv",
                self._trace_recv,
            ),
            (
                "azure.ai.voicelive.aio._patch",
                "VoiceLiveConnection",
                "close",
                self._trace_close,
            ),
        ]

    def _instrument_voicelive(self, enable_content_recording: bool = False) -> None:
        """Apply monkey-patches to VoiceLive classes to enable tracing.

        Iterates through the API list returned by :meth:`_voicelive_apis`,
        imports each target module, and replaces the original method with a
        tracing wrapper. The original method is stored on the wrapper via the
        ``_original`` attribute so it can be restored by
        :meth:`_uninstrument_voicelive`.

        :param enable_content_recording: Whether to capture full message content
            in span events.
        :type enable_content_recording: bool
        :raises RuntimeError: If tracing is already enabled.
        """
        global _voicelive_traces_enabled, _trace_voicelive_content  # pylint: disable=global-statement
        if _voicelive_traces_enabled:
            raise RuntimeError("VoiceLive tracing is already enabled")

        _voicelive_traces_enabled = True
        _trace_voicelive_content = enable_content_recording

        # Initialize metrics instruments
        self._initialize_metrics()

        for module_name, class_name, method_name, wrapper_factory in self._voicelive_apis():
            try:
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                original = getattr(cls, method_name)
                if not hasattr(original, "_original"):
                    setattr(cls, method_name, wrapper_factory(original))
            except (AttributeError, ImportError) as exc:
                logger.warning(
                    "Could not instrument %s.%s.%s: %s",
                    module_name,
                    class_name,
                    method_name,
                    exc,
                )

    def _uninstrument_voicelive(self) -> None:
        """Restore original methods on VoiceLive classes, removing tracing wrappers.

        Each patched method is reverted to its ``_original`` reference and the
        global tracing flags are reset.
        """
        global _voicelive_traces_enabled, _trace_voicelive_content  # pylint: disable=global-statement
        _trace_voicelive_content = False

        for module_name, class_name, method_name, _ in self._voicelive_apis():
            try:
                module = importlib.import_module(module_name)
                cls = getattr(module, class_name)
                current = getattr(cls, method_name)
                if hasattr(current, "_original"):
                    setattr(cls, method_name, current._original)  # pylint: disable=protected-access
            except (AttributeError, ImportError) as exc:
                logger.warning(
                    "Could not uninstrument %s.%s.%s: %s",
                    module_name,
                    class_name,
                    method_name,
                    exc,
                )

        _voicelive_traces_enabled = False

    def _set_enable_content_recording(self, enable_content_recording: bool = False) -> None:
        """Update the content recording flag without re-instrumenting.

        :param enable_content_recording: Whether to capture full message content.
        :type enable_content_recording: bool
        """
        global _trace_voicelive_content  # pylint: disable=global-statement
        _trace_voicelive_content = enable_content_recording
