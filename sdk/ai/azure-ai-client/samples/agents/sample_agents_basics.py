"""
# These are needed for SDK logging. You can ignore them.
import sys
import logging
logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))
# End of logging setup
"""

import os
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
assistant = ai_client.agents.create_agent(
    model="gpt-4-1106-preview", name="my-assistant", instructions="You are helpful assistant"
)
print("Created assistant, assistant ID", assistant.id)

ai_client.agents.delete_agent(assistant.id)
print("Deleted assistant")
