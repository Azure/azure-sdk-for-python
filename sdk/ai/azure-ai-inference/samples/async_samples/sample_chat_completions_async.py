# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion response
    from the service using an asynchronous client.

USAGE:
    python sample_chat_completion_async.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio


async def sample_chat_completions_async():
    import os
    from azure.ai.inference.aio import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create a chat completion client for synchronous operations
    async with ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as client:

        # Do a single chat completion operation
        response = await client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="How many feet are in a mile?"),
            ]
        )

        # Print response the the console
        print(response.choices[0].message.content)


async def main():
    await sample_chat_completions_async()


if __name__ == "__main__":
    asyncio.run(main())
