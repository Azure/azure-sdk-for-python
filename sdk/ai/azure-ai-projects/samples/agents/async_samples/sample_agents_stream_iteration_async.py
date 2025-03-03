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

    pip install azure-ai-projects azure-identity aiohttp

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import asyncio

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import AgentStreamEvent
from azure.ai.projects.models import MessageDeltaChunk, RunStep, ThreadMessage, ThreadRun
from azure.identity.aio import DefaultAzureCredential

import os


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

            async with await project_client.agents.create_stream(thread_id=thread.id, assistant_id=agent.id) as stream:
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

            await project_client.agents.delete_agent(agent.id)
            print("Deleted agent")

            messages = await project_client.agents.list_messages(thread_id=thread.id)
            print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
