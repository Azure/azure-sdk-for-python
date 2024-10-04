# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to get information about the AI model, using the
    synchronous chat completions client. Similarly can be done with the other
    clients.

    The get_model_info() method on the client only works with Serverless API or
    Managed Compute endpoints.

USAGE:
    python sample_get_model_info.py

    Set these two environment variables before running the sample:
    1) AZURE_AI_CHAT_ENDPOINT - Your endpoint URL, in the form 
        https://<your-deployment-name>.<your-azure-region>.models.ai.azure.com
        where `your-deployment-name` is your unique AI Model deployment name, and
        `your-azure-region` is the Azure region where your model is deployed.
    2) AZURE_AI_CHAT_KEY - Your model key (a 32-character string). Keep it secret.
"""


def sample_get_model_info():
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

    # [START get_model_info]
    model_info = client.get_model_info()

    print(f"Model name: {model_info.model_name}")
    print(f"Model provider name: {model_info.model_provider_name}")
    print(f"Model type: {model_info.model_type}")
    # [END get_model_info]


if __name__ == "__main__":
    sample_get_model_info()
