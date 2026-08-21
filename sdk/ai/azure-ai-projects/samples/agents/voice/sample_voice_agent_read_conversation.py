# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates reading a persisted voice conversation back over
    the read-only conversation API exposed by `project_client.agent_endpoint_conversations`:
    the conversation envelope, its responses (model inference turns), and its
    ordered items (the transcript). Conversations are created and written by
    the voice orchestrator during a live session; this client can only read
    them, and only when the agent was configured with `store=True` (see
    sample_voice_agent_basic.py).

USAGE:
    python sample_voice_agent_read_conversation.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint.
    2) FOUNDRY_VOICE_AGENT_NAME - The name of the voice agent.
    3) FOUNDRY_VOICE_CONVERSATION_ID - The id of a persisted conversation
       (captured from the `conversation.created` event during a live session,
       see sample_voice_agent_live_audio_conversation_async.py).
"""

import os
from dotenv import load_dotenv
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ["FOUNDRY_VOICE_AGENT_NAME"]
conversation_id = os.environ["FOUNDRY_VOICE_CONVERSATION_ID"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    conversations = project_client.agent_endpoint_conversations
    try:
        # The conversation envelope: status, timestamps, aggregate usage.
        conversation = conversations.get_agent_conversation(agent_name, conversation_id)
        print(f"Conversation {conversation.id}: status={conversation.status}, created_at={conversation.created_at}")

        # The responses (model inference turns) in the conversation.
        print("Responses:")
        for response in conversations.list_agent_conversation_responses(agent_name, conversation_id):
            print(f"  - {response.id}: status={response.status}")

            # Read a single response back, with its output and token usage.
            detail = conversations.get_agent_conversation_response(agent_name, conversation_id, response.id)
            print(f"      usage={detail.usage}")

            # The items produced by this specific response. Conversation items
            # belong to an open union, so on read they surface as mappings
            # keyed by their wire fields (``type``, ``id``, ...).
            for response_item in conversations.list_agent_conversation_response_items(
                agent_name, conversation_id, response.id
            ):
                print(f"      item {response_item.get('type')} id={response_item.get('id')}")

        # The ordered conversation items -- the full transcript (user + assistant + tool events).
        print("Items (transcript):")
        for item in conversations.list_agent_conversation_items(agent_name, conversation_id):
            item_id = item.get("id")
            print(f"  - {item.get('type')} id={item_id}")

            # Read a single item back by id.
            if item_id:
                single = conversations.get_agent_conversation_item(agent_name, conversation_id, item_id)
                print(f"      fetched item id={single.get('id')}")

        # Deleting a conversation removes it and all of its responses, items, and audio.
        # This is destructive, so it is shown but not run by default. Uncomment to enable.
        # deleted = conversations.delete_agent_conversation(agent_name, conversation_id)
        # print(f"Deleted conversation {deleted.id}: deleted={deleted.deleted}")
    except HttpResponseError as e:
        # 404 typically means the conversation was not persisted (agent ran with `store=False`).
        print(f"Service responded with an error: {e.status_code} {e.reason}")
