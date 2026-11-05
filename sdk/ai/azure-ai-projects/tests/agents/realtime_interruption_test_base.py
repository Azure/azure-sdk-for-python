# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Prepare an owned interrupted response outside HTTP recording; playback is offline."""

import asyncio
from contextlib import AsyncExitStack
from dataclasses import dataclass
import functools
import logging
from pathlib import Path
import re
import runpy
from urllib.parse import urlsplit
from uuid import uuid4

from azure.ai.projects import models
from azure.ai.projects.aio import AIProjectClient
from azure.core.exceptions import ResourceNotFoundError
from devtools_testutils import EnvironmentVariableLoader, add_general_regex_sanitizer, is_live
from devtools_testutils.preparers import AbstractPreparer

from live_conversation_test_base import assert_wav


_LOGGER = logging.getLogger(__name__)
_AGENT = "sanitized-interrupted-audio-agent"
_CONVERSATION = "sanitized-interrupted-conversation"
_ITEM = "sanitized-interrupted-item"

interruptionServicePreparer = functools.partial(
    EnvironmentVariableLoader,
    "",
    foundry_project_endpoint="https://sanitized-account-name.services.ai.azure.com/api/projects/sanitized-project-name",
    foundry_voice_model_name="sanitized-realtime-deployment-name",
)


@dataclass(frozen=True)
class RealtimeInterruptionFixture:
    agent_name: str
    conversation_id: str
    item_id: str
    version: str = ""


def playback_fixture() -> RealtimeInterruptionFixture:
    return RealtimeInterruptionFixture(_AGENT, _CONVERSATION, _ITEM)


def _sample_helpers():
    path = Path(__file__).parents[2] / "samples" / "agents" / "voice" / "realtime_interruption_utils.py"
    return runpy.run_path(str(path))


async def _delete_fixture(client: AIProjectClient, fixture: RealtimeInterruptionFixture) -> None:
    async def delete_conversation() -> None:
        if fixture.conversation_id:
            try:
                await client.beta.voice_agents.conversations.delete(fixture.agent_name, fixture.conversation_id)
            except ResourceNotFoundError:
                _LOGGER.info("Owned interrupted conversation was not persisted or was already deleted.")

    async def delete_agent() -> None:
        try:
            await client.agents.delete(agent_name=fixture.agent_name)
        except ResourceNotFoundError:
            _LOGGER.info("Owned interruption agent was not created or was already deleted.")

    async with AsyncExitStack() as cleanup:
        cleanup.push_async_callback(delete_agent)
        cleanup.push_async_callback(delete_conversation)


class RealtimeInterruptionPreparer(AbstractPreparer):
    def __init__(self) -> None:
        super().__init__("interrupted-audio-", 32, disable_recording=True)
        self.resource_moniker = _AGENT
        self.fixture: RealtimeInterruptionFixture | None = None
        self.endpoint: str | None = None

    def create_resource(self, name, **kwargs):
        self.fixture = None
        self.endpoint = None
        if not is_live():
            return {"interrupted_audio_fixture": playback_fixture()}
        self.endpoint = kwargs["foundry_project_endpoint"]
        model = kwargs["foundry_voice_model_name"]
        self.fixture = asyncio.run(self._create_fixture(f"voice-interruption-{uuid4().hex}", model))
        return {"interrupted_audio_fixture": self.fixture}

    async def _create_fixture(self, agent_name: str, model: str) -> RealtimeInterruptionFixture:
        helpers = _sample_helpers()
        turn = helpers["InterruptedTurn"]()
        assert self.endpoint, "A live recording requires a configured project endpoint"
        credential = self.test_class_instance.get_credential(AIProjectClient, is_async=True)
        async with (
            credential,
            AIProjectClient(endpoint=self.endpoint, credential=credential, allow_preview=True) as client,
        ):
            agent = None
            completed = False
            try:
                agent = await client.agents.create_version(
                    agent_name=agent_name, definition=helpers["interruption_definition"](model)
                )
                async with client.beta.voice_agents.realtime.connect(agent_name=agent_name) as connection:
                    await helpers["interrupt_reply_async"](connection, turn)
                await helpers["wait_for_generated_audio_async"](client, agent_name, turn)
                fixture = RealtimeInterruptionFixture(
                    agent_name, turn.conversation_id, turn.stored_item_id, agent.version
                )
                completed = True
                return fixture
            finally:
                if not completed and agent is not None:
                    await _delete_fixture(
                        client,
                        RealtimeInterruptionFixture(
                            agent_name, turn.conversation_id, turn.stored_item_id, agent.version
                        ),
                    )

    def remove_resource(self, name, **kwargs):
        if self.fixture is not None:
            asyncio.run(self._cleanup_fixture())
            self.fixture = None
            self.endpoint = None

    async def _cleanup_fixture(self) -> None:
        fixture, endpoint = self.fixture, self.endpoint
        assert fixture is not None and endpoint
        credential = self.test_class_instance.get_credential(AIProjectClient, is_async=True)
        async with credential, AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as client:
            await _delete_fixture(client, fixture)


def add_interruption_sanitizers(fixture: RealtimeInterruptionFixture) -> None:
    for actual, replacement in (
        (fixture.agent_name, _AGENT),
        (fixture.conversation_id, _CONVERSATION),
        (fixture.item_id, _ITEM),
    ):
        add_general_regex_sanitizer(regex=re.escape(actual), value=replacement, function_scoped=True)


def assert_generated_status(expected: int):
    def verify(response):
        assert response.http_response.status_code == expected
        path = urlsplit(response.http_request.url).path
        assert "/protocols/voice/conversations/" in path
        assert "/audio/generated" in path
        assert response.http_request.headers["Foundry-Features"] == "VoiceAgents=V1Preview"

    return verify


def assert_conversation_deleted(response) -> None:
    assert response.http_response.status_code == 204
    assert "/protocols/voice/conversations/" in urlsplit(response.http_request.url).path
    assert response.http_request.headers["Foundry-Features"] == "VoiceAgents=V1Preview"


def assert_generated_metadata(metadata, fixture: RealtimeInterruptionFixture) -> None:
    assert isinstance(metadata, models.VoiceGeneratedAudioItem)
    assert metadata.conversation_id == fixture.conversation_id and metadata.item_id == fixture.item_id
    assert metadata.role == "agent" and metadata.codec == "pcm16"
    assert metadata.format == "wav" and metadata.sample_rate == 24000 and metadata.channels == 1
    assert metadata.duration_ms is not None and metadata.duration_ms.total_seconds() > 0
    assert metadata.blob_uri is None, "This recording must exercise the Foundry-managed content route"


def assert_generated_wav(content: bytes, metadata, fixture: RealtimeInterruptionFixture) -> None:
    assert_generated_metadata(metadata, fixture)
    assert_wav(content, metadata)
