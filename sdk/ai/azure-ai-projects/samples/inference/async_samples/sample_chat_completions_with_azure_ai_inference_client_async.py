# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    async ChatCompletionsClient from the azure.ai.inference package. For more information
    on the azure.ai.inference package see https://pypi.org/project/azure-ai-inference/.

USAGE:
    python sample_get_chat_completions_client_async.py

    Before running the sample:

    pip install azure-ai-projects aiohttp azure-identity

    Set this environment variables with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import os
import asyncio
from azure.ai.projects.aio import AIProjectClient
from azure.ai.inference.models import UserMessage
from azure.identity import DefaultAzureCredential


async def sample_get_chat_completions_client_async():

    async with AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["PROJECT_CONNECTION_STRING"],
    ) as project_client:

        # Get an authenticated async ChatCompletionsClient (from azure.ai.inference) for your default Serverless connection:
        async with await project_client.inference.get_chat_completions_client() as client:

            response = await client.complete(messages=[UserMessage(content="How many feet are in a mile?")])
            print(response.choices[0].message.content)


async def main():
    await sample_get_chat_completions_client_async()


if __name__ == "__main__":
    asyncio.run(main())
