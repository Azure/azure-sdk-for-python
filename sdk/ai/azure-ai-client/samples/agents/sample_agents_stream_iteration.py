# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_iteration_with_toolset.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with toolset in streaming from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_iteration_with_toolset.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import logging
import os
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import (
    AgentStreamEvent,
    MessageDeltaTextContent,
    MessageDeltaChunk,
    ThreadMessage,
    ThreadRun,
    RunStep,
)

# Set logging level
logging.basicConfig(level=logging.INFO)

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

with ai_client:
    # Create an agent and run stream with iteration
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant"
    )
    logging.info(f"Created agent, ID {agent.id}")

    thread = ai_client.agents.create_thread()
    logging.info(f"Created thread, thread ID {thread.id}")

    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
    logging.info(f"Created message, message ID {message.id}")

    with ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id, stream=True) as stream:

        for event_type, event_data in stream:

            if isinstance(event_data, MessageDeltaChunk):
                for content_part in event_data.delta.content:
                    if isinstance(content_part, MessageDeltaTextContent):
                        text_value = content_part.text.value if content_part.text else "No text"
                        logging.info(f"Text delta received: {text_value}")

            elif isinstance(event_data, ThreadMessage):
                logging.info(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

            elif isinstance(event_data, ThreadRun):
                logging.info(f"ThreadRun status: {event_data.status}")

            elif isinstance(event_data, RunStep):
                logging.info(f"RunStep type: {event_data.type}, Status: {event_data.status}")

            elif event_type == AgentStreamEvent.ERROR:
                logging.info(f"An error occurred. Data: {event_data}")

            elif event_type == AgentStreamEvent.DONE:
                logging.info("Stream completed.")
                break

            else:
                print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    ai_client.agents.delete_agent(agent.id)
    logging.info("Deleted agent")

    messages = ai_client.agents.list_messages(thread_id=thread.id)
    logging.info(f"Messages: {messages}")
