# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: chat_completions_studio.py

DESCRIPTION:
    This sample contains the "view code" used in AI Studio's playground for Chat.

USAGE:
    python chat_completions_studio.py

    Before running the sample:

    pip install "openai" and "azure-identity"

    Set the environment variables with your own values:
    1) AZURE_OPENAI_ENDPOINT - the endpoint to your Azure OpenAI resource.
    2) AZURE_OPENAI_CHAT_DEPLOYMENT - the deployment name you chose when deploying your model.
"""

import os
os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv("AZ_OPENAI_ENDPOINT")

def chat_completion_studio_viewcode() -> None:
    #[START chat_completion_studio_viewcode]
    import os
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
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
                "content": "Who is DRI?",
            },
            {
                "role": "assistant",
                "content": "DRI stands for Directly Responsible Individual of a service. Which service are you asking about?",
            },
            {"role": "user", "content": "Opinion mining service"},
        ],
    )

    print(completion.to_json())
    #[END chat_completion_studio_viewcode]


if __name__ == "__main__":
    chat_completion_studio_viewcode()
