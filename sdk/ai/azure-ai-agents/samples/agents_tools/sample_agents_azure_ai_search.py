# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------


"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with the
    Azure AI Search tool from the Azure agents service using a synchronous client.

PREREQUISITES:
    You will need an Azure AI Search Resource.
    If you already have one, you must create an agent that can use an existing Azure AI Search index:
    https://learn.microsoft.com/azure/ai-services/agents/how-to/tools/azure-ai-search?tabs=azurecli%2Cpython&pivots=overview-azure-ai-search

    If you do not already have an agent Setup with an Azure AI Search resource, follow the guide for a Standard agent setup:
    https://learn.microsoft.com/azure/ai-services/agents/quickstart?pivots=programming-language-python-azure

USAGE:
    python sample_agents_azure_ai_search.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) AI_SEARCH_CONNECTION_NAME - The connection name of the AI Search connection to your Foundry project,
       as found under the "Name" column in the "Connected Resources" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import AzureAISearchQueryType, AzureAISearchTool, ListSortOrder, MessageRole

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# [START create_agent_with_azure_ai_search_tool]
conn_id = os.environ["AI_AZURE_AI_CONNECTION_ID"]

print(conn_id)

# Initialize agent AI search tool and add the search index connection id
ai_search = AzureAISearchTool(
    index_connection_id=conn_id, index_name="sample_index", query_type=AzureAISearchQueryType.SIMPLE, top_k=3, filter=""
)

# Create agent with AI search tool and process agent run
with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=ai_search.definitions,
        tool_resources=ai_search.resources,
    )
    # [END create_agent_with_azure_ai_search_tool]
    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="What is the temperature rating of the cozynights sleeping bag?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Fetch run steps to get the details of the agent run
    run_steps = agents_client.run_steps.list(thread_id=thread.id, run_id=run.id)
    for step in run_steps:
        print(f"Step {step['id']} status: {step['status']}")
        step_details = step.get("step_details", {})
        tool_calls = step_details.get("tool_calls", [])

        if tool_calls:
            print("  Tool calls:")
            for call in tool_calls:
                print(f"    Tool Call ID: {call.get('id')}")
                print(f"    Type: {call.get('type')}")

                azure_ai_search_details = call.get("azure_ai_search", {})
                if azure_ai_search_details:
                    print(f"    azure_ai_search input: {azure_ai_search_details.get('input')}")
                    print(f"    azure_ai_search output: {azure_ai_search_details.get('output')}")
        print()  # add an extra newline between steps

    # Delete the agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # [START populate_references_agent_with_azure_ai_search_tool]
    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for message in messages:
        if message.role == MessageRole.AGENT and message.url_citation_annotations:
            placeholder_annotations = {
                annotation.text: f" [see {annotation.url_citation.title}] ({annotation.url_citation.url})"
                for annotation in message.url_citation_annotations
            }
            for message_text in message.text_messages:
                message_str = message_text.text.value
                for k, v in placeholder_annotations.items():
                    message_str = message_str.replace(k, v)
                print(f"{message.role}: {message_str}")
        else:
            for message_text in message.text_messages:
                print(f"{message.role}: {message_text.text.value}")
    # [END populate_references_agent_with_azure_ai_search_tool]
