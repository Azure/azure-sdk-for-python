# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with Azure Function capabilities
    using the AzureFunctionTool and synchronous Azure AI Projects client. The agent can call
    an Azure Function via Storage Queue input/output bindings.

USAGE:
    python sample_agent_azure_function.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) STORAGE_INPUT_QUEUE_NAME - The name of the Azure Storage Queue to use for input and output in the Azure Function tool.
    5) STORAGE_OUTPUT_QUEUE_NAME - The name of the Azure Storage Queue to use for output in the Azure Function tool.
    6) STORAGE_QUEUE_SERVICE_ENDPOINT - The endpoint of the Azure Storage Queue service.
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
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

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


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

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    create_version_with_endpoint(
        project_client=project_client,
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=os.environ["FOUNDRY_MODEL_NAME"],
            instructions="You are a helpful assistant.",
            tools=[tool],
        ),
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    user_input = "What is the weather in Seattle?"

    response = openai_client.responses.create(
        tool_choice="required",
        input=user_input,
    )

    print(f"Response output: {response.output_text}")
