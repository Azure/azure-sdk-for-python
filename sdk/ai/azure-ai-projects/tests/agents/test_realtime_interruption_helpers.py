# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline protocol, audio, and ownership guards for interrupted-audio recordings."""

import base64
import io
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import wave

import pytest

from azure.ai.projects import models
from azure.core.exceptions import ResourceNotFoundError
from azure.core.rest import HttpRequest
import realtime_interruption_test_base as recording_helpers


@pytest.fixture
def helpers():
    return recording_helpers._sample_helpers()


def _events():
    return [
        {"type": "session.created", "conversation_id": "conversation-test"},
        {"type": "response.created", "response": {"id": "response-test"}},
        {
            "type": "response.audio.delta",
            "response_id": "response-test",
            "item_id": "item-test",
            "delta": base64.b64encode(b"\x00\x08" * 4800).decode(),
        },
        {"type": "response.done", "response": {"id": "response-test", "status": "cancelled"}},
        {"type": "conversation.item.truncated", "item_id": "item-test", "audio_end_ms": 0},
    ]


def _connection(is_async, events):
    connection = MagicMock()
    factory = AsyncMock if is_async else MagicMock
    connection.recv = factory(side_effect=events)
    connection.response.create = factory()
    connection.response.cancel = factory()
    connection.conversation.item.create = factory()
    connection.conversation.item.truncate = factory()
    return connection


def _metadata(**overrides):
    payload = {
        "conversation_id": "conversation-test",
        "item_id": "item-test",
        "role": "agent",
        "format": "wav",
        "codec": "pcm16",
        "sample_rate": 24000,
        "channels": 1,
        "duration_ms": 50,
    }
    return models.VoiceGeneratedAudioItem(dict(payload, **overrides))


def _wav(*, silent=False):
    output = io.BytesIO()
    with wave.open(output, "wb") as recording:
        recording.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
        recording.writeframes((b"\x00\x00" if silent else b"\x00\x08") * 1200)
    return output.getvalue()


@pytest.mark.asyncio
@pytest.mark.parametrize("is_async", [False, True])
@pytest.mark.parametrize("reverse_acknowledgements", [False, True])
@pytest.mark.parametrize("audio_event_type", ["response.audio.delta", "response.output_audio.delta"])
async def test_interruption_requires_both_cancel_and_truncation(
    helpers, is_async, reverse_acknowledgements, audio_event_type
):
    events = _events()
    events[2]["type"] = audio_event_type
    if reverse_acknowledgements:
        events[-2:] = reversed(events[-2:])
    connection = _connection(is_async, events)
    turn = helpers["InterruptedTurn"]()

    if is_async:
        await helpers["interrupt_reply_async"](connection, turn)
        connection.response.cancel.assert_awaited_once_with(response_id="response-test")
        connection.conversation.item.truncate.assert_awaited_once_with(
            item_id="item-test", content_index=0, audio_end_ms=0
        )
    else:
        helpers["interrupt_reply"](connection, turn)
        connection.response.cancel.assert_called_once_with(response_id="response-test")
        connection.conversation.item.truncate.assert_called_once_with(
            item_id="item-test", content_index=0, audio_end_ms=0
        )
    assert turn.cancelled and turn.truncated and turn.interruption_requested
    assert turn.received_audio_bytes == 9600
    assert turn.conversation_id == "conversation-test" and turn.item_id == "item-test"


@pytest.mark.parametrize(
    "event",
    [
        {"type": "session.created"},
        {"type": "error", "error": {"code": "invalid_request", "message": "synthetic failure"}},
        {"type": "response.created", "response": {}},
    ],
)
def test_missing_identifiers_and_service_errors_cannot_be_success(helpers, event):
    with pytest.raises(RuntimeError):
        helpers["InterruptedTurn"]().consume(event)


def test_silent_or_unrelated_audio_does_not_trigger_interruption(helpers):
    turn = helpers["InterruptedTurn"](response_id="response-test")
    turn.consume(
        {
            "type": "response.audio.delta",
            "response_id": "other-response",
            "item_id": "other-item",
            "delta": base64.b64encode(b"\x00\x08" * 4800).decode(),
        }
    )
    assert turn.received_audio_bytes == 0
    turn.consume(
        {
            "type": "response.audio.delta",
            "response_id": "response-test",
            "item_id": "item-test",
            "delta": base64.b64encode(bytes(9600)).decode(),
        }
    )
    assert not turn.ready_to_interrupt


def test_partial_pcm_and_unconfirmed_cancellation_are_errors(helpers):
    turn = helpers["InterruptedTurn"](response_id="response-test")
    with pytest.raises(ValueError, match="partial PCM16"):
        turn.consume(
            {
                "type": "response.audio.delta",
                "response_id": "response-test",
                "item_id": "item-test",
                "delta": base64.b64encode(b"\x01").decode(),
            }
        )
    with pytest.raises(RuntimeError, match="cancellation"):
        turn.consume({"type": "response.done", "response": {"id": "response-test", "status": "completed"}})
    turn.item_id = "item-test"
    turn.interruption_requested = True
    with pytest.raises(RuntimeError, match="playback position"):
        turn.consume({"type": "conversation.item.truncated", "item_id": "item-test", "audio_end_ms": 1})


@pytest.mark.asyncio
async def test_expired_async_deadline_does_not_create_an_unawaited_receive(helpers, monkeypatch):
    function = helpers["interrupt_reply_async"]
    monkeypatch.setitem(function.__globals__, "TURN_TIMEOUT", -1)
    connection = _connection(True, [])
    with pytest.raises(TimeoutError, match="session.created"):
        await function(connection, helpers["InterruptedTurn"]())
    connection.recv.assert_not_called()
    connection.response.create.assert_not_called()


@pytest.mark.parametrize(
    "overrides",
    [
        {"conversation_id": "wrong-conversation"},
        {"item_id": "wrong-item"},
        {"role": "user"},
        {"sample_rate": 16000},
        {"channels": 2},
        {"duration_ms": 0},
        {"blob_uri": "https://example.invalid/customer-recording"},
    ],
)
def test_generated_audio_metadata_must_match_the_interrupted_item(helpers, overrides):
    turn = helpers["InterruptedTurn"](
        conversation_id="conversation-test", item_id="wire-item-test", stored_item_id="item-test"
    )
    with pytest.raises(ValueError):
        helpers["validate_generated_audio"](_metadata(**overrides), _wav(), turn)


def test_generated_audio_requires_actual_non_silent_matching_wav(helpers):
    turn = helpers["InterruptedTurn"](
        conversation_id="conversation-test", item_id="wire-item-test", stored_item_id="item-test"
    )
    helpers["validate_generated_audio"](_metadata(), _wav(), turn)
    with pytest.raises(ValueError, match="not a WAV"):
        helpers["validate_generated_audio"](_metadata(), b"not audio", turn)
    with pytest.raises(ValueError, match="non-silent"):
        helpers["validate_generated_audio"](_metadata(), _wav(silent=True), turn)
    with pytest.raises(ValueError, match="does not match"):
        helpers["validate_generated_audio"](_metadata(duration_ms=1000), _wav(), turn)
    fixture = recording_helpers.RealtimeInterruptionFixture("owned-agent", "conversation-test", "item-test")
    recording_helpers.assert_generated_wav(_wav(), _metadata(), fixture)


def test_playback_never_creates_resources_or_loads_websocket_setup(monkeypatch):
    monkeypatch.setattr(recording_helpers, "is_live", lambda: False)
    client = MagicMock(side_effect=AssertionError("Playback attempted a live connection"))
    loader = MagicMock(side_effect=AssertionError("Playback loaded a live fixture"))
    monkeypatch.setattr(recording_helpers, "AIProjectClient", client)
    monkeypatch.setattr(recording_helpers, "_sample_helpers", loader)
    preparer = recording_helpers.RealtimeInterruptionPreparer()
    preparer.test_class_instance = SimpleNamespace(get_credential=MagicMock())

    assert preparer.create_resource("unused") == {"interrupted_audio_fixture": recording_helpers.playback_fixture()}
    preparer.remove_resource("unused")

    client.assert_not_called()
    loader.assert_not_called()
    preparer.test_class_instance.get_credential.assert_not_called()


@pytest.mark.asyncio
async def test_recording_cleanup_still_deletes_owned_agent_after_conversation_failure():
    client = MagicMock()
    client.voice_agents.conversations.delete = AsyncMock(side_effect=RuntimeError("cleanup failed"))
    client.agents.delete = AsyncMock()
    fixture = recording_helpers.RealtimeInterruptionFixture("owned-agent", "conversation-test", "item-test")
    with pytest.raises(RuntimeError, match="cleanup failed"):
        await recording_helpers._delete_fixture(client, fixture)
    client.agents.delete.assert_awaited_once_with(agent_name="owned-agent")


@pytest.mark.asyncio
async def test_failed_recording_creation_does_not_delete_an_unacknowledged_name(monkeypatch):
    credential = MagicMock()
    credential.__aenter__ = AsyncMock(return_value=credential)
    credential.__aexit__ = AsyncMock(return_value=False)
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.agents.create_version = AsyncMock(side_effect=RuntimeError("create failed"))
    client.agents.delete = AsyncMock(side_effect=ResourceNotFoundError("not materialized"))
    monkeypatch.setattr(recording_helpers, "AIProjectClient", MagicMock(return_value=client))
    preparer = recording_helpers.RealtimeInterruptionPreparer()
    preparer.endpoint = "https://example.invalid/api/projects/test"
    preparer.test_class_instance = SimpleNamespace(get_credential=MagicMock(return_value=credential))

    with pytest.raises(RuntimeError, match="create failed"):
        await preparer._create_fixture("owned-agent", "realtime-deployment-test")

    client.agents.delete.assert_not_called()
    client.voice_agents.conversations.delete.assert_not_called()


def test_interruption_sanitizers_preserve_cross_request_references(monkeypatch):
    recorded = []
    monkeypatch.setattr(recording_helpers, "add_general_regex_sanitizer", lambda **kwargs: recorded.append(kwargs))
    fixture = recording_helpers.RealtimeInterruptionFixture("owned-agent", "conversation-test", "item-test")
    recording_helpers.add_interruption_sanitizers(fixture)
    assert [entry["value"] for entry in recorded] == [
        "sanitized-interrupted-audio-agent",
        "sanitized-interrupted-conversation",
        "sanitized-interrupted-item",
    ]


@pytest.mark.parametrize("deleted", [False, True])
@pytest.mark.parametrize("header_name", [None, "Foundry-Features", "foundry-features"])
def test_ga_audio_response_hooks_reject_preview_headers(deleted, header_name):
    path = "/agents/owned-agent/protocols/voice/conversations/conversation-test"
    if not deleted:
        path += "/items/item-test/audio/generated"
    response = SimpleNamespace(
        http_response=SimpleNamespace(status_code=204 if deleted else 200),
        http_request=HttpRequest(
            "DELETE" if deleted else "GET",
            f"https://example.invalid{path}",
            headers={header_name: "VoiceAgents=V1Preview"} if header_name else {},
        ),
    )
    verify = (
        recording_helpers.assert_conversation_deleted
        if deleted
        else recording_helpers.assert_generated_status((200, 404))
    )

    if header_name:
        with pytest.raises(AssertionError):
            verify(response)
    else:
        verify(response)


def test_stored_item_lookup_uses_response_correlation_not_websocket_item_id(helpers):
    stored = [
        {"type": "message", "role": "user", "id": "stored-user"},
        {"type": "message", "role": "assistant", "response_id": "other-response", "id": "other-stored-item"},
        {"type": "message", "role": "assistant", "response_id": "response-test", "id": "stored-assistant"},
    ]
    assert helpers["_stored_audio_item"](stored, "response-test") == "stored-assistant"
    assert helpers["_stored_audio_item"]([], "response-test") is None
    with pytest.raises(RuntimeError, match="exactly one"):
        helpers["_stored_audio_item"]([stored[-1], stored[-1]], "response-test")
