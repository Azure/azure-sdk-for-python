# pylint: disable=too-many-lines,line-too-long,useless-suppression,too-many-statements,broad-exception-caught
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Recorded tests covering the read-only voice-agent conversation REST API surface exposed through
``project_client.beta.agent_endpoint_conversations`` (async client).

Async counterpart of ``test_voice_agent_conversations.py``. See that module's docstring for the
overall rationale (live-only setup to obtain a real conversation id, sanitized to a fixed
placeholder so the recorded REST calls that follow can be replayed).
"""

import re
import asyncio
import time
from typing import Final, Optional

from test_base import TestBase, servicePreparer
from devtools_testutils import is_live, add_general_regex_sanitizer
from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError
from azure.ai.projects.models import (
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventResponseDone,
    RealtimeServerEventSessionCreated,
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceModelType,
    VoiceOutputModality,
)

# Fixed test-owned agent name: unlike conversation_id (server-generated, truly dynamic), this is
# our own choice and does not need is_live()/sanitizer handling -- it is identical in both modes.
_AGENT_NAME: Final = "test-conversations-read-agent-async"

# Best-effort fixed wait (live only, seconds) after the realtime session ends, before reading the
# conversation back, so persistence finalization (items/audio) is more likely to have completed.
# This must be a single, fixed wait rather than a poll loop through the recorded client: repeated
# polling would record multiple cassette entries for the same "get conversation" request, but
# playback only ever issues that request once (polling itself is live-only), so a replay would
# incorrectly consume the *first* (possibly still "in_progress") recorded entry instead of the
# settled one. A single wait keeps exactly one logical call -- and therefore one cassette entry
# -- for both the live recording and the replay to agree on.
_FINALIZATION_WAIT_SECONDS: Final = 30


async def _create_live_conversation(project_client, model: str) -> str:
    """Create a `store=True` voice agent, hold one turn over a live realtime session, and
    return the resulting conversation id. Only ever called when ``is_live()``.

    :param project_client: The Foundry project client.
    :param model: The realtime model deployment name.
    :type project_client: ~azure.ai.projects.aio.AIProjectClient
    :type model: str
    :return: The persisted conversation id.
    :rtype: str
    """
    try:
        await project_client.agents.delete(agent_name=_AGENT_NAME)
    except Exception:  # pylint: disable=broad-except
        pass

    await project_client.agents.create_version(
        agent_name=_AGENT_NAME,
        definition=VoiceAgentDefinition(
            model_type=VoiceModelType.MANAGED,
            model=model,
            instructions="You are a helpful voice assistant. Keep replies short.",
            audio=VoiceAgentAudioConfig(
                output=VoiceAgentAudioOutputConfig(voice="en-US-AvaNeural", voice_type="azure-standard")
            ),
            output_modalities=[VoiceOutputModality.AUDIO],
            store=True,
        ),
    )

    conversation_id: Optional[str] = None
    async with project_client.realtime.connect(agent_name=_AGENT_NAME) as conn:
        session_created = await asyncio.wait_for(conn.recv(), timeout=30)
        assert isinstance(session_created, RealtimeServerEventSessionCreated)
        conversation_id = session_created.conversation_id

        await conn.conversation.item.create(
            item=RealtimeConversationItemMessageUser(
                type=RealtimeConversationItemType.MESSAGE,
                content=[RealtimeConversationItemMessageUserContent(type="input_text", text="Say hello.")],
            )
        )
        await conn.response.create()

        got_response_done = False
        deadline = time.monotonic() + 45
        while time.monotonic() < deadline and not got_response_done:
            remaining = max(deadline - time.monotonic(), 0.1)
            event = await asyncio.wait_for(conn.recv(), timeout=min(30, remaining))
            if isinstance(event, RealtimeServerEventResponseDone):
                got_response_done = True

    assert conversation_id is not None, "Expected session.created to carry a conversation_id (store=True)"
    await asyncio.sleep(_FINALIZATION_WAIT_SECONDS)
    return conversation_id


class TestVoiceAgentConversationsAsync(TestBase):
    """
    Recorded tests covering the read-only voice-agent conversation REST API surface exposed
    through ``project_client.beta.agent_endpoint_conversations`` (conversation envelope,
    responses, items, and audio), using the async client.

    NOTE: The top-level (non-beta) ``agent_endpoint_conversations.get_agent_conversation_item_
    generated_audio*`` methods are intentionally NOT covered here: they return the played-back-
    interrupted subordinate "generated" audio, which requires deliberately barging in mid-reply
    during a live session to produce -- not exercised by the simple single-turn conversation
    created here. See this package's engineering notes.
    """

    # To run only this test:
    # pytest tests\agents\test_voice_agent_conversations_async.py::TestVoiceAgentConversationsAsync::test_read_conversation_async -s
    @servicePreparer()
    @recorded_by_proxy_async()
    async def test_read_conversation_async(self, **kwargs):  # pylint: disable=too-many-locals
        """
        Test reading back a persisted voice-agent conversation: the envelope, its responses
        (with per-response output items), its ordered items (the transcript), the merged
        whole-call audio recording, a single item's audio, and finally deleting the conversation.

        Routes used in this test: see the sync counterpart's docstring in
        ``test_voice_agent_conversations.py`` for the full route table (identical here).
        """
        print("\n")
        project_client = self.create_async_client(operation_group="agents", allow_preview=True, **kwargs)
        conversations = project_client.beta.agent_endpoint_conversations

        async with project_client:
            if is_live():
                model = kwargs.get("foundry_voice_model_name")
                assert model is not None
                conversation_id = await _create_live_conversation(project_client, model)
                add_general_regex_sanitizer(
                    regex=re.escape(conversation_id), value="sanitized-conversation-id", function_scoped=True
                )
            else:
                conversation_id = "sanitized-conversation-id"

            try:
                # The conversation should appear in the agent's conversation list.
                found = False
                async for c in conversations.list_agent_conversations(_AGENT_NAME):
                    if c.id == conversation_id:
                        found = True
                        break
                assert found, "Expected the new conversation to appear in list_agent_conversations"

                # The conversation envelope.
                conversation = await conversations.get_agent_conversation(_AGENT_NAME, conversation_id)
                assert conversation.id == conversation_id
                assert conversation.status in ("in_progress", "completed", "failed")
                assert conversation.created_at is not None

                # The responses (model inference turns) in the conversation.
                responses = [
                    r async for r in conversations.list_agent_conversation_responses(_AGENT_NAME, conversation_id)
                ]
                assert len(responses) >= 1
                first_response = responses[0]
                response_detail = await conversations.get_agent_conversation_response(
                    _AGENT_NAME, conversation_id, first_response.id
                )
                assert response_detail.id == first_response.id

                # The items produced by that response (does not raise; count may be 0 or more).
                _ = [
                    item
                    async for item in conversations.list_agent_conversation_response_items(
                        _AGENT_NAME, conversation_id, first_response.id
                    )
                ]

                # The ordered conversation items -- the full transcript (user + assistant + tool events).
                items = [
                    item async for item in conversations.list_agent_conversation_items(_AGENT_NAME, conversation_id)
                ]
                assert len(items) >= 1
                first_item_id = items[0].get("id")
                assert first_item_id
                fetched_item = await conversations.get_agent_conversation_item(
                    _AGENT_NAME, conversation_id, first_item_id
                )
                assert fetched_item.get("id") == first_item_id

                # The merged whole-call recording, if the session had time to finalize.
                if str(conversation.status) == "completed" or conversation.status == "completed":
                    recording = await conversations.get_agent_conversation_audio(_AGENT_NAME, conversation_id)
                    assert recording.format is not None
                    if not recording.blob_uri:
                        audio_chunks = [
                            chunk
                            async for chunk in await conversations.get_agent_conversation_audio_content(
                                _AGENT_NAME, conversation_id
                            )
                        ]
                        assert len(b"".join(audio_chunks)) > 0

                    # A single item's audio, if any item has one.
                    for item in items:
                        item_id = item.get("id")
                        if not item_id:
                            continue
                        try:
                            item_audio = await conversations.get_agent_conversation_item_audio(
                                _AGENT_NAME, conversation_id, item_id
                            )
                        except HttpResponseError as e:
                            if e.status_code == 404:
                                continue
                            raise
                        assert item_audio.role is not None
                        if not item_audio.blob_uri:
                            item_audio_chunks = [
                                chunk
                                async for chunk in await conversations.get_agent_conversation_item_audio_content(
                                    _AGENT_NAME, conversation_id, item_id
                                )
                            ]
                            assert len(b"".join(item_audio_chunks)) > 0
                        break
                else:
                    print(
                        f"Conversation did not finalize in time (status={conversation.status}); skipping audio checks."
                    )
            finally:
                # Deleting a conversation removes it and all of its responses, items, and audio.
                await conversations.delete_agent_conversation(_AGENT_NAME, conversation_id)
                if is_live():
                    await project_client.agents.delete(agent_name=_AGENT_NAME)
