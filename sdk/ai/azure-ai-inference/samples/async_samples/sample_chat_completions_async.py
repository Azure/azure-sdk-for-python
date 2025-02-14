# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion response
    from the service using an asynchronous client.

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completion_async.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key. Keep it secret.
"""
import asyncio


async def sample_chat_completions_async():
    import os
    from azure.ai.inference.aio import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    async with ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key)) as client:

        response = await client.complete(
            messages=[
                SystemMessage("You are a helpful assistant."),
                UserMessage("How many feet are in a mile?"),
            ]
        )

        print(response.choices[0].message.content)
        print(f"\nToken usage: {response.usage}")


async def main():
    await sample_chat_completions_async()


if __name__ == "__main__":
    asyncio.run(main())
