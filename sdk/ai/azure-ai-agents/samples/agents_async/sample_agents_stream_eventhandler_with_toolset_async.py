# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler and toolset from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_stream_eventhandler_with_toolset_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_ENDPOINT - the Azure AI Agents endpoint.
"""
import asyncio
from typing import Any

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import MessageDeltaChunk, RunStep, ThreadMessage, ThreadRun
from azure.ai.agents.models import AsyncAgentEventHandler, AsyncFunctionTool, AsyncToolSet
from azure.identity.aio import DefaultAzureCredential

import os

from utils.user_async_functions import user_async_functions


class MyEventHandler(AsyncAgentEventHandler):

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
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:

            # Initialize toolset with user functions
            functions = AsyncFunctionTool(user_async_functions)
            toolset = AsyncToolSet()
            toolset.add(functions)

            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"],
                name="my-agent",
                instructions="You are helpful agent",
                toolset=toolset,
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id,
                role="user",
                content="Hello, send an email with the datetime and weather information in New York? Also let me know the details",
            )
            print(f"Created message, message ID {message.id}")

            async with await agents_client.runs.stream(
                thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()
            ) as stream:
                await stream.until_done()

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = await agents_client.messages.list(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
