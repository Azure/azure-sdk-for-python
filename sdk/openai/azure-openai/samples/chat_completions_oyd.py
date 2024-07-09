# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

def chat_completion_oyd_studio_viewcode() -> None:

    import os
    from openai import AzureOpenAI
    from azure.identity import DefaultAzureCredential, get_bearer_token_provider

    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT"]

    # token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

    client = AzureOpenAI(
        azure_endpoint=endpoint,
        api_key=os.environ["AZURE_OPENAI_KEY"],
        api_version="2024-02-01",
    )

    completion = (
        client.chat.completions.create(
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
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": os.environ["AZURE_OPENAI_SEARCH_ENDPOINT"],
                            "index_name": os.environ["AZURE_OPENAI_SEARCH_INDEX"],
                            "authentication": {
                                "type": "system_assigned_managed_identity"
                            },
                        },
                    }
                ]
            },
        ),
    )

    print(completion.to_json())


if __name__ == "__main__":
    chat_completion_oyd_studio_viewcode()
