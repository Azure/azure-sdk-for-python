# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from the service using a synchronous client.

USAGE:
    python sample_chat_completions.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""

def sample_chat_completions():
    import os
    from azure.ai.inference.models import ChatRequestSystemMessage, ChatRequestUserMessage
    
    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    # [START create_client]
    from azure.ai.inference import ModelClient
    from azure.core.credentials import AzureKeyCredential

    # Create Model Client for synchronous operations
    client = ModelClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )
    # [END create_client]

    # [START chat_completions]
    # Do a single chat completion operation. This will be a synchronously (blocking) call.
    result = client.get_chat_completions(
        messages=[
            ChatRequestSystemMessage(content="You are an AI assistant that helps people find information."),
            ChatRequestUserMessage(content="How many feet are in a mile?"),
        ],
        # Examples of setting extra parameters (TODO: move this to advanced sample)
        extras=dict(key1="value1", key2="value2"),
    )

    # Print results the the console
    print("Chat Completions:")
    print(f"choices[0].message.content: {result.choices[0].message.content}")
    print(f"choices[0].message.role: {result.choices[0].message.role}")
    print(f"choices[0].finish_reason: {result.choices[0].finish_reason}")
    print(f"choices[0].index: {result.choices[0].index}")
    print(f"id: {result.id}")
    print(f"created: {result.created}")
    print(f"model: {result.model}")
    print(f"object: {result.object}")
    print(f"usage.capacity_type: {result.usage.capacity_type}")
    print(f"usage.prompt_tokens: {result.usage.prompt_tokens}")
    print(f"usage.completion_tokens: {result.usage.completion_tokens}")
    print(f"usage.total_tokens: {result.usage.total_tokens}")
    # [END chat_completions]


if __name__ == "__main__":
    sample_chat_completions()
