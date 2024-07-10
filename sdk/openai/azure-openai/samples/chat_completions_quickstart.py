# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


def chat_completion_quickstart() -> None:
    import os
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
    )

    client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        azure_ad_token_provider=token_provider,
        api_version="2024-02-01",
    )

    response = client.chat.completions.create(
        model=os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"],
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


if __name__ == "__main__":
    chat_completion_quickstart()
