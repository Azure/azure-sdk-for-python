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
    """Send one short realtime text turn to an existing voice agent and return the resulting
    persisted conversation id, once it has finished finalizing.

    Samples that read a conversation back (transcript, responses, audio) do not always have a
    live call handy to read. This helper produces a minimal real conversation on demand so those
    samples can run without requiring a conversation id up front. The agent named ``agent_name``
    must already exist (see sample_voice_agent_basic.py) and be configured with ``store=True`` so
    its conversations are persisted. For a full interactive conversation and a fuller explanation
    of the realtime event flow used here, see sample_voice_agent_live_text_conversation.py.

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
                # The persisted conversation id (only present when conversation persistence is
                # enabled) is set here, not on response.done.
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

    # `response.done` only means the model finished replying, not that the service has finished
    # persisting the conversation -- immediately after the session closes, the conversation can
    # still briefly report `in_progress` while that finalization completes in the background.
    # Poll until it settles so callers can read a complete transcript right away.
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
