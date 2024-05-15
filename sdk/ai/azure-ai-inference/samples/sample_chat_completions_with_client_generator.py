# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client that was obtained from a
    `ClientGenerator.from_endpoint` call.

USAGE:
    python sample_chat_completions_with_client_generator

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions_with_client_generator():
    import os

    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    # [START chat_completions_with_client_generator]
    from azure.ai.inference import ClientGenerator, ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    client = ClientGenerator.from_endpoint(endpoint=endpoint, credential=AzureKeyCredential(key))

    if isinstance(client, ChatCompletionsClient):
        result = client.create(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="How many feet are in a mile?"),
            ]
        )

        print(result.choices[0].message.content)
    # [END chat_completions_with_client_generator]


if __name__ == "__main__":
    sample_chat_completions_with_client_generator()
