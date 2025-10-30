# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to do Create/Read/Update/Delete (CRUD) Agent conversations
    using the synchronous client.

USAGE:
    python sample_conversation_crud.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-identity load_dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    # [START conversation_crud]

    # Get OpenAI client
    openai_client = project_client.get_openai_client()

    # Create conversations
    conversation1 = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation1.id})")

    conversation2 = openai_client.conversations.create()
    print(f"Created conversation (id: {conversation2.id})")

    # Retrieve a conversation
    conversation = openai_client.conversations.retrieve(conversation_id=conversation1.id)
    print(f"Retrieved conversation (id: {conversation.id}, metadata: {conversation.metadata})")

    # List conversations
    # Disabled since OpenAI client does not have a conversation listing API.
    # for conversation in openai_client.conversations.list():
    #     print(f"Listed conversation (id: {conversation.id})")

    # Update conversation
    openai_client.conversations.update(conversation_id=conversation1.id, metadata={"key": "value"})
    print(f"Conversation updated")

    conversation = openai_client.conversations.retrieve(conversation_id=conversation1.id)
    print(f"Got updated conversation (id: {conversation.id}, metadata: {conversation.metadata})")

    # Delete conversation
    result = openai_client.conversations.delete(conversation_id=conversation1.id)
    print(f"Conversation deleted (id: {result.id}, deleted: {result.deleted})")

    result = openai_client.conversations.delete(conversation_id=conversation2.id)
    print(f"Conversation deleted (id: {result.id}, deleted: {result.deleted})")
    # [END conversation_crud]
