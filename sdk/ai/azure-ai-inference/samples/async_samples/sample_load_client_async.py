# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to create an asynchronous client from a given endpoint URL using
    the load_client() function, imported from azure.ai.inference.aio.
    In this sample, we get an asynchronous embeddings client and do one embeddings call.

    The load_client() function only works with Serverless API or Managed Compute endpoints.

USAGE:
    python sample_load_client_async.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_EMBEDDINGS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_EMBEDDINGS_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio


async def sample_load_client_async():
    import os

    try:
        endpoint = os.environ["AZURE_AI_EMBEDDINGS_ENDPOINT"]
        key = os.environ["AZURE_AI_EMBEDDINGS_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_EMBEDDINGS_ENDPOINT' or 'AZURE_AI_EMBEDDINGS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference.aio import load_client, EmbeddingsClient
    from azure.core.credentials import AzureKeyCredential

    async with await load_client(endpoint=endpoint, credential=AzureKeyCredential(key)) as client:

        # This should create a client of type `EmbeddingsClient`
        print(f"Created client of type `{type(client).__name__}`.")

        if type(client) is EmbeddingsClient:
            response = await client.embed(input=["first phrase", "second phrase", "third phrase"])

            print("Embeddings response:")
            for item in response.data:
                length = len(item.embedding)
                print(
                    f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, ..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
                )


async def main():
    await sample_load_client_async()


if __name__ == "__main__":
    asyncio.run(main())
