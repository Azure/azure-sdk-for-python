# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to create a client from a given endpoint URL using
    the load_client() function, imported from azure.ai.inference.
    In this sample, we get a synchronous chat completions client and do one
    chat completions call.

    The load_client() function only works with Serverless API or Managed Compute endpoints.

USAGE:
    python sample_load_client.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_load_client():
    import os

    try:
        endpoint = os.environ["AZURE_AI_CHAT_ENDPOINT"]
        key = os.environ["AZURE_AI_CHAT_KEY"]
    except KeyError:
        print("Missing environment variable 'AZURE_AI_CHAT_ENDPOINT' or 'AZURE_AI_CHAT_KEY'")
        print("Set them before running this sample.")
        exit()

    # [START load_client]
    from azure.ai.inference import load_client, ChatCompletionsClient
    from azure.ai.inference.models import SystemMessage, UserMessage
    from azure.core.credentials import AzureKeyCredential

    client = load_client(endpoint=endpoint, credential=AzureKeyCredential(key))

    # This should create a client of type `ChatCompletionsClient`
    print(f"Created client of type `{type(client).__name__}`.")

    if type(client) is ChatCompletionsClient:
        response = client.complete(
            messages=[
                SystemMessage(content="You are a helpful assistant."),
                UserMessage(content="How many feet are in a mile?"),
            ]
        )

        print(response.choices[0].message.content)
    # [END load_client]


if __name__ == "__main__":
    sample_load_client()
