# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Prompt Agent operations
    using the synchronous AIProjectClient. It uses Entra ID authentication to
    connect to the Microsoft Foundry service.

    The OpenAI compatible Responses and Conversation calls in this sample are made using
    the OpenAI client from the `openai` package. See https://platform.openai.com/docs/api-reference
    for more information.

USAGE:
    python sample_agent_basic.py

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
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentEndpointConfig,
    FixedRatioVersionSelectionRule,
    PromptAgentDefinition,
    ProtocolConfiguration,
    ResponsesProtocolConfiguration,
    VersionSelector,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
):
    created_version = None
    original_agent_endpoint = None

    try:
        created_version = project_client.agents.create_version(
            agent_name=agent_name,
            definition=PromptAgentDefinition(
                model=os.environ["FOUNDRY_MODEL_NAME"],
                instructions="You are a helpful assistant that answers general questions",
            ),
        )
        print(
            f"Agent created (id: {created_version.id}, name: {created_version.name}, version: {created_version.version})"
        )

        original_agent_endpoint = project_client.agents.get(agent_name=agent_name).agent_endpoint
        endpoint_config = AgentEndpointConfig(
            version_selector=VersionSelector(
                version_selection_rules=[
                    FixedRatioVersionSelectionRule(agent_version=created_version.version, traffic_percentage=100),
                ]
            ),
            protocol_configuration=ProtocolConfiguration(responses=ResponsesProtocolConfiguration()),
        )
        project_client.agents.update_details(agent_name=agent_name, agent_endpoint=endpoint_config)
        print(f"Agent endpoint configured for version {created_version.version}")

        with project_client.get_openai_client(agent_name=agent_name) as openai_client:

            conversation = openai_client.conversations.create(
                items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
            )
            print(f"Created conversation with initial user message (id: {conversation.id})")

            response = openai_client.responses.create(
                conversation=conversation.id,
            )
            print(f"Response output: {response.output_text}")

            openai_client.conversations.items.create(
                conversation_id=conversation.id,
                items=[{"type": "message", "role": "user", "content": "And what is the capital city?"}],
            )
            print("Added a second user message to the conversation")

            response = openai_client.responses.create(
                conversation=conversation.id,
            )
            print(f"Response output: {response.output_text}")

            openai_client.conversations.delete(conversation_id=conversation.id)
            print("Conversation deleted")
    finally:
        if original_agent_endpoint is not None:
            project_client.agents.update_details(agent_name=agent_name, agent_endpoint=original_agent_endpoint)

        if created_version is not None:
            project_client.agents.delete_version(
                agent_name=agent_name, agent_version=created_version.version, force=True
            )
