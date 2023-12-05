# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import openai
from devtools_testutils import AzureRecordedTestCase
from azure.identity.aio import DefaultAzureCredential
from conftest import (
    AZURE,
    ENV_AZURE_OPENAI_ENDPOINT,
    ENV_AZURE_OPENAI_KEY,
    ENV_AZURE_OPENAI_API_VERSION,
    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
    configure_async,
    reload,
)


class TestClientAsync(AzureRecordedTestCase):
    """Azure AD with token provider is missing here because it is tested per feature"""

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_chat_completion_bad_deployment(self, client_async, azure_openai_creds, api_type, **kwargs):

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        with pytest.raises(openai.NotFoundError) as e:
            await client_async.chat.completions.create(messages=messages, model="bad_deployment")
        assert e.value.status_code == 404
        assert "The API deployment for this resource does not exist" in e.value.message

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_chat_completion_endpoint_deployment(self, client_async, azure_openai_creds, api_type, **kwargs):

        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_deployment=ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = await client.chat.completions.create(messages=messages, model="placeholder")
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

        # try to call some other feature not under the same deployment name
        with pytest.raises(openai.BadRequestError) as e:
            await client.embeddings.create(input=["Hello world!"], model="placeholder")
        assert e.value.status_code == 400
        assert "The embeddings operation does not work with the specified model, " \
        f"{ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME}. Please choose different model and try again" in e.value.message

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_chat_completion_base_url(self, client_async, azure_openai_creds, api_type, **kwargs):

        client = openai.AsyncAzureOpenAI(
            base_url=f"{os.getenv(ENV_AZURE_OPENAI_ENDPOINT)}/openai/deployments/{ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME}",
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = await client.chat.completions.create(messages=messages, **kwargs)
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

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_client_str_token(self, client_async, azure_openai_creds, api_type, **kwargs):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        credential = DefaultAzureCredential()
        access_token = await credential.get_token("https://cognitiveservices.azure.com/.default")

        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token=access_token.token,
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
        completion = await client.chat.completions.create(messages=messages, **kwargs)
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

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_client_no_api_key(self, client_async, azure_openai_creds, api_type, **kwargs):

        with pytest.raises(openai.OpenAIError) as e:
            openai.AsyncAzureOpenAI(
                azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
                api_key=None,
                api_version=ENV_AZURE_OPENAI_API_VERSION,
            )
        assert 'Missing credentials. Please pass one of `api_key`, `azure_ad_token`, `azure_ad_token_provider`, or the `AZURE_OPENAI_API_KEY` or `AZURE_OPENAI_AD_TOKEN` environment variables.' in str(e.value.args)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_client_bad_token(self, client_async, azure_openai_creds, api_type, **kwargs):

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token="None",
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
        with pytest.raises(openai.AuthenticationError) as e: 
            await client.chat.completions.create(messages=messages, **kwargs)
        assert e.value.status_code == 401

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_client_bad_token_provider(self, client_async, azure_openai_creds, api_type, **kwargs):

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token_provider=lambda: None,
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
        with pytest.raises(ValueError) as e:
            await client.chat.completions.create(messages=messages, **kwargs)
        assert "Expected `azure_ad_token_provider` argument to return a string but it returned None" in str(e.value.args)

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_client_env_vars_key(self, client_async, azure_openai_creds, api_type, **kwargs):
        with reload():
            os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
            os.environ["OPENAI_API_VERSION"] = ENV_AZURE_OPENAI_API_VERSION
            os.environ["AZURE_OPENAI_API_KEY"] = os.getenv(ENV_AZURE_OPENAI_KEY)

            try:
                client = openai.AsyncAzureOpenAI()
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Who won the world series in 2020?"}
                ]
                completion = await client.chat.completions.create(messages=messages, **kwargs)
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
            finally:
                del os.environ['AZURE_OPENAI_ENDPOINT']
                del os.environ['AZURE_OPENAI_API_KEY']
                del os.environ['OPENAI_API_VERSION']

    @configure_async
    @pytest.mark.asyncio
    @pytest.mark.parametrize("api_type", [AZURE])
    async def test_client_env_vars_token(self, client_async, azure_openai_creds, api_type, **kwargs):
        with reload():
            os.environ["AZURE_OPENAI_ENDPOINT"] = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
            os.environ["OPENAI_API_VERSION"] = ENV_AZURE_OPENAI_API_VERSION
            credential = DefaultAzureCredential()
            access_token = await credential.get_token("https://cognitiveservices.azure.com/.default")
            os.environ["AZURE_OPENAI_AD_TOKEN"] = access_token.token

            try:
                client = openai.AsyncAzureOpenAI()
                messages = [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Who won the world series in 2020?"}
                ]
                completion = await client.chat.completions.create(messages=messages, **kwargs)
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
            finally:
                del os.environ['AZURE_OPENAI_ENDPOINT']
                del os.environ['AZURE_OPENAI_AD_TOKEN']
                del os.environ['OPENAI_API_VERSION']
