# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_iteration_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with interation in streaming from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_stream_iteration_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models import AgentStreamEvent
from azure.ai.projects.models import MessageDeltaChunk, MessageDeltaTextContent, RunStep, ThreadMessage, ThreadRun
from azure.identity.aio import DefaultAzureCredential

import os


async def main() -> None:
    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
    # Customer needs to login to Azure subscription via Azure CLI and set the environment variables

    project_client = AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
    )

    async with project_client:
        agent = await project_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = await project_client.agents.create_thread()
        print(f"Created thread, thread ID {thread.id}")

        message = await project_client.agents.create_message(
            thread_id=thread.id, role="user", content="Hello, tell me a joke"
        )
        print(f"Created message, message ID {message.id}")

        async with await project_client.agents.create_stream(thread_id=thread.id, assistant_id=agent.id) as stream:
            async for event_type, event_data in stream:

                if isinstance(event_data, MessageDeltaChunk):
                    for content_part in event_data.delta.content:
                        if isinstance(content_part, MessageDeltaTextContent):
                            text_value = content_part.text.value if content_part.text else "No text"
                            print(f"Text delta received: {text_value}")

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
