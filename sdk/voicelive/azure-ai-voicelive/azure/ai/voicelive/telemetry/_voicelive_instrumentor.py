# pylint: disable=line-too-long,useless-suppression
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
from typing import Any, Callable, Dict, Optional, Tuple, Union

from azure.core.settings import settings
from azure.core.tracing import AbstractSpan

from ._utils import (
    AZ_AI_VOICELIVE_SYSTEM,
    ERROR_TYPE,
    GEN_AI_EVENT_CONTENT,
    GEN_AI_OPERATION_NAME,
    GEN_AI_REQUEST_MODEL,
    GEN_AI_SYSTEM,
    GEN_AI_USAGE_INPUT_TOKENS,
    GEN_AI_USAGE_OUTPUT_TOKENS,
    GEN_AI_VOICE_AUDIO_BYTES_RECEIVED,
    GEN_AI_VOICE_AUDIO_BYTES_SENT,
    GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS,
    GEN_AI_VOICE_INPUT_AUDIO_FORMAT,
    GEN_AI_VOICE_INTERRUPTION_COUNT,
    GEN_AI_VOICE_MESSAGE_SIZE,
    GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT,
    GEN_AI_VOICE_SESSION_ID,
    GEN_AI_VOICE_TURN_COUNT,
    OperationName,
    start_span,
)

logger = logging.getLogger(__name__)

try:
    from opentelemetry import context as otel_context
    from opentelemetry.trace import Span, StatusCode, set_span_in_context

    _tracing_library_available = True
except ModuleNotFoundError:
    _tracing_library_available = False

__all__ = ["VoiceLiveInstrumentor"]

_voicelive_traces_enabled: bool = False
_trace_voicelive_content: bool = False


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

        :rtype: bool
        """
        return _voicelive_traces_enabled

    def is_content_recording_enabled(self) -> bool:
        """Return ``True`` if message content recording is enabled.

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
        if isinstance(span.span_instance, Span):  # pyright: ignore[reportPossiblyUnboundVariable]
            span.span_instance.set_status(
                StatusCode.ERROR,  # pyright: ignore[reportPossiblyUnboundVariable]
                description=str(exc),
            )
        module = getattr(exc, "__module__", "")
        module = module if module != "builtins" else ""
        error_type = f"{module}.{type(exc).__name__}" if module else type(exc).__name__
        self._set_attributes(span, (ERROR_TYPE, error_type))

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
        """Wrap ``_VoiceLiveConnectionManager.__aenter__``."""
        instrumentor = self

        @functools.wraps(original_aenter)
        async def wrapper(mgr_self, *args, **kwargs):
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
                # Attach the connect span to the OTel context so that
                # send/recv/close spans are automatically parented under it.
                # We bypass azure-core's _SuppressionContextManager to avoid
                # suppressing child CLIENT spans.
                ctx = set_span_in_context(span.span_instance)
                result._telemetry_context_token = otel_context.attach(ctx)
                return result
            except Exception as exc:
                instrumentor.record_error(span, exc)
                span.__exit__(type(exc), exc, exc.__traceback__)
                raise

        wrapper._original = original_aenter  # type: ignore[attr-defined]
        return wrapper

    def _trace_aexit(self, original_aexit: Callable) -> Callable:
        """Wrap ``_VoiceLiveConnectionManager.__aexit__``."""
        instrumentor = self

        @functools.wraps(original_aexit)
        async def wrapper(mgr_self, exc_type, exc, exc_tb):
            conn = getattr(mgr_self, "_VoiceLiveConnectionManager__connection", None)
            span = getattr(conn, "_telemetry_span", None) if conn else None

            await original_aexit(mgr_self, exc_type, exc, exc_tb)

            if span is not None:
                # Detach the connect span's context token so it is no longer
                # the active span after the session closes.
                context_token = getattr(conn, "_telemetry_context_token", None)
                if context_token is not None:
                    otel_context.detach(context_token)

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

    def _trace_send(self, original_send: Callable) -> Callable:
        """Wrap ``VoiceLiveConnection.send``."""
        instrumentor = self

        @functools.wraps(original_send)
        async def wrapper(conn_self, event, *args, **kwargs):
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
            if "input_audio_buffer.append" in event_type_str:
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
            if "response.cancel" in event_type_str:
                current = getattr(conn_self, "_telemetry_interruption_count", 0)
                conn_self._telemetry_interruption_count = current + 1

            # Track response.create timestamp for first-token latency
            if "response.create" in event_type_str:
                conn_self._telemetry_response_create_time = time.monotonic()
                conn_self._telemetry_first_token_latency_recorded = False

            # Extract audio format from session.update
            if "session.update" in event_type_str:
                instrumentor._extract_audio_format_from_send(conn_self, event)

            op_name = OperationName.SEND
            span_name = f"send {event_type}" if event_type else "send"
            span = start_span(
                op_name,
                server_address=getattr(conn_self, "_telemetry_server_address", None),
                port=getattr(conn_self, "_telemetry_port", None),
                model=getattr(conn_self, "_telemetry_model", None),
                span_name=span_name,
            )

            if span is None:
                return await original_send(conn_self, event, *args, **kwargs)

            try:
                with span:
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

    def _trace_recv(self, original_recv: Callable) -> Callable:
        """Wrap ``VoiceLiveConnection.recv``."""
        instrumentor = self

        @functools.wraps(original_recv)
        async def wrapper(conn_self, *args, **kwargs):
            span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
            if span_impl_type is None:
                return await original_recv(conn_self, *args, **kwargs)

            span = start_span(
                OperationName.RECV,
                server_address=getattr(conn_self, "_telemetry_server_address", None),
                port=getattr(conn_self, "_telemetry_port", None),
                model=getattr(conn_self, "_telemetry_model", None),
            )

            if span is None:
                return await original_recv(conn_self, *args, **kwargs)

            try:
                with span:
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

                    # --- Session ID tracking ---
                    if event_type_str in ("session.created", "session.updated"):
                        instrumentor._extract_session_id(conn_self, result)

                    # --- First-token latency ---
                    if event_type_str in ("response.audio.delta", "response.text.delta"):
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
                    if event_type_str == "response.audio.delta":
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
                    if event_type_str == "response.done":
                        current = getattr(conn_self, "_telemetry_turn_count", 0)
                        conn_self._telemetry_turn_count = current + 1

                    # --- Rate limit / error events ---
                    if event_type_str == "error" or event_type_str == "rate_limits.updated":
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
                        if output_tokens is not None:
                            span.add_attribute(GEN_AI_USAGE_OUTPUT_TOKENS, output_tokens)

                    return result
            except Exception as exc:
                instrumentor.record_error(span, exc)
                raise

        wrapper._original = original_recv  # type: ignore[attr-defined]
        return wrapper

    def _trace_close(self, original_close: Callable) -> Callable:
        """Wrap ``VoiceLiveConnection.close``."""
        instrumentor = self

        @functools.wraps(original_close)
        async def wrapper(conn_self, *args, **kwargs):
            span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
            if span_impl_type is None:
                return await original_close(conn_self, *args, **kwargs)

            span = start_span(
                OperationName.CLOSE,
                server_address=getattr(conn_self, "_telemetry_server_address", None),
                port=getattr(conn_self, "_telemetry_port", None),
            )

            if span is None:
                return await original_close(conn_self, *args, **kwargs)

            try:
                with span:
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
        :param result: The received event object.
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
                conn_self._telemetry_session_id = session_id
                connect_span = getattr(conn_self, "_telemetry_span", None)
                if connect_span is not None:
                    connect_span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)

    @staticmethod
    def _extract_audio_format_from_send(conn_self: Any, event: Any) -> None:
        """Extract audio format, codec, and sample rate from a session.update
        send event and store on the connection. Also sets on the parent connect span.

        :param conn_self: The ``VoiceLiveConnection`` instance.
        :param event: The event being sent.
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
            conn_self._telemetry_input_audio_format = input_fmt_str
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_INPUT_AUDIO_FORMAT, input_fmt_str)

        # Output audio format
        output_audio_format = None
        if hasattr(session, "get"):
            output_audio_format = session.get("output_audio_format")
        elif hasattr(session, "output_audio_format"):
            output_audio_format = getattr(session, "output_audio_format", None)
        if output_audio_format:
            output_fmt_str = str(output_audio_format)
            conn_self._telemetry_output_audio_format = output_fmt_str
            if connect_span is not None:
                connect_span.add_attribute(GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT, output_fmt_str)

    @staticmethod
    def _add_rate_limit_event(span: "AbstractSpan", event_type: str, result: Any) -> None:
        """Add a span event for rate limit or error events from the server.

        :param span: The active span.
        :type span: ~azure.core.tracing.AbstractSpan
        :param event_type: The event type string (``"error"`` or ``"rate_limits.updated"``).
        :type event_type: str
        :param result: The received event object.
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
                    setattr(cls, method_name, current._original)
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

    def _is_content_recording_enabled(self) -> bool:
        """Return ``True`` if content recording is currently enabled.

        :rtype: bool
        """
        return _trace_voicelive_content
