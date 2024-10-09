# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_chat_completions_client_async.py

DESCRIPTION:
    This sample demonstrates how to get an authenticated ChatCompletionsClient
    from the azure.ai.inference package, from an AzureAIClient.

USAGE:
    python sample_get_chat_completions_client_async.py

    Before running the sample:

    pip install azure.ai.client aiohttp azure-identity

    Set the environment variables with your own values:
    1) AI_CLIENT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os
import asyncio
from azure.ai.client.aio import AzureAIClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential

async def sample_get_chat_completions_client_async():

    # Create an Azure AI Client from a connection string, copied from your AI Studio project.
    # It should have the format "<Endpoint>;<AzureSubscriptionId>;<ResourceGroup>;<WorkspaceName>"
    async with AzureAIClient.from_connection_string(
        credential=DefaultAzureCredential(),
        connection=os.environ["AI_CLIENT_CONNECTION_STRING"],
    ) as ai_client:

    # Or, you can create the Azure AI Client by giving all required parameters directly
    # async with AzureAIClient(
    #     credential=DefaultAzureCredential(),
    #     endpoint=os.environ["AI_CLIENT_ENDPOINT"],
    #     subscription_id=os.environ["AI_CLIENT_SUBSCRIPTION_ID"],
    #     resource_group_name=os.environ["AI_CLIENT_RESOURCE_GROUP_NAME"],
    #     workspace_name=os.environ["AI_CLIENT_WORKSPACE_NAME"],
    # ) as ai_client:

        # Get an authenticated async ChatCompletionsClient (from azure.ai.inference) for your default Serverless connection:
        async with await ai_client.inference.get_chat_completions_client() as client:

            response = await client.complete(messages=[UserMessage(content="How many feet are in a mile?")])
            print(response.choices[0].message.content)


async def main():
    await sample_get_chat_completions_client_async()

if __name__ == "__main__":
    asyncio.run(main())
