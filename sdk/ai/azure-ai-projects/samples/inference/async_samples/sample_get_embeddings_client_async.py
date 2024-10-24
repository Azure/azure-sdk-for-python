# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

"""
FILE: sample_get_embeddings_client_async.py

DESCRIPTION:
    Given an AIProjectClient, this sample demonstrates how to get an authenticated 
    async EmbeddingsClient from the azure.ai.inference package.

USAGE:
    python sample_get_embeddings_client_async.py

    Before running the sample:

    pip install azure.ai.projects aiohttp azure-identity

    Set this environment variable with your own values:
    PROJECT_CONNECTION_STRING - the Azure AI Project connection string, as found in your AI Studio Project.
"""
import asyncio
import os
from azure.ai.projects.aio import AIProjectClient
from azure.identity import DefaultAzureCredential


async def sample_get_embeddings_client_async():

    async with AIProjectClient.from_connection_string(
        credential=DefaultAzureCredential(),
        conn_str=os.environ["PROJECT_CONNECTION_STRING"],
    ) as project_client:

        # Get an authenticated async azure.ai.inference embeddings client for your default Serverless connection:
        async with await project_client.inference.get_embeddings_client() as client:

            response = await client.embed(input=["first phrase", "second phrase", "third phrase"])

            for item in response.data:
                length = len(item.embedding)
                print(
                    f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                    f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                )


async def main():
    await sample_get_embeddings_client_async()


if __name__ == "__main__":
    asyncio.run(main())
