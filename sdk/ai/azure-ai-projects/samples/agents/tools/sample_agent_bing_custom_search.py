# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
WARNING:
Grounding with Bing Custom Search tool uses Grounding with Bing, which has additional costs and terms.
    Terms of use:
        https://www.microsoft.com/bing/apis/grounding-legal-enterprise
    Privacy statement:
        https://go.microsoft.com/fwlink/?LinkId=521839&clcid=0x409
    Customer data will flow outside the Azure compliance boundary.
    Learn more:
        https://learn.microsoft.com/azure/ai-foundry/agents/how-to/tools/bing-tools

DESCRIPTION:
    This sample demonstrates how to create an AI agent with Bing Custom Search capabilities
    using the BingCustomSearchPreviewTool and synchronous Azure AI Projects client. The agent can search
    custom search instances and provide responses with relevant results.

USAGE:
    python sample_agent_bing_custom_search.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) BING_CUSTOM_SEARCH_PROJECT_CONNECTION_ID - The Bing Custom Search project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
    5) BING_CUSTOM_SEARCH_INSTANCE_NAME - The Bing Custom Search instance name
    6) BING_CUSTOM_USER_INPUT - (Optional) The question to ask. If not set, you will be prompted.
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    BingCustomSearchPreviewTool,
    BingCustomSearchToolParameters,
    BingCustomSearchConfiguration,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


tool = BingCustomSearchPreviewTool(
    bing_custom_search_preview=BingCustomSearchToolParameters(
        search_configurations=[
            BingCustomSearchConfiguration(
                project_connection_id=os.environ["BING_CUSTOM_SEARCH_PROJECT_CONNECTION_ID"],
                instance_name=os.environ["BING_CUSTOM_SEARCH_INSTANCE_NAME"],
            )
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
            instructions="""You are a helpful agent that can use Bing Custom Search tools to assist users.
            Use the available Bing Custom Search tools to answer questions and perform tasks.""",
            tools=[tool],
        ),
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    user_input = os.environ.get("BING_CUSTOM_USER_INPUT") or input("Enter your question: \n")

    # Send initial request that will trigger the Bing Custom Search tool
    stream_response = openai_client.responses.create(
        stream=True,
        input=user_input,
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
                            print(
                                f"URL Citation: {annotation.url}, "
                                f"Start index: {annotation.start_index}, "
                                f"End index: {annotation.end_index}"
                            )
        elif event.type == "response.completed":
            print("\nFollow-up completed!")
            print(f"Full response: {event.response.output_text}")
