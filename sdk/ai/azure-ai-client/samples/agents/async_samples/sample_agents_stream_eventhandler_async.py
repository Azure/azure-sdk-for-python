# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
import logging
from typing import Any

from azure.ai.client.aio import AzureAIClient
from azure.ai.client.models._models import MessageDeltaChunk, MessageDeltaTextContent, RunStep, ThreadMessage, ThreadRun
from azure.ai.client.models._patch import AsyncAgentEventHandler
from azure.identity import DefaultAzureCredential

import os

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

connection_string = os.environ["AI_CLIENT_CONNECTION_STRING"]

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=connection_string,
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

class MyEventHandler(AsyncAgentEventHandler):
    async def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                logging.info(f"Text delta received: {text_value}")

    async def on_thread_message(self, message: "ThreadMessage") -> None:
        logging.info(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    async def on_thread_run(self, run: "ThreadRun") -> None:
        logging.info(f"ThreadRun status: {run.status}")

    async def on_run_step(self, step: "RunStep") -> None:
        logging.info(f"RunStep type: {step.type}, Status: {step.status}")

    async def on_error(self, data: str) -> None:
        logging.error(f"An error occurred. Data: {data}")

    async def on_done(self) -> None:
        logging.info("Stream completed.")

    async def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        logging.warning(f"Unhandled Event Type: {event_type}, Data: {event_data}")


async def main():
    async with ai_client:    
        agent = await ai_client.agents.create_agent(
            model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
        )
        logging.info(f"Created agent, agent ID: {agent.id}")

        thread = await ai_client.agents.create_thread()
        logging.info(f"Created thread, thread ID {thread.id}")

        message = await ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
        logging.info(f"Created message, message ID {message.id}")

        async with await ai_client.agents.create_and_process_run(
            thread_id=thread.id, 
            assistant_id=agent.id,
            stream=True,
            event_handler=MyEventHandler()
        ) as stream:
            await stream.until_done()

        await ai_client.agents.delete_agent(agent.id)
        logging.info("Deleted assistant")

        messages = await ai_client.agents.list_messages(thread_id=thread.id)
        logging.info(f"Messages: {messages}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
