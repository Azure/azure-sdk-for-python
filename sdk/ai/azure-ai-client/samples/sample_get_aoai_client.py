"""


"""

import sys
import logging

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

import os
from azure.ai.client import AzureAIClient
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential

ai_client = AzureAIClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AI_STUDIO_HUB"],
    logging_enable=True,
)

key, endpoint = ai_client.connections.get_credential(connection_name=os.environ["AI_STUDIO_CONNECTION_1"])

client = AzureOpenAI(
    api_key=key,
    azure_endpoint=endpoint,
    api_version="2024-08-01-preview",  # See https://learn.microsoft.com/en-us/azure/ai-services/openai/reference-preview#api-specs
)

completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "user",
            "content": "How many feet are in a mile?",
        },
    ],
)

print(f"\n\n===============> {completion.choices[0].message.content}\n\n")

exit()

# Get an AOAI client for an AAD-auth connection:
aoai_client = client.get_azure_openai_client(connection_name=os.environ["AI_STUDIO_CONNECTION_2"])

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
