# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os, time
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.client.models import FunctionTool
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

# Initialize function tool with user functions
functions = FunctionTool(functions=user_functions)

# Create an agent and run user's request with function calls
agent = ai_client.agents.create_agent(
    model="gpt-4-1106-preview",
    name="my-assistant",
    instructions="You are a helpful assistant",
    tools=functions.definitions,
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

run = ai_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
print(f"Created run, ID: {run.id}")

while run.status in ["queued", "in_progress", "requires_action"]:
    time.sleep(1)
    run = ai_client.agents.get_run(thread_id=thread.id, run_id=run.id)

    if run.status == "requires_action" and run.required_action.submit_tool_outputs:
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        if not tool_calls:
            print("No tool calls provided - cancelling run")
            ai_client.agents.cancel_run(thread_id=thread.id, run_id=run.id)
            break

        tool_outputs = []
        for tool_call in tool_calls:
            output = functions.execute(tool_call)
            tool_output = {
                "tool_call_id": tool_call.id,
                "output": output,
            }
            tool_outputs.append(tool_output)

        print(f"Tool outputs: {tool_outputs}")
        if tool_outputs:
            ai_client.agents.submit_tool_outputs_to_run(thread_id=thread.id, run_id=run.id, tool_outputs=tool_outputs)

    print(f"Current run status: {run.status}")

print(f"Run completed with status: {run.status}")

# Delete the agent when done
ai_client.agents.delete_agent(agent.id)
print("Deleted agent")

# Fetch and log all messages
messages = ai_client.agents.list_messages(thread_id=thread.id)
print(f"Messages: {messages}")
