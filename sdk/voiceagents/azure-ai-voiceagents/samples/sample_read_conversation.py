# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

"""
FILE: sample_read_conversation.py

DESCRIPTION:
    This sample demonstrates reading a persisted voice conversation back over the
    read-only conversation API: the conversation envelope, its responses (model
    inference turns), and its ordered items (the transcript). Conversations are
    created and written by the voice orchestrator during a live session; this
    client can only read them, and only when the agent was configured with
    `store = true`.

USAGE:
    python sample_read_conversation.py

    Set these environment variables before running the sample:
    1) AZURE_VOICE_AGENTS_ENDPOINT - the Foundry project endpoint, in the form
       https://<account>.services.ai.azure.com/api/projects/<project>
    2) AZURE_VOICE_AGENTS_AGENT_NAME - the name of the voice agent.
    3) AZURE_VOICE_AGENTS_CONVERSATION_ID - the id of a persisted conversation
       (captured from the `conversation.created` event during a live session).

    The sample authenticates with DefaultAzureCredential, so sign in first
    (for example, with `az login`).
"""

import os
from typing import Final

from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential

from azure.ai.voiceagents import VoiceAgentsClient
from azure.ai.voiceagents.models import AgentDefinitionOptInKeys


def read_conversation() -> None:
    endpoint = os.environ["AZURE_VOICE_AGENTS_ENDPOINT"]
    agent_name = os.environ["AZURE_VOICE_AGENTS_AGENT_NAME"]
    conversation_id = os.environ["AZURE_VOICE_AGENTS_CONVERSATION_ID"]
    preview: Final = AgentDefinitionOptInKeys.VOICE_AGENTS_V1_PREVIEW

    with VoiceAgentsClient(endpoint=endpoint, credential=DefaultAzureCredential()) as client:
        conversations = client.agent_endpoint_conversations
        try:
            # The conversation envelope: status, timestamps, aggregate usage.
            conversation = conversations.get_agent_conversation(agent_name, conversation_id, foundry_features=preview)
            print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

            # The responses (model inference turns) in the conversation.
            print("Responses:")
            for response in conversations.list_agent_conversation_responses(
                agent_name, conversation_id, foundry_features=preview
            ):
                print(f"  - {response.id}: status={response.status}")

                # Read a single response back, with its output and token usage.
                detail = conversations.get_agent_conversation_response(
                    agent_name, conversation_id, response.id, foundry_features=preview
                )
                print(f"      usage={detail.usage}")

                # The items produced by this specific response. Conversation items
                # belong to an open union, so on read they surface as mappings keyed
                # by their wire fields (``type``, ``id``, ...).
                for response_item in conversations.list_agent_conversation_response_items(
                    agent_name, conversation_id, response.id, foundry_features=preview
                ):
                    print(f"      item {response_item.get('type')} id={response_item.get('id')}")

            # The ordered conversation items — the full transcript (user + assistant + tool events).
            print("Items (transcript):")
            for item in conversations.list_agent_conversation_items(
                agent_name, conversation_id, foundry_features=preview
            ):
                item_id = item.get("id")
                print(f"  - {item.get('type')} id={item_id}")

                # Read a single item back by id.
                if item_id:
                    single = conversations.get_agent_conversation_item(
                        agent_name, conversation_id, item_id, foundry_features=preview
                    )
                    print(f"      fetched item id={single.get('id')}")

            # Deleting a conversation removes it and all of its responses, items, and audio.
            # This is destructive, so it is shown but not run by default. Uncomment to enable.
            # deleted = conversations.delete_agent_conversation(
            #     agent_name, conversation_id, foundry_features=preview
            # )
            # print(f"Deleted conversation {deleted.id}: deleted={deleted.deleted}")
        except HttpResponseError as e:
            # 404 typically means the conversation was not persisted (agent ran with `store = false`).
            print(f"Service responded with an error: {e.status_code} {e.reason}")


if __name__ == "__main__":
    read_conversation()
