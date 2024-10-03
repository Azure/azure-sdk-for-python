
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
from azure.ai.client.models import EndpointType, AuthenticationType
from openai import AzureOpenAI
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.core.credentials import AzureKeyCredential

# Create an Azure AI Client from a connection string, copied from your AI Studio project.
# At the moment, it should be in the format "<Endpoint>;<AzureSubscriptionId>;<ResourceGroup>;<WorkspaceName>"
ai_client = AzureAIClient.from_connection_string(
    credential=DefaultAzureCredential(),
    connection=os.environ["AI_CLIENT_CONNECTION_STRING"],
    #logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
)

# Or, you can create the Azure AI Client by giving all required parameters directly
ai_client = AzureAIClient(
    credential=DefaultAzureCredential(),
    endpoint=os.environ["AI_CLIENT_ENDPOINT"],
    subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
    resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
    workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
    logging_enable=True, # Optional. Remove this line if you don't want to show how to enable logging
)

# You can list all endpoints of a particular "type", with or without their credentials:
endpoints = ai_client.endpoints.list(
    endpoint_type=EndpointType.AZURE_OPEN_AI, # Optional. Defaults to all types.
    populate_secrets=True # Optional. Defaults to "False"
)
print("====> Listing all Azure Open AI endpoints:")
for endpoint in endpoints:
    print(endpoint)

# You can get the default endpoint of a particular "type" (note that since at the moment the service
# does not have a notion of a default endpoint, this will return the first endpoint of that type):
endpoint = ai_client.endpoints.get_default(
    endpoint_type=EndpointType.AZURE_OPEN_AI, # Required.
    populate_secrets=True # Optional. Defaults to "False"
)
print("====> Get default Azure Open AI endpoint:")
print(endpoint)

# You can get an endpoint by its name:
endpoint = ai_client.endpoints.get(
    endpoint_name=os.environ["AI_CLIENT_CONNECTION_NAME"], # Required.
    populate_secrets=True
)
print("====> Print properties of a particular endpoint:")
print(endpoint)

# Here is how you would create the appropriate AOAI or Inference SDK for these endpoint
if endpoint.endpoint_type == EndpointType.AZURE_OPEN_AI:

    if endpoint.authentication_type == AuthenticationType.API_KEY:
        print("====> Creating AzureOpenAI client using API key authentication")
        client = AzureOpenAI(
            api_key=endpoint.key,
            azure_endpoint=endpoint.endpoint_url,
            api_version="2024-08-01-preview", # TODO: Is this needed?
        )
    elif endpoint.authentication_type == AuthenticationType.AAD:
        print("====> Creating AzureOpenAI client using Entra ID authentication")
        client = AzureOpenAI(
            # See https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
            azure_ad_token_provider=get_bearer_token_provider(endpoint.token_credential, "https://cognitiveservices.azure.com/.default"),
            azure_endpoint=endpoint.endpoint_url,
            api_version="2024-08-01-preview",
        )
    elif endpoint.authentication_type == AuthenticationType.SAS:
        # TODO - Not yet supported by the service. Expected 9/27.
        print("====> Creating AzureOpenAI client using SAS authentication")
        client = AzureOpenAI(
            azure_ad_token_provider=get_bearer_token_provider(endpoint.token_credential, "https://cognitiveservices.azure.com/.default"),
            azure_endpoint=endpoint.endpoint_url,
            api_version="2024-08-01-preview",
        )

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

elif endpoint.endpoint_type == EndpointType.SERVERLESS:

    if endpoint.authentication_type == AuthenticationType.API_KEY:
        print("====> Creating ChatCompletionsClient using API key authentication")
        client = ChatCompletionsClient(
           endpoint=endpoint.endpoint_url,
           credential=AzureKeyCredential(endpoint.properties.credentials.key)
        )
    elif endpoint.authentication_type == AuthenticationType.AAD:
        # MaaS models do not yet support EntraID auth
        print("====> Creating ChatCompletionsClient using Entra ID authentication")
        client = ChatCompletionsClient(
           endpoint=endpoint.endpoint_url,
           credential=endpoint.properties.token_credential
        )
    elif endpoint.authentication_type == AuthenticationType.SAS:
        # TODO - Not yet supported by the service. Expected 9/27.
        print("====> Creating ChatCompletionsClient using SAS authentication")
        client = ChatCompletionsClient(
           endpoint=endpoint.endpoint_url,
           credential=endpoint.token_credential
        )

    response = client.complete(
        messages=[
            UserMessage(content="How many feet are in a mile?")
        ]
    )

    print(response.choices[0].message.content)