# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with toolset and iteration in streaming from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_iteration_with_toolset.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os, sys
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import AgentStreamEvent, RunStepDeltaChunk
from azure.ai.agents.models import (
    MessageDeltaChunk,
    ListSortOrder,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.agents.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential

current_path = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from samples.utils.user_functions import user_functions

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

with agents_client:
    agents_client.enable_auto_function_calls(toolset)
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        toolset=toolset,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.messages.create(thread_id=thread.id, role="user", content="Hello, what's the time?")
    print(f"Created message, message ID {message.id}")

    with agents_client.runs.stream(thread_id=thread.id, agent_id=agent.id) as stream:

        for event_type, event_data, _ in stream:

            if isinstance(event_data, MessageDeltaChunk):
                print(f"Text delta received: {event_data.text}")

            elif isinstance(event_data, RunStepDeltaChunk):
                print(f"RunStepDeltaChunk received. ID: {event_data.id}.")

            elif isinstance(event_data, ThreadMessage):
                print(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

            elif isinstance(event_data, ThreadRun):
                print(f"ThreadRun status: {event_data.status}")

                if event_data.status == "failed":
                    print(f"Run failed. Error: {event_data.last_error}")

            elif isinstance(event_data, RunStep):
                print(f"RunStep type: {event_data.type}, Status: {event_data.status}")

            elif event_type == AgentStreamEvent.ERROR:
                print(f"An error occurred. Data: {event_data}")

            elif event_type == AgentStreamEvent.DONE:
                print("Stream completed.")

            else:
                print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
