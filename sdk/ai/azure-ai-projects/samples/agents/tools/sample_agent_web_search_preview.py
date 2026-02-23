# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
WARNING:
    Web Search uses Grounding with Bing, which has additional costs and terms.
    Terms of use:
        https://www.microsoft.com/bing/apis/grounding-legal-enterprise
    Privacy statement:
        https://go.microsoft.com/fwlink/?LinkId=521839&clcid=0x409
    Customer data will flow outside the Azure compliance boundary.
    Learn more:
        https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/web-search

DESCRIPTION:
    This sample demonstrates how to run Prompt Agent operations
    using the Web Search Preview Tool and a synchronous client.

USAGE:
    python sample_agent_web_search_preview.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0b4" python-dotenv

    Set these environment variables with your own values:
    1) AZURE_AI_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) AZURE_AI_MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, WebSearchPreviewTool, ApproximateLocation

load_dotenv()


endpoint = os.environ["AZURE_AI_PROJECT_ENDPOINT"]

with (
    DefaultAzureCredential() as credential,
    AIProjectClient(endpoint=endpoint, credential=credential) as project_client,
    project_client.get_openai_client() as openai_client,
):
    # [START tool_declaration]
    tool = WebSearchPreviewTool(user_location=ApproximateLocation(country="GB", city="London", region="London"))
    # [END tool_declaration]
    # Create Agent with web search tool
    agent = project_client.agents.create_version(
        agent_name="MyAgent105",
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
    user_input = "Show me the latest London Underground service updates"
    stream_response = openai_client.responses.create(
        stream=True,
        input=user_input,
        tool_choice="required",
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

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
            print(f"\nFollow-up completed!")
            print(f"Full response: {event.response.output_text}")

    print("\nCleaning up...")
    project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
    print("Agent deleted")
