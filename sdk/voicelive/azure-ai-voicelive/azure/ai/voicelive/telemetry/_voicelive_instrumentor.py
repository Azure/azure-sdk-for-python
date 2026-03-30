# pylint: disable=line-too-long,useless-suppression,protected-access,too-many-statements
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
    GEN_AI_AGENT_NAME,
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
    GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS,
    GEN_AI_VOICE_INPUT_AUDIO_FORMAT,
    GEN_AI_VOICE_INPUT_SAMPLE_RATE,
    GEN_AI_VOICE_INTERRUPTION_COUNT,
    GEN_AI_VOICE_MESSAGE_SIZE,
    GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT,
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
    ) -> None:
        """Add a ``gen_ai.output.messages`` event to the span.

        :param span: The active span.
        :type span: ~azure.core.tracing.AbstractSpan
        :param event_type: The VoiceLive event type (e.g. ``"response.done"``).
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
        span.span_instance.add_event(name="gen_ai.output.messages", attributes=attrs)

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
        async def wrapper(mgr_self, *args, **kwargs):  # pylint: disable=protected-access
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
            content_str = None
            if hasattr(event, "get"):
                event_type = event.get("type")
            elif hasattr(event, "type"):
                event_type = getattr(event, "type", None)

            # Build content for content recording
            if _trace_voicelive_content:
                try:
                    if hasattr(event, "as_dict"):
                        content_str = json.dumps(event.as_dict(), default=str)
                    elif isinstance(event, dict):
                        content_str = json.dumps(event, default=str)
                except (TypeError, ValueError):
                    pass

            # Compute message size
            message_size = len(content_str) if content_str else None
            if message_size is None:
                try:
                    if isinstance(event, dict):
                        message_size = len(json.dumps(event, default=str))
                    elif hasattr(event, "as_dict"):
                        message_size = len(json.dumps(event.as_dict(), default=str))
                except (TypeError, ValueError):
                    pass

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
            parent_span = getattr(conn_self, "_telemetry_span", None)
            parent_token = None
            if parent_span is not None and set_span_in_context is not None and otel_context is not None:
                parent_ctx = set_span_in_context(parent_span.span_instance)
                parent_token = otel_context.attach(parent_ctx)

            try:
                span = start_span(
                    op_name,
                    server_address=getattr(conn_self, "_telemetry_server_address", None),
                    port=getattr(conn_self, "_telemetry_port", None),
                    model=getattr(conn_self, "_telemetry_model", None),
                    span_name=span_name,
                )
            finally:
                if parent_token is not None:
                    otel_context.detach(parent_token)  # pyright: ignore[reportOptionalMemberAccess]

            if span is None:
                return await original_send(conn_self, event, *args, **kwargs)

            try:
                with span:
                    # Add session_id if available
                    session_id = getattr(conn_self, "_telemetry_session_id", None)
                    if session_id:
                        span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)
                    # Add conversation_id if available
                    conv_id = getattr(conn_self, "_telemetry_conversation_id", None)
                    if conv_id:
                        span.add_attribute(GEN_AI_CONVERSATION_ID, conv_id)
                    if event_type:
                        span.add_attribute("gen_ai.voice.event_type", event_type)
                    if message_size is not None:
                        span.add_attribute(GEN_AI_VOICE_MESSAGE_SIZE, message_size)
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
            parent_span = getattr(conn_self, "_telemetry_span", None)
            parent_token = None
            if parent_span is not None and set_span_in_context is not None and otel_context is not None:
                parent_ctx = set_span_in_context(parent_span.span_instance)
                parent_token = otel_context.attach(parent_ctx)

            try:
                span = start_span(
                    OperationName.RECV,
                    server_address=getattr(conn_self, "_telemetry_server_address", None),
                    port=getattr(conn_self, "_telemetry_port", None),
                    model=getattr(conn_self, "_telemetry_model", None),
                )
            finally:
                if parent_token is not None:
                    otel_context.detach(parent_token)  # pyright: ignore[reportOptionalMemberAccess]

            if span is None:
                return await original_recv(conn_self, *args, **kwargs)

            try:
                with span:
                    # Add session_id if available
                    session_id = getattr(conn_self, "_telemetry_session_id", None)
                    if session_id:
                        span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)
                    # Add conversation_id if available
                    conv_id = getattr(conn_self, "_telemetry_conversation_id", None)
                    if conv_id:
                        span.add_attribute(GEN_AI_CONVERSATION_ID, conv_id)

                    result = await original_recv(conn_self, *args, **kwargs)
                    # Extract event type from the result
                    event_type = None
                    content_str = None
                    if hasattr(result, "get"):
                        event_type = result.get("type")
                    elif hasattr(result, "type"):
                        event_type = getattr(result, "type", None)

                    event_type_str = str(event_type) if event_type else ""

                    if event_type:
                        span.add_attribute("gen_ai.voice.event_type", event_type_str)
                        # Update span name to include event type (e.g. "recv session.created")
                        span.span_instance.update_name(f"recv {event_type_str}")

                    # Compute and record message size
                    message_size = None
                    if _trace_voicelive_content:
                        try:
                            if hasattr(result, "as_dict"):
                                content_str = json.dumps(result.as_dict(), default=str)
                            elif isinstance(result, dict):
                                content_str = json.dumps(result, default=str)
                        except (TypeError, ValueError):
                            pass
                        if content_str:
                            message_size = len(content_str)
                    if message_size is None:
                        try:
                            if isinstance(result, dict):
                                message_size = len(json.dumps(result, default=str))
                            elif hasattr(result, "as_dict"):
                                message_size = len(json.dumps(result.as_dict(), default=str))
                        except (TypeError, ValueError):
                            pass
                    if message_size is not None:
                        span.add_attribute(GEN_AI_VOICE_MESSAGE_SIZE, message_size)

                    instrumentor._add_recv_event(span, event_type_str if event_type else None, content_str)

                    # --- Session ID and audio format tracking ---
                    if event_type_str in (ServerEventType.SESSION_CREATED, ServerEventType.SESSION_UPDATED):
                        instrumentor._extract_session_id(conn_self, result)
                        instrumentor._extract_audio_format_from_recv(conn_self, result)

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

                    # Capture token usage if present on the event
                    usage = None
                    if hasattr(result, "get"):
                        usage = result.get("usage")
                    elif hasattr(result, "usage"):
                        usage = getattr(result, "usage", None)

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
            parent_span = getattr(conn_self, "_telemetry_span", None)
            parent_token = None
            if parent_span is not None and set_span_in_context is not None and otel_context is not None:
                parent_ctx = set_span_in_context(parent_span.span_instance)
                parent_token = otel_context.attach(parent_ctx)

            try:
                span = start_span(
                    OperationName.CLOSE,
                    server_address=getattr(conn_self, "_telemetry_server_address", None),
                    port=getattr(conn_self, "_telemetry_port", None),
                )
            finally:
                if parent_token is not None:
                    otel_context.detach(parent_token)  # pyright: ignore[reportOptionalMemberAccess]

            if span is None:
                return await original_close(conn_self, *args, **kwargs)

            try:
                with span:
                    # Add session_id if available
                    session_id = getattr(conn_self, "_telemetry_session_id", None)
                    if session_id:
                        span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)
                    # Add conversation_id if available
                    conv_id = getattr(conn_self, "_telemetry_conversation_id", None)
                    if conv_id:
                        span.add_attribute(GEN_AI_CONVERSATION_ID, conv_id)
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
        session = None
        if hasattr(result, "get"):
            session = result.get("session")
        elif hasattr(result, "session"):
            session = getattr(result, "session", None)

        if session is not None:
            session_id = None
            if hasattr(session, "get"):
                session_id = session.get("id")
            elif hasattr(session, "id"):
                session_id = getattr(session, "id", None)

            if session_id:
                conn_self._telemetry_session_id = session_id  # pylint: disable=protected-access
                connect_span = getattr(conn_self, "_telemetry_span", None)
                if connect_span is not None:
                    connect_span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)

    @staticmethod
    def _extract_audio_format_from_send(conn_self: Any, event: Any) -> None:
        """Extract audio format, codec, and sample rate from a session.update
        send event and store on the connection. Also sets on the parent connect span.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param event: The event being sent.
        :type event: any
        """
        session = None
        if hasattr(event, "get"):
            session = event.get("session")
        elif hasattr(event, "session"):
            session = getattr(event, "session", None)

        if session is None:
            return

        connect_span = getattr(conn_self, "_telemetry_span", None)

        # Input audio format
        input_audio_format = None
        if hasattr(session, "get"):
            input_audio_format = session.get("input_audio_format")
        elif hasattr(session, "input_audio_format"):
            input_audio_format = getattr(session, "input_audio_format", None)
        if input_audio_format:
            input_fmt_str = str(input_audio_format)
            conn_self._telemetry_input_audio_format = input_fmt_str  # pylint: disable=protected-access
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_INPUT_AUDIO_FORMAT, input_fmt_str)

        # Input audio sampling rate (explicit field on the session model)
        input_sampling_rate = None
        if hasattr(session, "get"):
            input_sampling_rate = session.get("input_audio_sampling_rate")
        elif hasattr(session, "input_audio_sampling_rate"):
            input_sampling_rate = getattr(session, "input_audio_sampling_rate", None)
        if input_sampling_rate is not None and connect_span is not None:
            connect_span.add_attribute(GEN_AI_VOICE_INPUT_SAMPLE_RATE, input_sampling_rate)

        # Output audio format
        output_audio_format = None
        if hasattr(session, "get"):
            output_audio_format = session.get("output_audio_format")
        elif hasattr(session, "output_audio_format"):
            output_audio_format = getattr(session, "output_audio_format", None)
        if output_audio_format:
            output_fmt_str = str(output_audio_format)
            conn_self._telemetry_output_audio_format = output_fmt_str  # pylint: disable=protected-access
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT, output_fmt_str)

    @staticmethod
    def _extract_audio_format_from_recv(conn_self: Any, result: Any) -> None:
        """Extract audio format and sample rate from a session.created or
        session.updated server event. The server response is authoritative and
        may include values the client did not explicitly set (e.g. defaults).

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :type conn_self: ~azure.ai.voicelive.aio.VoiceLiveConnection
        :param result: The received server event.
        :type result: any
        """
        session = None
        if hasattr(result, "get"):
            session = result.get("session")
        elif hasattr(result, "session"):
            session = getattr(result, "session", None)

        if session is None:
            return

        connect_span = getattr(conn_self, "_telemetry_span", None)

        # Input audio format
        input_audio_format = None
        if hasattr(session, "get"):
            input_audio_format = session.get("input_audio_format")
        elif hasattr(session, "input_audio_format"):
            input_audio_format = getattr(session, "input_audio_format", None)
        if input_audio_format:
            input_fmt_str = str(input_audio_format)
            conn_self._telemetry_input_audio_format = input_fmt_str  # pylint: disable=protected-access
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_INPUT_AUDIO_FORMAT, input_fmt_str)

        # Input audio sampling rate (explicit field on the session model)
        input_sampling_rate = None
        if hasattr(session, "get"):
            input_sampling_rate = session.get("input_audio_sampling_rate")
        elif hasattr(session, "input_audio_sampling_rate"):
            input_sampling_rate = getattr(session, "input_audio_sampling_rate", None)
        if input_sampling_rate is not None and connect_span is not None:
            connect_span.add_attribute(GEN_AI_VOICE_INPUT_SAMPLE_RATE, input_sampling_rate)

        # Output audio format
        output_audio_format = None
        if hasattr(session, "get"):
            output_audio_format = session.get("output_audio_format")
        elif hasattr(session, "output_audio_format"):
            output_audio_format = getattr(session, "output_audio_format", None)
        if output_audio_format:
            output_fmt_str = str(output_audio_format)
            conn_self._telemetry_output_audio_format = output_fmt_str  # pylint: disable=protected-access
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT, output_fmt_str)

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
        session = None
        if hasattr(event, "get"):
            session = event.get("session")
        elif hasattr(event, "session"):
            session = getattr(event, "session", None)

        if session is None:
            return

        connect_span = getattr(conn_self, "_telemetry_span", None)

        # System instructions
        instructions = None
        if hasattr(session, "get"):
            instructions = session.get("instructions")
        elif hasattr(session, "instructions"):
            instructions = getattr(session, "instructions", None)
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
        temperature = None
        if hasattr(session, "get"):
            temperature = session.get("temperature")
        elif hasattr(session, "temperature"):
            temperature = getattr(session, "temperature", None)
        if temperature is not None and connect_span is not None:
            connect_span.add_attribute(GEN_AI_REQUEST_TEMPERATURE, str(temperature))

        # Max output tokens
        max_output_tokens = None
        if hasattr(session, "get"):
            max_output_tokens = session.get("max_response_output_tokens")
        elif hasattr(session, "max_response_output_tokens"):
            max_output_tokens = getattr(session, "max_response_output_tokens", None)
        if max_output_tokens is not None and connect_span is not None:
            connect_span.add_attribute(GEN_AI_REQUEST_MAX_OUTPUT_TOKENS, max_output_tokens)

        # Tools
        tools = None
        if hasattr(session, "get"):
            tools = session.get("tools")
        elif hasattr(session, "tools"):
            tools = getattr(session, "tools", None)
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
    def _extract_response_done(conn_self: Any, result: Any, span: "AbstractSpan") -> None:
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
    def _record_operation_duration(
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
    def _add_rate_limit_event(span: "AbstractSpan", event_type: str, result: Any) -> None:
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
