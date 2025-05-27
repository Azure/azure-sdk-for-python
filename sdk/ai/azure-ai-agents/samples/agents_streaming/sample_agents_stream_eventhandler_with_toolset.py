# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler and toolset from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_eventhandler_with_toolset.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    MessageDeltaChunk,
    ListSortOrder,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.agents.models import AgentEventHandler
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import FunctionTool, ToolSet

import os, sys
from typing import Any

current_path = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from samples.utils.user_functions import user_functions

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)


# When using FunctionTool with ToolSet in agent creation, the tool call events are handled inside the create_stream
# method and functions gets automatically called by default.
class MyEventHandler(AgentEventHandler):

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")


with agents_client:
    # [START create_agent_with_function_tool]
    functions = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(functions)
    agents_client.enable_auto_function_calls(toolset)

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        toolset=toolset,
    )
    # [END create_agent_with_function_tool]
    print(f"Created agent, ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York? Also let me know the details",
    )
    print(f"Created message, message ID {message.id}")

    with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()) as stream:
        stream.until_done()

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
