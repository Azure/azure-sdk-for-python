# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous client. Instead of creating a new Agent
    and Conversation, it retrieves existing ones.

USAGE:
    python sample_agent_retrieve_basic.py

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

    # [START prompt_agent_retrieve_basic]
    openai_client = project_client.get_openai_client()

    # Retrieves latest version of an existing Agent
    agent = project_client.agents.retrieve(agent_name="MyAgent")  # Update Agent name here
    print(f"Agent retrieved (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # Retrieved a stored conversation
    # See https://platform.openai.com/docs/api-reference/conversations/retrieve?lang=python
    conversation = openai_client.conversations.retrieve(
        conversation_id="MyConversationId"
    )  # Update conversation ID here
    print(f"Retrieved conversation (id: {conversation.id})")

    # Add a new user text message to the conversation
    # See https://platform.openai.com/docs/api-reference/conversations/create-items?lang=python
    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": "How many feet are in a mile?"}],
    )
    print(f"Added a user message to the conversation")

    response = openai_client.responses.create(
        conversation=conversation.id, extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}
    )
    print(f"Response output: {response.output_text}")
    # [END prompt_agent_retrieve_basic]
