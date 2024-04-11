# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion streaming response
    from the service using an asynchronous client.

USAGE:
    python sample_streaming_chat_completion_async.py

    Set these two environment variables before running the sample:
    1) MODEL_ENDPOINT - Your endpoint URL, in the form https://<deployment-name>.<azure-region>.inference.ai.azure.com
                        where `deployment-name` is your unique AI Model deployment name, and
                        `azure-region` is the Azure region where your model is deployed.
    2) MODEL_KEY - Your model key (a 32-character string). Keep it secret.
"""
import asyncio

import os
from azure.ai.inference.aio import ModelClient
from azure.ai.inference.models import ChatRequestSystemMessage, ChatRequestUserMessage, ChatCompletionsDelta
from azure.core.credentials import AzureKeyCredential

async def sample_streaming_chat_completions_async():

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["MODEL_ENDPOINT"]
        key = os.environ["MODEL_KEY"]
    except KeyError:
        print("Missing environment variable 'MODEL_ENDPOINT' or 'MODEL_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create Model Client for synchronous operations
    client = ModelClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Do a single streaming chat completion operation. Start the operation and get a Future object.
    future = asyncio.ensure_future(
        client.get_streaming_chat_completions(
            messages=[
                ChatRequestSystemMessage(content="You are an AI assistant that helps people find information."),
                ChatRequestUserMessage(content="Give me 5 good reasons why I should exercise every day."),
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
    accumulated_content = ""
    async for element in result:
        accumulated_content += element.choices[0].delta.content if element.choices[0].delta.content is not None else ""
        print_chat_completions_delta(element)

    print(f"Accumulated content: {accumulated_content}")

    # Remember to always close the asynchronous client when you are done with it
    await client.close()


def print_chat_completions_delta(element: ChatCompletionsDelta):
    print(f"content: {repr(element.choices[0].delta.content)}, "\
        f"role: {element.choices[0].delta.role}, "\
        f"finish_reason: {element.choices[0].finish_reason}, "\
        f"index: {element.choices[0].index}") 
    print(f"id: {element.id}, created: {element.created}, model: {element.model}, object: {element.object}")
    if element.usage is not None:
        print(f"usage: capacity_type: {element.usage.capacity_type}, "\
            f"prompt_tokens: {element.usage.prompt_tokens}, "\
            f"completion_tokens: {element.usage.completion_tokens}, "\
            f"usage.total_tokens: {element.usage.total_tokens}")


async def main():
    await sample_streaming_chat_completions_async()


if __name__ == "__main__":
    asyncio.run(main())
