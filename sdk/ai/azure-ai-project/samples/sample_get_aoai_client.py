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

# Create a project client (or runtime client, name TBD...)
project = ProjectClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AI_STUDIO_HUB"],
    logging_enable=True,
)

# Get an AOAI client for a key-auth connection:
aoai_client = project.get_azure_openai_client(connection_name=os.environ["AI_STUDIO_CONNECTION_1"])

completion = aoai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "How many feet are in a mile?",
        },
    ],
)
print(f"\n\n===============> {completion.choices[0].message.content}\n\n")

# Get an AOAI client for an AAD-auth connection:
aoai_client = project.get_azure_openai_client(connection_name=os.environ["AI_STUDIO_CONNECTION_2"])

completion = aoai_client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "What's the distance from earth to the moon in miles?",
        },
    ],
)
print(f"\n\n===============> {completion.choices[0].message.content}\n\n")
