# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get embeddings for a list of sentences using an asynchronous client.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_embeddings_async.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_EMBEDDINGS_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_EMBEDDINGS_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio


async def sample_embeddings_async():
    import os
    from azure.ai.inference.aio import EmbeddingsClient
    from azure.core.credentials import AzureKeyCredential

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["AZURE_AI_EMBEDDINGS_ENDPOINT"]
        key = os.environ["AZURE_AI_EMBEDDINGS_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_EMBEDDINGS_ENDPOINT' or 'AZURE_AI_EMBEDDINGS_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create a text embeddings client for synchronous operations
    async with EmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as client:

        # Do a single embeddings operation. Start the operation and get a Future object.
        response = await client.embed(input=["first phrase", "second phrase", "third phrase"])

        print("Embeddings response:")
        for item in response.data:
            length = len(item.embedding)
            print(
                f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, ..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
            )


async def main():
    await sample_embeddings_async()


if __name__ == "__main__":
    asyncio.run(main())
