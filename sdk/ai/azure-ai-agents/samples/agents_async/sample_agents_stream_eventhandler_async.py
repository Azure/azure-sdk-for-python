# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler in streaming from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_stream_eventhandler_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model.
"""
import asyncio
from typing import Any, Optional

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import (
    ListSortOrder,
    MessageTextContent,
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.agents.models import AsyncAgentEventHandler
from azure.identity.aio import DefaultAzureCredential

import os


class MyEventHandler(AsyncAgentEventHandler[str]):

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
        async with AgentsClient(
            endpoint=os.environ["PROJECT_ENDPOINT"],
            credential=creds,
        ) as agents_client:
            agent = await agents_client.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await agents_client.threads.create()
            print(f"Created thread, thread ID {thread.id}")

            message = await agents_client.messages.create(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID {message.id}")

            async with await agents_client.runs.stream(
                thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()
            ) as stream:
                async for event_type, event_data, func_return in stream:
                    print(f"Received data.")
                    print(f"Streaming receive Event Type: {event_type}")
                    print(f"Event Data: {str(event_data)[:100]}...")
                    print(f"Event Function return: {func_return}\n")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
