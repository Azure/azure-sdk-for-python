# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import FunctionTool, ToolSet, CodeInterpreterTool
from user_functions import user_functions

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

connection_string = os.environ["AI_CLIENT_CONNECTION_STRING"]

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=connection_string,
)

# Initialize agent toolset with user functions and code interpreter
functions = FunctionTool(user_functions)
code_interpreter = CodeInterpreterTool()

toolset = ToolSet()
toolset.add(functions)
toolset.add(code_interpreter)

# Create agent with toolset and process assistant run
agent = ai_client.agents.create_agent(
    model="gpt-4o-mini", name="my-assistant", instructions="You are a helpful assistant", toolset=toolset
)
print(f"Created agent, ID: {agent.id}")

# Create thread for communication
thread = ai_client.agents.create_thread()
print(f"Created thread, ID: {thread.id}")

# Create message to thread
message = ai_client.agents.create_message(
    thread_id=thread.id,
    role="user",
    content="Hello, send an email with the datetime and weather information in New York?",
)
print(f"Created message, ID: {message.id}")

# Create and process agent run in thread with tools
run = ai_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
print(f"Run finished with status: {run.status}")

if run.status == "failed":
    print(f"Run failed: {run.last_error}")

# Delete the assistant when done
ai_client.agents.delete_agent(agent.id)
print("Deleted agent")

# Fetch and log all messages
messages = ai_client.agents.list_messages(thread_id=thread.id)
print(f"Messages: {messages}")
