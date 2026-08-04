# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
WARNING:
Grounding with Bing Search tool uses Grounding with Bing, which has additional costs and terms.
    Terms of use:
        https://www.microsoft.com/bing/apis/grounding-legal-enterprise
    Privacy statement:
        https://go.microsoft.com/fwlink/?LinkId=521839&clcid=0x409
    Customer data will flow outside the Azure compliance boundary.
    Learn more:
        https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/bing-tools

DESCRIPTION:
    This sample demonstrates how to create an AI agent with Bing grounding capabilities
    using the BingGroundingTool and synchronous Azure AI Projects client. The agent can search
    the web for current information and provide grounded responses with URL citations.

    The sample shows:
    - Creating an agent with BingGroundingTool configured for web search
    - Making requests that require current information from the web
    - Extracting URL citations from the response annotations
    - Processing grounded responses with source citations
    - Proper cleanup of created resources

USAGE:
    python sample_agent_bing_grounding.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) BING_PROJECT_CONNECTION_ID - The Bing project connection ID, as found in the "Connections" tab in your Microsoft Foundry project.
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    BingGroundingTool,
    BingGroundingSearchToolParameters,
    BingGroundingSearchConfiguration,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


tool = BingGroundingTool(
    bing_grounding=BingGroundingSearchToolParameters(
        search_configurations=[
            BingGroundingSearchConfiguration(project_connection_id=os.environ["BING_PROJECT_CONNECTION_ID"])
        ]
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
        description="You are a helpful agent.",
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    stream_response = openai_client.responses.create(
        stream=True,
        tool_choice="required",
        input="What is today's date and whether in Seattle?",
    )

    for event in stream_response:
        if event.type == "response.created":
            print(f"Follow-up response created with ID: {event.response.id}")
        elif event.type == "response.output_text.delta":
            print(f"Delta: {event.delta}")
        elif event.type == "response.text.done":
            print("\nFollow-up response done!")
        elif event.type == "response.output_item.done":
            if event.item.type == "message":
                item = event.item
                if item.content[-1].type == "output_text":
                    text_content = item.content[-1]
                    for annotation in text_content.annotations:
                        if annotation.type == "url_citation":
                            print(f"URL Citation: {annotation.url}")
        elif event.type == "response.completed":
            print("\nFollow-up completed!")
            print(f"Full response: {event.response.output_text}")
