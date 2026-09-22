# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates reading a persisted voice conversation back over
    the read-only conversation API exposed by `project_client.beta.voice_agents.conversations`:
    the conversation envelope, its responses (model inference turns), and its
    ordered items (the transcript). Conversations are created and written by
    the voice orchestrator during a live session; this client can only read
    them, and only when the agent was configured with `store=True` (see
    sample_voice_agent_basic.py).

    Runs with no setup beyond the endpoint: if FOUNDRY_VOICE_CONVERSATION_ID is
    not set, this sample creates a temporary voice agent, holds one short
    realtime text turn to produce a real conversation, reads it back, then
    deletes the agent version it created. Set FOUNDRY_VOICE_AGENT_NAME to hold
    that conversation against your own existing agent instead -- it is never
    created, modified, or deleted by this sample. Additionally set
    FOUNDRY_VOICE_CONVERSATION_ID to skip holding a new conversation entirely
    and just read back one your agent already produced.

USAGE:
    python sample_voice_agent_read_conversation.py

    Before running the sample:

    pip install "azure-ai-projects[voice]>=2.7.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME - Optional. The name of an existing voice agent
       (configured with `store=True`) to hold or read a conversation on.
       Defaults to a temporary agent, created and deleted by this sample, when
       unset.
    3) FOUNDRY_VOICE_CONVERSATION_ID - Optional. The id of a persisted
       conversation owned by FOUNDRY_VOICE_AGENT_NAME. If unset, this sample
       holds one short realtime text turn to produce one; see
       voice_sample_util.py in this folder and
       sample_voice_agent_live_text_conversation.py for a full interactive
       version.
    4) FOUNDRY_VOICE_MODEL - Optional. The realtime model deployment name,
       used only when creating the temporary agent. Defaults to "gpt-realtime".
"""

import os
from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    VoiceAgentAudioConfig,
    VoiceAgentAudioOutputConfig,
    VoiceAgentDefinition,
    VoiceModelType,
    VoiceOutputModality,
    VoiceType,
)

from voice_sample_util import hold_sample_conversation

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_VOICE_AGENT_NAME")
conversation_id = os.environ.get("FOUNDRY_VOICE_CONVERSATION_ID")
model = os.environ.get("FOUNDRY_VOICE_MODEL") or "gpt-realtime"
# Only create (and later clean up) a temporary agent when the caller didn't name their own --
# creating a version on someone's existing agent could unexpectedly mutate it, and deleting that
# version afterward could delete the agent entirely if it was the agent's only version.
owns_agent = not agent_name
agent_name = agent_name or "sample-read-conversation-agent"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential, allow_preview=True) as project_client,
):
    conversations = project_client.beta.voice_agents.conversations
    created_version = None
    try:
        if not conversation_id:
            print(f"No FOUNDRY_VOICE_CONVERSATION_ID set; holding a short conversation with '{agent_name}' first...")
            if owns_agent:
                created_version = project_client.agents.create_version(
                    agent_name=agent_name,
                    definition=VoiceAgentDefinition(
                        model_type=VoiceModelType.MANAGED,
                        model=model,
                        instructions="You are a friendly voice assistant. Keep replies short and natural.",
                        audio=VoiceAgentAudioConfig(
                            output=VoiceAgentAudioOutputConfig(
                                voice="en-US-AvaNeural", voice_type=VoiceType.AZURE_STANDARD
                            ),
                        ),
                        output_modalities=[VoiceOutputModality.AUDIO],
                        store=True,
                    ),
                )
            conversation_id = hold_sample_conversation(project_client, agent_name)
            print(f"Created conversation: {conversation_id}")

        # The conversation envelope: status, timestamps, aggregate usage.
        conversation = conversations.get(agent_name, conversation_id)
        print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

        # The responses (model inference turns) in the conversation.
        print("Responses:")
        for response in conversations.list_responses(agent_name, conversation_id):
            print(f"  - {response.id}: status={response.status}")

            # Read a single response back, with its output and token usage.
            detail = conversations.get_response(agent_name, conversation_id, response.id)
            print(f"      usage={detail.usage}")

            # The items produced by this specific response. Conversation items
            # belong to an open union, so on read they surface as mappings
            # keyed by their wire fields (``type``, ``id``, ...).
            for response_item in conversations.list_response_items(agent_name, conversation_id, response.id):
                print(f"      item {response_item.get('type')} id={response_item.get('id')}")

        # The ordered conversation items -- the full transcript (user + assistant + tool events).
        print("Items (transcript):")
        for item in conversations.list_items(agent_name, conversation_id):
            item_id = item.get("id")
            print(f"  - {item.get('type')} id={item_id}")

            # Read a single item back by id.
            if item_id:
                single = conversations.get_item(agent_name, conversation_id, item_id)
                print(f"      fetched item id={single.get('id')}")

        # Deleting a conversation removes it and all of its responses, items, and audio.
        # This is destructive, so it is shown but not run by default. Uncomment to enable.
        # deleted = conversations.delete(agent_name, conversation_id)
        # print(f"Deleted conversation {deleted.id}: deleted={deleted.deleted}")
    except HttpResponseError as e:
        # 404 typically means the conversation was not persisted (agent ran with `store=False`).
        print(f"Service responded with an error: {e.status_code} {e.reason}")
    finally:
        if created_version is not None:
            project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
            print(f"Deleted temporary voice agent version: {created_version.version}")
