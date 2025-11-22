# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using the Web Search Tool and a synchronous client.

USAGE:
    python sample_agent_web_search.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from typing import Optional
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WebSearchPreviewTool,
    ApproximateLocation,
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
            tool = WebSearchPreviewTool(user_location=ApproximateLocation(country="GB", city="London", region="London"))
            # [END tool_declaration]

            # Create Agent with web search tool
            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                    instructions="You are a helpful assistant that can search the web",
                    tools=[tool],
                ),
                description="Agent for web search.",
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

            # Create a conversation for the agent interaction
            conversation = openai_client.conversations.create()
            print(f"Created conversation (id: {conversation.id})")

            # Send a query to search the web
            response = openai_client.responses.create(
                conversation=conversation.id,
                input="Show me the latest London Underground service updates",
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )
            output = response.output_text
            print(f"Response: {output}")
        finally:
            if isinstance(agent, AgentVersionDetails):
                print("\nCleaning up...")
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
                print("Agent deleted")


if __name__ == "__main__":
    main()
    assert isinstance(output, str) and len(output) > 0, "Output is invalid"
