# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ----------------------------------d--

"""
FILE: sample_agents_sharepoint.py

DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Microsoft SharePoint grounding tool from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_sharepoint.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
    SHAREPOINT_CONNECTION_NAME - the name of your SharePoint connection in AI Studio.
    MODEL_DEPLOYMENT_NAME - the name of your model deployment.

SETTING UP A SHAREPOINT DATA CONNECTION:
    1. Go to your Azure AI Studio project (https://ai.azure.com)
    2. Navigate to the "Connections" section in the left sidebar
    3. Click on "Create" to add a new connection
    4. Select "SharePoint" as the connection type
    5. Enter a name for your connection in the "Connection name" field
       (This will be used as the SHAREPOINT_CONNECTION_NAME environment variable)
    6. Follow the authentication flow to connect to your SharePoint account
    7. Select the SharePoint site(s) you want to include in your connection
    8. Complete the setup by clicking "Create"
    9. After creation, the connection will be available to use in your AI Projects

    Note: The SharePoint connection provides access to documents, lists, and other content 
    stored in your organization's SharePoint sites through the AI agent.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import SharepointTool

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# [START create_agent_with_sharepoint_tool]
sharepoint_connection = project_client.connections.get(connection_name=os.environ["SHAREPOINT_CONNECTION_NAME"])
conn_id = sharepoint_connection.id

print(conn_id)

# Initialize an Agent SharePoint tool and add the connection id
sharepoint = SharepointTool(connection_id=conn_id)

# Create an Agent with the SharePoint tool and process an Agent run
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="sharepoint-agent",
        instructions="You are a helpful agent that can search and retrieve information from SharePoint",
        tools=sharepoint.definitions,
        headers={"x-ms-enable-preview": "true"},
    )
    # [END create_agent_with_sharepoint_tool]
    print(f"Created Agent, ID: {agent.id}")

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Find documents in our SharePoint related to quarterly performance reports",
    )
    print(f"Created message, ID: {message.id}")

    # Create and process an Agent run in thread with tools
    run = project_client.agents.create_and_process_run(thread_id=thread.id, agent_id=agent.id)
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    # Delete the Agent when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = project_client.agents.list_messages(thread_id=thread.id)
    print("Messages:")
    for msg in messages:
        print(f"Role: {msg.role}, Content: {msg.content}")
