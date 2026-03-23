# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Semantic attribute constants and span helpers for VoiceLive telemetry."""

from typing import Optional
import logging
from enum import Enum

from azure.core.tracing import AbstractSpan, SpanKind
from azure.core.settings import settings

try:
    _span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
except ModuleNotFoundError:
    _span_impl_type = None

logger = logging.getLogger(__name__)

# --- GenAI Semantic Convention attributes (v1.34.0) ---
GEN_AI_OPERATION_NAME = "gen_ai.operation.name"
GEN_AI_SYSTEM = "gen_ai.system"
GEN_AI_REQUEST_MODEL = "gen_ai.request.model"
GEN_AI_USAGE_INPUT_TOKENS = "gen_ai.usage.input_tokens"
GEN_AI_USAGE_OUTPUT_TOKENS = "gen_ai.usage.output_tokens"
GEN_AI_EVENT_CONTENT = "gen_ai.event.content"

# --- Server attributes ---
SERVER_ADDRESS = "server.address"
SERVER_PORT = "server.port"

# --- Azure namespace ---
AZ_NAMESPACE = "az.namespace"
AZ_NAMESPACE_VALUE = "Microsoft.CognitiveServices"
AZ_AI_VOICELIVE_SYSTEM = "az.ai.voicelive"

# --- VoiceLive-specific attributes ---
GEN_AI_VOICE_SESSION_ID = "gen_ai.voice.session_id"
GEN_AI_VOICE_SAMPLE_RATE = "gen_ai.voice.sample_rate"
GEN_AI_VOICE_CODEC = "gen_ai.voice.codec"
GEN_AI_VOICE_INPUT_AUDIO_FORMAT = "gen_ai.voice.input_audio_format"
GEN_AI_VOICE_OUTPUT_AUDIO_FORMAT = "gen_ai.voice.output_audio_format"

# --- Session-level telemetry counters ---
GEN_AI_VOICE_TURN_COUNT = "gen_ai.voice.turn_count"
GEN_AI_VOICE_INTERRUPTION_COUNT = "gen_ai.voice.interruption_count"
GEN_AI_VOICE_AUDIO_BYTES_SENT = "gen_ai.voice.audio_bytes_sent"
GEN_AI_VOICE_AUDIO_BYTES_RECEIVED = "gen_ai.voice.audio_bytes_received"

# --- Per-message attributes ---
GEN_AI_VOICE_MESSAGE_SIZE = "gen_ai.voice.message_size"
GEN_AI_VOICE_FIRST_TOKEN_LATENCY_MS = "gen_ai.voice.first_token_latency_ms"

# --- Error attributes ---
ERROR_TYPE = "error.type"

GEN_AI_SEMANTIC_CONVENTIONS_SCHEMA_VERSION = "1.34.0"


class OperationName(Enum):
    """Voice Live operation names used for span naming and ``gen_ai.operation.name`` attributes.

    Each member maps to a logical operation in the VoiceLive connection lifecycle.
    """

    CONNECT = "connect"
    SEND = "send"
    RECV = "recv"
    CLOSE = "close"
    SESSION_UPDATE = "session_update"
    RESPONSE_CREATE = "response_create"
    RESPONSE_CANCEL = "response_cancel"
    INPUT_AUDIO_BUFFER_APPEND = "input_audio_buffer_append"
    INPUT_AUDIO_BUFFER_COMMIT = "input_audio_buffer_commit"
    INPUT_AUDIO_BUFFER_CLEAR = "input_audio_buffer_clear"


def start_span(  # pylint: disable=R0913,R0917
    operation_name: OperationName,
    *,
    server_address: Optional[str] = None,
    port: Optional[int] = None,
    span_name: Optional[str] = None,
    model: Optional[str] = None,
    session_id: Optional[str] = None,
    kind: SpanKind = SpanKind.CLIENT,
) -> "Optional[AbstractSpan]":
    """Create and configure a new span for a VoiceLive operation.

    The span is pre-populated with standard GenAI semantic convention attributes
    (``az.namespace``, ``gen_ai.system``, ``gen_ai.operation.name``) and optional
    server / model / session attributes.

    :param operation_name: The logical operation being performed.
    :type operation_name: ~azure.ai.voicelive.telemetry._utils.OperationName
    :param server_address: The server hostname (``server.address`` attribute).
    :type server_address: str or None
    :param port: The server port (``server.port`` attribute).
    :type port: int or None
    :param span_name: Custom span name. Defaults to ``operation_name.value``.
    :type span_name: str or None
    :param model: The model identifier (``gen_ai.request.model`` attribute).
    :type model: str or None
    :param session_id: The voice session identifier (``gen_ai.voice.session_id`` attribute).
    :type session_id: str or None
    :param kind: The span kind. Defaults to ``SpanKind.CLIENT``.
    :type kind: ~azure.core.tracing.SpanKind
    :return: The created span, or ``None`` if no tracing implementation is configured.
    :rtype: ~azure.core.tracing.AbstractSpan or None
    """
    global _span_impl_type  # pylint: disable=global-statement
    if _span_impl_type is None:
        _span_impl_type = settings.tracing_implementation()  # pylint: disable=not-callable
        if _span_impl_type is None:
            return None

    span = _span_impl_type(
        name=span_name or operation_name.value,
        kind=kind,
        schema_version=GEN_AI_SEMANTIC_CONVENTIONS_SCHEMA_VERSION,
    )

    if span and span.span_instance.is_recording:
        span.add_attribute(AZ_NAMESPACE, AZ_NAMESPACE_VALUE)
        span.add_attribute(GEN_AI_SYSTEM, AZ_AI_VOICELIVE_SYSTEM)
        span.add_attribute(GEN_AI_OPERATION_NAME, operation_name.value)

        if server_address:
            span.add_attribute(SERVER_ADDRESS, server_address)
        if port:
            span.add_attribute(SERVER_PORT, port)
        if model:
            span.add_attribute(GEN_AI_REQUEST_MODEL, model)
        if session_id:
            span.add_attribute(GEN_AI_VOICE_SESSION_ID, session_id)

    return span
