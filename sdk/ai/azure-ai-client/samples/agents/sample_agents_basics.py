# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os, time, logging
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<HostName>;<AzureSubscriptionId>;<ResourceGroup>;<HubName>"
# Customer needs to login to Azure subscription via Azure CLI and set the environment variables

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.environ["AI_CLIENT_CONNECTION_STRING"],
)

agent = ai_client.agents.create_agent(
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
)
print("Created agent, agent ID", agent.id)

thread = ai_client.agents.create_thread()
print("Created thread, thread ID", thread.id)

message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
print("Created message, message ID", message.id)

run = ai_client.agents.create_run(thread_id=thread.id, assistant_id=agent.id)
print("Created run, run ID", run.id)

# poll the run as long as run status is queued or in progress
while run.status in ["queued", "in_progress", "requires_action"]:
    # wait for a second
    time.sleep(1)
    run = ai_client.agents.get_run(thread_id=thread.id, run_id=run.id)

    print("Run status:", run.status)

print("Run completed with status:", run.status)

ai_client.agents.delete_agent(agent.id)
print("Deleted agent")

messages = ai_client.agents.list_messages(thread_id=thread.id)
print("messages:", messages)
