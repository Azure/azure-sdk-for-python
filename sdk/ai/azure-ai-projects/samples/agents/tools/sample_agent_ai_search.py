# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to create an AI agent with Azure AI Search capabilities
    using the AzureAISearchTool and synchronous Azure AI Projects client. The agent can search
    indexed content and provide responses with citations from search results.

USAGE:
    python sample_agent_ai_search.py

    Before running the sample:

    pip install "azure-ai-projects>=2.0.0" python-dotenv

    Set these environment variables with your own values:
    1) FOUNDRY_PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
       page of your Microsoft Foundry portal.
    2) FOUNDRY_MODEL_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Microsoft Foundry project.
    3) FOUNDRY_AGENT_NAME - Optional. The name of the AI agent. If not set, defaults to "MyAgent".
    4) AI_SEARCH_PROJECT_CONNECTION_ID - The AI Search project connection ID,
       as found in the "Connections" tab in your Microsoft Foundry project.
    5) AI_SEARCH_INDEX_NAME - The name of the AI Search index to use for searching.
    6) AI_SEARCH_USER_INPUT - (Optional) The question to ask. If not set, you will be prompted.
"""

import os
from dotenv import load_dotenv
from util import create_version_with_endpoint
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AzureAISearchTool,
    PromptAgentDefinition,
    AzureAISearchToolResource,
    AISearchIndexResource,
    AzureAISearchQueryType,
)

load_dotenv()

endpoint = os.environ["FOUNDRY_PROJECT_ENDPOINT"]
agent_name = os.environ.get("FOUNDRY_AGENT_NAME", "MyAgent")


tool = AzureAISearchTool(
    azure_ai_search=AzureAISearchToolResource(
        indexes=[
            AISearchIndexResource(
                project_connection_id=os.environ["AI_SEARCH_PROJECT_CONNECTION_ID"],
                index_name=os.environ["AI_SEARCH_INDEX_NAME"],
                query_type=AzureAISearchQueryType.SIMPLE,
            ),
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
            instructions="""You are a helpful assistant. You must always provide citations for
            answers using the tool and render them as: `\u3010message_idx:search_idx\u2020source\u3011`.""",
            tools=[tool],
        ),
        description="You are a helpful agent.",
    ),
    project_client.get_openai_client(agent_name=agent_name) as openai_client,
):
    # Get user input from environment variable or prompt
    user_input = os.environ.get("AI_SEARCH_USER_INPUT")
    if not user_input:
        user_input = input("Enter your question (e.g., 'Tell me about mental health services'): \n")

    stream_response = openai_client.responses.create(
        stream=True,
        tool_choice="required",
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
            print(f"Agent response: {event.response.output_text}")
