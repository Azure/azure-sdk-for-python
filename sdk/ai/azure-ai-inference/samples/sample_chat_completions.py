# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion response from the service using a synchronous client.

USAGE:
    python sample_chat_completion.py

    Set these two environment variables before running the sample:
    1) MODEL_ENDPOINT - Your endpoint URL, in the form https://<deployment-name>.<azure-region>.inference.ai.azure.com
                        where `deployment-name` is your unique AI Model deployment name, and
                        `azure-region` is the Azure region where your model is deployed.
    2) MODEL_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions():
    # [START create_client]
    import os
    from azure.ai.inference import ModelClient
    from azure.ai.inference.models import ChatRequestSystemMessage, ChatRequestUserMessage, ExtraParameters
    from azure.core.credentials import AzureKeyCredential

    # [START logging]
    import sys
    import logging

    # Acquire the logger for this client library. Use 'azure' to affect both
    # 'azure.core` and `azure.ai.vision.imageanalysis' libraries.
    logger = logging.getLogger("azure")

    # Set the desired logging level. logging.INFO or logging.DEBUG are good options.
    logger.setLevel(logging.DEBUG)

    # Direct logging output to stdout (the default):
    handler = logging.StreamHandler(stream=sys.stdout)
    # Or direct logging output to a file:
    # handler = logging.FileHandler(filename = 'sample.log')
    logger.addHandler(handler)

    # Optional: change the default logging format. Here we add a timestamp.
    formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(name)s:%(message)s")
    handler.setFormatter(formatter)
    # [END logging]

    # Read the values of your model endpoint and key from environment variables
    try:
        endpoint = os.environ["MODEL_ENDPOINT"]
        key = os.environ["MODEL_KEY"]
    except KeyError:
        print("Missing environment variable 'MODEL_ENDPOINT' or 'MODEL_KEY'")
        print("Set them before running this sample.")
        exit()

    # Create Model Client for synchronous operations
    client = ModelClient(endpoint=endpoint, credential=AzureKeyCredential(key), logging_enable=True)
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
        extra_parameters=ExtraParameters.ALLOW
    )

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
    # [END chat_completions]


if __name__ == "__main__":
    sample_chat_completions()
