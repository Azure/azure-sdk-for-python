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

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio
from typing import Any, Optional

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.projects.models import AsyncAgentEventHandler
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
        async with AIProjectClient.from_connection_string(
            credential=creds, conn_str=os.environ["PROJECT_CONNECTION_STRING"]
        ) as project_client:
            agent = await project_client.agents.create_agent(
                model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-assistant", instructions="You are helpful assistant"
            )
            print(f"Created agent, agent ID: {agent.id}")

            thread = await project_client.agents.create_thread()
            print(f"Created thread, thread ID {thread.id}")

            message = await project_client.agents.create_message(
                thread_id=thread.id, role="user", content="Hello, tell me a joke"
            )
            print(f"Created message, message ID {message.id}")

            async with await project_client.agents.create_stream(
                thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
            ) as stream:
                async for event_type, event_data, func_return in stream:
                    print(f"Received data.")
                    print(f"Streaming receive Event Type: {event_type}")
                    print(f"Event Data: {str(event_data)[:100]}...")
                    print(f"Event Function return: {func_return}\n")

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
