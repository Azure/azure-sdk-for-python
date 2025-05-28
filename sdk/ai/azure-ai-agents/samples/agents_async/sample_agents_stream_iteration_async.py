# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with interation in streaming from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_stream_iteration_async.py

    Before running the sample:

    pip install azure-ai-agents azure-identity aiohttp

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model.
"""
import asyncio

from azure.ai.agents.aio import AgentsClient
from azure.ai.agents.models import AgentStreamEvent
from azure.ai.agents.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
    ListSortOrder,
    MessageTextContent,
)
from azure.identity.aio import DefaultAzureCredential

import os


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

            async with await agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:
                async for event_type, event_data, _ in stream:

                    if isinstance(event_data, MessageDeltaChunk):
                        print(f"Text delta received: {event_data.text}")

                    elif isinstance(event_data, ThreadMessage):
                        print(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

                    elif isinstance(event_data, ThreadRun):
                        print(f"ThreadRun status: {event_data.status}")
                    elif isinstance(event_data, RunStep):
                        print(f"RunStep type: {event_data.type}, Status: {event_data.status}")

                    elif event_type == AgentStreamEvent.ERROR:
                        print(f"An error occurred. Data: {event_data}")

                    elif event_type == AgentStreamEvent.DONE:
                        print("Stream completed.")
                        break

                    else:
                        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

            await agents_client.delete_agent(agent.id)
            print("Deleted agent")

            messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
            async for msg in messages:
                last_part = msg.content[-1]
                if isinstance(last_part, MessageTextContent):
                    print(f"{msg.role}: {last_part.text.value}")


if __name__ == "__main__":
    asyncio.run(main())
