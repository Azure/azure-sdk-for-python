# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import json
import openai
from devtools_testutils import AzureRecordedTestCase
from conftest import (
    AZURE,
    AZURE_KEY,
    GPT_4_AZURE,
    configure,
    GA,
    PREVIEW,
    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_ENDPOINT,
    ENV_AZURE_OPENAI_KEY,
    ENV_AZURE_OPENAI_SEARCH_ENDPOINT,
    ENV_AZURE_OPENAI_SEARCH_INDEX
)


class ChatCompletionsSnippets(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE_KEY, GA), (AZURE_KEY, PREVIEW)]
    )
    def test_azure_api_key(self, client, api_type, api_version, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, **kwargs)
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE, GA), (AZURE, PREVIEW), (OPENAI, "v1")]
    )
    def test_chat_completion(self, client, api_type, api_version, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = client.chat.completions.create(messages=messages, **kwargs)
        assert completion.id
        assert completion.object == "chat.completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].message.content is not None
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize(
        "api_type, api_version",
        [(AZURE_KEY, GA)]
    )
    def chat_completion_studio_viewcode(self, api_type, api_version, **kwargs):

        import os
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider

        endpoint = os.environ[ENV_AZURE_OPENAI_ENDPOINT]
        deployment = os.environ[ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME]

        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

        client = AzureOpenAI(
            azure_endpoint = endpoint,
            azure_ad_token_provider = token_provider,
            api_version = os.environ[GA],
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
                    "content": "DRI stands for Directly Responsible Individual of a service. Which service are you asking about?"
                },
                {
                    "role": "user",
                    "content": "Opinion mining service"
                }
            ]
        )

        print(completion.to_json())

    def chat_completion_oyd_studio_viewcode(self, api_type, api_version, **kwargs):

        import os
        from openai import AzureOpenAI
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider

        endpoint = os.environ[ENV_AZURE_OPENAI_ENDPOINT]
        deployment = os.environ[ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME]

        token_provider = get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default")

        client = AzureOpenAI(
            azure_endpoint = endpoint,
            azure_ad_token_provider = token_provider,
            api_version = os.environ[GA],
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
                    "content": "DRI stands for Directly Responsible Individual of a service. Which service are you asking about?"
                },
                {
                    "role": "user",
                    "content": "Opinion mining service"
                }
            ],
            extra_body={
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": os.environ[ENV_AZURE_OPENAI_SEARCH_ENDPOINT],
                            "index_name": os.environ[ENV_AZURE_OPENAI_SEARCH_INDEX],
                            "authentication": {
                                "type": "system_assigned_managed_identity"
                            }
                        }
                    }
                ]
            }
        ),

        print(completion.to_json())

    def chat_completion_quickstart(self, api_type, api_version, **kwargs):
        import os
        from openai import AzureOpenAI

        client = AzureOpenAI(
            azure_endpoint = os.getenv[ENV_AZURE_OPENAI_ENDPOINT],
            api_key = os.getenv[ENV_AZURE_OPENAI_KEY],
            api_version = os.environ[GA]
        )

        response = client.chat.completions.create(
            model = os.environ[ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME],
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Does Azure OpenAI support customer managed keys?"},
                {"role": "assistant", "content": "Yes, customer managed keys are supported by Azure OpenAI."},
                {"role": "user", "content": "Do other Azure AI services support this too?"}
            ]
        )

        print(response.choices[0].message.content)