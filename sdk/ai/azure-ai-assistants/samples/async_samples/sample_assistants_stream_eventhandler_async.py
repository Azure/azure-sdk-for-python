# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with an event handler in streaming from
    the Azure Assistants service using a asynchronous client.

USAGE:
    python sample_assistants_stream_eventhandler_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
from typing import Any, Optional

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.assistants.models import AsyncAssistantEventHandler
from azure.identity.aio import DefaultAzureCredential

import os


class MyEventHandler(AsyncAssistantEventHandler[str]):

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> Optional[str]:
        return f"Text delta received: {delta.text}"

    async def on_thread_message(self, message: "ThreadMessage") -> Optional[str]:
        return f"ThreadMessage created. ID: {message.id}, Status: {message.status}"

    async def on_thread_run(self, run: "ThreadRun") -> Optional[str]:
        return f"ThreadRun status: {run.status}"

    async def on_run_step(self, step: "RunStep") -> Optional[str]:
        return f"RunStep type: {step.type}, Status: {step.status}"

    async def on_error(self, data: str) -> Optional[str]:
        return f"An error occurred. Data: {data}"

    async def on_done(self) -> Optional[str]:
        return "Stream completed."

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> Optional[str]:
        return f"Unhandled Event Type: {event_type}, Data: {event_data}"


async def main() -> None:

    async with DefaultAzureCredential() as creds:
        async with AssistantsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as assistants_client:
            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are helpful assistant"
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID {thread.id}")

            message = await assistants_client.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID {message.id}")

            async with await assistants_client.create_stream(
                thread_id=thread.id, assistant_id=assistant.id, event_handler=MyEventHandler()
            ) as stream:
                async for event_type, event_data, func_return in stream:
                    print(f"Received data.")
                    print(f"Streaming receive Event Type: {event_type}")
                    print(f"Event Data: {str(event_data)[:100]}...")
                    print(f"Event Function return: {func_return}\n")

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistants_client.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
