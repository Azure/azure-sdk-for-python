# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Recording-only Live fixtures and shared REST assertions.

The preparer runs outside the recorded decorator. Recording creates two owned
stored greeting sessions and waits for durable audio before REST recording
starts. Playback uses sanitized IDs and never opens a WebSocket or creates an
agent. Recording uses an existing GPT Live deployment and needs no microphone
or prerecorded audio file.
"""

import array
import asyncio
import base64
from contextlib import AsyncExitStack
from dataclasses import dataclass
import datetime
import functools
import io
import re
import sys
import time
from typing import Any
from urllib.parse import urlsplit
import uuid
import wave

from azure.ai.projects import models
from azure.ai.projects.aio import AIProjectClient
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
from devtools_testutils import EnvironmentVariableLoader, add_general_regex_sanitizer, is_live
from devtools_testutils.preparers import AbstractPreparer


liveConversationServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_voice_live_model_name="sanitized-live-deployment-name",
)

_AGENT = "sanitized-live-rest-agent"
_CONVERSATIONS = ("sanitized-live-conversation-1", "sanitized-live-conversation-2")
_SILENCE = bytes(2400)
_SESSION_TIMEOUT = 45
_FINALIZATION_TIMEOUT = 90


@dataclass(frozen=True)
class LiveConversationFixture:
    agent_name: str
    conversation_ids: tuple[str, ...]
    item_ids: tuple[tuple[str, ...], ...] = ()
    version: str = ""


def playback_fixture() -> LiveConversationFixture:
    return LiveConversationFixture(_AGENT, _CONVERSATIONS)


def add_live_conversation_sanitizers(fixture: LiveConversationFixture) -> None:
    pairs = [(fixture.agent_name, _AGENT)]
    for index, conversation_id in enumerate(fixture.conversation_ids):
        pairs.append((conversation_id, _CONVERSATIONS[index]))
        for item_index, item_id in enumerate(fixture.item_ids[index]):
            pairs.append((item_id, f"sanitized-live-item-{index + 1}-{item_index + 1}"))
    for actual, replacement in pairs:
        add_general_regex_sanitizer(regex=re.escape(actual), value=replacement, function_scoped=True)


def _check_live_error(event: Any) -> None:
    if event.get("type") == "error":
        error = event.get("error") or {}
        raise RuntimeError(f"Live recording fixture failed: {error.get('code')}: {error.get('message')}")


async def _receive_event(connection, event_type: str):
    deadline = time.monotonic() + _SESSION_TIMEOUT
    while time.monotonic() < deadline:
        event = await asyncio.wait_for(connection.recv(), timeout=deadline - time.monotonic())
        _check_live_error(event)
        if event.get("type") == event_type:
            return event
        if event.get("type") == "session.closed":
            raise RuntimeError(f"Live recording fixture closed early: {event.get('reason')}")
    raise TimeoutError(f"Live recording fixture did not receive {event_type}")


async def _hold_greeting(client: AIProjectClient, agent_name: str, version: str, conversations: list[str]) -> None:
    async with client.beta.voice_agents.live.connect(
        agent_name=agent_name, agent_version=version, store=True
    ) as connection:
        started = await _receive_event(connection, "session.started")
        assert started.conversation_id and started.conversation_id != started.session.id
        conversations.append(started.conversation_id)
        stop = asyncio.Event()

        async def clock():
            while not stop.is_set():
                await connection.session.input_audio.append(audio=_SILENCE)
                await asyncio.sleep(0.05)

        sender = asyncio.create_task(clock())
        speech = False
        transcript = ""
        last_content = time.monotonic()
        deadline = time.monotonic() + _SESSION_TIMEOUT
        try:
            while time.monotonic() < deadline:
                if sender.done():
                    sender.result()
                if speech and transcript.strip() and time.monotonic() - last_content >= 2:
                    break
                try:
                    event = await asyncio.wait_for(connection.recv(), timeout=min(0.5, deadline - time.monotonic()))
                except asyncio.TimeoutError:
                    continue
                _check_live_error(event)
                if isinstance(event, models.LiveOutputAudioDelta):
                    pcm = base64.b64decode(event.delta, validate=True)
                    assert len(pcm) % 2 == 0
                    if any(
                        abs(int.from_bytes(pcm[i : i + 2], "little", signed=True)) > 256 for i in range(0, len(pcm), 2)
                    ):
                        speech = True
                        last_content = time.monotonic()
                elif isinstance(event, models.LiveServerEventLiveOutputTranscriptDelta):
                    transcript += event.delta
                    if event.delta.strip():
                        last_content = time.monotonic()
                elif event.get("type") == "session.closed":
                    raise RuntimeError("Live recording fixture ended before greeting audio was captured")
            else:
                raise TimeoutError("Live recording fixture did not finish greeting speech")
        finally:
            stop.set()
            try:
                await sender
            finally:
                await connection.session.close()
                closed = await _receive_event(connection, "session.closed")
                assert closed.reason == "close_requested"


async def _wait_for_recording(client: AIProjectClient, agent_name: str, conversation_id: str) -> tuple[str, ...]:
    operations = client.beta.voice_agents.live_conversations
    deadline = time.monotonic() + _FINALIZATION_TIMEOUT
    while time.monotonic() < deadline:
        try:
            conversation = await operations.get(agent_name, conversation_id)
        except ResourceNotFoundError:
            await asyncio.sleep(1)
            continue
        if conversation.status == "failed":
            raise AssertionError(f"Live recording persistence failed: {conversation.last_error}")
        if conversation.status == "completed":
            try:
                recording = await operations.get_audio(agent_name, conversation_id)
            except HttpResponseError as exc:
                if exc.status_code != 409 or getattr(exc.error, "code", None) != "recording_not_ready":
                    raise
            else:
                assert recording.blob_uri is None, "Recorded audio tests require Foundry-managed storage, not BYOS"
                items = [item async for item in operations.list_items(agent_name, conversation_id)]
                assert items and any(
                    isinstance(item, models.VoiceAgentLiveOutputConversationItem) and item.audio is not None
                    for item in items
                )
                return tuple(item.id for item in items)
        await asyncio.sleep(1)
    raise TimeoutError("Live recording fixture did not reach completed persistence/audio state")


async def _delete_fixture(client: AIProjectClient, fixture: LiveConversationFixture) -> None:
    async def delete_conversation(conversation_id: str) -> None:
        try:
            await client.beta.voice_agents.live_conversations.delete(fixture.agent_name, conversation_id)
        except ResourceNotFoundError:
            pass

    async with AsyncExitStack() as cleanup:
        cleanup.push_async_callback(
            client.agents.delete_version, agent_name=fixture.agent_name, agent_version=fixture.version
        )
        for conversation_id in reversed(fixture.conversation_ids):
            cleanup.push_async_callback(delete_conversation, conversation_id)


class LiveConversationPreparer(AbstractPreparer):
    def __init__(self) -> None:
        super().__init__("live-rest-", 24, disable_recording=True)
        self.resource_moniker = _AGENT
        self.fixture: LiveConversationFixture | None = None
        self.endpoint: str | None = None

    def create_resource(self, name, **kwargs):
        self.fixture = None
        self.endpoint = None
        if not is_live():
            return {"live_conversation_fixture": playback_fixture()}
        self.endpoint = kwargs["foundry_project_endpoint"]
        model = kwargs["foundry_voice_live_model_name"]
        self.fixture = asyncio.run(self._create_fixture(f"{name}-{uuid.uuid4().hex[:8]}", model))
        return {"live_conversation_fixture": self.fixture}

    async def _create_fixture(self, agent_name: str, model: str) -> LiveConversationFixture:
        endpoint = self.endpoint
        assert isinstance(endpoint, str) and endpoint.strip(), "A recording fixture needs a project endpoint"
        credential = self.test_class_instance.get_credential(AIProjectClient, is_async=True)
        async with credential, AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as client:
            agent = None
            conversation_ids: list[str] = []
            complete = False
            try:
                agent = await client.agents.create_version(
                    agent_name=agent_name,
                    definition=models.VoiceAgentLiveDefinition(
                        model=model,
                        instructions="Greet the caller briefly.",
                        greeting=models.VoiceAgentTemplateGreetingConfig(text="Hello, welcome."),
                        audio=models.LiveInitialSessionAudioParam(
                            format=models.LiveSessionAudioFormatPCMParam(rate=24000),
                            output=models.LiveInitialSessionAudioOutputParam(voice="marin"),
                        ),
                        delegation=models.LiveClientDelegationParam(),
                        store=True,
                    ),
                )
                items = []
                for _ in _CONVERSATIONS:
                    await _hold_greeting(client, agent_name, agent.version, conversation_ids)
                    items.append(await _wait_for_recording(client, agent_name, conversation_ids[-1]))
                fixture = LiveConversationFixture(agent_name, tuple(conversation_ids), tuple(items), agent.version)
                complete = True
                return fixture
            finally:
                if agent is not None and not complete:
                    await _delete_fixture(
                        client, LiveConversationFixture(agent_name, tuple(conversation_ids), version=agent.version)
                    )

    def remove_resource(self, name, **kwargs):
        if self.fixture is not None:
            asyncio.run(self._cleanup_fixture())
            self.fixture = None
            self.endpoint = None

    async def _cleanup_fixture(self) -> None:
        fixture, endpoint = self.fixture, self.endpoint
        assert fixture is not None and isinstance(endpoint, str), "No owned recording fixture was prepared"
        credential = self.test_class_instance.get_credential(AIProjectClient, is_async=True)
        async with credential, AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as client:
            await _delete_fixture(client, fixture)


def assert_live_status(expected: int):
    def verify(response):
        assert response.http_response.status_code == expected
        assert "/protocols/voice/live/conversations" in urlsplit(response.http_request.url).path
        assert response.http_request.headers["Foundry-Features"] == "VoiceAgents=V1Preview"

    return verify


def assert_completed_conversation(conversation, conversation_id: str) -> None:
    assert isinstance(conversation, models.VoiceAgentLiveConversation)
    assert conversation.id == conversation_id
    assert conversation.object == "voice.conversation" and conversation.status == "completed"
    assert isinstance(conversation.created_at, datetime.datetime)
    assert isinstance(conversation.completed_at, datetime.datetime)
    assert conversation.last_error is None


def assert_speech_item(item, expected_id: str | None = None) -> models.VoiceAgentLiveOutputConversationItem:
    assert isinstance(item, models.VoiceAgentLiveOutputConversationItem)
    assert item.id and (expected_id is None or item.id == expected_id)
    assert item.transcription and item.transcription.strip()
    assert isinstance(item.audio, models.VoiceAudioItem)
    assert item.audio.item_id == item.id
    return item


def assert_audio_metadata(audio, conversation_id: str, *, item_id: str | None = None) -> None:
    assert audio.conversation_id == conversation_id
    assert audio.format == "wav" and audio.sample_rate == 24000
    assert isinstance(audio.duration_ms, datetime.timedelta) and audio.duration_ms.total_seconds() > 0
    assert audio.blob_uri is None, "This test must exercise the Foundry-managed content routes"
    if item_id is None:
        assert isinstance(audio, models.VoiceRecording) and audio.channels == 2
        assert audio.channel_layout.left == "user" and audio.channel_layout.right == "agent"
    else:
        assert isinstance(audio, models.VoiceAudioItem) and audio.item_id == item_id
        assert audio.role == "agent" and audio.channels == 1 and audio.codec == "pcm16"


def assert_wav(content: bytes, metadata) -> None:
    assert content[:4] == b"RIFF" and content[8:12] == b"WAVE"
    with wave.open(io.BytesIO(content), "rb") as recording:
        assert recording.getcomptype() == "NONE" and recording.getsampwidth() == 2
        assert recording.getframerate() == metadata.sample_rate
        assert recording.getnchannels() == metadata.channels
        frames = recording.getnframes()
        pcm = recording.readframes(frames)
        assert frames > 0 and len(pcm) == frames * metadata.channels * 2
        assert abs(frames / metadata.sample_rate - metadata.duration_ms.total_seconds()) <= 0.01
    samples = array.array("h", pcm)
    if sys.byteorder != "little":
        samples.byteswap()
    channel = 1 if metadata.channels == 2 else 0
    assert any(abs(sample) > 256 for sample in samples[channel :: metadata.channels]), "Expected non-silent agent audio"
