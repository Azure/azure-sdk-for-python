# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with Microsoft Fabric capabilities
    using the MicrosoftFabricPreviewTool and synchronous Azure AI Projects client. The agent can query
    Fabric data sources and provide responses based on data analysis.

USAGE:
    python sample_agent_fabric.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FABRIC_PROJECT_CONNECTION_ID - The Fabric project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureFunctionBinding,
    AzureFunctionDefinition,
    AzureFunctionStorageQueue,
    AzureFunctionDefinitionFunction,
    AzureFunctionTool,
    FabricDataAgentToolParameters,
    MicrosoftFabricPreviewTool,
    PromptAgentDefinition,
    ToolProjectConnection,
)

load_dotenv()

endpoint = "https://foundygejp.services.ai.azure.com/api/projects/projectgejp"

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # [START tool_declaration]
    tool = AzureFunctionTool(
        azure_function=AzureFunctionDefinition(
            input_binding=AzureFunctionBinding(
                storage_queue=AzureFunctionStorageQueue(
                    queue_name="azure-function-foo-input",
                    queue_service_endpoint="https://gejpstorage.queue.core.windows.net/azure-function-foo-input",
                )
            ),
            output_binding=AzureFunctionBinding(
                storage_queue=AzureFunctionStorageQueue(
                    queue_name="azure-function-foo-output",
                    queue_service_endpoint="https://gejpstorage.queue.core.windows.net/azure-function-foo-output",
                )
            ),
            function=AzureFunctionDefinitionFunction(
                name="greet",
                description="Get weather for a given city",
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "location to get weather"}},
                },
            ),
        )
    )
    # [END tool_declaration]

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model="gpt-4.1",
            instructions="You are a helpful assistant.",
            tools=[tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    user_input = "What is the weather in Seattle?"

    response = openai_client.responses.create(
        tool_choice="required",
        input=user_input,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Response output: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
