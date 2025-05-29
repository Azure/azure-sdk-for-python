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

    pip install azure-ai-agents azure-identity

    Set this environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) SHAREPOINT_CONNECTION_ID  - The ID of the Sharepoint connection, in the format of:
       /subscriptions/{subscription-id}/resourceGroups/{resource-group-name}/providers/Microsoft.MachineLearningServices/workspaces/{workspace-name}/connections/{connection-name}
"""

import os
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import SharepointTool


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

conn_id = os.environ["SHAREPOINT_CONNECTION_ID"]

# Initialize Sharepoint tool with connection id
sharepoint = SharepointTool(connection_id=conn_id)

# Create agent with Sharepoint tool and process agent run
with agents_client:
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
    messages = agents_client.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
