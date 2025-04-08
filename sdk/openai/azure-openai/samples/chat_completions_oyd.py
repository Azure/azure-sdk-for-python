# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: chat_completions_oyd.py

DESCRIPTION:
    This sample demonstrates how to use your own data with Azure OpenAI Chat Completions.

USAGE:
    python chat_completions_oyd.py

    Before running the sample:

    pip install "openai" and "azure-identity"

    Set the environment variables with your own values:
    1) AZURE_OPENAI_ENDPOINT - the endpoint to your Azure OpenAI resource.
    2) AZURE_OPENAI_CHAT_DEPLOYMENT - the deployment name you chose when deploying your model.
    3) AZURE_OPENAI_SEARCH_ENDPOINT - the endpoint to your Azure Search resource.
    4) AZURE_OPENAI_SEARCH_INDEX - the index name you chose when creating your Azure Search index.
"""

# These lines are intentionally excluded from the sample code, we use them to configure any vars
# or to tweak usage in ways that keep samples looking consistent when rendered in docs and tools
import os
os.environ["AZURE_OPENAI_ENDPOINT"] = os.environ["AZ_OPENAI_ENDPOINT"]

def chat_completion_oyd_studio_viewcode() -> None:
    import os
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        azure_ad_token_provider=token_provider,
        api_version=os.environ["API_VERSION_GA"],
    )

    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {
                "role": "user",
                "content": "What languages have libraries you know about for Azure OpenAI?",
            }
        ],
        extra_body={
            "data_sources": [
                {
                    "type": "azure_search",
                    "parameters": {
                        "endpoint": os.environ["AZURE_OPENAI_SEARCH_ENDPOINT"],
                        "index_name": os.environ["AZURE_OPENAI_SEARCH_INDEX"],
                        "authentication": {"type": "system_assigned_managed_identity"},
                    },
                }
            ]
        },
    )

    print(completion.choices[0].message.content)


if __name__ == "__main__":
    chat_completion_oyd_studio_viewcode()
