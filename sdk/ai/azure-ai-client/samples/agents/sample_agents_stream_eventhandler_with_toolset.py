# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import logging
import os
from azure.ai.client import AzureAIClient
from azure.ai.client.models import Agent, MessageDeltaChunk, MessageDeltaTextContent, RunStep, SubmitToolOutputsAction, ThreadMessage, ThreadRun
from azure.ai.client.models import AgentEventHandler
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import FunctionTool, ToolSet


import os, logging
from typing import Any

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


class MyEventHandler(AgentEventHandler):

    def __init__(self, client: Agent):
        self._client = client

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                logging.info(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        logging.info(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        logging.info(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            logging.error(f"Run failed. Error: {run.last_error}")

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            self._handle_submit_tool_outputs(run)

    def on_run_step(self, step: "RunStep") -> None:
        logging.info(f"RunStep type: {step.type}, Status: {step.status}")

    def on_run_step(self, step: "RunStep") -> None:
        logging.info(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        logging.error(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        logging.info("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        logging.warning(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    def _handle_submit_tool_outputs(self, run: "ThreadRun") -> None:
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        if not tool_calls:
            logging.warning("No tool calls to execute.")
            return
        if not self._client:
            logging.warning("AssistantClient not set. Cannot execute tool calls using toolset.")
            return

        toolset = self._client.get_toolset()
        if toolset:
            tool_outputs = toolset.execute_tool_calls(tool_calls)
        else:
            raise ValueError("Toolset is not available in the client.")
        
        logging.info(f"Tool outputs: {tool_outputs}")
        if tool_outputs:
            with self._client.submit_tool_outputs_to_run(
                thread_id=run.thread_id, 
                run_id=run.id, 
                tool_outputs=tool_outputs, 
                stream=True,
                event_handler=self
        ) as stream:
                stream.until_done()


functions = FunctionTool(user_functions)
toolset = ToolSet()
toolset.add(functions)


with ai_client:
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
    )
    logging.info(f"Created agent, ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    logging.info(f"Created thread, thread ID {thread.id}")

    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, send an email with the datetime and weather information in New York? Also let me know the details")
    logging.info(f"Created message, message ID {message.id}")

    with ai_client.agents.create_and_process_run(
        thread_id=thread.id, 
        assistant_id=agent.id,
        stream=True,
        event_handler=MyEventHandler(agent)
    ) as stream:
        stream.until_done()

    ai_client.agents.delete_agent(agent.id)
    logging.info("Deleted assistant")

    messages = ai_client.agents.list_messages(thread_id=thread.id)
    logging.info(f"Messages: {messages}")
