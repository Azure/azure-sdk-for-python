# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Context-free codec for the Voice Live Bridge text/control profile."""

from __future__ import annotations

import datetime
import json
import math
import re
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any, cast

from azure.ai.agentserver.core import experimental

from ._models import (
    AgentError,
    BargeIn,
    EndCall,
    EndCallMode,
    InboundVoiceMessage,
    InputTextPart,
    OutboundVoiceMessage,
    ResponseAccepted,
    ResponseCancel,
    ResponseCancelled,
    ResponseCreated,
    ResponseDone,
    ResponseDropped,
    ResponseNone,
    ResponseOutputTextDelta,
    ResponseOutputTextDone,
    ResponseTimeout,
    ResponseTimeouts,
    SessionEnd,
    SessionReady,
    SessionRejected,
    SessionStart,
    UserMessage,
    UserNoInput,
    UserSpeechStarted,
)

MAX_FRAME_BYTES = 1_048_576
MAX_IDENTIFIER_BYTES = 256
MAX_INTEGER_DIGITS = 128
MAX_JSON_DEPTH = 32
MAX_JSON_NODES = 8_192
MAX_ADMISSION_TIMEOUT_MS = 60_000

_CREDENTIAL_FIELD = re.compile(
    r"(?:^|_)(?:authorization(?:_header)?|credentials?|password|passwd|pwd|secret(?:_value)?|"
    r"api_(?:key|token)|auth_token|bearer_token|access_(?:key|token)|refresh_token|id_token|"
    r"client_(?:assertion|secret)|private_key|connection_string|sas(?:_token|_url)?|account_key|"
    r"subscription_key|shared_access_(?:key|signature))(?:_|$)"
)
_VOICE_TYPE_ALIASES = {"azure-platform": "azure-standard", "custom": "azure-custom"}
_VOICE_TYPES = {
    "openai",
    "azure-standard",
    "azure-custom",
    "azure-personal",
    "avatar-voice-sync",
    "azure-realtime-native",
}
_RFC3339 = re.compile(
    r"^(?P<date>[0-9]{4}-[0-9]{2}-[0-9]{2})T(?P<time>(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9])"
    r"(?:\.[0-9]{1,9})?(?:Z|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)
_KNOWN_UNSUPPORTED_INBOUND = {
    "conversation.item.create",
    "conversation.item.delete",
    "dtmf",
    "dtmf.collect.cancelled",
    "dtmf.collect.rejected",
    "handoff.failed",
}
_OUTBOUND_TYPES = {
    "end_call",
    "error",
    "response.cancel",
    "response.created",
    "response.done",
    "response.none",
    "response.output_text.delta",
    "response.output_text.done",
    "session.ready",
    "session.rejected",
}


@experimental
class VoiceProtocolError(ValueError):
    """Raised when one frame violates the selected Voice protocol profile.

    :param message: Content-free diagnostic detail.
    :param close_code: RFC 6455 close code for the violation.
    """

    def __init__(self, message: str, *, close_code: int = 1002) -> None:
        super().__init__(message)
        self.close_code = close_code


@experimental
class VoiceUnsupportedMessageError(VoiceProtocolError):
    """Raised for a known Protocol 1.0 family excluded from this profile."""

    def __init__(self, message: str) -> None:
        super().__init__(message, close_code=1003)


def decode_inbound_message(frame: str) -> InboundVoiceMessage | None:  # pylint: disable=too-many-return-statements
    """Decode one Bridge-to-agent text frame.

    Unknown future message types return ``None`` for forward compatibility.
    The function retains no ID, payload, or cross-message state.

    :param frame: One WebSocket text frame.
    :type frame: str
    :return: An immutable selected message, or ``None`` for an unknown type.
    :rtype: InboundVoiceMessage or None
    :raises VoiceProtocolError: If the frame is malformed or violates the selected profile.
    """
    payload = _decode_json_object(frame)
    message_type = _required_string(payload, "type", non_empty=True)
    message_id = _identifier(payload, "id")
    timestamp = _timestamp(payload.get("ts"))

    if message_type in _KNOWN_UNSUPPORTED_INBOUND:
        raise VoiceUnsupportedMessageError("Voice message type is not supported by this profile")
    if message_type in _OUTBOUND_TYPES:
        raise VoiceProtocolError("Agent-to-Bridge message received in the inbound direction")

    common = {"id": message_id, "ts": timestamp}
    if message_type == "session.start":
        return _parse_session_start(payload, common)
    if message_type == "user.message":
        return _parse_user_message(payload, common)
    if message_type == "user.no_input":
        return UserNoInput(
            **common,
            item_id=_prefixed_identifier(payload, "item_id", "in_"),
            count=_positive_integer(payload, "count"),
        )
    if message_type == "user.speech_started":
        return UserSpeechStarted(**common)
    if message_type == "barge_in":
        return BargeIn(
            **common,
            response_id=_prefixed_identifier(payload, "response_id", "r_"),
            item_id=_optional_prefixed_identifier(payload, "item_id", "it_"),
            heard_text=_required_string(payload, "heard_text"),
        )
    if message_type == "response.accepted":
        return ResponseAccepted(
            **common,
            response_id=_prefixed_identifier(payload, "response_id", "r_"),
        )
    if message_type == "response.dropped":
        return ResponseDropped(
            **common,
            response_id=_prefixed_identifier(payload, "response_id", "r_"),
            reason=_required_string(payload, "reason", non_empty=True),
        )
    if message_type == "response.cancelled":
        return ResponseCancelled(
            **common,
            response_id=_prefixed_identifier(payload, "response_id", "r_"),
            item_id=_optional_prefixed_identifier(payload, "item_id", "it_"),
            heard_text=_required_string(payload, "heard_text"),
        )
    if message_type == "response.timeout":
        return _parse_response_timeout(payload, common)
    if message_type == "session.end":
        return SessionEnd(
            **common,
            reason=_required_string(payload, "reason", non_empty=True),
        )
    return None


def encode_outbound_message(message: OutboundVoiceMessage) -> str:
    """Validate and encode one agent-to-Bridge message.

    :param message: Immutable selected outbound message.
    :type message: OutboundVoiceMessage
    :return: One compact JSON text frame.
    :rtype: str
    :raises TypeError: If *message* is not a selected outbound model.
    :raises ValueError: If one field is invalid or the encoded frame is too large.
    """
    if not isinstance(
        message,
        (
            SessionReady,
            SessionRejected,
            ResponseCreated,
            ResponseNone,
            ResponseOutputTextDelta,
            ResponseOutputTextDone,
            ResponseDone,
            ResponseCancel,
            EndCall,
            AgentError,
        ),
    ):
        raise TypeError("message must be a selected outbound Voice message")

    payload: dict[str, Any] = {
        "type": message.type,
        "id": _validate_identifier_value(message.id, "id"),
        "ts": _timestamp(message.ts),
    }
    if isinstance(message, SessionRejected):
        payload.update(
            code=_validate_string_value(message.code, "code", non_empty=True),
            retriable=_validate_boolean_value(message.retriable, "retriable"),
        )
        _put_optional_string(payload, "message", message.message)
    elif isinstance(message, ResponseCreated):
        payload["response_id"] = _validate_prefixed_identifier_value(message.response_id, "response_id", "r_")
        if message.in_reply_to is not None:
            payload["in_reply_to"] = _validate_input_prefix(message.in_reply_to)
            if message.admission_timeout_ms is not None or message.supersede_key is not None:
                raise ValueError("reply response.created cannot contain proactive admission controls")
        else:
            if message.admission_timeout_ms is not None:
                payload["admission_timeout_ms"] = _validate_admission_timeout_ms(message.admission_timeout_ms)
            _put_optional_string(payload, "supersede_key", message.supersede_key, non_empty=True)
    elif isinstance(message, ResponseNone):
        payload["in_reply_to"] = _validate_input_prefix(message.in_reply_to)
        _put_optional_string(payload, "reason", message.reason)
    elif isinstance(message, ResponseOutputTextDelta):
        payload.update(
            response_id=_validate_prefixed_identifier_value(message.response_id, "response_id", "r_"),
            item_id=_validate_prefixed_identifier_value(message.item_id, "item_id", "it_"),
            delta=_validate_string_value(message.delta, "delta", non_empty=True),
        )
        _put_optional_voice(payload, message.voice)
    elif isinstance(message, ResponseOutputTextDone):
        payload.update(
            response_id=_validate_prefixed_identifier_value(message.response_id, "response_id", "r_"),
            item_id=_validate_prefixed_identifier_value(message.item_id, "item_id", "it_"),
            text=_validate_string_value(message.text, "text"),
        )
        _put_optional_voice(payload, message.voice)
    elif isinstance(message, ResponseDone):
        payload["response_id"] = _validate_prefixed_identifier_value(message.response_id, "response_id", "r_")
    elif isinstance(message, ResponseCancel):
        payload["response_id"] = _validate_prefixed_identifier_value(message.response_id, "response_id", "r_")
        _put_optional_string(payload, "reason", message.reason)
    elif isinstance(message, EndCall):
        if not isinstance(message.mode, EndCallMode):
            raise TypeError("mode must be an EndCallMode")
        payload.update(
            reason=_validate_string_value(message.reason, "reason", non_empty=True),
            mode=message.mode.value,
        )
    elif isinstance(message, AgentError):
        payload.update(
            code=_validate_string_value(message.code, "code", non_empty=True),
            message=_validate_string_value(message.message, "message"),
        )
        if message.response_id is not None:
            payload["response_id"] = _validate_prefixed_identifier_value(
                message.response_id,
                "response_id",
                "r_",
            )
        if message.item_id is not None:
            if message.response_id is None:
                raise ValueError("item_id requires response_id")
            payload["item_id"] = _validate_prefixed_identifier_value(message.item_id, "item_id", "it_")

    try:
        frame = json.dumps(payload, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        encoded_size = len(frame.encode("utf-8"))
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise ValueError("Voice message contains a value that cannot be encoded") from exc
    if encoded_size > MAX_FRAME_BYTES:
        raise ValueError("Voice message exceeds the maximum encoded frame size")
    return frame


def _parse_session_start(payload: Mapping[str, Any], common: Mapping[str, str]) -> SessionStart:
    timeout_payload = _required_mapping(payload, "response_timeouts")
    reconnect = payload.get("reconnect")
    if not isinstance(reconnect, bool):
        raise VoiceProtocolError("session.start reconnect must be a boolean")
    if reconnect and "greeting" in payload:
        raise VoiceProtocolError("session.start greeting must be absent on reconnect")
    greeting = _optional_string(payload, "greeting")
    no_input_timeout_ms = (
        _positive_integer(payload, "no_input_timeout_ms") if "no_input_timeout_ms" in payload else None
    )
    caller = None
    if "caller" in payload:
        caller_payload = _required_mapping(payload, "caller")
        _reject_caller_credentials(caller_payload)
        caller = cast(Mapping[str, Any], _freeze_json(caller_payload))
    return SessionStart(
        **common,
        protocol_version=_required_string(payload, "protocol_version", non_empty=True),
        reconnect=reconnect,
        response_timeouts=ResponseTimeouts(
            first_output_ms=_positive_integer(timeout_payload, "first_output_ms"),
            idle_ms=_positive_integer(timeout_payload, "idle_ms"),
            max_duration_ms=_positive_integer(timeout_payload, "max_duration_ms"),
        ),
        greeting=greeting,
        no_input_timeout_ms=no_input_timeout_ms,
        caller=caller,
    )


def _parse_user_message(payload: Mapping[str, Any], common: Mapping[str, str]) -> UserMessage | None:
    raw_content = payload.get("content")
    if not isinstance(raw_content, list) or not raw_content:
        raise VoiceProtocolError("user.message content must be a non-empty array")
    content: list[InputTextPart] = []
    for raw_part in raw_content:
        if not isinstance(raw_part, dict):
            raise VoiceProtocolError("user.message content parts must be objects")
        part_type = raw_part.get("type")
        if part_type == "input_text":
            content.append(InputTextPart(text=_required_string(raw_part, "text")))
        elif part_type == "input_image":
            raise VoiceUnsupportedMessageError("Image content is not supported by this profile")
        elif not isinstance(part_type, str):
            raise VoiceProtocolError("user.message content part type must be a string")
    if not content:
        return None
    return UserMessage(
        **common,
        item_id=_prefixed_identifier(payload, "item_id", "in_"),
        content=tuple(content),
    )


def _parse_response_timeout(payload: Mapping[str, Any], common: Mapping[str, str]) -> ResponseTimeout:
    has_response_id = "response_id" in payload
    has_item_ids = "item_ids" in payload
    if has_response_id == has_item_ids:
        raise VoiceProtocolError("response.timeout requires exactly one target")
    if has_response_id:
        response_id = _prefixed_identifier(payload, "response_id", "r_")
        item_ids = None
    else:
        raw_item_ids = payload.get("item_ids")
        if not isinstance(raw_item_ids, list) or not raw_item_ids:
            raise VoiceProtocolError("response.timeout item_ids must be a non-empty array")
        try:
            item_ids = tuple(_validate_prefixed_identifier_value(item, "item_ids", "in_") for item in raw_item_ids)
        except (TypeError, ValueError) as exc:
            raise VoiceProtocolError(str(exc)) from exc
        if len(set(item_ids)) != len(item_ids):
            raise VoiceProtocolError("response.timeout item_ids must be unique")
        response_id = None
    return ResponseTimeout(
        **common,
        stage=_required_string(payload, "stage", non_empty=True),
        response_id=response_id,
        item_ids=item_ids,
    )


def _decode_json_object(frame: str) -> dict[str, Any]:
    if not isinstance(frame, str):
        raise TypeError("frame must be text")
    try:
        encoded_size = len(frame.encode("utf-8"))
    except UnicodeEncodeError as exc:
        raise VoiceProtocolError("Voice frame contains invalid Unicode") from exc
    if encoded_size > MAX_FRAME_BYTES:
        raise VoiceProtocolError("Voice frame exceeds the maximum size", close_code=1009)
    try:
        value = json.loads(
            frame,
            object_pairs_hook=_object_without_duplicate_keys,
            parse_constant=_reject_json_constant,
            parse_int=_parse_integer,
        )
    except (json.JSONDecodeError, RecursionError, ValueError) as exc:
        raise VoiceProtocolError("Voice frame is not valid JSON") from exc
    if not isinstance(value, dict):
        raise VoiceProtocolError("Voice frame must be a JSON object")
    _validate_json_tree(value)
    return cast(dict[str, Any], value)


def _object_without_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON object key")
        value[key] = item
    return value


def _reject_json_constant(value: str) -> Any:
    raise ValueError(f"non-standard JSON constant: {value}")


def _parse_integer(value: str) -> int:
    digits = value[1:] if value.startswith("-") else value
    if len(digits) > MAX_INTEGER_DIGITS:
        raise ValueError("JSON integer exceeds the maximum digit count")
    return int(value)


def _validate_json_tree(value: Any) -> None:
    pending: list[tuple[Any, int]] = [(value, 1)]
    nodes = 0
    while pending:
        current, depth = pending.pop()
        nodes += 1
        if nodes > MAX_JSON_NODES:
            raise VoiceProtocolError("Voice frame exceeds the maximum JSON node count")
        if depth > MAX_JSON_DEPTH:
            raise VoiceProtocolError("Voice frame exceeds the maximum JSON depth")
        if isinstance(current, str):
            try:
                current.encode("utf-8")
            except UnicodeEncodeError as exc:
                raise VoiceProtocolError("Voice frame contains invalid Unicode") from exc
        elif isinstance(current, float):
            if not math.isfinite(current):
                raise VoiceProtocolError("Voice frame contains a non-finite number")
        elif isinstance(current, dict):
            for key in current:
                try:
                    key.encode("utf-8")
                except UnicodeEncodeError as exc:
                    raise VoiceProtocolError("Voice frame contains invalid Unicode") from exc
            pending.extend((item, depth + 1) for item in current.values())
        elif isinstance(current, list):
            pending.extend((item, depth + 1) for item in current)
        elif current is not None and not isinstance(current, (bool, int)):
            raise VoiceProtocolError("Voice frame contains an unsupported JSON value")


def _timestamp(value: Any) -> str:
    if not isinstance(value, str):
        raise VoiceProtocolError("ts must be a string")
    match = _RFC3339.fullmatch(value)
    if match is None:
        raise VoiceProtocolError("ts must match the RFC 3339 profile")
    try:
        datetime.datetime.strptime(
            f"{match.group('date')}T{match.group('time')}",
            "%Y-%m-%dT%H:%M:%S",
        )
    except ValueError as exc:
        raise VoiceProtocolError("ts must contain a valid calendar timestamp") from exc
    return value


def _required_mapping(payload: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    value = payload.get(name)
    if not isinstance(value, dict):
        raise VoiceProtocolError(f"{name} must be an object")
    return value


def _required_string(payload: Mapping[str, Any], name: str, *, non_empty: bool = False) -> str:
    try:
        value = payload[name]
    except KeyError as exc:
        raise VoiceProtocolError(f"{name} is required") from exc
    try:
        return _validate_string_value(value, name, non_empty=non_empty)
    except (TypeError, ValueError) as exc:
        raise VoiceProtocolError(str(exc)) from exc


def _optional_string(payload: Mapping[str, Any], name: str) -> str | None:
    if name not in payload:
        return None
    return _required_string(payload, name)


def _positive_integer(payload: Mapping[str, Any], name: str) -> int:
    try:
        value = payload[name]
    except KeyError as exc:
        raise VoiceProtocolError(f"{name} is required") from exc
    try:
        return _validate_positive_integer_value(value, name)
    except (TypeError, ValueError) as exc:
        raise VoiceProtocolError(str(exc)) from exc


def _identifier(payload: Mapping[str, Any], name: str) -> str:
    value = _required_string(payload, name, non_empty=True)
    try:
        return _validate_identifier_value(value, name)
    except (TypeError, ValueError) as exc:
        raise VoiceProtocolError(str(exc)) from exc


def _prefixed_identifier(payload: Mapping[str, Any], name: str, prefix: str) -> str:
    value = _identifier(payload, name)
    if not value.startswith(prefix) or len(value) == len(prefix):
        raise VoiceProtocolError(f"{name} must start with {prefix}")
    return value


def _optional_prefixed_identifier(payload: Mapping[str, Any], name: str, prefix: str) -> str | None:
    if name not in payload:
        return None
    return _prefixed_identifier(payload, name, prefix)


def _validate_string_value(value: Any, name: str, *, non_empty: bool = False) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    if non_empty and not value:
        raise ValueError(f"{name} must be non-empty")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise ValueError(f"{name} contains invalid Unicode") from exc
    return value


def _validate_boolean_value(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")
    return value


def _validate_positive_integer_value(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def _validate_admission_timeout_ms(value: Any) -> int:
    timeout = _validate_positive_integer_value(value, "admission_timeout_ms")
    if timeout > MAX_ADMISSION_TIMEOUT_MS:
        raise ValueError("admission_timeout_ms must be at most 60000")
    return timeout


def _validate_identifier_value(value: Any, name: str) -> str:
    identifier = _validate_string_value(value, name, non_empty=True)
    if len(identifier.encode("utf-8")) > MAX_IDENTIFIER_BYTES:
        raise ValueError(f"{name} exceeds the maximum identifier size")
    return identifier


def _validate_prefixed_identifier_value(value: Any, name: str, prefix: str) -> str:
    identifier = _validate_identifier_value(value, name)
    if not identifier.startswith(prefix) or len(identifier) == len(prefix):
        raise ValueError(f"{name} must start with {prefix}")
    return identifier


def _validate_input_prefix(value: Any) -> list[str]:
    if not isinstance(value, tuple) or not value:
        raise ValueError("in_reply_to must be a non-empty tuple")
    validated = [_validate_prefixed_identifier_value(item, "in_reply_to", "in_") for item in value]
    if len(set(validated)) != len(validated):
        raise ValueError("in_reply_to must contain unique identifiers")
    return validated


def _put_optional_string(
    payload: dict[str, Any],
    name: str,
    value: str | None,
    *,
    non_empty: bool = False,
) -> None:
    if value is not None:
        payload[name] = _validate_string_value(value, name, non_empty=non_empty)


def _put_optional_voice(payload: dict[str, Any], value: Mapping[str, Any] | None) -> None:
    normalized = _normalize_voice(value)
    if normalized is not None:
        payload["voice"] = normalized


def _normalize_voice(value: Mapping[str, Any] | None) -> dict[str, Any] | None:
    """Validate and materialize an optional Voice Live voice merge patch.

    :param value: Optional immutable or mutable voice merge patch.
    :type value: Mapping[str, Any] or None
    """
    if value is None:
        return None
    if not isinstance(value, Mapping) or not value:
        raise TypeError("voice must be a non-empty mapping")
    materialized = cast(dict[str, Any], _thaw_json(value))
    _validate_json_tree(materialized)
    voice_type = materialized.get("type")
    if "type" not in materialized:
        return materialized
    if not isinstance(voice_type, str):
        raise TypeError("voice.type must be a string")
    voice_type = _VOICE_TYPE_ALIASES.get(voice_type, voice_type)
    if voice_type not in _VOICE_TYPES:
        raise ValueError("voice.type is not a supported Voice Live variant")
    materialized["type"] = voice_type
    return materialized


def _reject_caller_credentials(value: Mapping[str, Any]) -> None:
    pending: list[Any] = [value]
    while pending:
        current = pending.pop()
        if isinstance(current, Mapping):
            for key, item in current.items():
                key_text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", str(key)).casefold()
                normalized_key = re.sub(r"[^a-z0-9]+", "_", key_text).strip("_")
                if _CREDENTIAL_FIELD.search(normalized_key):
                    raise VoiceProtocolError("session.start caller must not contain credentials")
                pending.append(item)
        elif isinstance(current, Sequence) and not isinstance(current, (str, bytes, bytearray)):
            pending.extend(current)


def _freeze_json(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({str(key): _freeze_json(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze_json(item) for item in value)
    return value


def _thaw_json(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _thaw_json(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_thaw_json(item) for item in value]
    return value
