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

connection_string = os.environ["AI_CLIENT_CONNECTION_STRING"]

ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=connection_string,
    # logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
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
agent = ai_client.agents.create_agent(
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
)
logging.info("Created agent, agent ID", agent.id)

thread = ai_client.agents.create_thread()
logging.info("Created thread, thread ID", thread.id)

message = ai_client.agents.create_message(thread_id=thread.id, role="user", content="Hello, tell me a joke")
logging.info("Created message, message ID", message.id)

run = ai_client.agents.create_run(thread_id=thread.id, agent_id=agent.id)
logging.info("Created run, run ID", run.id)

# poll the run as long as run status is queued or in progress
while run.status in ["queued", "in_progress", "requires_action"]:
    # wait for a second
    time.sleep(1)
    run = ai_client.agents.get_run(thread_id=thread.id, run_id=run.id)

    logging.info("Run status:", run.status)

logging.info("Run completed with status:", run.status)

ai_client.agents.delete_agent(agent.id)
logging.info("Deleted agent")

messages = ai_client.agents.list_messages(thread_id=thread.id)
logging.info("messages:", messages)
