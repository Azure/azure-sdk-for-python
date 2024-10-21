# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_connections_async.py

DESCRIPTION:
    Given an asynchronous AzureAIClient, this sample demonstrates how to enumerate connections
    and get connections properties.

USAGE:
    python sample_connections_async.py

    Before running the sample:

    pip install azure.ai.client aiohttp azure-identity

    Set the environment variables with your own values:
    1) PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""

import asyncio
import os
from azure.ai.client.aio import AzureAIClient
from azure.ai.client.models import ConnectionType, AuthenticationType
from azure.identity import DefaultAzureCredential


async def sample_connections_async():

    ai_client = AzureAIClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["PROJECT_CONNECTION_STRING"],
    )

    async with ai_client:

        # List the properties of all connections
        print("====> Listing of all connections:")
        async for connection in ai_client.connections.list():
            print(connection)

        # List the properties of all connections of a particular "type" (In this sample, Azure OpenAI connections)
        print("====> Listing of all Azure Open AI connections:")
        async for connection in ai_client.connections.list(connection_type=ConnectionType.AZURE_OPEN_AI):
            print(connection)

        # Get the properties of the default connection of a particular "type", with credentials
        connection = await ai_client.connections.get_default(
            connection_type=ConnectionType.AZURE_OPEN_AI,
            with_credentials=True,  # Optional. Defaults to "False"
        )
        print("====> Get default Azure Open AI connection:")
        print(connection)

        # Get the properties of a connection by connection name:
        connection = await ai_client.connections.get(
            connection_name=os.environ["AI_CLIENT_CONNECTION_NAME"],
            with_credentials=True  # Optional. Defaults to "False"
        )
        print("====> Get connection by name:")
        print(connection)


    # Examples of how you would create Inference client
    if connection.connection_type == ConnectionType.AZURE_OPEN_AI:

        from openai import AsyncAzureOpenAI

        if connection.authentication_type == AuthenticationType.API_KEY:
            print("====> Creating AzureOpenAI client using API key authentication")
            client = AsyncAzureOpenAI(
                api_key=connection.key,
                azure_endpoint=connection.endpoint_url,
                api_version="2024-06-01",  # See "Data plane - inference" row in table https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs
            )
        elif connection.authentication_type == AuthenticationType.AAD:
            print("====> Creating AzureOpenAI client using Entra ID authentication")
            from azure.identity import get_bearer_token_provider

            client = AsyncAzureOpenAI(
                # See https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity?view=azure-python#azure-identity-get-bearer-token-provider
                azure_ad_token_provider=get_bearer_token_provider(
                    connection.token_credential, "https://cognitiveservices.azure.com/.default"
                ),
                azure_endpoint=connection.endpoint_url,
                api_version="2024-06-01",  # See "Data plane - inference" row in table https://learn.microsoft.com/en-us/azure/ai-services/openai/reference#api-specs
            )
        else:
            raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

        response = await client.chat.completions.create(
            model="gpt-4-0613",
            messages=[
                {
                    "role": "user",
                    "content": "How many feet are in a mile?",
                },
            ],
        )
        print(response.choices[0].message.content)

    elif connection.connection_type == ConnectionType.SERVERLESS:

        from azure.ai.inference.aio import ChatCompletionsClient
        from azure.ai.inference.models import UserMessage

        if connection.authentication_type == AuthenticationType.API_KEY:
            print("====> Creating ChatCompletionsClient using API key authentication")
            from azure.core.credentials import AzureKeyCredential

            client = ChatCompletionsClient(
                endpoint=connection.endpoint_url, credential=AzureKeyCredential(connection.key)
            )
        elif connection.authentication_type == AuthenticationType.AAD:
            # MaaS models do not yet support EntraID auth
            print("====> Creating ChatCompletionsClient using Entra ID authentication")
            client = ChatCompletionsClient(
                endpoint=connection.endpoint_url, credential=connection.properties.token_credential
            )
        else:
            raise ValueError(f"Authentication type {connection.authentication_type} not supported.")

        response = await client.complete(messages=[UserMessage(content="How many feet are in a mile?")])
        await client.close()
        print(response.choices[0].message.content)


async def main():
    await sample_connections_async()


if __name__ == "__main__":
    asyncio.run(main())
