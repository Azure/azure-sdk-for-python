# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get embeddings for a list of sentences using an asynchronous client.

USAGE:
    python sample_embeddings_async.py

    Set these two environment variables before running the sample:
    1) MODEL_ENDPOINT - Your endpoint URL, in the form https://<deployment-name>.<azure-region>.inference.ai.azure.com
                        where `deployment-name` is your unique AI Model deployment name, and
                        `azure-region` is the Azure region where your model is deployed.
    2) MODEL_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio

async def sample_embeddings_async():
    import os
    from azure.ai.inference.aio import ModelClient
    from azure.core.credentials import AzureKeyCredential

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["MODEL_ENDPOINT"]
        key = os.environ["MODEL_KEY"]
    except KeyError:
        print("Missing environment variable 'MODEL_ENDPOINT' or 'MODEL_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create an Image Analysis client for synchronous operations
    client = ModelClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Do a single embeddings operation. Start the operation and get a Future object.
    future = asyncio.ensure_future(client.get_embeddings(input=["first sentence", "second sentence", "third sentence"]))

    # Loop until the operation is done
    while not future.done():
        await asyncio.sleep(0.1)
        print("Waiting...")

    # Get the result
    result = future.result()
    await client.close()

    # Print results the the console
    print("Embeddings result:")
    for index, item in enumerate(result.data):
        len = item.embedding.__len__()
        print(f"data[{index}].index: {item.index}")
        print(f"data[{index}].embedding[0]: {item.embedding[0]}")
        print(f"data[{index}].embedding[1]: {item.embedding[1]}")
        print("...")
        print(f"data[{index}].embedding[{len-2}]: {item.embedding[len-2]}")
        print(f"data[{index}].embedding[{len-1}]: {item.embedding[len-1]}")
    print(f"id: {result.id}")
    print(f"model: {result.model}")
    print(f"object: {result.object}")
    print(f"usage.prompt_tokens: {result.usage.prompt_tokens}")
    print(f"usage.total_tokens: {result.usage.total_tokens}")


async def main():
    await sample_embeddings_async()


if __name__ == "__main__":
    asyncio.run(main())
