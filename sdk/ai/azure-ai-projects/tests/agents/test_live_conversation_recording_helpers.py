# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline guards for the recorded REST tests; no service or cassette is used here."""

import datetime
import importlib
import io
import json
from pathlib import Path
import re
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import wave

import pytest
from azure.ai.projects import models
from azure.core.exceptions import ResourceNotFoundError

import live_conversation_test_base as helpers


def _audio(channels=1):
    common = {
        "conversation_id": "conversation-test",
        "format": "wav",
        "sample_rate": 24000,
        "channels": channels,
        "duration_ms": 50,
    }
    if channels == 1:
        return models.VoiceAudioItem(dict(common, item_id="item-test", role="agent", codec="pcm16"))
    return models.VoiceRecording(dict(common, channel_layout={"left": "user", "right": "agent"}))


def _wav(channels=1, silent=False):
    stream = io.BytesIO()
    sample = b"\x00\x00" if silent else b"\x00\x08"
    frame = sample if channels == 1 else b"\x00\x00" + sample
    with wave.open(stream, "wb") as recording:
        recording.setparams((channels, 2, 24000, 0, "NONE", "not compressed"))
        recording.writeframes(frame * 1200)
    return stream.getvalue()


def test_playback_fixture_never_creates_an_agent_or_opens_a_websocket(monkeypatch):
    monkeypatch.setattr(helpers, "is_live", lambda: False)
    create_client = MagicMock(side_effect=AssertionError("Playback attempted live setup"))
    monkeypatch.setattr(helpers, "AIProjectClient", create_client)
    preparer = helpers.LiveConversationPreparer()
    preparer.test_class_instance = SimpleNamespace(get_credential=MagicMock())
    preparer.fixture = helpers.LiveConversationFixture("previous-owned-agent", ("previous-conversation",), version="1")
    preparer.endpoint = "https://example.invalid/previous-recording"

    result = preparer.create_resource("unused")
    preparer.remove_resource("unused")

    assert result["live_conversation_fixture"] == helpers.playback_fixture()
    create_client.assert_not_called()
    preparer.test_class_instance.get_credential.assert_not_called()


def test_playback_preparer_does_not_require_the_legacy_test_resource_counter(monkeypatch):
    monkeypatch.setattr(helpers, "is_live", lambda: False)
    case = SimpleNamespace(is_live=False, in_recording=False)
    received = []

    def recorded_body(instance, live_conversation_fixture):
        assert instance is case
        received.append(live_conversation_fixture)

    helpers.LiveConversationPreparer()(recorded_body)(case)
    assert received == [helpers.playback_fixture()]


@pytest.mark.parametrize("fail_test", [False, True])
def test_websocket_setup_and_owned_cleanup_are_outside_recorded_transport_patching(monkeypatch, fail_test):
    monkeypatch.setattr(helpers, "is_live", lambda: True)
    active = {"recorded": False}
    calls = []
    fixture = helpers.LiveConversationFixture(
        "owned-agent", ("owned-conversation-1", "owned-conversation-2"), (("owned-item-1",), ("owned-item-2",)), "1"
    )
    preparer = helpers.LiveConversationPreparer()

    async def create(*args):
        assert not active["recorded"]
        calls.append("setup")
        return fixture

    async def cleanup():
        assert not active["recorded"]
        calls.append("cleanup")

    monkeypatch.setattr(preparer, "_create_fixture", create)
    monkeypatch.setattr(preparer, "_cleanup_fixture", cleanup)

    def recorded_body(instance, **kwargs):
        active["recorded"] = True
        try:
            assert kwargs["live_conversation_fixture"] is fixture
            calls.append("recorded-rest")
            if fail_test:
                raise ValueError("recorded test failed")
        finally:
            active["recorded"] = False

    instance = SimpleNamespace(in_recording=False, is_live=True, test_resources_count=0)
    wrapped = preparer(recorded_body)
    if fail_test:
        with pytest.raises(ValueError, match="recorded test failed"):
            wrapped(
                instance, foundry_project_endpoint="https://example.invalid", foundry_voice_live_model_name="live-test"
            )
    else:
        wrapped(instance, foundry_project_endpoint="https://example.invalid", foundry_voice_live_model_name="live-test")
    assert calls == ["setup", "recorded-rest", "cleanup"]


@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True])
async def test_failed_recorded_assertions_do_not_append_unexpected_cleanup_requests(monkeypatch, asynchronous):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1]))
    module = importlib.import_module("test_voice_agent_live_conversations" + ("_async" if asynchronous else ""))
    monkeypatch.setattr(module, "is_live", lambda: False)
    case = getattr(module, "TestVoiceAgentLiveConversations" + ("Async" if asynchronous else ""))
    body = getattr(case, "_test_live_conversation_rest_lifecycle" + ("_async" if asynchronous else ""))
    client = MagicMock()
    client.__enter__.return_value = client
    client.__aenter__.return_value = client
    client.beta.voice_agents.live_conversations.list.return_value.__iter__.return_value = iter(())
    client.beta.voice_agents.live_conversations.list.return_value.__aiter__.return_value = []
    instance = SimpleNamespace(
        create_client=MagicMock(return_value=client), create_async_client=MagicMock(return_value=client)
    )
    with pytest.raises(AssertionError):
        if asynchronous:
            await body(instance, live_conversation_fixture=helpers.playback_fixture())
        else:
            body(instance, live_conversation_fixture=helpers.playback_fixture())
    client.beta.voice_agents.live_conversations.delete.assert_not_called()


def test_sanitizers_keep_agent_conversation_item_and_cursor_references_consistent(monkeypatch):
    sanitize = MagicMock()
    monkeypatch.setattr(helpers, "add_general_regex_sanitizer", sanitize)
    fixture = helpers.LiveConversationFixture(
        "owned-agent",
        ("owned.conversation+1", "owned.conversation+2"),
        (("owned.item+1", "owned.item+2"), ("owned.item+3",)),
        "1",
    )
    helpers.add_live_conversation_sanitizers(fixture)
    assert sanitize.call_count == 6
    wire = json.dumps(
        {
            "agent_name": fixture.agent_name,
            "conversation_ids": fixture.conversation_ids,
            "item_ids": fixture.item_ids,
            "after": fixture.conversation_ids[0],
            "audio": {"conversation_id": fixture.conversation_ids[0], "item_id": fixture.item_ids[0][0]},
        }
    )
    for call in sanitize.call_args_list:
        assert call.kwargs["function_scoped"] is True
        wire = re.sub(call.kwargs["regex"], call.kwargs["value"], wire)
    parsed = json.loads(wire)
    expected = helpers.playback_fixture()
    assert parsed["agent_name"] == expected.agent_name
    assert parsed["conversation_ids"] == list(expected.conversation_ids)
    assert parsed["after"] == parsed["audio"]["conversation_id"] == expected.conversation_ids[0]
    assert parsed["audio"]["item_id"] == parsed["item_ids"][0][0] == "sanitized-live-item-1-1"
    assert "owned" not in wire


@pytest.mark.asyncio
async def test_fixture_cleanup_deletes_only_owned_versions_even_if_conversation_delete_fails():
    client = MagicMock()
    client.beta.voice_agents.live_conversations.delete = AsyncMock(side_effect=[ValueError("delete failed"), None])
    client.agents.delete_version = AsyncMock()
    fixture = helpers.LiveConversationFixture("owned-agent", ("first", "second"), version="7")
    with pytest.raises(ValueError, match="delete failed"):
        await helpers._delete_fixture(client, fixture)
    assert client.beta.voice_agents.live_conversations.delete.await_count == 2
    assert [call.args for call in client.beta.voice_agents.live_conversations.delete.await_args_list] == [
        ("owned-agent", "first"),
        ("owned-agent", "second"),
    ]
    client.agents.delete_version.assert_awaited_once_with(agent_name="owned-agent", agent_version="7")
    client.agents.delete.assert_not_called()


@pytest.mark.asyncio
async def test_fixture_cleanup_tolerates_a_conversation_already_deleted_by_the_recorded_test():
    client = MagicMock()
    client.beta.voice_agents.live_conversations.delete = AsyncMock(side_effect=[ResourceNotFoundError("deleted"), None])
    client.agents.delete_version = AsyncMock()
    fixture = helpers.LiveConversationFixture("owned-agent", ("first", "second"), version="1")
    await helpers._delete_fixture(client, fixture)
    assert client.beta.voice_agents.live_conversations.delete.await_count == 2
    client.agents.delete_version.assert_awaited_once_with(agent_name="owned-agent", agent_version="1")


@pytest.mark.asyncio
@pytest.mark.parametrize("setup_fails", [False, True])
async def test_recording_setup_tracks_owned_ids_and_cleans_partial_websocket_failure(monkeypatch, setup_fails):
    credential = MagicMock()
    credential.__aenter__.return_value = credential
    client = MagicMock()
    client.__aenter__.return_value = client
    client.agents.create_version = AsyncMock(return_value=SimpleNamespace(version="1"))
    client.agents.delete_version = AsyncMock()
    client.beta.voice_agents.live_conversations.delete = AsyncMock()
    constructor = MagicMock(return_value=client)
    monkeypatch.setattr(helpers, "AIProjectClient", constructor)
    preparer = helpers.LiveConversationPreparer()
    preparer.endpoint = "https://example.invalid/api/projects/test"
    preparer.test_class_instance = SimpleNamespace(get_credential=MagicMock(return_value=credential))

    async def hold_greeting(project_client, name, version, conversation_ids):
        assert project_client is client and name == "owned-agent" and version == "1"
        conversation_ids.append(f"owned-conversation-{len(conversation_ids) + 1}")
        if setup_fails:
            raise ConnectionError("WebSocket fixture failed")

    monkeypatch.setattr(helpers, "_hold_greeting", hold_greeting)
    ready = AsyncMock(side_effect=[("owned-item-1",), ("owned-item-2",)])
    monkeypatch.setattr(helpers, "_wait_for_recording", ready)
    if setup_fails:
        with pytest.raises(ConnectionError, match="WebSocket fixture failed"):
            await preparer._create_fixture("owned-agent", "live-model-test")
        client.beta.voice_agents.live_conversations.delete.assert_awaited_once_with(
            "owned-agent", "owned-conversation-1"
        )
        ready.assert_not_awaited()
    else:
        fixture = await preparer._create_fixture("owned-agent", "live-model-test")
        assert fixture.conversation_ids == ("owned-conversation-1", "owned-conversation-2")
        assert fixture.item_ids == (("owned-item-1",), ("owned-item-2",))
        assert fixture.version == "1"
        client.agents.delete_version.assert_not_awaited()
        preparer.fixture = fixture
        await preparer._cleanup_fixture()
        assert client.beta.voice_agents.live_conversations.delete.await_count == 2
    client.agents.delete_version.assert_awaited_once_with(agent_name="owned-agent", agent_version="1")
    client.agents.delete.assert_not_called()
    definition = client.agents.create_version.call_args.kwargs["definition"]
    assert definition.store is True and definition.sub_protocol == "live"
    assert definition.greeting.text


@pytest.mark.parametrize("channels", [1, 2])
def test_recorded_audio_assertions_parse_pcm_shape_duration_and_agent_channel(channels):
    audio = _audio(channels)
    helpers.assert_audio_metadata(audio, "conversation-test", item_id="item-test" if channels == 1 else None)
    helpers.assert_wav(_wav(channels), audio)


@pytest.mark.parametrize("failure", ["silent", "truncated", "wrong-duration", "wrong-format"])
def test_recorded_audio_assertions_reject_success_shaped_but_invalid_audio(failure):
    audio = _audio()
    content = _wav(silent=failure == "silent")
    if failure == "truncated":
        content = content[:-2]
    elif failure == "wrong-duration":
        audio.duration_ms = datetime.timedelta(seconds=5)
    elif failure == "wrong-format":
        content = b"not-a-wave-recording"
    with pytest.raises(AssertionError):
        helpers.assert_wav(content, audio)


def test_recorded_audio_requires_actual_managed_content_and_transcript():
    audio = _audio()
    assert isinstance(audio, models.VoiceAudioItem)
    audio.blob_uri = "https://example.invalid/customer-recording"
    with pytest.raises(AssertionError, match="managed content"):
        helpers.assert_audio_metadata(audio, "conversation-test", item_id="item-test")
    audio.blob_uri = None
    item = models.VoiceAgentLiveOutputConversationItem(id="item-test", transcription=" ", audio=audio)
    with pytest.raises(AssertionError):
        helpers.assert_speech_item(item)
    item.transcription = "A synthetic recorded greeting."
    helpers.assert_speech_item(item, "item-test")


@pytest.mark.parametrize("status", ["in_progress", "failed"])
def test_recorded_conversation_must_be_durably_completed(status):
    conversation = models.VoiceAgentLiveConversation(
        {"id": "conversation-test", "status": status, "created_at": 1, "completed_at": 2}
    )
    with pytest.raises(AssertionError):
        helpers.assert_completed_conversation(conversation, "conversation-test")


@pytest.mark.parametrize("invalid", ["route", "status", "header"])
def test_recorded_http_assertions_reject_old_routes_wrong_status_or_missing_preview(invalid):
    response = SimpleNamespace(
        http_response=SimpleNamespace(status_code=200),
        http_request=SimpleNamespace(
            url="https://example.invalid/agents/agent-test/endpoint/protocols/voice/live/conversations",
            headers={"Foundry-Features": "VoiceAgents=V1Preview"},
        ),
    )
    if invalid == "route":
        response.http_request.url = response.http_request.url.replace("/live/", "/")
    elif invalid == "status":
        response.http_response.status_code = 204
    else:
        response.http_request.headers["Foundry-Features"] = "wrong-feature"
    with pytest.raises(AssertionError):
        helpers.assert_live_status(200)(response)
