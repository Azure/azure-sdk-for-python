"""


"""

import sys
import logging

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

import os
from azure.ai.client import AzureAIClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage

ai_client = AzureAIClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AI_STUDIO_HUB"],
    logging_enable=True,
)

credential, endpoint = ai_client.connections.get_credential(connection_name=os.environ["AI_STUDIO_CONNECTION_3"])

client = ChatCompletionsClient(
    endpoint=endpoint,
    credential=credential
)

response = client.complete(
    messages=[
        UserMessage(content="How many feet are in a mile?")
    ]
)

print(f"\n\n===============> {response.choices[0].message.content}\n\n")
