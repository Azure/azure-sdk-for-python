# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Internal codec for Voice Live Bridge Protocol 1.0."""

# Internal codec helpers are documented at the public host/model layer.
# pylint: disable=docstring-missing-param,docstring-missing-return,docstring-missing-rtype

from __future__ import annotations

import datetime
import json
import re
import uuid
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any, cast

from azure.ai.agentserver.core import experimental

from ._models import (
    ConversationHistoryItem,
    ConversationItemCreateEvent,
    ConversationItemDeleteEvent,
    DtmfCollectedEvent,
    DtmfCollectionCancelledEvent,
    DtmfCollectionRejectedEvent,
    DtmfKeyEvent,
    HandoffFailedEvent,
    InputImagePart,
    InputTextPart,
    ResponseTimeoutEvent,
    ResponseTimeouts,
    SessionStartEvent,
    UserMessageEvent,
)

PROTOCOL_VERSION = "1.0"
MAX_ERROR_MESSAGE_LENGTH = 1024
_SAFE_CODE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
_VOICE_TYPE_ALIASES = {"azure-platform": "azure-standard", "custom": "azure-custom"}
_VOICE_TYPES = {
    "openai",
    "azure-standard",
    "azure-custom",
    "azure-personal",
    "avatar-voice-sync",
    "azure-realtime-native",
}
_VOICE_REQUIRED_STRING_FIELDS = {
    "name",
    "endpoint_id",
    "model",
}
_VOICE_NULLABLE_STRING_FIELDS = {
    "locale",
    "style",
    "pitch",
    "rate",
    "volume",
    "custom_lexicon_url",
    "custom_text_normalization_url",
    "multi_talker_speaker_name",
}
_VOICE_FIELDS = {
    "type",
    "temperature",
    "prefer_locales",
    *_VOICE_REQUIRED_STRING_FIELDS,
    *_VOICE_NULLABLE_STRING_FIELDS,
}
_AZURE_VOICE_OPTIONAL_FIELDS = {
    "temperature",
    "custom_lexicon_url",
    "custom_text_normalization_url",
    "prefer_locales",
    "locale",
    "style",
    "pitch",
    "rate",
    "volume",
}
_VOICE_VARIANT_FIELDS = {
    "openai": {"type", "name"},
    "azure-realtime-native": {"type", "name"},
    "azure-standard": {"type", "name", "multi_talker_speaker_name", *_AZURE_VOICE_OPTIONAL_FIELDS},
    "azure-custom": {"type", "name", "endpoint_id", *_AZURE_VOICE_OPTIONAL_FIELDS},
    "azure-personal": {"type", "name", "model", *_AZURE_VOICE_OPTIONAL_FIELDS},
    "avatar-voice-sync": {"type", "model", *_AZURE_VOICE_OPTIONAL_FIELDS},
}
_RFC3339 = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>(?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d)"
    r"(?:\.\d{1,9})?(?:Z|[+-](?:[01]\d|2[0-3]):[0-5]\d)$"
)


@experimental
class VoiceBridgeProtocolError(ValueError):
    """Raised when a frame violates the typed protocol.

    :param message: Safe diagnostic message.
    :param close_code: RFC 6455 close code to use for the violation.
    """

    def __init__(self, message: str, *, close_code: int = 1002) -> None:
        super().__init__(message)
        self.close_code = close_code


@experimental
class VoiceBridgeConnectionClosedError(RuntimeError):
    """Raised when customer code uses a terminal response or connection."""


@experimental
class VoiceProactiveResponseDroppedError(RuntimeError):
    """Raised when the bridge does not admit a proactive response.

    :param response_id: Terminal proactive response identifier.
    :param reason: Open-enum drop reason supplied by the bridge.
    """

    def __init__(self, response_id: str, reason: str) -> None:
        super().__init__(f"Proactive response was dropped: {reason}")
        self.response_id = response_id
        self.reason = reason


def new_id(prefix: str) -> str:
    """Return a random protocol identifier in one namespace."""
    if not isinstance(prefix, str) or not prefix or "_" in prefix:
        raise ValueError("prefix must be a non-empty namespace without underscores")
    return f"{prefix}_{uuid.uuid4().hex}"


def new_timestamp() -> str:
    """Return the canonical UTC-millisecond timestamp form."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def validate_timestamp(value: object) -> str:
    """Validate and return one strict cross-language RFC 3339 timestamp."""
    if not isinstance(value, str):
        raise VoiceBridgeProtocolError("ts must be a string")
    match = _RFC3339.fullmatch(value)
    if match is None:
        raise VoiceBridgeProtocolError("ts must match the RFC 3339 profile")
    try:
        datetime.datetime.strptime(
            f"{match.group('date')}T{match.group('time')}",
            "%Y-%m-%dT%H:%M:%S",
        )
    except ValueError as exc:
        raise VoiceBridgeProtocolError("ts must contain a valid calendar timestamp") from exc
    return value


def decode_frame(frame: str) -> dict[str, Any]:
    """Decode one JSON object and validate its common envelope."""
    try:
        raw_payload: Any = json.loads(frame, parse_constant=_reject_json_constant)
    except (json.JSONDecodeError, ValueError) as exc:
        raise VoiceBridgeProtocolError("Bridge frame is not valid JSON") from exc
    if not isinstance(raw_payload, dict):
        raise VoiceBridgeProtocolError("Bridge frame must be a JSON object")
    payload = cast(dict[str, Any], raw_payload)
    require_string(payload, "type", non_empty=True)
    require_string(payload, "id", non_empty=True)
    validate_timestamp(payload.get("ts"))
    return payload


def _reject_json_constant(value: str) -> Any:
    raise ValueError(f"Non-standard JSON constant: {value}")


def encode_frame(message_type: str, **fields: Any) -> str:
    """Encode one SDK-owned protocol frame with envelope fields."""
    if not isinstance(message_type, str) or not message_type:
        raise ValueError("message_type must be a non-empty string")
    payload = {
        "type": message_type,
        "id": new_id("m"),
        "ts": new_timestamp(),
        **fields,
    }
    return json.dumps(payload, separators=(",", ":"), ensure_ascii=False)


def canonical_payload(payload: Mapping[str, Any]) -> str:
    """Return a stable representation used for exact decoded-payload dedupe."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def parse_session_start(payload: Mapping[str, Any]) -> SessionStartEvent:
    """Validate ``session.start`` and return a deeply read-only event."""
    if payload.get("protocol_version") != PROTOCOL_VERSION:
        raise VoiceBridgeProtocolError("Unsupported bridge protocol version")
    reconnect = payload.get("reconnect")
    if not isinstance(reconnect, bool):
        raise VoiceBridgeProtocolError("session.start reconnect must be a boolean")

    timeout_payload = require_mapping(payload, "response_timeouts")
    timeouts = ResponseTimeouts(
        first_output_ms=require_positive_int(timeout_payload, "first_output_ms"),
        idle_ms=require_positive_int(timeout_payload, "idle_ms"),
        max_duration_ms=require_positive_int(timeout_payload, "max_duration_ms"),
    )

    greeting = optional_string(payload, "greeting")
    if reconnect and greeting is not None:
        raise VoiceBridgeProtocolError("session.start greeting must be absent on reconnect")

    no_input_timeout_ms: int | None = None
    if payload.get("no_input_timeout_ms") is not None:
        no_input_timeout_ms = require_positive_int(payload, "no_input_timeout_ms")

    caller_value = payload.get("caller")
    caller: Mapping[str, Any] | None = None
    if caller_value is not None:
        if not isinstance(caller_value, dict):
            raise VoiceBridgeProtocolError("session.start caller must be an object")
        caller = cast(Mapping[str, Any], freeze_json(caller_value))

    return SessionStartEvent(
        protocol_version=PROTOCOL_VERSION,
        reconnect=reconnect,
        response_timeouts=timeouts,
        greeting=greeting,
        no_input_timeout_ms=no_input_timeout_ms,
        caller=caller,
    )


def parse_user_message(payload: Mapping[str, Any]) -> UserMessageEvent:
    """Validate ``user.message`` and preserve supported content-part order."""
    item_id = require_prefixed_id(payload, "item_id", "in_")
    content = parse_content_parts(payload.get("content"), "user.message")
    return UserMessageEvent(item_id=item_id, content=content)


def parse_conversation_item_create(payload: Mapping[str, Any]) -> ConversationItemCreateEvent:
    """Validate one non-triggering history create request."""
    request_id = require_string(payload, "id", non_empty=True)
    raw_item = require_mapping(payload, "item")
    item_id = require_prefixed_id(raw_item, "id", "hi_")
    if raw_item.get("role") != "user":
        raise VoiceBridgeProtocolError("conversation.item.create role must be user", close_code=1008)
    content = parse_content_parts(raw_item.get("content"), "conversation.item.create")
    previous_item_id = optional_string(payload, "previous_item_id")
    if previous_item_id == "":
        raise VoiceBridgeProtocolError("previous_item_id must be non-empty when present")
    return ConversationItemCreateEvent(
        request_id=request_id,
        item=ConversationHistoryItem(item_id=item_id, content=content),
        previous_item_id=previous_item_id,
    )


def parse_conversation_item_delete(payload: Mapping[str, Any]) -> ConversationItemDeleteEvent:
    """Validate one non-triggering history delete request."""
    item_id = require_string(payload, "item_id", non_empty=True)
    if not ((item_id.startswith("hi_") and len(item_id) > 3) or (item_id.startswith("it_") and len(item_id) > 3)):
        raise VoiceBridgeProtocolError("conversation.item.delete item_id must start with hi_ or it_", close_code=1008)
    return ConversationItemDeleteEvent(
        request_id=require_string(payload, "id", non_empty=True),
        item_id=item_id,
    )


def parse_dtmf(payload: Mapping[str, Any]) -> DtmfKeyEvent | DtmfCollectedEvent:
    """Validate raw-key and collected-result DTMF shapes."""
    digits = require_string(payload, "digits")
    collection_value = payload.get("collection_id")
    item_value = payload.get("item_id")
    reason_value = payload.get("completion_reason")
    collected_values = (collection_value, item_value, reason_value)
    if all(value is None for value in collected_values):
        if len(digits) != 1 or digits not in "0123456789*#":
            raise VoiceBridgeProtocolError("Raw dtmf digits must contain exactly one DTMF key")
        return DtmfKeyEvent(digit=digits)
    if any(value is None for value in collected_values):
        raise VoiceBridgeProtocolError("Collected dtmf requires collection_id, item_id, and completion_reason")
    if any(character not in "0123456789*#" for character in digits):
        raise VoiceBridgeProtocolError("Collected dtmf digits contain an invalid key")
    return DtmfCollectedEvent(
        item_id=require_prefixed_id(payload, "item_id", "in_"),
        collection_id=require_prefixed_id(payload, "collection_id", "dc_"),
        digits=digits,
        completion_reason=require_string(payload, "completion_reason", non_empty=True),
    )


def parse_dtmf_collection_rejected(payload: Mapping[str, Any]) -> DtmfCollectionRejectedEvent:
    """Validate one DTMF collection rejection."""
    return DtmfCollectionRejectedEvent(
        collection_id=require_prefixed_id(payload, "collection_id", "dc_"),
        reason=require_string(payload, "reason", non_empty=True),
    )


def parse_dtmf_collection_cancelled(payload: Mapping[str, Any]) -> DtmfCollectionCancelledEvent:
    """Validate one DTMF collection cancellation."""
    return DtmfCollectionCancelledEvent(
        collection_id=require_prefixed_id(payload, "collection_id", "dc_"),
        reason=require_string(payload, "reason", non_empty=True),
    )


def parse_handoff_failed(payload: Mapping[str, Any]) -> HandoffFailedEvent:
    """Validate one bridge-generated handoff recovery turn."""
    return HandoffFailedEvent(
        item_id=require_prefixed_id(payload, "item_id", "in_"),
        target=require_string(payload, "target", non_empty=True),
        code=require_string(payload, "code", non_empty=True),
        message=optional_string(payload, "message"),
    )


def parse_content_parts(raw_content: object, message_name: str) -> tuple[InputTextPart | InputImagePart, ...]:
    """Validate ordered user content parts shared by turns and history."""
    if not isinstance(raw_content, list) or not raw_content:
        raise VoiceBridgeProtocolError(f"{message_name} content must be a non-empty array")

    content: list[InputTextPart | InputImagePart] = []
    for raw_part in raw_content:
        if not isinstance(raw_part, dict):
            raise VoiceBridgeProtocolError(f"{message_name} content parts must be objects")
        part_type = raw_part.get("type")
        if part_type == "input_text":
            content.append(InputTextPart(text=require_string(raw_part, "text")))
        elif part_type == "input_image":
            content.append(
                InputImagePart(
                    image_ref=require_string(raw_part, "image_ref", non_empty=True),
                    mime_type=require_string(raw_part, "mime_type", non_empty=True),
                    alt=optional_string(raw_part, "alt"),
                )
            )
        elif isinstance(part_type, str):
            continue
        else:
            raise VoiceBridgeProtocolError(f"{message_name} content part requires a string type")

    if not content:
        raise VoiceBridgeProtocolError(f"{message_name} contains no supported content parts")
    return tuple(content)


def parse_response_timeout(payload: Mapping[str, Any]) -> ResponseTimeoutEvent:
    """Validate the exclusive response/input-batch timeout shapes."""
    stage = require_string(payload, "stage", non_empty=True)
    response_value = payload.get("response_id")
    item_values = payload.get("item_ids")
    if (response_value is None) == (item_values is None):
        raise VoiceBridgeProtocolError("response.timeout requires exactly one of response_id or item_ids")
    if response_value is not None:
        return ResponseTimeoutEvent(
            stage=stage,
            response_id=require_prefixed_id(payload, "response_id", "r_"),
        )
    if not isinstance(item_values, list) or not item_values:
        raise VoiceBridgeProtocolError("response.timeout item_ids must be a non-empty array")
    item_ids: list[str] = []
    for value in item_values:
        if not isinstance(value, str) or not value.startswith("in_") or len(value) <= 3:
            raise VoiceBridgeProtocolError("response.timeout item_ids must contain in_ identifiers")
        item_ids.append(value)
    if len(set(item_ids)) != len(item_ids):
        raise VoiceBridgeProtocolError("response.timeout item_ids must not contain duplicates")
    return ResponseTimeoutEvent(stage=stage, item_ids=tuple(item_ids))


def require_mapping(payload: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    """Return one required JSON object field."""
    value = payload.get(name)
    if not isinstance(value, dict):
        raise VoiceBridgeProtocolError(f"{name} must be an object")
    return value


def require_string(payload: Mapping[str, Any], name: str, *, non_empty: bool = False) -> str:
    """Return one required string field.

    :keyword non_empty: Require at least one character when ``True``.
    :paramtype non_empty: bool
    """
    value = payload.get(name)
    if not isinstance(value, str) or (non_empty and not value):
        qualifier = "non-empty " if non_empty else ""
        raise VoiceBridgeProtocolError(f"{name} must be a {qualifier}string")
    return value


def optional_string(payload: Mapping[str, Any], name: str) -> str | None:
    """Return one optional string field."""
    value = payload.get(name)
    if value is not None and not isinstance(value, str):
        raise VoiceBridgeProtocolError(f"{name} must be a string")
    return cast(str | None, value)


def require_positive_int(payload: Mapping[str, Any], name: str) -> int:
    """Return one required positive integer field."""
    value = payload.get(name)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise VoiceBridgeProtocolError(f"{name} must be a positive integer")
    return value


def require_prefixed_id(payload: Mapping[str, Any], name: str, prefix: str) -> str:
    """Return one required protocol identifier in the expected namespace."""
    value = payload.get(name)
    if not isinstance(value, str) or not value.startswith(prefix) or len(value) <= len(prefix):
        raise VoiceBridgeProtocolError(f"{name} must start with {prefix}")
    return value


def safe_code(value: object, fallback: str) -> str:
    """Bound an untrusted open-enum value before logging or wire use."""
    return value if isinstance(value, str) and _SAFE_CODE.fullmatch(value) else fallback


def safe_message(value: object, fallback: str) -> str:
    """Return one bounded wire message without logging its content."""
    if not isinstance(value, str):
        return fallback
    return value[:MAX_ERROR_MESSAGE_LENGTH]


def normalize_voice(value: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Validate and materialize an optional Voice Live voice merge patch."""
    if value is None:
        return None
    if not isinstance(value, Mapping) or not value:
        raise TypeError("voice must be a non-empty mapping")
    raw_materialized = cast(dict[str, Any], thaw_json(value))
    materialized = {key: item for key, item in raw_materialized.items() if key in _VOICE_FIELDS}
    if not materialized:
        raise ValueError("voice must contain at least one supported field")
    try:
        json.dumps(materialized, ensure_ascii=False, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise TypeError("voice must contain only JSON-compatible values") from exc

    voice_type = materialized.get("type")
    if "type" in materialized:
        if not isinstance(voice_type, str):
            raise TypeError("voice.type must be a string")
        voice_type = _VOICE_TYPE_ALIASES.get(voice_type, voice_type)
        if voice_type not in _VOICE_TYPES:
            raise ValueError("voice.type is not a supported Voice Live variant")
        materialized["type"] = voice_type

    for field_name in _VOICE_REQUIRED_STRING_FIELDS:
        if field_name in materialized:
            field_value = materialized[field_name]
            if not isinstance(field_value, str) or not field_value:
                raise TypeError(f"voice.{field_name} must be a non-empty string")

    for field_name in _VOICE_NULLABLE_STRING_FIELDS:
        field_value = materialized.get(field_name)
        if field_value is not None and (not isinstance(field_value, str) or not field_value):
            raise TypeError(f"voice.{field_name} must be a non-empty string or null")

    temperature = materialized.get("temperature")
    if temperature is not None:
        if isinstance(temperature, bool) or not isinstance(temperature, (int, float)):
            raise TypeError("voice.temperature must be a number or null")
        if not 0.0 <= float(temperature) <= 1.0:
            raise ValueError("voice.temperature must be between 0.0 and 1.0")

    prefer_locales = materialized.get("prefer_locales")
    if prefer_locales is not None:
        if not isinstance(prefer_locales, list) or any(
            not isinstance(locale, str) or not locale for locale in prefer_locales
        ):
            raise TypeError("voice.prefer_locales must be an array of non-empty strings or null")

    if voice_type is not None and voice_type != "azure-custom" and materialized.get("endpoint_id") is not None:
        raise ValueError("voice.endpoint_id is valid only for azure-custom")
    if voice_type is not None:
        invalid_fields = set(materialized) - _VOICE_VARIANT_FIELDS[voice_type]
        if invalid_fields:
            field_name = sorted(invalid_fields)[0]
            raise ValueError(f"voice.{field_name} is not valid for {voice_type}")
    return materialized


def freeze_json(value: Any) -> Any:
    """Deeply freeze one decoded JSON value."""
    if isinstance(value, dict):
        return MappingProxyType({str(key): freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze_json(item) for item in value)
    return value


def thaw_json(value: Any) -> Any:
    """Materialize mappings/sequences as ordinary JSON containers."""
    if isinstance(value, Mapping):
        return {str(key): thaw_json(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [thaw_json(item) for item in value]
    return value
