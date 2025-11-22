# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with SharePoint capabilities
    using the SharepointAgentTool and synchronous Azure AI Projects client. The agent can search
    SharePoint content and provide responses with relevant information from SharePoint sites.

USAGE:
    python sample_agent_sharepoint.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b1" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) SHAREPOINT_PROJECT_CONNECTION_ID - The SharePoint project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
    4) SHAREPOINT_USER_INPUT - (Optional) The question to ask. If not set, you will be prompted.
"""

import os
from typing import Optional
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    SharepointAgentTool,
    SharepointGroundingToolParameters,
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
            tool = SharepointAgentTool(
                sharepoint_grounding_preview=SharepointGroundingToolParameters(
                    project_connections=[
                        ToolProjectConnection(project_connection_id=os.environ["SHAREPOINT_PROJECT_CONNECTION_ID"])
                    ]
                )
            )
            # [END tool_declaration]

            agent = project_client.agents.create_version(
                agent_name="MyAgent",
                definition=PromptAgentDefinition(
                    model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
                    instructions="""You are a helpful agent that can use SharePoint tools to assist users. 
            Use the available SharePoint tools to answer questions and perform tasks.""",
                    tools=[tool],
                ),
            )
            print(f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})")

            # Get user input from environment variable or prompt
            user_input = os.environ.get("SHAREPOINT_USER_INPUT")
            if not user_input:
                user_input = input("Enter your question corresponded to the documents in SharePoint:\n")

            print(f"Question: {user_input}\n")

            # Send initial request that will trigger the SharePoint tool
            stream_response = openai_client.responses.create(
                stream=True,
                input=user_input,
                extra_body={"agent": {"name": agent.name, "type": "agent_reference"}},
            )

            output = None
            for event in stream_response:
                if event.type == "response.created":
                    print(f"Follow-up response created with ID: {event.response.id}")
                elif event.type == "response.output_text.delta":
                    print(f"Delta: {event.delta}")
                elif event.type == "response.text.done":
                    print(f"\nFollow-up response done!")
                elif event.type == "response.output_item.done":
                    if event.item.type == "message":
                        item = event.item
                        if item.content[-1].type == "output_text":
                            text_content = item.content[-1]
                            for annotation in text_content.annotations:
                                if annotation.type == "url_citation":
                                    print(
                                        f"URL Citation: {annotation.url}, "
                                        f"Start index: {annotation.start_index}, "
                                        f"End index: {annotation.end_index}"
                                    )
                elif event.type == "response.completed":
                    output = event.response.output_text
                    print(f"\nFollow-up completed!")
                    print(f"Full response: {output}")
        finally:
            if isinstance(agent, AgentVersionDetails):
                print("\nCleaning up...")
                project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
                print("Agent deleted")


if __name__ == "__main__":
    main()
    assert isinstance(output, str) and len(output) > 0, "Output is invalid"
