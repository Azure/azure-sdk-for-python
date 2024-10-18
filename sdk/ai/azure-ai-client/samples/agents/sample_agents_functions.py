# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_agents_functions.py

DESCRIPTION:
    This sample demonstrates how to use agent operations with custom functions from
    the Azure Agents service using a synchronous client.

USAGE:
    python sample_agents_functions.py

    Before running the sample:

    pip install azure.ai.client azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os, time
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import FunctionTool, SubmitToolOutputsAction, RequiredFunctionToolCall
from user_functions import user_functions


# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.environ["PROJECT_CONNECTION_STRING"]
)

# Initialize function tool with user functions
functions = FunctionTool(functions=user_functions)

with ai_client:
    # Create an agent and run user's request with function calls
    agent = ai_client.agents.create_agent(
        model="gpt-4-1106-preview",
        name="my-assistant",
        instructions="You are a helpful assistant",
        tools=[functions]
    )
    print(f"Created agent, ID: {agent.id}")

    thread = ai_client.agents.create_thread()
    print(f"Created thread, ID: {thread.id}")

    message = ai_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content="Hello, send an email with the datetime and weather information in New York?",
    )
    print(f"Created message, ID: {message.id}")

    run = ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Current run status: {run.status}")

    print(f"Run completed with status: {run.status}")

    # Delete the agent when done
    ai_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Fetch and log all messages
    messages = ai_client.agents.list_messages(thread_id=thread.id)
    print(f"Messages: {messages}")
