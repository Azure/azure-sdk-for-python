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

    pip install azure-ai-projects azure-ai-agents azure-identity

    Set these environment variables with your own values:
    1) PROJECT_ENDPOINT - The Azure AI Project endpoint, as found in the Overview
                          page of your Azure AI Foundry portal.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import os, time, sys
from typing import Any, Optional
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import (
    FunctionTool,
    ListSortOrder,
    RequiredFunctionToolCall,
    RunHandler,
    ThreadRun,
    RequiredFunctionToolCall,
    RequiredFunctionToolCallDetails,
)

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

# Initialize function tool with user functions
functions = FunctionTool(functions=user_functions)


class MyRunHandler(RunHandler):
    def submit_function_call_output(
        self, run: ThreadRun, tool_call: RequiredFunctionToolCall, tool_call_details: RequiredFunctionToolCallDetails, **kwargs: Any
    ) -> Optional[Any]:
        print(f"Call function: {tool_call_details.name}")
        return functions.execute(tool_call)


with project_client:
    agents_client = project_client.agents

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

    run_handler = MyRunHandler()
    run = agents_client.runs.create_and_process(thread_id=thread.id, agent_id=agent.id, run_handler=run_handler)

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
