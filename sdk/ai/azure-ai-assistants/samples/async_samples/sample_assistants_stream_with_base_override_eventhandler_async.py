# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to override the base event handler, parse the events, and iterate through them.
    In your use case, you might not want to write the iteration code similar to sample_assistants_stream_iteration_async.py.
    If you have multiple places to call create_stream, you might find the iteration code cumbersome.
    This example shows how to override the base event handler, parse the events, and iterate through them, which can be 
    reused in multiple create_stream calls to help keep the code clean.

USAGE:
    python sample_assistants_stream_with_base_override_eventhandler_async.py

    Before running the sample:

    pip install azure-ai-assistants azure-identity aiohttp

    Set these environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
import json
from typing import AsyncGenerator, Optional

from azure.ai.assistants.aio import AssistantsClient
from azure.ai.assistants.models._models import (
    MessageDeltaChunk,
    MessageDeltaTextContent,
)
from azure.ai.assistants.models import AssistantStreamEvent, BaseAsyncAssistantEventHandler
from azure.identity.aio import DefaultAzureCredential

import os


# Our goal is to parse the event data in a string and return the chunk in text for each iteration.
# Because we want the iteration to be a string, we define str as the generic type for BaseAsyncAssistantEventHandler
# and override the _process_event method to return a string.
# The get_stream_chunks method is defined to return the chunks as strings because the iteration is a string.
class MyEventHandler(BaseAsyncAssistantEventHandler[Optional[str]]):

    async def _process_event(self, event_data_str: str) -> Optional[str]:

        event_lines = event_data_str.strip().split("\n")
        event_type: Optional[str] = None
        event_data = ""
        for line in event_lines:
            if line.startswith("event:"):
                event_type = line.split(":", 1)[1].strip()
            elif line.startswith("data:"):
                event_data = line.split(":", 1)[1].strip()

        if not event_type:
            raise ValueError("Event type not specified in the event data.")

        if event_type == AssistantStreamEvent.THREAD_MESSAGE_DELTA.value:

            event_obj: MessageDeltaChunk = MessageDeltaChunk(**json.loads(event_data))

            for content_part in event_obj.delta.content:
                if isinstance(content_part, MessageDeltaTextContent):
                    if content_part.text is not None:
                        return content_part.text.value
        return None

    async def get_stream_chunks(self) -> AsyncGenerator[str, None]:
        async for chunk in self:
            if chunk:
                yield chunk


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
                async for chunk in stream.get_stream_chunks():
                    print(chunk)

            await assistants_client.delete_assistant(assistant.id)
            print("Deleted assistant")

            messages = await assistants_client.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
