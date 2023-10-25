# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import os
import pytest
import openai
from importlib import reload
from devtools_testutils import AzureRecordedTestCase
from conftest import (
    configure,
    ENV_AZURE_OPENAI_ENDPOINT,
    ENV_AZURE_OPENAI_KEY,
    ENV_AZURE_OPENAI_API_VERSION,
    ENV_AZURE_OPENAI_WHISPER_ENDPOINT,
    ENV_AZURE_OPENAI_WHISPER_KEY,
    ENV_AZURE_OPENAI_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
    ENV_AZURE_OPENAI_EMBEDDINGS_NAME,
    ENV_AZURE_OPENAI_AUDIO_NAME,
    AZURE,
)

audio_test_file = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "./assets/hello.m4a"))


class TestModuleClient(AzureRecordedTestCase):

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_module_client_completions(self, client, azure_openai_creds, api_type, **kwargs):
        reload(openai)
        openai.azure = True
        openai.azure_endpoint = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
        openai.api_key = os.getenv(ENV_AZURE_OPENAI_KEY)
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION

        completion = openai.completions.create(prompt="hello world", model=ENV_AZURE_OPENAI_COMPLETIONS_NAME)
        assert completion.id
        assert completion.object == "text_completion"
        assert completion.model
        assert completion.created
        assert completion.usage.completion_tokens is not None
        assert completion.usage.prompt_tokens is not None
        assert completion.usage.total_tokens == completion.usage.completion_tokens + completion.usage.prompt_tokens
        assert len(completion.choices) == 1
        assert completion.choices[0].finish_reason
        assert completion.choices[0].index is not None
        assert completion.choices[0].text

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_module_client_chat_completions(self, client, azure_openai_creds, api_type, **kwargs):
        reload(openai)
        openai.azure = True
        openai.azure_endpoint = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
        openai.api_key = os.getenv(ENV_AZURE_OPENAI_KEY)
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"}
        ]

        completion = openai.chat.completions.create(messages=messages, model=ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME)
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
    def test_module_client_embeddings(self, client, azure_openai_creds, api_type, **kwargs):
        reload(openai)
        openai.azure = True
        openai.azure_endpoint = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
        openai.api_key = os.getenv(ENV_AZURE_OPENAI_KEY)
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION

        embedding = openai.embeddings.create(input="hello world", model=ENV_AZURE_OPENAI_EMBEDDINGS_NAME)
        assert embedding.object == "list"
        assert embedding.model
        assert embedding.usage.prompt_tokens is not None
        assert embedding.usage.total_tokens is not None
        assert len(embedding.data) == 1
        assert embedding.data[0].object == "embedding"
        assert embedding.data[0].index is not None
        assert len(embedding.data[0].embedding) > 0

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_module_client_models(self, client, azure_openai_creds, api_type, **kwargs):
        reload(openai)
        openai.azure = True
        openai.azure_endpoint = os.getenv(ENV_AZURE_OPENAI_ENDPOINT)
        openai.api_key = os.getenv(ENV_AZURE_OPENAI_KEY)
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION

        models = openai.models.list()
        for model in models:
            assert model.id

        model = openai.models.retrieve(model=ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME)
        assert model.id

    @configure
    @pytest.mark.parametrize("api_type", [AZURE])
    def test_module_client_audio(self, client, azure_openai_creds, api_type, **kwargs):
        reload(openai)
        openai.azure = True
        openai.azure_endpoint = os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT)
        openai.api_key = os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY)
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION

        result = openai.audio.transcriptions.create(
            file=open(audio_test_file, "rb"),
            model=ENV_AZURE_OPENAI_AUDIO_NAME
        )
        assert result.text == "Hello."

        result = openai.audio.translations.create(
            file=open(audio_test_file, "rb"),
            model=ENV_AZURE_OPENAI_AUDIO_NAME
        )
        assert result.text == "Hello."
