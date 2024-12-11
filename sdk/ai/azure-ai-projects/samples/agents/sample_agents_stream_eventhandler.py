# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_eventhandler.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler in streaming from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_eventhandler.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

from azure.ai.projects.models import (
    AgentEventHandler,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)

from typing import Any


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)


# [START stream_event_handler]
class MyEventHandler(AgentEventHandler[str]):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        self.custom_data = f"Text delta received: {delta.text}"

    def on_thread_message(self, message: "ThreadMessage") -> None:
        self.custom_data = f"ThreadMessage created. ID: {message.id}, Status: {message.status}"

    def on_thread_run(self, run: "ThreadRun") -> None:
        self.custom_data = f"ThreadRun status: {run.status}"

    def on_run_step(self, step: "RunStep") -> None:
        self.custom_data = f"RunStep type: {step.type}, Status: {step.status}"

    def on_error(self, data: str) -> None:
        self.custom_data = f"An error occurred. Data: {data}"

    def on_done(self) -> None:
        self.custom_data = "Stream completed."

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        self.custom_data = f"Unhandled Event Type: {event_type}, Data: {event_data}"


# [END stream_event_handler]


with project_client:
    # Create an agent and run stream with event handler
    agent = project_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant"
    )
    print(f"Created agent, agent ID {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID {message.id}")

    # [START create_stream]
    with project_client.agents.create_stream(
        thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
    ) as stream:
        for _, _, custom_data in stream:
            print(custom_data)
    # [END create_stream]

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
