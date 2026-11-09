# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline guards for sync REST samples and async WebSocket samples."""

import base64
import io
from pathlib import Path
import runpy
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
import wave

import pytest

from azure.ai.projects import models
from azure.core.exceptions import ResourceNotFoundError

_SAMPLES = Path(__file__).parents[2] / "samples" / "agents" / "voice"


def _environment(monkeypatch):
    monkeypatch.syspath_prepend(str(_SAMPLES))
    monkeypatch.setattr("dotenv.load_dotenv", lambda: None)
    monkeypatch.setenv("FOUNDRY_PROJECT_ENDPOINT", "https://example.invalid/api/projects/test")
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_MODEL", "realtime-deployment-test")
    monkeypatch.delenv("FOUNDRY_VOICE_RECORDING_OUTPUT_PATH", raising=False)


@pytest.fixture
def websocket_sample(monkeypatch):
    _environment(monkeypatch)
    monkeypatch.delenv("FOUNDRY_VOICE_AGENT_NAME", raising=False)
    credential = MagicMock()
    credential.__aenter__ = AsyncMock(return_value=credential)
    credential.__aexit__ = AsyncMock(return_value=False)
    client = MagicMock()
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)
    client.agents.create_version = AsyncMock(return_value=SimpleNamespace(version="owned-version"))
    client.agents.delete_version = AsyncMock()
    client.voice_agents.conversations.delete = AsyncMock()
    connection = MagicMock()
    connection.recv = AsyncMock(
        side_effect=[
            {"type": "session.created", "conversation_id": "conversation-test"},
            {"type": "response.created", "response": {"id": "response-test"}},
            {
                "type": "response.output_audio.delta",
                "response_id": "response-test",
                "item_id": "item-test",
                "delta": base64.b64encode(b"\x00\x08" * 4800).decode(),
            },
            {"type": "response.done", "response": {"id": "response-test", "status": "cancelled"}},
            {"type": "conversation.item.truncated", "item_id": "item-test", "audio_end_ms": 0},
        ]
    )
    connection.response.create = AsyncMock()
    connection.response.cancel = AsyncMock()
    connection.conversation.item.create = AsyncMock()
    connection.conversation.item.truncate = AsyncMock()
    manager = client.voice_agents.realtime.connect.return_value
    manager.__aenter__ = AsyncMock(return_value=connection)
    manager.__aexit__ = AsyncMock(return_value=False)
    monkeypatch.setattr("azure.identity.aio.DefaultAzureCredential", MagicMock(return_value=credential))
    monkeypatch.setattr("azure.ai.projects.aio.AIProjectClient", MagicMock(return_value=client))
    sample = runpy.run_path(str(_SAMPLES / "sample_voice_agent_realtime_interruption_async.py"))
    return SimpleNamespace(sample=sample, client=client, connection=connection)


@pytest.mark.asyncio
async def test_async_interruption_confirms_control_events_and_cleans_owned_resources(websocket_sample):
    env = websocket_sample
    await env.sample["main"]()
    name = env.client.agents.create_version.call_args.kwargs["agent_name"]
    env.connection.response.cancel.assert_awaited_once_with(response_id="response-test")
    env.connection.conversation.item.truncate.assert_awaited_once_with(
        item_id="item-test", content_index=0, audio_end_ms=0
    )
    env.client.voice_agents.conversations.delete.assert_awaited_once_with(name, "conversation-test")
    env.client.agents.delete_version.assert_awaited_once_with(agent_name=name, agent_version="owned-version")
    env.client.voice_agents.conversations.download_generated_audio_item.assert_not_called()


@pytest.mark.asyncio
async def test_async_interruption_create_failure_cannot_delete_existing_resources(websocket_sample):
    env = websocket_sample
    env.client.agents.create_version.side_effect = RuntimeError("create failed")
    with pytest.raises(RuntimeError, match="create failed"):
        await env.sample["main"]()
    env.client.agents.delete_version.assert_not_called()
    env.client.voice_agents.conversations.delete.assert_not_called()


@pytest.mark.asyncio
async def test_async_interruption_stream_failure_still_cleans_its_owned_resources(websocket_sample):
    env = websocket_sample
    env.connection.recv.side_effect = [
        {"type": "session.created", "conversation_id": "conversation-test"},
        {"type": "error", "error": {"code": "invalid_request", "message": "synthetic failure"}},
    ]
    with pytest.raises(RuntimeError, match="synthetic failure"):
        await env.sample["main"]()
    name = env.client.agents.create_version.call_args.kwargs["agent_name"]
    env.client.voice_agents.conversations.delete.assert_awaited_once_with(name, "conversation-test")
    env.client.agents.delete_version.assert_awaited_once_with(agent_name=name, agent_version="owned-version")


@pytest.fixture
def rest_sample(monkeypatch):
    _environment(monkeypatch)
    monkeypatch.setenv("FOUNDRY_VOICE_AGENT_NAME", "existing-agent")
    monkeypatch.setenv("FOUNDRY_VOICE_CONVERSATION_ID", "conversation-test")
    monkeypatch.setenv("FOUNDRY_VOICE_ITEM_ID", "stored-item-test")
    credential = MagicMock()
    credential.__enter__.return_value = credential
    client = MagicMock()
    client.__enter__.return_value = client
    conversations = client.voice_agents.conversations
    conversations.get_generated_audio_item.return_value = models.VoiceGeneratedAudioItem(
        conversation_id="conversation-test", item_id="stored-item-test", format="wav"
    )
    output = io.BytesIO()
    with wave.open(output, "wb") as recording:
        recording.setparams((1, 2, 24000, 0, "NONE", "not compressed"))
        recording.writeframes(b"\x00\x08" * 1200)
    conversations.download_generated_audio_item.return_value = iter([output.getvalue()])
    monkeypatch.setattr("azure.identity.DefaultAzureCredential", MagicMock(return_value=credential))
    monkeypatch.setattr("azure.ai.projects.AIProjectClient", MagicMock(return_value=client))
    sample = runpy.run_path(str(_SAMPLES / "sample_voice_agent_read_generated_audio.py"))
    return SimpleNamespace(sample=sample, client=client, conversations=conversations)


def test_sync_rest_sample_only_reads_existing_resources(rest_sample):
    env = rest_sample
    env.sample["main"]()
    env.conversations.get_generated_audio_item.assert_called_once_with(
        "existing-agent", "conversation-test", "stored-item-test"
    )
    env.conversations.download_generated_audio_item.assert_called_once_with(
        "existing-agent", "conversation-test", "stored-item-test"
    )
    env.client.agents.create_version.assert_not_called()
    env.conversations.delete.assert_not_called()
    env.client.voice_agents.realtime.connect.assert_not_called()
    env.client.beta.voice_agents.live.connect.assert_not_called()


def test_sync_rest_sample_reports_missing_artifacts_without_success_fallback(rest_sample):
    env = rest_sample
    env.conversations.get_generated_audio_item.side_effect = ResourceNotFoundError("missing artifact")
    with pytest.raises(ResourceNotFoundError):
        env.sample["main"]()
    env.conversations.download_generated_audio_item.assert_not_called()


def test_sync_rest_sample_never_overwrites_an_existing_output(rest_sample, monkeypatch, tmp_path):
    destination = tmp_path / "existing.wav"
    destination.write_bytes(b"keep")
    monkeypatch.setenv("FOUNDRY_VOICE_RECORDING_OUTPUT_PATH", str(destination))
    with pytest.raises(FileExistsError):
        rest_sample.sample["main"]()
    assert destination.read_bytes() == b"keep"
    rest_sample.conversations.get_generated_audio_item.assert_not_called()
