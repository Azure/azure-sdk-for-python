# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_with_base_override_eventhandler_async.py

DESCRIPTION:
    This sample demonstrates how to override the base event handler and parse the events and iterate through them

USAGE:
    python sample_agents_stream_with_base_override_eventhandler_async.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio
import json
from typing import AsyncGenerator, Generator, Optional

from azure.ai.projects.aio import AIProjectClient
from azure.ai.projects.models._models import (
    MessageDeltaChunk,
    MessageDeltaTextContent,
)
from azure.ai.projects.models import AgentStreamEvent, BaseAsyncAgentEventHandler
from azure.identity.aio import DefaultAzureCredential

import os


class MyEventHandler(BaseAsyncAgentEventHandler[str]):
    
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
        
        if event_type == AgentStreamEvent.THREAD_MESSAGE_DELTA.value:

            event_obj: MessageDeltaChunk = MessageDeltaChunk(**json.loads(event_data))

            for content_part in event_obj.delta.content:
                if isinstance(content_part, MessageDeltaTextContent):
                    if content_part.text is not None:
                        return content_part.text.value
    
    async def get_stream_chunks(self) -> AsyncGenerator[str, None]:
        async for chunk in self:
            yield chunk
    

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

        async with await project_client.agents.create_stream(
            thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
        ) as stream:
            async for chunk in stream.get_stream_chunks():
                print(chunk)

        await project_client.agents.delete_agent(agent.id)
        print("Deleted agent")

        messages = await project_client.agents.list_messages(thread_id=thread.id)
        print(f"Messages: {messages}")


if __name__ == "__main__":
    asyncio.run(main())
