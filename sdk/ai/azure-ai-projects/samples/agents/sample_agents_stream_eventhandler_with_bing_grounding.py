# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler and
    the Bing grounding tool from the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_eventhandler_with_bing_grounding.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
    3) BING_CONNECTION_NAME - The connection name of the Bing connection, as found in the "Connected resources" tab
       in your Azure AI Foundry project.
"""
"""
import sys
import logging
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
"""
import os
from azure.identity import DefaultAzureCredential
from typing import Any
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    MessageDeltaChunk,
    RunStep,
    ThreadMessage,
    ThreadRun,
    AgentEventHandler,
    BingGroundingTool,
)
from user_functions import user_functions

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]  # , logging_enable=True
)

# TODO: Move into "with project_client" block
bing_connection = project_client.connections.get(connection_name=os.environ["BING_CONNECTION_NAME"])
conn_id = bing_connection.id

print(conn_id)

# Initialize agent bing tool and add the connection id
bing = BingGroundingTool(connection_id=conn_id)


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


with project_client:

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=bing.definitions,
    )
    print(f"Created agent, ID: {agent.id}")

    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="How does wikipedia explain Euler's Identity?",
    )
    print(f"Created message, message ID {message.id}")

    with project_client.agents.create_stream(
        thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler()
    ) as stream:
        stream.until_done()

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = project_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
