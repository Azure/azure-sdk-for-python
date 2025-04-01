# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_fabric.py

DESCRIPTION:
    This sample demonstrates how to use Agent operations with the Microsoft Fabric grounding tool from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_fabric.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import FabricTool

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# [START create_agent_with_fabric_tool]
fabric_connection = project_client.connections.get(connection_name=os.environ["FABRIC_CONNECTION_NAME"])
conn_id = fabric_connection.id

print(conn_id)

# Initialize an Agent Fabric tool and add the connection id
fabric = FabricTool(connection_id=conn_id)

# Create an Agent with the Fabric tool and process an Agent run
with project_client:
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=fabric.definitions,
        headers={"x-ms-enable-preview": "true"},
    )
    # [END create_agent_with_fabric_tool]
    print(f"Created Agent, ID: {agent.id}")

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="<User query against Fabric resource>",
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
    print(f"Messages: {messages}")
