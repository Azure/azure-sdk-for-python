# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with iteration and functions from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_stream_iteration_with_functions.py

    Before running the sample:

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
from typing import Any

import os, sys
from azure.ai.projects import AIProjectClient
from azure.ai.agents.models import (
    FunctionTool,
    ListSortOrder,
    MessageDeltaChunk,
    RequiredFunctionToolCall,
    RunStep,
    SubmitToolOutputsAction,
    ThreadMessage,
    ThreadRun,
    ToolOutput,
    AgentStreamEvent,
    RunStepDeltaChunk,
)
from azure.identity import DefaultAzureCredential

# Add package directory to sys.path to import user_functions
current_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.abspath(os.path.join(current_dir, os.pardir, os.pardir))
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)
from samples.utils.user_functions import user_functions

project_client = AIProjectClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

with project_client:
    agents_client = project_client.agents

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

    thread = agents_client.threads.create()
    print(f"Created thread, thread ID {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York? Also let me know the details.",
    )
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

                if event_data.status == "requires_action" and isinstance(
                    event_data.required_action, SubmitToolOutputsAction
                ):
                    tool_calls = event_data.required_action.submit_tool_outputs.tool_calls

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
                        agents_client.runs.submit_tool_outputs_stream(
                            thread_id=event_data.thread_id,
                            run_id=event_data.id,
                            tool_outputs=tool_outputs,
                            event_handler=stream,
                        )

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
