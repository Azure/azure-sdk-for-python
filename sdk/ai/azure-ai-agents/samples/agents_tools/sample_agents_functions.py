# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with custom functions from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_functions.py

    Before running the sample:

    pip install azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import os, time, sys
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    FunctionTool,
    ListSortOrder,
    RequiredFunctionToolCall,
    SubmitToolOutputsAction,
    ToolOutput,
)

current_path = os.path.dirname(__file__)
root_path = os.path.abspath(os.path.join(current_path, os.pardir, os.pardir))
if root_path not in sys.path:
    sys.path.insert(0, root_path)
from samples.utils.user_functions import user_functions

agents_client = AgentsClient(
    endpoint=os.environ["PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential(),
)

# Initialize function tool with user functions
functions = FunctionTool(functions=user_functions)

with agents_client:
    # Create an agent and run user's request with function calls
    agent = agents_client.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-agent",
        instructions="You are a helpful agent",
        tools=functions.definitions,
    )
    print(f"Created agent, ID: {agent.id}")

    thread = agents_client.threads.create()
    print(f"Created thread, ID: {thread.id}")

    message = agents_client.messages.create(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York?",
    )
    print(f"Created message, ID: {message.id}")

    run = agents_client.runs.create(thread_id=thread.id, agent_id=agent.id)
    print(f"Created run, ID: {run.id}")

    while run.status in ["queued", "in_progress", "requires_action"]:
        time.sleep(1)
        run = agents_client.runs.get(thread_id=thread.id, run_id=run.id)

        if run.status == "requires_action" and isinstance(run.required_action, SubmitToolOutputsAction):
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            if not tool_calls:
                print("No tool calls provided - cancelling run")
                agents_client.runs.cancel(thread_id=thread.id, run_id=run.id)
                break

            tool_outputs = []
            for tool_call in tool_calls:
                if isinstance(tool_call, RequiredFunctionToolCall):
                    try:
                        print(f"Executing tool call: {tool_call}")
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
                agents_client.runs.submit_tool_outputs(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

        print(f"Current run status: {run.status}")

    print(f"Run completed with status: {run.status}")

    # Delete the agent when done
    agents_client.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = agents_client.messages.list(thread_id=thread.id, order=ListSortOrder.ASCENDING)
    for msg in messages:
        if msg.text_messages:
            last_text = msg.text_messages[-1]
            print(f"{msg.role}: {last_text.text.value}")
