# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion streaming response
    from the service using an asynchronous client.

USAGE:
    python sample_streaming_chat_completions_async.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio
import os
from azure.ai.inference.aio import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, ChatCompletionsUpdate
from azure.core.credentials import AzureKeyCredential


async def sample_chat_completions_streaming_async():

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create chat completions client for synchronous operations
    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Do a single streaming chat completion operation. Start the operation and get a Future object.
    future = asyncio.ensure_future(
        client.create_streaming(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="Give me 5 good reasons why I should exercise every day."),
            ]
        )
    )

    # Loop until you get the HTTP response headers from the service
    while not future.done():
        await asyncio.sleep(0.1)
        print("Waiting...")

    # Get the result
    result = future.result()

    # Iterate on the result to get chat completion updates, as they arrive from the service
    async for update in result:
        if update.choices[0].delta.content:
            print(update.choices[0].delta.content, end="")

    # Remember to always close the asynchronous client when you are done with it
    await client.close()

async def main():
    await sample_chat_completions_streaming_async()


if __name__ == "__main__":
    asyncio.run(main())
