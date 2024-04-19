# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get a chat completions response from
    the service using a synchronous client, and directly providing the 
    IO[bytes] request body (containing input chat messages).

USAGE:
    python sample_chat_completions_from_input_bytes.py

    Set these two environment variables before running the sample:
    1) CHAT_COMPLETIONS_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.inference.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) CHAT_COMPLETIONS_KEY - Your model key (a 32-character string). Keep it secret.
"""
import io

def sample_chat_completions_from_input_bytes():
    import os

    try:
        endpoint = os.environ["CHAT_COMPLETIONS_ENDPOINT"]
        key = os.environ["CHAT_COMPLETIONS_KEY"]
    except KeyError:
        print("Missing environment variable 'CHAT_COMPLETIONS_ENDPOINT' or 'CHAT_COMPLETIONS_KEY'")
        print("Set them before running this sample.")
        exit()

    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(key))

    # Make a chat completion call, by directly providing the
    # HTTP request body as IO[bytes], containing chat messages.
    result = client.create(read_text_file("example_chat.json"))

    print(result.choices[0].message.content)

def read_text_file(file_path: str) -> io.BytesIO:
    """Reads a text file and returns a BytesIO object with the file content in UTF-8 encoding."""
    try:
        with open(file_path, 'r') as file:
            return io.BytesIO(file.read().encode('utf-8'))
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None

if __name__ == "__main__":
    sample_chat_completions_from_input_bytes()
