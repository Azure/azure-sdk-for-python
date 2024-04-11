# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion streaming response 
    from the service using a synchronous client.

USAGE:
    python sample_streaming_chat_completions.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""

import os
from azure.ai.inference import ModelClient
from azure.ai.inference.models import ChatRequestSystemMessage, ChatRequestUserMessage, ChatCompletionsDelta
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.transport import RequestsTransport

def sample_streaming_chat_completions():

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create Model Client for synchronous operations
    client = ModelClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    messages = [
        ChatRequestSystemMessage(content="You are an AI assistant that helps people find information."),
        ChatRequestUserMessage(content="Give me 5 good reasons why I should exercise every day."),
    ]

    # [START streaming_chat_completions]
    # Do a single chat completion operation. This will be a synchronously (blocking) call.
    result = client.get_streaming_chat_completions(messages=messages)

    # Iterate on the result to get chat completion updates, as they arrive from the service
    accumulated_content = ""
    for element in result:
        accumulated_content += element.choices[0].delta.content if element.choices[0].delta.content is not None else ""
        print_chat_completions_delta(element)

    print(f"Accumulated content: {accumulated_content}")
    # [END streaming_chat_completions]


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

if __name__ == "__main__":
    sample_streaming_chat_completions()
