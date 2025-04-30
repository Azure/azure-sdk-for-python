# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with an event handler and toolset from
    the Azure Assistants service using a synchronous client.

USAGE:
    python sample_assistants_stream_eventhandler_with_toolset.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

from azure.ai.assistants import AssistantsClient
from azure.ai.assistants.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.assistants.models import AssistantEventHandler
from azure.identity import DefaultAzureCredential
from azure.ai.assistants.models import FunctionTool, ToolSet

import os
from typing import Any
from user_functions import user_functions

assistants_client = AssistantsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)


# When using FunctionTool with ToolSet in assistant creation, the tool call events are handled inside the create_stream
# method and functions gets automatically called by default.
class MyEventHandler(AssistantEventHandler):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


with assistants_client:
    # [START create_assistant_with_function_tool]
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)

    assistant = assistants_client.create_assistant(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        toolset=toolset,
    )
    # [END create_assistant_with_function_tool]
    print(f"Created assistant, ID: {assistant.id}")

    thread = assistants_client.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = assistants_client.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York? Also let me know the details",
    )
    print(f"Created message, message ID {message.id}")

    with assistants_client.create_stream(
        thread_id=thread.id, assistant_id=assistant.id, event_handler=MyEventHandler()
    ) as stream:
        stream.until_done()

    assistants_client.delete_assistant(assistant.id)
    print("Deleted assistant")

    messages = assistants_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
