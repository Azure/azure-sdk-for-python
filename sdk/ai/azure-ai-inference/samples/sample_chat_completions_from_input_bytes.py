# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client, and directly providing the 
    IO[bytes] request body (containing input chat messages).

    This sample assumes the AI model is hosted on a Serverless API or
    Managed Compute endpoint. For GitHub Models or Azure OpenAI endpoints,
    the client constructor needs to be modified. See package documentation:
    https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-inference/README.md#key-concepts

USAGE:
    python sample_chat_completions_from_input_bytes.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""
# mypy: disable-error-code="union-attr"
# pyright: reportAttributeAccessIssue=false


import io


def sample_chat_completions_from_input_bytes():
    import os

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.core.credentials import AzureKeyCredential

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Make a chat completion call, by directly providing the
    # HTTP request body as IO[bytes], containing chat messages.
    response = client.complete(read_text_file("example_chat.json"))

    print(response.choices[0].message.content)


def read_text_file(file_name: str) -> io.BytesIO:
    """
    Reads a text file and returns a BytesIO object with the file content in UTF-8 encoding.
    The file is expected to be in the same directory as this Python script.
    """
    from pathlib import Path

    with Path(__file__).with_name(file_name).open("r") as f:
        return io.BytesIO(f.read().encode("utf-8"))


if __name__ == "__main__":
    sample_chat_completions_from_input_bytes()
