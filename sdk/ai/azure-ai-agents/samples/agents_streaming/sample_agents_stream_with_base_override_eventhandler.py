# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to override the base event handler and parse the events and iterate through them
    In your use case, you might not want to write the iteration code similar to sample_agents_stream_iteration_async.py.
    If you have multiple places to call stream, you might find the iteration code cumbersome.
    This example shows how to override the base event handler, parse the events, and iterate through them, which can be reused in multiple stream calls to help keep the code clean.

USAGE:
    python sample_agents_stream_with_base_override_eventhandler.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import json
from typing import Generator, Optional

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    MessageDeltaChunk,
    MessageDeltaTextContent,
    ListSortOrder,
)
from azure.ai.agents.models import AgentStreamEvent, BaseAgentEventHandler
from azure.identity import DefaultAzureCredential

import os


# Our goal is to parse the event data in a string and return the chunk in text for each iteration.
# Because we want the iteration to be a string, we define str as the generic type for BaseAsyncAgentEventHandler
# and override the _process_event method to return a string.
# The get_stream_chunks method is defined to return the chunks as strings because the iteration is a string.
class MyEventHandler(BaseAgentEventHandler[Optional[str]]):

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
            if chunk:
                yield chunk


agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with agents_client:
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"], name="my-agent", instructions="You are helpful agent"
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.messages.create(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    print(f"Created message, message ID {message.id}")

    with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()) as stream:
        for chunk in stream.get_stream_chunks():
            print(chunk)

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
