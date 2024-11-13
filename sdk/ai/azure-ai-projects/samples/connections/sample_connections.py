# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to enumerate connections,
    get connection properties, and create a chat completions client using the connection
    properties.

USAGE:
    python sample_connections.py

    Before running the sample:

    pip install azure-ai-projects azure-identity azure-ai-inference openai

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The Azure AI Project connection string, as found in the "Project overview"
       tab in your AI Studio Project page.
    2) CONNECTION_NAME - The name of a Serverless or Azure OpenAI connection, as found in the "Connections" tab
       in your AI Studio Hub page.
    3) MODEL_DEPLOYMENT_NAME - The model deployment name, as found in your AI Studio Project.
"""
from typing import cast

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType, AuthenticationType
from azure.identity import DefaultAzureCredential

project_connection_string = os.environ["PROJECT_CONNECTION_STRING"]
connection_name = os.environ["CONNECTION_NAME"]
model_deployment_name = os.environ["MODEL_DEPLOYMENT_NAME"]

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=project_connection_string,
)

with project_client:

    # List the properties of all connections
    connections = project_client.connections.list()
    print(f"====> Listing of all connections (found {len(connections)}):")
    for connection in connections:
        print(connection)

    # List the properties of all connections of a particular "type" (In this sample, Azure OpenAI connections)
    connections = project_client.connections.list(
        connection_type=ConnectionType.AZURE_OPEN_AI,
    )
    print("====> Listing of all Azure Open AI connections (found {len(connections)}):")
    for connection in connections:
        print(connection)

    # Get the properties of the default connection of a particular "type", with credentials
    connection = project_client.connections.get_default(
        connection_type=ConnectionType.AZURE_AI_SERVICES,
        include_credentials=True,  # Optional. Defaults to "False"
    )
    print("====> Get default Azure AI Services connection:")
    print(connection)

    # Get the properties of a connection by connection name:
    connection = project_client.connections.get(
        connection_name=connection_name, include_credentials=True  # Optional. Defaults to "False"
    )
    print("====> Get connection by name:")
    print(connection)


# Examples of how you would create Inference client
if connection.connection_type == ConnectionType.AZURE_OPEN_AI:

    from openai import AzureOpenAI

    if connection.authentication_type == AuthenticationType.API_KEY:
        print("====> Creating AzureOpenAI client using API key authentication")
        aoai_client = AzureOpenAI(
            api_key=connection.key,
            azure_endpoint=connection.endpoint_url,
            api_version="2024-06-01",  # See "Data plane - inference" row in table https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs
        )
    elif connection.authentication_type == AuthenticationType.ENTRA_ID:
        print("====> Creating AzureOpenAI client using Entra ID authentication")
        from azure.core.credentials import TokenCredential
        from azure.identity import get_bearer_token_provider

        aoai_client = AzureOpenAI(
            # See https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
            azure_ad_token_provider=get_bearer_token_provider(
                cast(TokenCredential, connection.token_credential), "https://cognitiveservices.azure.com/.default"
            ),
            azure_endpoint=connection.endpoint_url,
            api_version="2024-06-01",  # See "Data plane - inference" row in table https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs
        )
    else:
        raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

    aoai_response = aoai_client.chat.completions.create(
        model=model_deployment_name,
        messages=[
            {
                "role": "user",
                "content": "How many feet are in a mile?",
            },
        ],
    )
    aoai_client.close()
    print(aoai_response.choices[0].message.content)

elif connection.connection_type == ConnectionType.SERVERLESS:

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import UserMessage

    if connection.authentication_type == AuthenticationType.API_KEY:
        print("====> Creating ChatCompletionsClient using API key authentication")
        from azure.core.credentials import AzureKeyCredential

        inference_client = ChatCompletionsClient(
            endpoint=connection.endpoint_url, credential=AzureKeyCredential(connection.key or "")
        )
    elif connection.authentication_type == AuthenticationType.ENTRA_ID:
        from azure.core.credentials import TokenCredential

        # MaaS models do not yet support EntraID auth
        print("====> Creating ChatCompletionsClient using Entra ID authentication")
        inference_client = ChatCompletionsClient(
            endpoint=connection.endpoint_url, credential=cast(TokenCredential, connection.token_credential)
        )
    else:
        raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

    inference_response = inference_client.complete(
        model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
    )
    inference_client.close()
    print(inference_response.choices[0].message.content)
