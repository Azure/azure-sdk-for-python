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

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import AgentStreamEvent, RunStepDeltaChunk
from azure.ai.projects.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
)
from azure.ai.projects.models import FunctionTool, ToolSet
from azure.identity import DefaultAzureCredential
from user_functions import user_functions

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

with project_client:
    project_client.agents.enable_auto_function_calls(toolset=toolset)
    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        toolset=toolset,
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = project_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
    print(f"Created message, message ID {message.id}")

    with project_client.agents.create_stream(thread_id=thread.id, agent_id=agent.id) as stream:

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

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
