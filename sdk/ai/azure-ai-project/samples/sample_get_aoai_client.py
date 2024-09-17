import sys
import logging

logger = logging.getLogger("azure")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))

import os
from azure.ai.project import ProjectClient
from azure.identity import DefaultAzureCredential

project = ProjectClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AI_STUDIO_HUB"],
    logging_enable=True,
)

#response = project._list_secrets(connection_name=os.environ["AI_STUDIO_CONNECTION"])
#print(response)
#print(f"This is the key: {response.properties.credentials.key}")

aoai_client = project.get_azure_openai_client(
    connection_name=os.environ["AI_STUDIO_CONNECTION"])

completion = aoai_client.chat.completions.create(
    model="gpt-4o-mini", # Deployment name
    # prompt = "How many feet are in a mile?",
    messages=[
        {
            "role": "user",
            "content": "How many feet are in a mile?",
        },
    ],
)
print(completion.to_json())
