# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous client. Instead of creating a new Agent
    and Conversation, it retrieves existing ones.

    For OpenAI operations in this sample, see:
    https://platform.openai.com/docs/api-reference/conversations/retrieve?lang=python
    https://platform.openai.com/docs/api-reference/conversations/create-items?lang=python

USAGE:
    python sample_agent_retrieve_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AGENT_NAME - The name of an existing Agent in your Microsoft Foundry project.
    3) CONVERSATION_ID - The ID of an existing Conversation associated with the Agent
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

load_dotenv()

agent_name = os.environ["AGENT_NAME"]
conversation_id = os.environ["CONVERSATION_ID"]

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    # Retrieves latest version of an existing Agent
    agent = project_client.agents.get(agent_name=agent_name)
    print(f"Agent retrieved (id: {agent.id}, name: {agent.name}, version: {agent.versions.latest.version})")

    # Retrieved a stored conversation
    conversation = openai_client.conversations.retrieve(conversation_id=conversation_id)
    print(f"Retrieved conversation (id: {conversation.id})")

    # Add a new user text message to the conversation
    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": "How many feet are in a mile?"}],
    )
    print(f"Added a user message to the conversation")

    response = openai_client.responses.create(
        conversation=conversation.id, extra_body={"agent": {"name": agent.name, "type": "agent_reference"}}, input=""
    )
    print(f"Response output: {response.output_text}")
