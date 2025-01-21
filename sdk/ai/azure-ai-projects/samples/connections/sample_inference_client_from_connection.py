# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates:
    - How to get the properties of an AI Services or Azure OpenAI connection, by its connection name. Then,
    - Create the appropriate inference client (either azure-ai-inference client or Azure OpenAI client),
      from those properties, based on the authentication type. Then,
    - Do a chat completions call using that inference client.

USAGE:
    python sample_inference_client_from_connection.py

    Before running the sample:

    pip install azure-ai-projects azure-identity azure-ai-inference openai

    Set these environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - The project connection string, as found in the overview page of your
       Azure AI Foundry project.
    2) CONNECTION_NAME - The name of a AI Services or Azure OpenAI connection, as found in the "Connected resources" tab
       in the Management Center of your AI Foundry project. 
    3) MODEL_DEPLOYMENT_NAME - The model deployment name, as found in the "Models + endpoints" tab of your AI Foundry project.
"""
import os
from typing import cast
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

    # Get the properties of a connection by its connection name:
    connection = project_client.connections.get(connection_name=connection_name, include_credentials=True)
    print("====> Get connection by name (credentials printout redacted)):")
    print(connection)


# Examples of how you would create an inference client
if connection.connection_type == ConnectionType.AZURE_OPEN_AI:

    from openai import AzureOpenAI

    if connection.authentication_type == AuthenticationType.API_KEY:
        print("====> Creating AzureOpenAI client using API key authentication")
        aoai_client = AzureOpenAI(
            api_key=connection.key,
            azure_endpoint=connection.endpoint_url,
            api_version="2024-06-01",  # See "Data plane - inference" row in table https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
        )
    elif connection.authentication_type == AuthenticationType.ENTRA_ID:
        print("====> Creating AzureOpenAI client using Entra ID authentication")
        from azure.core.credentials import TokenCredential
        from azure.identity import get_bearer_token_provider

        aoai_client = AzureOpenAI(
            # See https://learn.microsoft.com/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
            azure_ad_token_provider=get_bearer_token_provider(
                cast(TokenCredential, connection.token_credential), "https://cognitiveservices.azure.com/.default"
            ),
            azure_endpoint=connection.endpoint_url,
            api_version="2024-06-01",  # See "Data plane - inference" row in table https://learn.microsoft.com/azure/ai-services/openai/reference#api-specs
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

elif connection.connection_type == ConnectionType.AZURE_AI_SERVICES:

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import UserMessage

    if connection.authentication_type == AuthenticationType.API_KEY:
        print("====> Creating ChatCompletionsClient using API key authentication")
        from azure.core.credentials import AzureKeyCredential

        inference_client = ChatCompletionsClient(
            endpoint=f"{connection.endpoint_url}/models", credential=AzureKeyCredential(connection.key or "")
        )
    elif connection.authentication_type == AuthenticationType.ENTRA_ID:
        from azure.core.credentials import TokenCredential

        print("====> Creating ChatCompletionsClient using Entra ID authentication")
        inference_client = ChatCompletionsClient(
            endpoint=f"{connection.endpoint_url}/models",
            credential=cast(TokenCredential, connection.token_credential),
            credential_scopes=["https://cognitiveservices.azure.com/.default"],
        )
    else:
        raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

    inference_response = inference_client.complete(
        model=model_deployment_name, messages=[UserMessage(content="How many feet are in a mile?")]
    )
    inference_client.close()
    print(inference_response.choices[0].message.content)
