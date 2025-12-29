# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_sharepoint.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with the
    Sharepoint tool from the Azure Agents service using a synchronous client.
    The sharepoint tool is currently available only to whitelisted customers.
    For access and onboarding instructions, please contact azureagents-preview@microsoft.com.

USAGE:
    python sample_agents_sharepoint.py

    Before running the sample:

    pip install azure-identity
    pip install --pre azure-ai-projects

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) SHAREPOINT_CONNECTION_NAME  - The name of a connection to the SharePoint resource as it is
       listed in Azure AI Foundry connected resources.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder, SharepointTool

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

conn_id = project_client.connections.get(os.environ["SHAREPOINT_CONNECTION_NAME"]).id

# Initialize Sharepoint tool with connection id
sharepoint = SharepointTool(connection_id=conn_id)

# Create agent with Sharepoint tool and process agent run
with project_client:
    agents_client = project_client.agents

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=sharepoint.definitions,
    )
    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, summarize the key points of the <sharepoint_resource_document>",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the agent when done
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
