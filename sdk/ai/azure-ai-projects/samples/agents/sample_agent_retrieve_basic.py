# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous client. It first creates an Agent version
    and Conversation as prerequisites, then demonstrates retrieve/get
    operations against those created resources.

    For OpenAI operations in this sample, see:
    https://platform.openai.com/docs/api-reference/conversations/retrieve?lang=python
    https://platform.openai.com/docs/api-reference/conversations/create-items?lang=python

USAGE:
    python sample_agent_retrieve_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
model = os.environ["FOUNDRY_MODEL_NAME"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")
with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_with_endpoint(
        project_client=project_client,
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model,
            instructions="You are a helpful assistant.",
        ),
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    agent = project_client.agents.get(agent_name=agent_name)
    conversation = openai_client.conversations.create()
    print(f"Conversation created (id: {conversation.id})")

    # Retrieve latest version for the prerequisite agent.
    print(f"Agent retrieved (id: {agent.id}, name: {agent.name}, version: {agent.versions.latest.version})")

    # Retrieve the prerequisite conversation.
    conversation = openai_client.conversations.retrieve(conversation_id=conversation.id)
    print(f"Retrieved conversation (id: {conversation.id})")

    # Add a new user text message to the conversation
    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": "How many feet are in a mile?"}],
    )
    print("Added a user message to the conversation")

    response = openai_client.responses.create(
        conversation=conversation.id,
    )
    print(f"Response output: {response.output_text}")
