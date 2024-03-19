# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import pytest
import importlib
import contextlib
import functools
import openai
from devtools_testutils.sanitizers import add_header_regex_sanitizer, add_oauth_response_sanitizer
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.identity.aio import (
    DefaultAzureCredential as AsyncDefaultAzureCredential,
    get_bearer_token_provider as get_bearer_token_provider_async,
)


# for pytest.parametrize
AZURE = "azure"
OPENAI = "openai"
AZURE_AD = "azuread"
ALL = [AZURE, AZURE_AD, OPENAI]
WHISPER_AZURE = "whisper_azure"
WHISPER_AZURE_AD = "whisper_azuread"
WHISPER_ALL = [WHISPER_AZURE, WHISPER_AZURE_AD, OPENAI]
TTS_OPENAI = "tts_openai"
TTS_AZURE = "tts_azure"
TTS_AZURE_AD = "tts_azuread"
TTS_ALL = [TTS_AZURE, TTS_AZURE_AD, TTS_OPENAI]
DALLE_AZURE = "dalle_azure"
DALLE_AZURE_AD = "dalle_azuread"
DALLE_ALL = [DALLE_AZURE, DALLE_AZURE_AD, OPENAI]
GPT_4_AZURE = "gpt_4_azure"
GPT_4_AZURE_AD = "gpt_4_azuread"
GPT_4_OPENAI = "gpt_4_openai"
GPT_4_ALL = [GPT_4_AZURE, GPT_4_AZURE_AD, GPT_4_OPENAI]
ASST_AZURE = "asst_azure"
ASST_AZUREAD = "asst_azuread"
ASST_ALL = [ASST_AZURE, ASST_AZUREAD, GPT_4_OPENAI]

# Environment variable keys
ENV_AZURE_OPENAI_ENDPOINT = "AZ_OPENAI_ENDPOINT"
ENV_AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT = "AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT"
ENV_AZURE_OPENAI_NORTHCENTRALUS_KEY = "AZURE_OPENAI_NORTHCENTRALUS_KEY"
ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT = "AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT"
ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY = "AZURE_OPENAI_SWEDENCENTRAL_KEY"
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
ENV_AZURE_OPENAI_SEARCH_ENDPOINT = "AZURE_OPENAI_SEARCH_ENDPOINT"
ENV_AZURE_OPENAI_SEARCH_KEY = "AZURE_OPENAI_SEARCH_KEY"
ENV_AZURE_OPENAI_SEARCH_INDEX = "AZURE_OPENAI_SEARCH_INDEX"

ENV_AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
ENV_AZURE_OPENAI_COMPLETIONS_NAME = "gpt-35-turbo-instruct"
ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME = "gpt-35-turbo-16k"
ENV_AZURE_OPENAI_EMBEDDINGS_NAME = "text-embedding-ada-002"
ENV_AZURE_OPENAI_AUDIO_NAME = "whisper"
ENV_AZURE_OPENAI_DALLE_NAME = "dall-e-3"
ENV_AZURE_OPENAI_CHAT_COMPLETIONS_GPT4_NAME = "gpt-4-1106-preview"
ENV_AZURE_OPENAI_TTS_NAME = "tts"

ENV_OPENAI_KEY = "OPENAI_KEY"
ENV_OPENAI_COMPLETIONS_MODEL = "gpt-3.5-turbo-instruct"
ENV_OPENAI_CHAT_COMPLETIONS_MODEL = "gpt-3.5-turbo"
ENV_OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
ENV_OPENAI_AUDIO_MODEL = "whisper-1"
ENV_OPENAI_DALLE_MODEL = "dall-e-3"
ENV_OPENAI_CHAT_COMPLETIONS_GPT4_MODEL = "gpt-4-1106-preview"
ENV_OPENAI_TTS_MODEL = "tts-1"

# Fake values
TEST_ENDPOINT = "https://test-resource.openai.azure.com/"
TEST_KEY = "0000000000000000"
TEST_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_AZURE_OPENAI_ENDPOINT: TEST_ENDPOINT,
        ENV_AZURE_OPENAI_KEY: TEST_KEY,
        ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT: TEST_ENDPOINT,
        ENV_AZURE_OPENAI_NORTHCENTRALUS_KEY: TEST_KEY,
        ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT: TEST_ENDPOINT,
        ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY: TEST_KEY,
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
        ENV_CLIENT_ID: TEST_ID,
        ENV_CLIENT_SECRET: TEST_ID,
        ENV_OPENAI_KEY: TEST_KEY,
        ENV_AZURE_OPENAI_SEARCH_ENDPOINT: TEST_ENDPOINT,
        ENV_AZURE_OPENAI_SEARCH_KEY: TEST_KEY,
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")


@pytest.fixture(scope="session")
def azure_openai_creds():
    yield {
        "completions_name": ENV_AZURE_OPENAI_COMPLETIONS_NAME,
        "chat_completions_name": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME,
        "embeddings_name": ENV_AZURE_OPENAI_EMBEDDINGS_NAME,
        "completions_model": ENV_OPENAI_COMPLETIONS_MODEL,
        "chat_completions_model": ENV_OPENAI_CHAT_COMPLETIONS_MODEL,
        "embeddings_model": ENV_OPENAI_EMBEDDINGS_MODEL,
        "search_endpoint": os.getenv(ENV_AZURE_OPENAI_SEARCH_ENDPOINT),
        "search_key": os.getenv(ENV_AZURE_OPENAI_SEARCH_KEY),
        "search_index": os.getenv(ENV_AZURE_OPENAI_SEARCH_INDEX),
        "audio_name": ENV_AZURE_OPENAI_AUDIO_NAME,
        "audio_model": ENV_OPENAI_AUDIO_MODEL,
        "dalle_name": ENV_AZURE_OPENAI_DALLE_NAME,
        "dalle_model": ENV_OPENAI_DALLE_MODEL,
        "chat_completion_gpt4_name": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_GPT4_NAME,
        "chat_completion_gpt4_model": ENV_OPENAI_CHAT_COMPLETIONS_GPT4_MODEL,
    }


@pytest.fixture
def client(api_type):
    if api_type == "azure":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type == "azuread":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["openai", "gpt_4_openai", "tts_openai"]:
        client = openai.OpenAI(
            api_key=os.getenv(ENV_OPENAI_KEY)
        )
    elif api_type in ["whisper_azure", "tts_azure"]:
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["whisper_azuread", "tts_azuread"]:
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["dalle_azure", "gpt_4_azure", "asst_azure"]:
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["dalle_azuread", "gpt_4_azuread", "asst_azuread"]:
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    return client


@pytest.fixture
def client_async(api_type):
    if api_type == "azure":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type == "azuread":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider_async(AsyncDefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["openai", "gpt_4_openai", "tts_openai"]:
        client = openai.AsyncOpenAI(
            api_key=os.getenv(ENV_OPENAI_KEY)
        )
    elif api_type in ["whisper_azure", "tts_azure"]:
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["whisper_azuread", "tts_azuread"]:
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider_async(AsyncDefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["dalle_azure", "gpt_4_azure", "asst_azure"]:
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type in ["dalle_azuread", "gpt_4_azuread", "asst_azuread"]:
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider_async(AsyncDefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    return client


def build_kwargs(args, api_type):
    test_feature = args[0].qualified_test_name
    if test_feature.startswith("test_audio"):
        if api_type in ["whisper_azure", "whisper_azuread"]:
            return {"model": ENV_AZURE_OPENAI_AUDIO_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_AUDIO_MODEL}
        elif api_type == "tts_openai":
            return {"model": ENV_OPENAI_TTS_MODEL}
        elif api_type in ["tts_azure", "tts_azuread"]:
            return {"model": ENV_AZURE_OPENAI_TTS_NAME}
    if test_feature.startswith("test_chat_completions") \
        or test_feature.startswith(("test_client", "test_models")):
        if api_type in ["azure", "azuread", "asst_azure"]:
            return {"model": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_CHAT_COMPLETIONS_MODEL}
        elif api_type in ["gpt_4_azure", "gpt_4_azuread"]:
            return {"model": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_GPT4_NAME}
        elif api_type == "gpt_4_openai":
            return {"model": ENV_OPENAI_CHAT_COMPLETIONS_GPT4_MODEL}
    if test_feature.startswith("test_completions"):
        if api_type in ["azure", "azuread"]:
            return {"model": ENV_AZURE_OPENAI_COMPLETIONS_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_COMPLETIONS_MODEL}
    if test_feature.startswith("test_embeddings"):
        if api_type in ["azure", "azuread"]:
            return {"model": ENV_AZURE_OPENAI_EMBEDDINGS_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_EMBEDDINGS_MODEL}
    if test_feature.startswith("test_dall_e"):
        if api_type in ["dalle_azure", "dalle_azuread"]:
            return {"model": ENV_AZURE_OPENAI_DALLE_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_DALLE_MODEL}
    if test_feature.startswith("test_assistants"):
        if api_type in ["asst_azure", "asst_azuread"]:
            return {"model": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_GPT4_NAME}
        elif api_type == "gpt_4_openai":
            return {"model": ENV_OPENAI_CHAT_COMPLETIONS_GPT4_MODEL}
    if test_feature.startswith(("test_module_client", "test_cli")):
        return {}
    raise ValueError(f"Test feature: {test_feature} needs to have its kwargs configured.")


def configure_async(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        client_async = kwargs.pop("client_async")
        azure_openai_creds = kwargs.pop("azure_openai_creds")
        kwargs = build_kwargs(args, api_type)
        try:
            return await f(*args, client_async=client_async, azure_openai_creds=azure_openai_creds, api_type=api_type, **kwargs)
        except openai.RateLimitError:
            pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Rate limit reached.")

    return wrapper


def configure(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        client = kwargs.pop("client")
        azure_openai_creds = kwargs.pop("azure_openai_creds")
        kwargs = build_kwargs(args, api_type)
        try:
            return f(*args, client=client, azure_openai_creds=azure_openai_creds, api_type=api_type, **kwargs)
        except openai.RateLimitError:
            pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Rate limit reached.")

    return wrapper



@contextlib.contextmanager
def reload():
    try:
        importlib.reload(openai)
        yield
    finally:
        importlib.reload(openai)
