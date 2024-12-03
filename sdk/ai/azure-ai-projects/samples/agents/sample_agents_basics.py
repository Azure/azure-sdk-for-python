# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_basics.py

DESCRIPTION:
    This sample demonstrates how to use basic agent operations from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_basics.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os, time
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import MessageTextContent

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

# [START create_project_client]
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)
# [END create_project_client]

with project_client:

    # [START create_agent]
    agent = project_client.agents.create_agent(
        model="gpt-4-1106-preview",
        name="my-assistant",
        instructions="You are helpful assistant",
    )
    # [END create_agent]
    print(f"Created agent, agent ID: {agent.id}")

    # [START create_thread]
    thread = project_client.agents.create_thread()
    # [END create_thread]
    print(f"Created thread, thread ID: {thread.id}")

    # [START create_message]
    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    # [END create_message]
    print(f"Created message, message ID: {message.id}")

    # [START create_run]
    run = project_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)

    # poll the run as long as run status is queued or in progress
    while run.status in ["queued", "in_progress", "requires_action"]:
        # wait for a second
        time.sleep(1)
        run = project_client.agents.get_run(thread_id=thread.id, run_id=run.id)
        # [END create_run]
        print(f"Run status: {run.status}")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # [START list_messages]
    messages = project_client.agents.list_messages(thread_id=thread.id)

    # The messages are following in the reverse order,
    # we will iterate them and output only text contents.
    for data_point in reversed(messages.data):
        last_message_content = data_point.content[-1]
        if isinstance(last_message_content, MessageTextContent):
            print(f"{data_point.role}: {last_message_content.text.value}")

    # [END list_messages]
    print(f"Messages: {messages}")
