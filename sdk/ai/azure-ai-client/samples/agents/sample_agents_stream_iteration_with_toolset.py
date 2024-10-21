# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_iteration_with_toolset.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with toolset and iteration in streaming from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_iteration_with_toolset.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.client import AzureAIClient
from azure.ai.client.models import AgentStreamEvent
from azure.ai.client.models import MessageDeltaChunk, MessageDeltaTextContent, RunStep, ThreadMessage, ThreadRun
from azure.ai.client.models import FunctionTool, ToolSet
from azure.ai.client.operations import AgentsOperations
from azure.identity import DefaultAzureCredential
from user_functions import user_functions


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"]
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


# Function to handle tool stream iteration
def handle_submit_tool_outputs(operations: AgentsOperations, thread_id, run_id, tool_outputs):
    try:
        with operations.submit_tool_outputs_to_stream(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
        ) as tool_stream:
            for tool_event_type, tool_event_data in tool_stream:
                if tool_event_type == AgentStreamEvent.ERROR:
                    print(f"An error occurred in tool stream. Data: {tool_event_data}")
                elif tool_event_type == AgentStreamEvent.DONE:
                    print("Tool stream completed.")
                    break
                else:
                    if isinstance(tool_event_data, MessageDeltaChunk):
                        handle_message_delta(tool_event_data)

    except Exception as e:
        print(f"Failed to process tool stream: {e}")


# Function to handle message delta chunks
def handle_message_delta(delta: MessageDeltaChunk) -> None:
    for content_part in delta.delta.content:
        if isinstance(content_part, MessageDeltaTextContent):
            text_value = content_part.text.value if content_part.text else "No text"
            print(f"Text delta received: {text_value}")


functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

with ai_client:
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
    )
    print(f"Created agent, agent ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
    print(f"Created message, message ID {message.id}")

    with ai_client.agents.create_stream(thread_id=thread.id, assistant_id=agent.id) as stream:

        for event_type, event_data in stream:

            if isinstance(event_data, MessageDeltaChunk):
                handle_message_delta(event_data)

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
                break

            else:
                print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    ai_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    messages = ai_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
