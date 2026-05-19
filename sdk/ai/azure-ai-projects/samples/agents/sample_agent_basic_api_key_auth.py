# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous AIProjectClient. It uses API key authentication to
    connect to the Microsoft Foundry service.

    Note that API key authentication is available starting with version
    2.0.2 of the client library.

    The OpenAI compatible Responses and Conversation calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_agent_basic_api_key_auth.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.2" python-dotenv

    Set these environment variables with your own values:
    2) FOUNDRY_PROJECT_API_KEY - The Project API key as found in your Foundry project home page.
    3) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.core.credentials import AzureKeyCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
api_key = os.environ["FOUNDRY_PROJECT_API_KEY"]

with (
    AIProjectClient(endpoint=endpoint, credential=AzureKeyCredential(api_key)) as project_client,
    project_client.get_openai_client() as openai_client,
):

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="You are a helpful assistant that answers general questions",
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response output: {response.output_text}")

    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": "And what is the capital city?"}],
    )
    print("Added a second user message to the conversation")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )
    print(f"Response output: {response.output_text}")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
