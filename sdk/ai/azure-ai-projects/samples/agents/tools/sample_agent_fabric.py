# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with Microsoft Fabric capabilities
    using the MicrosoftFabricAgentTool and synchronous Azure AI Projects client. The agent can query
    Fabric data sources and provide responses based on data analysis.

USAGE:
    python sample_agent_fabric.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" azure-identity openai python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Azure AI Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) FABRIC_PROJECT_CONNECTION_ID - The Fabric project connection ID, as found in the "Connections" tab in your Azure AI Foundry project.
"""

import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    MicrosoftFabricAgentTool,
    FabricDataAgentToolParameters,
    ToolProjectConnection,
)

load_dotenv()

project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
    headers={
        "x-ms-oai-response-testenv": "tip2-preview1"  # TODO: remove this line when the feature goes to production
    },
)

openai_client = project_client.get_openai_client()

with project_client:
    agent = project_client.agents.create_version(
        agent_name="MyFabricAgent4",
        definition=PromptAgentDefinition(
            model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
            instructions="You are a helpful assistant.",
            tools=[
                MicrosoftFabricAgentTool(
                    fabric_dataagent_preview=FabricDataAgentToolParameters(
                        project_connections=[
                            ToolProjectConnection(project_connection_id=os.environ["FABRIC_PROJECT_CONNECTION_ID"])
                        ]
                    )
                )
            ],
        ),
    )
    print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

    user_input = input("Enter your question for Fabric (e.g., 'Tell me about sales records'): \n")

    response = openai_client.responses.create(
        tool_choice="required",
        input=user_input,
        extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
    )

    print(f"Response output: {response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
