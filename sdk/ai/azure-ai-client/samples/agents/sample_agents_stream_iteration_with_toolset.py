# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os, logging
from azure.ai.client import AzureAIClient
from azure.ai.client.models import AgentStreamEvent
from azure.ai.client.models import Agent, MessageDeltaChunk, MessageDeltaTextContent, RunStep, SubmitToolOutputsAction, ThreadMessage, ThreadRun
from azure.ai.client.models import FunctionTool, ToolSet
from azure.ai.client.operations._operations import AgentsOperations
from azure.identity import DefaultAzureCredential
from user_functions import user_functions

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

# Function to handle tool stream iteration
def handle_submit_tool_outputs(operatiions: AgentsOperations, thread_id, run_id, tool_outputs):
    try:
        with operatiions.submit_tool_outputs_to_run(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=tool_outputs,
            stream=True
        ) as tool_stream:
            for tool_event_type, tool_event_data in tool_stream:
                if tool_event_type == AgentStreamEvent.ERROR:
                    logging.error(f"An error occurred in tool stream. Data: {tool_event_data}")
                elif tool_event_type == AgentStreamEvent.DONE:
                    logging.info("Tool stream completed.")
                    break
                else:
                    if isinstance(tool_event_data, MessageDeltaChunk):
                        handle_message_delta(tool_event_data)

    except Exception as e:
        logging.error(f"Failed to process tool stream: {e}")


# Function to handle message delta chunks
def handle_message_delta(delta: MessageDeltaChunk) -> None:
    for content_part in delta.delta.content:
        if isinstance(content_part, MessageDeltaTextContent):
            text_value = content_part.text.value if content_part.text else "No text"
            logging.info(f"Text delta received: {text_value}")


functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)

with ai_client:
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
    )
    logging.info(f"Created agent, agent ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    logging.info(f"Created thread, thread ID {thread.id}")

    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, what's the time?")
    logging.info(f"Created message, message ID {message.id}")

    with ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id, stream=True) as stream:

        for event_type, event_data in stream:

            if isinstance(event_data, MessageDeltaChunk):
                handle_message_delta(event_data)

            elif isinstance(event_data, ThreadMessage):
                logging.info(f"ThreadMessage created. ID: {event_data.id}, Status: {event_data.status}")

            elif isinstance(event_data, ThreadRun):
                logging.info(f"ThreadRun status: {event_data.status}")
                
                if event_data.status == "failed":
                    logging.error(f"Run failed. Error: {event_data.last_error}")

                if event_data.status == "requires_action" and isinstance(event_data.required_action, SubmitToolOutputsAction):
                    tool_calls = event_data.required_action.submit_tool_outputs.tool_calls
                    if not tool_calls:
                        logging.warning("No tool calls to execute.")
                        break

                    toolset = ai_client.agents.get_toolset()
                    if toolset:
                        tool_outputs = toolset.execute_tool_calls(tool_calls)
                    else:
                        raise ValueError("Toolset is not available in the client.")

                    if tool_outputs:
                        handle_submit_tool_outputs(ai_client.agents, event_data.thread_id, event_data.id, tool_outputs)
                           
            elif isinstance(event_data, RunStep):
                logging.info(f"RunStep type: {event_data.type}, Status: {event_data.status}")

            elif event_type == AgentStreamEvent.ERROR:
                logging.error(f"An error occurred. Data: {event_data}")

            elif event_type == AgentStreamEvent.DONE:
                logging.info("Stream completed.")
                break

            else:
                logging.warning(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    ai_client.agents.delete_agent(agent.id)
    logging.info("Deleted assistant")

    messages = ai_client.agents.list_messages(thread_id=thread.id)
    logging.info(f"Messages: {messages}")
