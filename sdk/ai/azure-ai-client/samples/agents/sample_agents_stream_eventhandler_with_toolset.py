# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_stream_eventhandler_with_toolset.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with an event handler and toolset from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_eventhandler_with_toolset.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import os
from azure.ai.client import AzureAIClient
from azure.ai.client.models import Agent, MessageDeltaChunk, MessageDeltaTextContent, RunStep, SubmitToolOutputsAction, ThreadMessage, ThreadRun
from azure.ai.client.models import AgentEventHandler
from azure.ai.client.operations._patch import AgentsOperations
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import FunctionTool, ToolSet


import os
from typing import Any

from user_functions import user_functions


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

    def __init__(self, agents: AgentsOperations):
        self._agents = agents

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        for content_part in delta.delta.content:
            if isinstance(content_part, MessageDeltaTextContent):
                text_value = content_part.text.value if content_part.text else "No text"
                print(f"Text delta received: {text_value}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            self._handle_submit_tool_outputs(run)

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_run_step(self, step: "RunStep") -> None:
        print(f"RunStep type: {step.type}, Status: {step.status}")

    def on_error(self, data: str) -> None:
        print(f"An error occurred. Data: {data}")

    def on_done(self) -> None:
        print("Stream completed.")

    def on_unhandled_event(self, event_type: str, event_data: Any) -> None:
        print(f"Unhandled Event Type: {event_type}, Data: {event_data}")

    def _handle_submit_tool_outputs(self, run: "ThreadRun") -> None:
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        if not tool_calls:
            print("No tool calls to execute.")
            return

        toolset = self._agents.get_toolset()
        if toolset:
            tool_outputs = toolset.execute_tool_calls(tool_calls)
        else:
            raise ValueError("Toolset is not available in the client.")
        
        print(f"Tool outputs: {tool_outputs}")
        if tool_outputs:
            with self._agents.submit_tool_outputs_to_stream(
                thread_id=run.thread_id, 
                run_id=run.id, 
                tool_outputs=tool_outputs, 
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
    print(f"Created agent, ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, send an email with the datetime and weather information in New York? Also let me know the details")
    print(f"Created message, message ID {message.id}")

    with ai_client.agents.create_and_process_stream(
        thread_id=thread.id, 
        assistant_id=agent.id,
        event_handler=MyEventHandler(ai_client.agents)
    ) as stream:
        stream.until_done()

    ai_client.agents.delete_agent(agent.id)
    print("Deleted assistant")

    messages = ai_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
