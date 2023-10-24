# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from azure.identity import DefaultAzureCredential
from conftest import (
    AZURE,
    ENV_AZURE_OPENAI_ENDPOINT,
    ENV_AZURE_OPENAI_API_VERSION,
    configure
)


class TestClient(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_client_str_token(self, client, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        client = openai.AzureOpenAI(
            endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token=DefaultAzureCredential().get_token("https://cognitiveservices.azure.com/.default").token,
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
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
        assert completion.choices[0].message.content
        assert completion.choices[0].message.role

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_client_no_api_key(self, client, azure_openai_creds, api_type, **kwargs):

        with pytest.raises(openai.OpenAIError) as e:
            openai.AzureOpenAI(
                endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
                api_key=None,
                api_version=ENV_AZURE_OPENAI_API_VERSION,
            )
        assert "The api_key client option must be set either by passing api_key to the client or by setting the AZURE_OPENAI_API_KEY environment variable; If you're using Azure AD you should pass either the `azure_ad_token` or the `azure_ad_token_provider` argument." in str(e.value.args)

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_client_bad_token(self, client, azure_openai_creds, api_type, **kwargs):

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        client = openai.AzureOpenAI(
            endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token="None",
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
        with pytest.raises(openai.AuthenticationError) as e: 
            client.chat.completions.create(messages=messages, **kwargs)
        assert e.value.status_code == 401

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_client_bad_token_provider(self, client, azure_openai_creds, api_type, **kwargs):

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        client = openai.AzureOpenAI(
            endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token_provider=lambda: None,
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
        with pytest.raises(ValueError) as e:
            client.chat.completions.create(messages=messages, **kwargs)
        assert "ValueError: Expected `azure_ad_token_provider` argument to return a string but it returned None" in str(e.value.args)
