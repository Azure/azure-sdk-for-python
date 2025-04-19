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
    python sample_agents_stream_eventhandler_with_functions.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - the Azure AI Agents endpoint.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
from typing import Any

import os
from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    AgentEventHandler,
    FunctionTool,
    MessageDeltaChunk,
    RequiredFunctionToolCall,
    RunStep,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
    ToolOutput,
)
from azure.identity import DefaultAzureCredential
from user_functions import user_functions

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)


class MyEventHandler(AgentEventHandler):

    def __init__(self, functions: FunctionTool) -> None:
        super().__init__()
        self.functions = functions

    def on_message_delta(self, delta: "MessageDeltaChunk") -> None:
        print(f"Text delta received: {delta.text}")

    def on_thread_message(self, message: "ThreadMessage") -> None:
        print(f"ThreadMessage created. ID: {message.id}, Status: {message.status}")

    def on_thread_run(self, run: "ThreadRun") -> None:
        print(f"ThreadRun status: {run.status}")

        if run.status == "failed":
            print(f"Run failed. Error: {run.last_error}")

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls

            tool_outputs = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredFunctionToolCall):
                    try:
                        output = functions.execute(tool_call)
                        tool_outputs.append(
                            ToolOutput(
                                tool_call_id=tool_call.id,
                                output=output,
                            )
                        )
                    except Exception as e:
                        print(f"Error executing tool_call {tool_call.id}: {e}")

            print(f"Tool outputs: {tool_outputs}")
            if tool_outputs:
                # Once we receive 'requires_action' status, the next event will be DONE.
                # Here we associate our existing event handler to the next stream.
                agents_client.submit_tool_outputs_to_stream(
                    thread_id=run.thread_id, run_id=run.id, tool_outputs=tool_outputs, event_handler=self
                )

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

    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=functions.definitions,
    )
    # [END create_agent_with_function_tool]
    print(f"Created agent, ID: {agent.id}")

    thread = agents_client.create_thread()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York? Also let me know the details.",
    )
    print(f"Created message, message ID {message.id}")

    with agents_client.create_stream(
        thread_id=thread.id, agent_id=agent.id, event_handler=MyEventHandler(functions)
    ) as stream:
        stream.until_done()

    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    messages = agents_client.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
