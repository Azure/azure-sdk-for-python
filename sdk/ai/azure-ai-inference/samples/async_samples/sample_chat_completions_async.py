# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion response from the service using an asynchronous client.

USAGE:
    python sample_chat_completion_async.py

    Set these two environment variables before running the sample:
    1) MODEL_ENDPOINT - Your endpoint URL, in the form https://<deployment-name>.<azure-region>.inference.ai.azure.com
                        where `deployment-name` is your unique AI Model deployment name, and
                        `azure-region` is the Azure region where your model is deployed.
    2) MODEL_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio

async def sample_chat_completions_async():
    import os
    from azure.ai.inference.aio import ModelClient
    from azure.ai.inference.models import ChatRequestSystemMessage, ChatRequestUserMessage
    from azure.core.credentials import AzureKeyCredential

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["MODEL_ENDPOINT"]
        key = os.environ["MODEL_KEY"]
    except KeyError:
        print("Missing environment variable 'MODEL_ENDPOINT' or 'MODEL_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create a Model Client for synchronous operations
    client = ModelClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Do a single chat completion operation. Start the operation and get a Future object.
    future = asyncio.ensure_future(
        client.get_chat_completions(
            messages=[
                ChatRequestSystemMessage(content="You are an AI assistant that helps people find information."),
                ChatRequestUserMessage(content="How many feet are in a mile?"),
            ]
        )
    )

    # Loop until the operation is done
    while not future.done():
        await asyncio.sleep(0.1)
        print("Waiting...")

    # Get the result
    result = future.result()
    await client.close()

    # Print results the the console
    print("Chat Completions:")
    for index, choice in enumerate(result.choices):
        print(f"choices[{index}].message.content: {choice.message.content}")
        print(f"choices[{index}].message.role: {choice.message.role}")
        print(f"choices[{index}].finish_reason: {choice.finish_reason}")
        print(f"choices[{index}].index: {choice.index}")
    print(f"id: {result.id}")
    print(f"created: {result.created}")
    print(f"model: {result.model}")
    print(f"object: {result.object}")
    print(f"usage.prompt_tokens: {result.usage.prompt_tokens}")
    print(f"usage.completion_tokens: {result.usage.completion_tokens}")
    print(f"usage.total_tokens: {result.usage.total_tokens}")


async def main():
    await sample_chat_completions_async()


if __name__ == "__main__":
    asyncio.run(main())
