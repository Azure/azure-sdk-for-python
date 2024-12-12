# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to override the base event handler and parse the events and iterate through them
    In your use case, you might not want to write the iteration code similar to sample_agents_stream_iteration_async.py.
    If you have multiple places to call create_stream, you might find the iteration code cumbersome.
    This example shows how to override the base event handler, parse the events, and iterate through them, which can be reused in multiple create_stream calls to help keep the code clean.

USAGE:
    python sample_agents_stream_with_base_override_eventhandler.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Foundry project.
"""
import io
import json
from typing import Generator, Generator, Optional

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MessageDeltaChunk,
    MessageDeltaTextContent,
)
from azure.ai.projects.models import AgentStreamEvent, BaseAgentEventHandler
from azure.identity import DefaultAzureCredential

import os


# Our goal is to parse the event data in a string and return the chunk in text for each iteration.
# Because we want the iteration to be a string, we define str as the generic type for BaseAsyncAgentEventHandler
# and override the _process_event method to return a string.
# The get_stream_chunks method is defined to return the chunks as strings because the iteration is a string.
class MyEventHandler(BaseAgentEventHandler[str]):

    def _process_event(self, event_data_str: str) -> Optional[str]:  # type: ignore[return]
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
        return None

    def get_stream_chunks(self) -> Generator[str, None, None]:
        for chunk in self:
            yield chunk


project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

with project_client:
    agent = project_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID {message.id}")

    with project_client.agents.create_stream(
        thread_id=thread.id, assistant_id=agent.id, event_handler=MyEventHandler()
    ) as stream:
        for chunk in stream.get_stream_chunks():
            print(chunk)

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
