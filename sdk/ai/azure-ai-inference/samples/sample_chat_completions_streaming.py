# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completion streaming response 
    from the service using a synchronous client.

USAGE:
    python sample_chat_completions_streaming.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_chat_completions_streaming():
    import os

    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    # [START chat_completions_streaming]
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    result = client.create_streaming(
        messages=[
            SystemMessage(content="You are a helpful assistant."),
            UserMessage(content="Give me 5 good reasons why I should exercise every day."),
        ]
    )

    for update in result:
        print(update.choices[0].delta.content, end="")
    # [END chat_completions_streaming]


if __name__ == "__main__":
    sample_chat_completions_streaming()
