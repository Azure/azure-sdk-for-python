# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_eventhandler_async.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler in streaming from
    the Azure Agents service using a asynchronous client.

USAGE:
    python sample_agents_stream_eventhandler_async.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio
from typing import Any

from azure.ai.client.aio import AzureAIClient
from azure.ai.client.models._models import MessageDeltaChunk, MessageDeltaTextContent, RunStep, ThreadMessage, ThreadRun
from azure.ai.client.models._patch import AsyncAgentEventHandler
from azure.identity import DefaultAzureCredential

import os


class MyEventHandler(AsyncAgentEventHandler):
    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    async def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

    async def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    async def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    async def on_done(self) -> None:
        print("Stream completed.")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


async def main():
    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
    # Customer needs to login to Azure subscription via Azure CLI and set the environment variables

    ai_client = AzureAIClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"]
    )

    # Or, you can create the Azure AI Client by giving all required parameters directly
    """
    ai_client = AzureAIClient(
        credential=DefaultAzureCredential(),
        host_name=os.environ["AI_CLIENT_HOST_NAME"],
        subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
        workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
        logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
    )
    """    
        
    async with ai_client:    
        agent = await ai_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
        )
        print(f"Created agent, agent ID: {agent.id}")

        thread = await ai_client.agents.create_thread()
        print(f"Created thread, thread ID {thread.id}")

        message = await ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        print(f"Created message, message ID {message.id}")

        async with await ai_client.agents.create_stream(
            thread_id=thread.id, 
            assistant_id=agent.id,
            event_handler=MyEventHandler()
        ) as stream:
            await stream.until_done()

        await ai_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        messages = await ai_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
