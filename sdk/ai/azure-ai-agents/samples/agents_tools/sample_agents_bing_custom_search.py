# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Bing Custom Search tool from
    the Azure Agents service using a synchronous client.
    For more information on the Bing Custom Search tool, see: https://aka.ms/AgentCustomSearchDoc

USAGE:
    python sample_agents_bing_custom_search.py

    Before running the sample:

    pip install azure-identity
    pip install --pre azure-ai-projects

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) BING_CUSTOM_CONNECTION_NAME - The name of a connection to the custom search Bing resource as it is
       listed in Azure AI Foundry connected resources.
    4) BING_CONFIGURATION_NAME - the name of a search configuration in Grounding with Bing Custom Search
       resource.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import BingCustomSearchTool, ListSortOrder

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

conn_id = project_client.connections.get(os.environ["BING_CUSTOM_CONNECTION_NAME"]).id

# Initialize Bing Custom Search tool with connection id and instance name
bing_custom_tool = BingCustomSearchTool(connection_id=conn_id, instance_name=os.environ["BING_CONFIGURATION_NAME"])

# Create Agent with the Bing Custom Search tool and process Agent run
with project_client:
    agents_client = project_client.agents

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=bing_custom_tool.definitions,
    )
    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="How many medals did the USA win in the 2024 summer olympics?",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process Agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            responses = []
            for text_message in msg.text_messages:
                responses.append(text_message.text.value)
            message = " ".join(responses)
            for annotation in msg.url_citation_annotations:
                message = message.replace(
                    annotation.text, f" [{annotation.url_citation.title}]({annotation.url_citation.url})"
                )
            print(f"{msg.role}: {message}")
