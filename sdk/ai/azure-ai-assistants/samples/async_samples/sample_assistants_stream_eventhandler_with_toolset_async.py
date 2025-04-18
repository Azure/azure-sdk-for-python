# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use assistant operations with an event handler and toolset from
    the Azure Assistants service using a asynchronous client.

USAGE:
    python sample_assistants_stream_eventhandler_with_toolset_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Assistants endpoint.
"""
import asyncio
from typing import Any

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models import MessageDeltaChunk, RunStep, ThreadMessage, ThreadRun
from azure.ai.assistants.models import AsyncAssistantEventHandler, AsyncFunctionTool, AsyncToolSet
from azure.identity.aio import DefaultAzureCredential

import os

from user_async_functions import user_async_functions


class MyEventHandler(AsyncAssistantEventHandler):

    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    async def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

    async def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_done(self) -> None:
        print("Stream completed.")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


async def main() -> None:
    async with DefaultAzureCredential() as creds:
        async with AssistantsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as assistants_client:

            # Initialize toolset with user functions
            functions = AsyncFunctionTool(user_async_functions)
            toolset = AsyncToolSet()
            toolset.add(functions)

            assistant = await assistants_client.create_assistant(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-assistant",
                instructions="You are helpful assistant",
                toolset=toolset,
            )
            print(f"Created assistant, assistant ID: {assistant.id}")

            thread = await assistants_client.create_thread()
            print(f"Created thread, thread ID {thread.id}")

            message = await assistants_client.create_message(
                thread_id=thread.id,
                role="user",
                content="Hello, send an email with the datetime and weather information in New York? Also let me know the details",
            )
            print(f"Created message, message ID {message.id}")

            async with await assistants_client.create_stream(
                thread_id=thread.id, assistant_id=assistant.id, event_handler=MyEventHandler()
            ) as stream:
                await stream.until_done()

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistants_client.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
