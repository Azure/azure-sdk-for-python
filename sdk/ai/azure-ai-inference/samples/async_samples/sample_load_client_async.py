# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to create an asynchronous client from a given
    endpoint URL using the load_async_client() function.
    In this sample, we get an asynchronous client and do a chat completions call.

USAGE:
    python sample_load_client_async.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio

async def sample_load_client_async():
    import os

    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import load_async_client
    from azure.ai.inference.aio import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    client = load_async_client(endpoint=endpoint, credential=AzureKeyCredential(key))

    # This should create a client of type `ChatCompletionsClient`
    print(f"Created client of type `{type(client).__name__}`.")

    # TODO: Why does this return False?
    #if isinstance(client, azure.ai.inference.aio.ChatCompletionsClient):
    # Do a single chat completion operation. Start the operation and get a Future object.
    future = asyncio.ensure_future(
        client.create(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="How many feet are in a mile?"),
            ]
        )
    )

    # Loop until the operation is done
    while not future.done():
        await asyncio.sleep(0.1)
        print("Waiting...")

    # Get the response
    response = future.result()
    await client.close()

    # Print results the the console
    print(f"choices[0].message.content: {response.choices[0].message.content}")


async def main():
    await sample_load_client_async()


if __name__ == "__main__":
    asyncio.run(main())
