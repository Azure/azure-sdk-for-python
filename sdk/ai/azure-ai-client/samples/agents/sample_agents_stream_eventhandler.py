# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential

from azure.ai.client.models import (
    AgentEventHandler,
    MessageDeltaTextContent,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)

from typing import Any

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

connection_string = os.environ["AI_CLIENT_CONNECTION_STRING"]

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=connection_string,
)

# Or, you can create the Azure AI Client by giving all required parameters directly
"""
ai_client = AzureAIClient(
    credential=DefaultAzureCredential(),
    host_name=os.environ["AI_CLIENT_HOST_NAME"],
    subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
    workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
    logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
)
"""


class MyEventHandler(AgentEventHandler):
    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


# Create an agent and run stream with event handler
agent = ai_client.agents.create_agent(
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant"
)
print(f"Created agent, agent ID {agent.id}")

thread = ai_client.agents.create_thread()
print(f"Created thread, thread ID {thread.id}")

message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
print(f"Created message, message ID {message.id}")

with ai_client.agents.create_and_process_run(
    thread_id=thread.id, assistant_id=agent.id, stream=True, event_handler=MyEventHandler()
) as stream:
    stream.until_done()

ai_client.agents.delete_agent(agent.id)
print("Deleted agent")

messages = ai_client.agents.list_messages(thread_id=thread.id)
print(f"Messages: {messages}")
