# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Read a stored Realtime conversation, its model replies, and its transcript
    through project_client.beta.voice_agents.conversations.

    With no conversation ID, send one text message to create a conversation.
    With no agent name, also create a temporary agent and delete its version
    afterward. An existing agent is not changed or deleted. Conversations
    created on an existing agent remain stored.

USAGE:
    python sample_voice_agent_read_conversation.py

    pip install "azure-ai-projects[voice]>=2.7.0" python-dotenv

    Environment variables:
    1) FOUNDRY_PROJECT_ENDPOINT (required) - The Foundry project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME (optional) - Existing agent with store=True;
       omit to create a temporary agent.
    3) FOUNDRY_VOICE_CONVERSATION_ID (optional) - Completed conversation from
       that agent. Omit to create a conversation with a text message.
    4) FOUNDRY_VOICE_AGENT_MODEL (optional) - Model for a temporary agent;
       defaults to "gpt-realtime".
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
model = os.environ.get("FOUNDRY_VOICE_AGENT_MODEL") or "gpt-realtime"
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
            response_id = response.id
            if not response_id:
                print("      No response ID available; skipping response details.")
                continue

            # Read a single response back, with its output and token usage.
            detail = conversations.get_response(agent_name, conversation_id, response_id)
            print(f"      usage={detail.usage}")

            # The items produced by this specific response. Conversation items
            # belong to an open union, so on read they surface as mappings
            # keyed by their wire fields (``type``, ``id``, ...).
            for response_item in conversations.list_response_items(agent_name, conversation_id, response_id):
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
        # conversations.delete(agent_name, conversation_id)
        # print(f"Deleted conversation {conversation_id}")
    except HttpResponseError as e:
        # 404 typically means the conversation was not persisted (agent ran with `store=False`).
        print(f"Service responded with an error: {e.status_code} {e.reason}")
    finally:
        if created_version is not None:
            project_client.agents.delete_version(agent_name=agent_name, agent_version=created_version.version)
            print(f"Deleted temporary voice agent version: {created_version.version}")
