import os
import json
from azure.ai.client import AzureAIClient
from azure.ai.client.models import ConnectionType, AuthenticationType
from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.credentials import AzureKeyCredential

ai_client = AzureAIClient(
    credential=DefaultAzureCredential(),
    subscription_id=os.environ["AZURE_SUBSCRIPTION"],
    resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
    workspace_name=os.environ["AI_STUDIO_HUB"],
)

connection = ai_client.connections.get(
    connection_name=os.environ["AI_STUDIO_CONNECTION_2"], 
    populate_secrets=True
)

# Remove trailing slash from the endpoint if exist
connection.properties.target = (
    connection.properties.target[:-1] if connection.properties.target.endswith("/") else connection.properties.target
)
print(json.dumps(connection.as_dict(), indent=2))

"""
print(connection)
print(json.dumps(connection.as_dict(), indent=2))
exit()

connection = ai_client.connections.get(
    connection_name=os.environ["AI_STUDIO_CONNECTION_3"], 
    populate_secrets=False
)
print(connection)
print(json.dumps(connection.as_dict(), indent=2))


connections = ai_client.connections.list(
    connection_type=ConnectionType.AZURE_OPEN_AI,
    populate_secrets=True
)
for connection in connections:
    print(json.dumps(connection.as_dict(), indent=2))

exit()
"""

# Here is how you would create the appropriate AOAI or Inference SDK for this connection
if connection.properties.category == ConnectionType.AZURE_OPEN_AI:

    if connection.properties.auth_type == AuthenticationType.API_KEY:
        client = AzureOpenAI(
            api_key=connection.properties.credentials.key,
            azure_endpoint=connection.properties.target,
            api_version="2024-08-01-preview",
        )
    elif connection.properties.auth_type == AuthenticationType.AAD:
        client = AzureOpenAI(
            azure_ad_token_provider=get_bearer_token_provider(connection.token_credential, "https://cognitiveservices.azure.com/.default"),
            azure_endpoint=connection.endpoint,
            api_version="2024-08-01-preview",
        )
    elif connection.properties.auth_type == AuthenticationType.SAS:
        # TODO
        pass

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": "How many feet are in a mile?",
            },
        ],
    )

    print(response.choices[0].message.content)

elif connection.properties.category == ConnectionType.SERVERLESS:

    if connection.properties.auth_type == AuthenticationType.API_KEY:
        client = ChatCompletionsClient(
           endpoint=connection.properties.target,
           credential=AzureKeyCredential(connection.properties.credentials.key)
        )
    elif connection.properties.auth_type == AuthenticationType.AAD:
        # TODO
        pass

    response = client.complete(
        messages=[
            UserMessage(content="How many feet are in a mile?")
        ]
    )

    print(response.choices[0].message.content)