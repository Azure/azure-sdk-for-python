# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    This sample demonstrates how to use agent operations with toolset from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_run_with_toolset.py

    Before running the sample:

    pip install azure-ai-projects azure-identity

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) MODEL_DEPLOYMENT_NAME - The deployment name of the AI model, as found under the "Name" column in 
       the "Models + endpoints" tab in your Azure AI Foundry project.
"""
import json
import os
import sys

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import FunctionTool, ToolSet, CodeInterpreterTool
from user_functions import user_functions
from dotenv import load_dotenv
from azure.ai.projects.models import RunStepType, MessageRole, ThreadMessage, MessageTextContent, MessageTextDetails, RunStepFunctionToolCall, RunStepFunctionToolCallDetails

load_dotenv()

class ThreadMessageEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, RunStepFunctionToolCallDetails):
            return obj.__dict__["_data"]
        if isinstance(obj, RunStepFunctionToolCall):
            return obj.__dict__["_data"]
        if isinstance(obj, MessageTextDetails):
            return obj.__dict__["_data"]
        if isinstance(obj, MessageTextContent):
            return obj.__dict__["_data"]
        if isinstance(obj, ThreadMessage):
            json_data = obj.__dict__["_data"]
            if obj.__dict__.get("tool_calls"):
                json_data["tool_calls"] = obj.__dict__["tool_calls"]
            return json_data  # or implement a method to convert to a dictionary
        return super().default(obj)

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["PROJECT_CONNECTION_STRING"],
)

# project_client.telemetry.enable(destination=sys.stdout)

def get_evaluation_data(thread_id, filter_run_id=None):
    """
    Fetches all messages in a thread and converts them to JSON.
    if filter_run_id is provided, only messages from that run are included. Assuming all messages before the last assistant messages for that run are part of that run.
    """
    messages = project_client.agents.list_messages(thread_id=thread_id).data
    assistant_message_index_for_run = None
    for i in range(0, len(messages)):
        message = messages[i]
        print(f"Message: {message.content}")
        message_id = message.id
        message_type = message.role
        run_id = message.run_id
        if message_type == MessageRole.AGENT:
            if filter_run_id is not None and run_id == filter_run_id:
                assistant_message_index_for_run = i
            tool_calls = []
            if filter_run_id is None or run_id == filter_run_id:
                run_details = project_client.agents.list_run_steps(thread_id=thread_id, run_id=run_id)
                for run_step in run_details.data:
                    print(f"Run step: {run_step.type}")
                    if run_step.type == RunStepType.MESSAGE_CREATION:
                        print(f"Assistant message: {run_step.step_details.message_creation.message_id}")
                    elif run_step.type == RunStepType.TOOL_CALLS:
                        tool_calls.extend(run_step.step_details.tool_calls)
                        print(f"Tool call: {run_step.step_details.tool_calls}")
                message.tool_calls = tool_calls

    json_data = json.dumps(messages[assistant_message_index_for_run:] if assistant_message_index_for_run is not None else messages, cls=ThreadMessageEncoder)
    print("Evaluation Data -----------------------------------------")
    print(json_data)


# def get_evaluation_data(thread_id, run_id):
#     messages = project_client.agents.list_messages(thread_id=thread_id)
#     run_details = project_client.agents.list_run_steps(thread_id=thread_id, run_id=run_id)
#     last_assistant_message = run_details.data[0] if run_details.data[0].type == RunStepType.MESSAGE_CREATION else None
#     last_assistant_message_id = run_details.data[0].step_details.message_creation.message_id
#
#     messages_for_run = []
#     # getting messages in thread before the assistant's last message including it.
#     for i in range(0, len(messages.data)):
#         if messages.data[i].id == last_assistant_message_id and messages.data[i].role == MessageRole.AGENT:
#             messages_for_run = messages.data[i:]
#
#     tool_calls_for_assistant_message = [item for run_step_details in run_details.data[1:] for item in run_step_details.step_details.tool_calls]
#
#     return messages, run_details

# Create agent with toolset and process assistant run
with project_client:
    # Initialize agent toolset with user functions and code interpreter
    # [START create_agent_toolset]
    functions = FunctionTool(user_functions)
    code_interpreter = CodeInterpreterTool()

    toolset = ToolSet()
    toolset.add(functions)
    toolset.add(code_interpreter)

    agent = project_client.agents.create_agent(
        model=os.environ["MODEL_DEPLOYMENT_NAME"],
        name="my-assistant",
        instructions="You are a helpful assistant",
        toolset=toolset,
    )
    # [END create_agent_toolset]
    print(f"Created agent, ID: {agent.id}")

    # Create thread for communication
    thread = project_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    # Create message to thread
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York?",
    )

    print(f"Created message, ID: {message.id}")

    # Create and process agent run in thread with tools
    # [START create_and_process_run]
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    # [END create_and_process_run]
    print(f"Run finished with status: {run.status}")

    if run.status == "failed":
        print(f"Run failed: {run.last_error}")

    message_1 = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="How about the weather in Seattle?",
    )

    run1 = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)

    if run1.status == "failed":
        print(f"Run failed: {run1.last_error}")


    # Delete the assistant when done
    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    run_details = project_client.agents.list_run_steps(thread_id=thread.id, run_id=run1.id)

    # Fetch and log all messages
    # messages = project_client.agents.list_messages(thread_id=thread.id)
    # run_details = project_client.agents.list_run_steps(thread_id=thread.id, run_id=run.id)
    # print(f"Messages: {messages}")
    get_evaluation_data(thread.id, run.id)
