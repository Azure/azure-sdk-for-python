# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run basic Container App Agent operations
    using the synchronous client.

USAGE:
    python sample_container_app_agent_basic.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" azure-identity load_dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) CONTAINER_APP_RESOURCE_ID - The resource ID of the Container App. It should have the format
       "/subscriptions/<your-subscription-id>/resourceGroups/<your-resource-group-name>/providers/Microsoft.App/containerApps/<your-app-name>"
    3) INGRESS_SUBDOMAIN_SUFFIX - The suffix to apply to the app subdomain when sending ingress to the agent.
       This can be a label (e.g., '---current'), a specific revision (e.g., '--0000001'), or an empty string to use the
       default endpoint for the container app.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ContainerAppAgentDefinition, ProtocolVersionRecord, AgentProtocol

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:

    openai_client = project_client.get_openai_client()

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=ContainerAppAgentDefinition(
            container_app_resource_id=os.environ["CONTAINER_APP_RESOURCE_ID"],
            ingress_subdomain_suffix=os.environ["INGRESS_SUBDOMAIN_SUFFIX"],
            container_protocol_versions=[ProtocolVersionRecord(protocol=AgentProtocol.RESPONSES, version="1")],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    # See https://platform.openai.com/docs/api-reference/conversations/create?lang=python
    conversation = openai_client.conversations.create(
        items=[{"type": "message", "role": "user", "content": "What is the size of France in square miles?"}],
    )
    print(f"Created conversation with initial user message (id: {conversation.id})")

    # See https://platform.openai.com/docs/api-reference/responses/create?lang=python
    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference", "version": agent.version}},
    )
    print(f"Response output: {response.output_text}")

    openai_client.conversations.items.create(
        conversation_id=conversation.id,
        items=[{"type": "message", "role": "user", "content": "And what is the capital city?"}],
    )
    print(f"Added a second user message to the conversation")

    response = openai_client.responses.create(
        conversation=conversation.id,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference", "version": agent.version}},
    )
    print(f"Response output: {response.output_text}")

    openai_client.conversations.delete(conversation_id=conversation.id)
    print("Conversation deleted")

    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
