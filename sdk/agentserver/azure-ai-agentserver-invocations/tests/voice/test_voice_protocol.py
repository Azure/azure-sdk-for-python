# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for strict Voice Live Bridge Protocol 1.0 helpers."""

from types import MappingProxyType

import pytest

from azure.ai.agentserver.invocations.voice import DtmfCollectedEvent, DtmfKeyEvent, InputImagePart, InputTextPart
from azure.ai.agentserver.invocations.voice._protocol import (
    VoiceBridgeProtocolError,
    canonical_payload,
    decode_frame,
    new_timestamp,
    normalize_voice,
    parse_conversation_item_create,
    parse_conversation_item_delete,
    parse_dtmf,
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
    with pytest.raises(VoiceBridgeProtocolError, match="id must be"):
        decode_frame('{"type":"user.message","ts":"2026-07-21T12:00:00Z"}')


def test_decode_rejects_non_standard_json_numbers() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="not valid JSON"):
        decode_frame('{"type":"future","id":"m_1","ts":"2026-07-24T12:34:56.789Z","value":NaN}')


def test_canonical_payload_ignores_object_key_order() -> None:
    assert canonical_payload({"a": 1, "b": 2}) == canonical_payload({"b": 2, "a": 1})


def test_session_start_is_deeply_read_only() -> None:
    event = parse_session_start(
        _start(
            greeting="Welcome",
            no_input_timeout_ms=8_000,
            caller={"channel": "pstn", "custom_parameters": {"campaign": "renewals"}},
        )
    )

    assert isinstance(event.caller, MappingProxyType)
    assert isinstance(event.caller["custom_parameters"], MappingProxyType)  # type: ignore[index]
    assert event.no_input_timeout_ms == 8_000
    with pytest.raises(TypeError):
        event.caller["channel"] = "websocket"  # type: ignore[index]


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


def test_user_message_rejects_no_supported_content() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="no supported"):
        parse_user_message(
            {
                "type": "user.message",
                "id": "m_user",
                "ts": _TS,
                "item_id": "in_1",
                "content": [{"type": "future_part"}],
            }
        )


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


def test_history_create_and_delete_models_preserve_correlation() -> None:
    created = parse_conversation_item_create(
        {
            "id": "m_history_create",
            "item": {
                "id": "hi_1",
                "role": "user",
                "content": [{"type": "input_text", "text": "selected order 42"}],
            },
            "previous_item_id": "root",
        }
    )
    deleted = parse_conversation_item_delete({"id": "m_history_delete", "item_id": "hi_1"})

    assert created.request_id == "m_history_create"
    assert created.item.item_id == "hi_1"
    assert created.item.role == "user"
    assert created.previous_item_id == "root"
    assert deleted.request_id == "m_history_delete"
    assert deleted.item_id == "hi_1"


def test_history_create_rejects_privileged_role() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="role must be user"):
        parse_conversation_item_create(
            {
                "id": "m_history",
                "item": {
                    "id": "hi_1",
                    "role": "system",
                    "content": [{"type": "input_text", "text": "secret"}],
                },
            }
        )


def test_history_delete_rejects_non_history_input_id() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="must start with hi_ or it_"):
        parse_conversation_item_delete({"id": "m_history_delete", "item_id": "in_1"})


def test_dtmf_parser_distinguishes_raw_and_collected_shapes() -> None:
    raw = parse_dtmf({"digits": "#"})
    collected = parse_dtmf(
        {
            "digits": "123",
            "collection_id": "dc_1",
            "item_id": "in_dtmf",
            "completion_reason": "max_digits",
        }
    )

    assert raw == DtmfKeyEvent(digit="#")
    assert collected == DtmfCollectedEvent(
        item_id="in_dtmf",
        collection_id="dc_1",
        digits="123",
        completion_reason="max_digits",
    )


def test_dtmf_parser_rejects_partial_collected_shape() -> None:
    with pytest.raises(VoiceBridgeProtocolError, match="requires collection_id"):
        parse_dtmf({"digits": "1", "collection_id": "dc_1"})


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
