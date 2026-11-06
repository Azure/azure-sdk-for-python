# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Shared helpers for the voice-agent samples in this folder."""

import time
from typing import Final

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    RealtimeConversationItemMessageUser,
    RealtimeConversationItemMessageUserContent,
    RealtimeConversationItemType,
    RealtimeServerEventError,
    RealtimeServerEventResponseDone,
    RealtimeServerEventSessionCreated,
    VoiceConversationStatus,
)

# Seconds to wait for the agent's reply before giving up.
_RESPONSE_TIMEOUT: Final = 45

# Seconds to wait for the service to finish finalizing the conversation after the session ends,
# and how many times to poll before giving up.
_FINALIZE_POLL_INTERVAL: Final = 1
_FINALIZE_POLL_ATTEMPTS: Final = 15


def hold_sample_conversation(
    project_client: AIProjectClient, agent_name: str, prompt: str = "Say a short, friendly hello."
) -> str:
    """Send one text message and return its stored Realtime conversation ID.

    The agent must already exist with ``store=True``. Wait for storage to finish
    before returning so callers can read the replies and transcript.

    :param project_client: The Foundry project client.
    :param agent_name: The name of an existing voice agent, configured with ``store=True``.
    :param prompt: The single text turn to send.
    :type project_client: ~azure.ai.projects.AIProjectClient
    :type agent_name: str
    :type prompt: str
    :return: The persisted conversation id.
    :rtype: str
    :raises RuntimeError: If the session ends without a persisted conversation id, the service
     reports a session error, or the conversation does not finish finalizing in time.
    """
    conversation_id = None
    with project_client.beta.voice_agents.realtime.connect(agent_name=agent_name) as conn:
        conn.conversation.item.create(
            item=RealtimeConversationItemMessageUser(
                type=RealtimeConversationItemType.MESSAGE,
                content=[RealtimeConversationItemMessageUserContent(type="input_text", text=prompt)],
            )
        )
        conn.response.create()
        while True:
            event = conn.recv(timeout=_RESPONSE_TIMEOUT)
            if isinstance(event, RealtimeServerEventSessionCreated):
                # The stored conversation ID arrives at session creation, not response.done.
                conversation_id = event.conversation_id or conversation_id
            if isinstance(event, RealtimeServerEventResponseDone):
                break
            if isinstance(event, RealtimeServerEventError):
                raise RuntimeError(f"Session error while holding a sample conversation: {event.error.message}")

    if not conversation_id:
        raise RuntimeError(
            "The realtime session ended without a persisted conversation id. Make sure the agent "
            "was configured with `store=True`."
        )

    # A reply can finish before its transcript is stored; wait for storage to finish too.
    conversations = project_client.beta.voice_agents.conversations
    for _ in range(_FINALIZE_POLL_ATTEMPTS):
        conversation = conversations.get(agent_name, conversation_id)
        if conversation.status != VoiceConversationStatus.IN_PROGRESS:
            break
        time.sleep(_FINALIZE_POLL_INTERVAL)
    else:
        raise RuntimeError(
            f"Conversation {conversation_id} did not finish finalizing within "
            f"{_FINALIZE_POLL_ATTEMPTS * _FINALIZE_POLL_INTERVAL} seconds."
        )

    return conversation_id
