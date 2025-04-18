# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with an event handler in streaming from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_stream_eventhandler.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.assistants import AssistantsClient
from azure.identity import DefaultAzureCredential

from azure.ai.assistants.models import (
    AssistantEventHandler,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)

from typing import Any, Optional

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)


# [START stream_event_handler]
# With AssistantEventHandler[str], the return type for each event functions is optional string.
class MyEventHandler(AssistantEventHandler[str]):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> Optional[str]:
        return f"Text delta received: {delta.text}"

    def on_thread_message(self, message: "ThreadMessage") -> Optional[str]:
        return f"ThreadMessage created. ID: {message.id}, Status: {message.status}"

    def on_thread_run(self, run: "ThreadRun") -> Optional[str]:
        return f"ThreadRun status: {run.status}"

    def on_run_step(self, step: "RunStep") -> Optional[str]:
        return f"RunStep type: {step.type}, Status: {step.status}"

    def on_error(self, data: str) -> Optional[str]:
        return f"An error occurred. Data: {data}"

    def on_done(self) -> Optional[str]:
        return "Stream completed."

    def on_unhandled_event(self, event_type: str, event_data: Any) -> Optional[str]:
        return f"Unhandled Event Type: {event_type}, Data: {event_data}"


# [END stream_event_handler]


with assistants_client:
    # Create an assistant and run stream with event handler
    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are a helpful assistant"
    )
    print(f"Created assistant, assistant ID {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = assistants_client.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID {message.id}")

    # [START create_stream]
    with assistants_client.create_stream(
        thread_id=thread.id, assistant_id=assistant.id, event_handler=MyEventHandler()
    ) as stream:
        for event_type, event_data, func_return in stream:
            print(f"Received data.")
            print(f"Streaming receive Event Type: {event_type}")
            print(f"Event Data: {str(event_data)[:100]}...")
            print(f"Event Function return: {func_return}\n")
    # [END create_stream]

    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
