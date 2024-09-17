"""


"""
import sys
import logging

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

import os
from azure.ai.project import ProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.inference.models import UserMessage

# Create a project client (or runtime client, name TBD...)
project = ProjectClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AI_STUDIO_HUB"],
    logging_enable=True,
)

# Get a ChatCompletionsClient for a key-auth connection:
client = project.get_maas_client(connection_name=os.environ["AI_STUDIO_CONNECTION_3"])

response = client.complete(
    messages=[
        UserMessage(content="How many feet are in a mile?")
    ]
)

print(f"\n\n===============> {completion.choices[0].message.content}\n\n")

