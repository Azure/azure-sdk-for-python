# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: chat_completions_quickstart.py

DESCRIPTION:
    This sample demonstrates how to get started with Azure OpenAI Chat Completions using the official OpenAI SDK for Python.

USAGE:
    python chat_completions_quickstart.py

    Before running the sample:

    pip install "openai" and "azure-identity"

    Set the environment variables with your own values:
    1) AZURE_OPENAI_ENDPOINT - the endpoint to your Azure OpenAI resource.
    2) AZURE_OPENAI_CHAT_DEPLOYMENT - the deployment name you chose when deploying your model.
"""

AZURE_OPENAI_ENDPOINT = "AZ_OPENAI_ENDPOINT"

def chat_completion_quickstart() -> None:
    #[START chat_completion_quickstart]
    import os
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        azure_endpoint=os.environ[AZURE_OPENAI_ENDPOINT],
        azure_ad_token_provider=token_provider,
        api_version="2024-05-13",
    )

    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"], #"gpt-4-0613",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": "Does Azure OpenAI support customer managed keys?",
            },
            {
                "role": "assistant",
                "content": "Yes, customer managed keys are supported by Azure OpenAI.",
            },
            {"role": "user", "content": "Do other Azure AI services support this too?"},
        ],
    )

    print(response.to_json())
    #[END chat_completion_quickstart]


if __name__ == "__main__":
    chat_completion_quickstart()
