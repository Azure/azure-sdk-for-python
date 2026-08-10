# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for strict Voice Live Bridge Protocol 1.0 helpers."""

import json
from types import MappingProxyType

import pytest

from azure.ai.agentserver.invocations.voice import InputImagePart, InputTextPart
from azure.ai.agentserver.invocations.voice._protocol import (
    VoiceBridgeProtocolError,
    canonical_payload,
    decode_frame,
    encode_frame,
    new_timestamp,
    normalize_voice,
    parse_handoff_failed,
    parse_response_timeout,
    parse_session_start,
    parse_user_message,
    validate_timestamp,
)

_TS = "2026-07-23T12:00:00.000Z"


def _start(**overrides):
    payload = {
        "type": "session.start",
        "id": "m_start",
        "ts": _TS,
        "protocol_version": "1.0",
        "reconnect": False,
        "response_timeouts": {
            "first_output_ms": 15_000,
            "idle_ms": 30_000,
            "max_duration_ms": 120_000,
        },
    }
    payload.update(overrides)
    return payload


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-07-21T12:00:00Z",
        "2026-07-21T12:00:00.1Z",
        "2026-07-21T12:00:00.123456789Z",
        "2026-07-21T12:00:00+08:00",
        "2026-07-21T12:00:00.123-07:30",
    ],
)
def test_shared_timestamp_valid_vectors(timestamp: str) -> None:
    assert validate_timestamp(timestamp) == timestamp


@pytest.mark.parametrize(
    "timestamp",
    [
        "2026-07-21 12:00:00Z",
        "2026-07-21t12:00:00Z",
        "2026-07-21T12:00:00z",
        "2026-07-21T12:00:00",
        "2026-07-21T12:00:00+0800",
        "2026-07-21T12:00:00,123Z",
        "2026-07-21T12:00:60Z",
        "2026-02-30T12:00:00Z",
    ],
)
def test_shared_timestamp_invalid_vectors(timestamp: str) -> None:
    with pytest.raises(VoiceBridgeProtocolError):
        validate_timestamp(timestamp)


def test_new_timestamp_uses_canonical_utc_milliseconds() -> None:
    timestamp = new_timestamp()
    assert timestamp.endswith("Z")
    assert len(timestamp.rsplit(".", maxsplit=1)[1].removesuffix("Z")) == 3
    validate_timestamp(timestamp)


def test_decode_requires_common_envelope() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="id must be a non-empty string"):
        decode_frame('{"type":"user.message","ts":"2026-07-21T12:00:00Z"}')


@pytest.mark.parametrize("message_id", ["opaque", "r_1", "in_1", "it_1", "dc_1", "m_", "消息-一"])
def test_decode_accepts_opaque_non_empty_message_id(message_id: str) -> None:
    frame = json.dumps({"type": "future", "id": message_id, "ts": _TS})

    assert decode_frame(frame)["id"] == message_id


@pytest.mark.parametrize("message_id", [None, "", 1, {}, []])
def test_decode_rejects_invalid_message_id(message_id: object) -> None:
    frame = json.dumps({"type": "future", "id": message_id, "ts": _TS})

    with pytest.raises(VoiceBridgeProtocolError, match="id must be a non-empty string"):
        decode_frame(frame)


def test_encode_uses_m_namespace_for_sdk_owned_envelope_id() -> None:
    message_id = json.loads(encode_frame("session.ready"))["id"]

    assert message_id.startswith("m_")
    assert len(message_id) > len("m_")


def test_decode_rejects_non_standard_json_numbers() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="not valid JSON"):
        decode_frame('{"type":"future","id":"m_1","ts":"2026-07-24T12:34:56.789Z","value":NaN}')


def test_decode_rejects_non_finite_number_from_valid_json_syntax() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="non-finite"):
        decode_frame('{"type":"future","id":"m_1","ts":"2026-07-24T12:34:56.789Z","value":1e400}')


def test_decode_rejects_oversized_integer_before_conversion() -> None:
    integer = "9" * 129
    with pytest.raises(VoiceBridgeProtocolError, match="not valid JSON"):
        decode_frame(f'{{"type":"future","id":"m_1","ts":"{_TS}","value":{integer}}}')


def test_decode_rejects_unpaired_unicode_surrogate() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="invalid Unicode"):
        decode_frame(r'{"type":"future","id":"m_1","ts":"2026-07-24T12:34:56.789Z","value":"\ud800"}')


def test_decode_rejects_excessive_json_depth() -> None:
    value: object = "leaf"
    for _ in range(130):
        value = [value]
    frame = json.dumps({"type": "future", "id": "m_1", "ts": _TS, "value": value})

    with pytest.raises(VoiceBridgeProtocolError, match="maximum JSON depth"):
        decode_frame(frame)


def test_canonical_payload_ignores_object_key_order() -> None:
    assert canonical_payload({"a": 1, "b": 2}) == canonical_payload({"b": 2, "a": 1})


def test_session_start_validates_preserves_and_freezes_caller_context() -> None:
    event = parse_session_start(
        _start(
            greeting="Welcome",
            no_input_timeout_ms=8_000,
            caller={
                "channel": "future-channel",
                "ani": "",
                "dnis": "+14255550100",
                "customer_id": "customer-1",
                "custom_parameters": {
                    "campaign": "renewals",
                    "enabled": True,
                    "attempt": 2,
                    "ratio": 0.5,
                    "optional": None,
                    "segments": ["a", {"rank": 1}],
                },
                "future_context": {"nested": ["value"]},
            },
        )
    )

    assert isinstance(event.caller, MappingProxyType)
    assert event.caller["channel"] == "future-channel"  # type: ignore[index]
    assert event.caller["ani"] == ""  # type: ignore[index]
    assert event.caller["dnis"] == "+14255550100"  # type: ignore[index]
    assert event.caller["customer_id"] == "customer-1"  # type: ignore[index]
    assert isinstance(event.caller["custom_parameters"], MappingProxyType)  # type: ignore[index]
    assert event.caller["custom_parameters"]["segments"][1]["rank"] == 1  # type: ignore[index]
    assert isinstance(event.caller["custom_parameters"]["segments"], tuple)  # type: ignore[index]
    assert event.caller["future_context"]["nested"] == ("value",)  # type: ignore[index]
    assert event.no_input_timeout_ms == 8_000
    with pytest.raises(TypeError):
        event.caller["channel"] = "websocket"  # type: ignore[index]
    with pytest.raises(TypeError):
        event.caller["future_context"]["other"] = "value"  # type: ignore[index]


@pytest.mark.parametrize("field_name", ["channel", "ani", "dnis", "customer_id"])
@pytest.mark.parametrize("value", [None, False, 1, 1.5, [], {}])
def test_session_start_rejects_invalid_known_caller_string_field(field_name: str, value: object) -> None:
    with pytest.raises(VoiceBridgeProtocolError, match=rf"caller\.{field_name} must be a string"):
        parse_session_start(_start(caller={field_name: value}))


@pytest.mark.parametrize("value", [None, False, 1, 1.5, "invalid", []])
def test_session_start_rejects_invalid_caller_custom_parameters(value: object) -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="caller.custom_parameters must be an object"):
        parse_session_start(_start(caller={"custom_parameters": value}))


@pytest.mark.parametrize("value", [None, False, 1, 1.5, "invalid", []])
def test_session_start_rejects_invalid_caller_object(value: object) -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="caller must be an object"):
        parse_session_start(_start(caller=value))


@pytest.mark.parametrize("value", [None, False, 1, 1.5, [], {}])
def test_session_start_rejects_invalid_greeting(value: object) -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="greeting must be a string"):
        parse_session_start(_start(greeting=value))


@pytest.mark.parametrize("value", [None, False, 0, -1, 1.5, "invalid", [], {}])
def test_session_start_rejects_invalid_no_input_timeout(value: object) -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="no_input_timeout_ms must be a positive integer"):
        parse_session_start(_start(no_input_timeout_ms=value))


def test_session_start_rejects_greeting_on_reconnect() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="absent on reconnect"):
        parse_session_start(_start(reconnect=True, greeting="Welcome back"))


def test_session_start_requires_all_positive_timeouts() -> None:
    payload = _start()
    payload["response_timeouts"]["first_output_ms"] = 0
    with pytest.raises(VoiceBridgeProtocolError, match="first_output_ms"):
        parse_session_start(payload)


def test_user_message_preserves_supported_content_order() -> None:
    event = parse_user_message(
        {
            "type": "user.message",
            "id": "m_user",
            "ts": _TS,
            "item_id": "in_1",
            "content": [
                {"type": "input_text", "text": "which receipt"},
                {"type": "future_part", "value": "ignored"},
                {
                    "type": "input_image",
                    "image_ref": "https://example.invalid/image",
                    "mime_type": "image/png",
                    "alt": "receipt",
                },
                {"type": "input_text", "text": "is mine"},
            ],
        }
    )

    assert event.item_id == "in_1"
    assert isinstance(event.content[0], InputTextPart)
    assert isinstance(event.content[1], InputImagePart)
    assert isinstance(event.content[2], InputTextPart)
    assert event.text == "which receipt is mine"


def test_user_message_allows_no_supported_content() -> None:
    event = parse_user_message(
        {
            "type": "user.message",
            "id": "m_user",
            "ts": _TS,
            "item_id": "in_1",
            "content": [{"type": "future_part"}],
        }
    )

    assert event.item_id == "in_1"
    assert event.content == ()


def test_user_message_preserves_long_item_id_for_fixed_digest_accounting() -> None:
    item_id = f"in_{'x' * 4096}"

    event = parse_user_message(
        {
            "item_id": item_id,
            "content": [{"type": "input_text", "text": "hello"}],
        }
    )

    assert event.item_id == item_id


def test_response_timeout_supports_response_and_input_batch_shapes() -> None:
    response_event = parse_response_timeout({"response_id": "r_1", "stage": "idle"})
    batch_event = parse_response_timeout({"item_ids": ["in_1", "in_2"], "stage": "first_output"})

    assert response_event.response_id == "r_1"
    assert response_event.item_ids is None
    assert batch_event.response_id is None
    assert batch_event.item_ids == ("in_1", "in_2")


@pytest.mark.parametrize(
    "payload",
    [
        {"stage": "idle"},
        {"response_id": "r_1", "item_ids": ["in_1"], "stage": "idle"},
        {"item_ids": [], "stage": "first_output"},
        {"item_ids": ["in_1", "in_1"], "stage": "first_output"},
    ],
)
def test_response_timeout_rejects_invalid_union(payload) -> None:
    with pytest.raises(VoiceBridgeProtocolError):
        parse_response_timeout(payload)


def test_normalize_voice_materializes_json_mapping() -> None:
    assert normalize_voice(MappingProxyType({"name": "en-US-Ava", "rate": "+10%"})) == {
        "name": "en-US-Ava",
        "rate": "+10%",
    }


def test_normalize_voice_requires_non_empty_json_mapping() -> None:
    with pytest.raises(TypeError, match="non-empty"):
        normalize_voice({})


def test_handoff_failed_parser_creates_recovery_turn() -> None:
    event = parse_handoff_failed(
        {
            "item_id": "in_recovery",
            "target": "billing",
            "code": "target_unavailable",
            "message": "Try later",
        }
    )
    assert event.item_id == "in_recovery"
    assert event.target == "billing"
    assert event.code == "target_unavailable"


def test_voice_patch_normalizes_alias_and_validates_constraints() -> None:
    assert normalize_voice({"type": "azure-platform", "name": "en-US-Ava", "avatar_character": "ignored"}) == {
        "type": "azure-standard",
        "name": "en-US-Ava",
    }
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        normalize_voice({"temperature": 1.1})
    with pytest.raises(ValueError, match="only for azure-custom"):
        normalize_voice({"type": "openai", "endpoint_id": "endpoint"})
    with pytest.raises(TypeError, match="voice.name must be a non-empty string"):
        normalize_voice({"name": None})
    with pytest.raises(TypeError, match="voice.type must be a string"):
        normalize_voice({"type": None})
    with pytest.raises(ValueError, match="at least one supported field"):
        normalize_voice({"avatar_style": "ignored"})
    with pytest.raises(ValueError, match="voice.rate is not valid for openai"):
        normalize_voice({"type": "openai", "name": "alloy", "rate": "+10%"})
    with pytest.raises(ValueError, match="voice.name is not valid for avatar-voice-sync"):
        normalize_voice({"type": "avatar-voice-sync", "name": "derived"})
