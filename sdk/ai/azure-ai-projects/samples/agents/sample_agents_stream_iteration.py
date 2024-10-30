# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_iteration.py

DESCRIPTION:
    This sample demonstrates how to use agent operations in streaming from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_iteration.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import (
    AgentStreamEvent,
    MessageDeltaTextContent,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

with project_client:
    # Create an agent and run stream with iteration
    agent = project_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant"
    )
    print(f"Created agent, ID {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID {message.id}")

    with project_client.agents.create_stream(thread_id=thread.id, assistant_id=agent.id) as stream:

        for event_type, event_data in stream:

            if isinstance(event_data, MessageDeltaChunk):
                for content_part in event_data.delta.content:
                    if isinstance(content_part, MessageDeltaTextContent):
                        text_value = content_part.text.value if content_part.text else "No text"
                        print(f"Text delta received: {text_value}")

            elif isinstance(event_data, ThreadMessage):
                print(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

            elif isinstance(event_data, ThreadRun):
                print(f"ThreadRun status: {event_data.status}")

            elif isinstance(event_data, RunStep):
                print(f"RunStep type: {event_data.type}, Status: {event_data.status}")

            elif event_type == AgentStreamEvent.ERROR:
                print(f"An error occurred. Data: {event_data}")

            elif event_type == AgentStreamEvent.DONE:
                print("Stream completed.")
                break

            else:
                print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
