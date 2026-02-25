# pylint: disable=line-too-long,useless-suppression
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
    3) STORAGE_INPUT_QUEUE_NAME - The name of the Azure Storage Queue to use for input and output in the Azure Function tool.
    4) STORAGE_OUTPUT_QUEUE_NAME - The name of the Azure Storage Queue to use for output in the Azure Function tool.
    5) STORAGE_QUEUE_SERVICE_ENDPOINT - The endpoint of the Azure Storage Queue service.
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
    PromptAgentDefinition,
)

load_dotenv()

agent = None

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

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
                    queue_name=os.environ["STORAGE_INPUT_QUEUE_NAME"],
                    queue_service_endpoint=os.environ["STORAGE_QUEUE_SERVICE_ENDPOINT"],
                )
            ),
            output_binding=AzureFunctionBinding(
                storage_queue=AzureFunctionStorageQueue(
                    queue_name=os.environ["STORAGE_OUTPUT_QUEUE_NAME"],
                    queue_service_endpoint=os.environ["STORAGE_QUEUE_SERVICE_ENDPOINT"],
                )
            ),
            function=AzureFunctionDefinitionFunction(
                name="queue_trigger",
                description="Get weather for a given location",
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string", "description": "location to determine weather for"}},
                },
            ),
        )
    )
    # [END tool_declaration]

    agent = project_client.agents.create_version(
        agent_name="MyAgent",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant.",
            tools=[tool],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    user_input = "What is the weather in Seattle?"

    response = openai_client.responses.create(
        tool_choice="required",
        input=user_input,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Response output: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
