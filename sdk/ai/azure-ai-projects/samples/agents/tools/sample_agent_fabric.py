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

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FABRIC_PROJECT_CONNECTION_ID - The Fabric project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
    4) FABRIC_USER_INPUT - (Optional) The question to ask. If not set, you will be prompted.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    MicrosoftFabricAgentTool,
    FabricDataAgentToolParameters,
    ToolProjectConnection,
    AgentVersionDetails,
)

load_dotenv()

endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

# Global variables to be asserted after main execution
output: Optional[str] = None


def main() -> None:
    global output
    agent: Optional[AgentVersionDetails] = None

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        try:
            # [START tool_declaration]
            tool = MicrosoftFabricAgentTool(
                fabric_dataagent_preview=FabricDataAgentToolParameters(
                    project_connections=[
                        ToolProjectConnection(project_connection_id=os.environ["FABRIC_PROJECT_CONNECTION_ID"])
                    ]
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

            # Get user input from environment variable or prompt
            user_input = os.environ.get("FABRIC_USER_INPUT")
            if not user_input:
                user_input = input("Enter your question (e.g., 'Tell me about sales records'): \n")

            print(f"Question: {user_input}\n")

            response = openai_client.responses.create(
                tool_choice="required",
                input=user_input,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            output = response.output_text
            print(f"Response output: {output}")
        finally:
            if isinstance(agent, AgentVersionDetails):
                print("\nCleaning up...")
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
                print("Agent deleted")


if __name__ == "__main__":
    main()
    assert isinstance(output, str) and len(output) > 0, "Output is invalid"
