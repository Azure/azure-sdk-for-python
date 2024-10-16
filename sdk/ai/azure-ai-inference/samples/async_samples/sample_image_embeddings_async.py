# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get image embeddings vectors for 
    two input images, using an asynchronous client.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_image_embeddings_async.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_IMAGE_EMBEDDINGS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_IMAGE_EMBEDDINGS_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio


async def sample_image_embeddings_async():
    import os
    import base64

    try:
        endpoint = os.environ["AZURE_AI_IMAGE_EMBEDDINGS_ENDPOINT"]
        key = os.environ["AZURE_AI_IMAGE_EMBEDDINGS_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_IMAGE_EMBEDDINGS_ENDPOINT' or 'AZURE_AI_IMAGE_EMBEDDINGS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference.aio import ImageEmbeddingsClient
    from azure.ai.inference.models import EmbeddingInput
    from azure.core.credentials import AzureKeyCredential

    with open("sample1.png", "rb") as f:
        image1: str = base64.b64encode(f.read()).decode("utf-8")
    with open("sample2.png", "rb") as f:
        image2: str = base64.b64encode(f.read()).decode("utf-8")

    async with ImageEmbeddingsClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as client:

        # Do a single image embeddings operation. Start the operation and get a Future object.
        response = await client.embed(input=[EmbeddingInput(image=image1), EmbeddingInput(image=image2)])

        print("Embeddings response:")
        for item in response.data:
            length = len(item.embedding)
            print(
                f"data[{item.index}]: length={length}, [{item.embedding[0]}, {item.embedding[1]}, "
                f"..., {item.embedding[length-2]}, {item.embedding[length-1]}]"
            )


async def main():
    await sample_image_embeddings_async()


if __name__ == "__main__":
    asyncio.run(main())
