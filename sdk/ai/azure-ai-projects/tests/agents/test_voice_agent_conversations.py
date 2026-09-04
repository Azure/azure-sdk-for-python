# pylint: disable=too-many-lines,line-too-long,useless-suppression,too-many-statements,broad-exception-caught
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# cSpell:disable

"""
Recorded tests covering the read-only voice-agent conversation REST API surface exposed through
``project_client.beta.agent_endpoint_conversations``.

Conversations, their responses/items, and audio are written by the realtime WebSocket subsystem
during a live session (see ``test_voice_agent_realtime_live.py``) and can only be *read* here --
there is no REST way to create one. A real ``conversation_id`` can therefore only be obtained by
actually running a live session, which is not itself something the test proxy can capture or
replay (it is a raw WebSocket connection, not an HTTP call through the SDK pipeline).

To get real recorded/replayable coverage of the REST read-back surface anyway, this test:
  * When run live (``AZURE_TEST_RUN_LIVE=true``): creates a `store=True` voice agent, opens a
    short-lived realtime session directly (bypassing the recorded pipeline, same as any other
    live network call), sends one turn, and waits for the resulting conversation to finalize.
    The dynamic conversation id is then sanitized to a fixed placeholder before any of the
    REST calls below are made, so what gets written to the recording cassette is stable.
  * When replayed from the recording (the normal case in CI): skips the live session entirely
    and uses the same fixed placeholder conversation id the cassette already expects.
Either way, the REST calls themselves (list/get conversation, responses, items, audio) go
through ``recorded_by_proxy`` exactly like any other recorded test in this package.
"""

import re
import time
from typing import Final, Optional

from test_base import TestBase, servicePreparer
from devtools_testutils import recorded_by_proxy, is_live, add_general_regex_sanitizer
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
_AGENT_NAME: Final = "test-conversations-read-agent"

# Best-effort fixed wait (live only, seconds) after the realtime session ends, before reading the
# conversation back, so persistence finalization (items/audio) is more likely to have completed.
# This must be a single, fixed wait rather than a poll loop through the recorded client: repeated
# polling would record multiple cassette entries for the same "get conversation" request, but
# playback only ever issues that request once (polling itself is live-only), so a replay would
# incorrectly consume the *first* (possibly still "in_progress") recorded entry instead of the
# settled one. A single wait keeps exactly one logical call -- and therefore one cassette entry
# -- for both the live recording and the replay to agree on.
_FINALIZATION_WAIT_SECONDS: Final = 30


def _create_live_conversation(project_client, model: str) -> str:
    """Create a `store=True` voice agent, hold one turn over a live realtime session, and
    return the resulting conversation id. Only ever called when ``is_live()``.

    :param project_client: The Foundry project client.
    :param model: The realtime model deployment name.
    :type project_client: ~azure.ai.projects.AIProjectClient
    :type model: str
    :return: The persisted conversation id.
    :rtype: str
    """
    try:
        project_client.agents.delete(agent_name=_AGENT_NAME)
    except Exception:  # pylint: disable=broad-except
        pass

    project_client.agents.create_version(
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
    with project_client.realtime.connect(agent_name=_AGENT_NAME) as conn:
        session_created = conn.recv(timeout=30)
        assert isinstance(session_created, RealtimeServerEventSessionCreated)
        conversation_id = session_created.conversation_id

        conn.conversation.item.create(
            item=RealtimeConversationItemMessageUser(
                type=RealtimeConversationItemType.MESSAGE,
                content=[RealtimeConversationItemMessageUserContent(type="input_text", text="Say hello.")],
            )
        )
        conn.response.create()

        deadline = time.monotonic() + 45
        while time.monotonic() < deadline:
            event = conn.recv(timeout=30)
            if isinstance(event, RealtimeServerEventResponseDone):
                break

    assert conversation_id is not None, "Expected session.created to carry a conversation_id (store=True)"
    time.sleep(_FINALIZATION_WAIT_SECONDS)
    return conversation_id


class TestVoiceAgentConversations(TestBase):
    """
    Recorded tests covering the read-only voice-agent conversation REST API surface exposed
    through ``project_client.beta.agent_endpoint_conversations`` (conversation envelope,
    responses, items, and audio).

    NOTE: The top-level (non-beta) ``agent_endpoint_conversations.get_agent_conversation_item_
    generated_audio*`` methods are intentionally NOT covered here: they return the played-back-
    interrupted subordinate "generated" audio, which requires deliberately barging in mid-reply
    during a live session to produce -- not exercised by the simple single-turn conversation
    created here. See this package's engineering notes.
    """

    # To run only this test:
    # pytest tests\agents\test_voice_agent_conversations.py::TestVoiceAgentConversations::test_read_conversation -s
    @servicePreparer()
    @recorded_by_proxy()
    def test_read_conversation(self, **kwargs):  # pylint: disable=too-many-locals
        """
        Test reading back a persisted voice-agent conversation: the envelope, its responses
        (with per-response output items), its ordered items (the transcript), the merged
        whole-call audio recording, a single item's audio, and finally deleting the conversation.

        Routes used in this test:

        Action REST API Route                                                                    Client Method
        ------+-------------------------------------------------------------------------------+-----------------------------------------------------------
        GET    /agents/{agent_name}/endpoint/protocols/voice/conversations                        beta.agent_endpoint_conversations.list_agent_conversations()
        GET    /agents/{agent_name}/endpoint/protocols/voice/conversations/{id}                    beta.agent_endpoint_conversations.get_agent_conversation()
        GET    .../conversations/{id}/responses                                                    beta.agent_endpoint_conversations.list_agent_conversation_responses()
        GET    .../conversations/{id}/responses/{response_id}                                       beta.agent_endpoint_conversations.get_agent_conversation_response()
        GET    .../conversations/{id}/responses/{response_id}/items                                 beta.agent_endpoint_conversations.list_agent_conversation_response_items()
        GET    .../conversations/{id}/items                                                         beta.agent_endpoint_conversations.list_agent_conversation_items()
        GET    .../conversations/{id}/items/{item_id}                                               beta.agent_endpoint_conversations.get_agent_conversation_item()
        GET    .../conversations/{id}/audio                                                         beta.agent_endpoint_conversations.get_agent_conversation_audio()
        GET    .../conversations/{id}/audio/content                                                 beta.agent_endpoint_conversations.get_agent_conversation_audio_content()
        GET    .../conversations/{id}/items/{item_id}/audio                                         beta.agent_endpoint_conversations.get_agent_conversation_item_audio()
        GET    .../conversations/{id}/items/{item_id}/audio/content                                 beta.agent_endpoint_conversations.get_agent_conversation_item_audio_content()
        DELETE .../conversations/{id}                                                               beta.agent_endpoint_conversations.delete_agent_conversation()
        """
        print("\n")
        project_client = self.create_client(operation_group="agents", allow_preview=True, **kwargs)
        conversations = project_client.beta.agent_endpoint_conversations

        if is_live():
            model = kwargs.get("foundry_voice_model_name")
            assert model is not None
            conversation_id = _create_live_conversation(project_client, model)
            add_general_regex_sanitizer(
                regex=re.escape(conversation_id), value="sanitized-conversation-id", function_scoped=True
            )
        else:
            conversation_id = "sanitized-conversation-id"

        try:
            # The conversation should appear in the agent's conversation list.
            found = any(c.id == conversation_id for c in conversations.list_agent_conversations(_AGENT_NAME))
            assert found, "Expected the new conversation to appear in list_agent_conversations"

            # The conversation envelope.
            conversation = conversations.get_agent_conversation(_AGENT_NAME, conversation_id)
            assert conversation.id == conversation_id
            assert conversation.status in ("in_progress", "completed", "failed")
            assert conversation.created_at is not None

            # The responses (model inference turns) in the conversation.
            responses = list(conversations.list_agent_conversation_responses(_AGENT_NAME, conversation_id))
            assert len(responses) >= 1
            first_response = responses[0]
            response_detail = conversations.get_agent_conversation_response(
                _AGENT_NAME, conversation_id, first_response.id
            )
            assert response_detail.id == first_response.id

            # The items produced by that response (does not raise; count may be 0 or more).
            list(
                conversations.list_agent_conversation_response_items(
                    _AGENT_NAME, conversation_id, first_response.id
                )
            )

            # The ordered conversation items -- the full transcript (user + assistant + tool events).
            items = list(conversations.list_agent_conversation_items(_AGENT_NAME, conversation_id))
            assert len(items) >= 1
            first_item_id = items[0].get("id")
            assert first_item_id
            fetched_item = conversations.get_agent_conversation_item(_AGENT_NAME, conversation_id, first_item_id)
            assert fetched_item.get("id") == first_item_id

            # The merged whole-call recording and per-item audio. Completion is a hard requirement
            # here (not a soft skip): a cassette recorded before the conversation finalized would
            # otherwise let this test pass while silently never exercising any of the four audio
            # methods below, hiding a regression in all of them (including permanently, if such a
            # response were ever re-recorded).
            assert (
                conversation.status == "completed"
            ), f"Expected a completed conversation to exercise audio assertions, got {conversation.status!r}"
            recording = conversations.get_agent_conversation_audio(_AGENT_NAME, conversation_id)
            assert recording.format is not None
            if not recording.blob_uri:
                audio_bytes = b"".join(
                    conversations.get_agent_conversation_audio_content(_AGENT_NAME, conversation_id)
                )
                assert len(audio_bytes) > 0

            # A single item's audio, if any item has one.
            for item in items:
                item_id = item.get("id")
                if not item_id:
                    continue
                try:
                    item_audio = conversations.get_agent_conversation_item_audio(
                        _AGENT_NAME, conversation_id, item_id
                    )
                except HttpResponseError as e:
                    if e.status_code == 404:
                        continue
                    raise
                assert item_audio.role is not None
                if not item_audio.blob_uri:
                    item_audio_bytes = b"".join(
                        conversations.get_agent_conversation_item_audio_content(
                            _AGENT_NAME, conversation_id, item_id
                        )
                    )
                    assert len(item_audio_bytes) > 0
                break
        finally:
            # Deleting a conversation removes it and all of its responses, items, and audio.
            conversations.delete_agent_conversation(_AGENT_NAME, conversation_id)
            if is_live():
                project_client.agents.delete(agent_name=_AGENT_NAME)
