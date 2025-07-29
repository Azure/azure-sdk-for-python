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
from azure.identity import get_bearer_token_provider
from azure.identity.aio import (
    get_bearer_token_provider as get_bearer_token_provider_async,
)
from ci_tools.variables import in_ci
from devtools_testutils import get_credential


# for pytest.parametrize
GA = "2024-10-21"
PREVIEW = "2025-03-01-preview"
LATEST = PREVIEW

AZURE = "azure"
OPENAI = "openai"
AZURE_KEY = "azure_key"
WHISPER_AZURE = "whisper_azure"
TTS_OPENAI = "tts_openai"
TTS_AZURE = "tts_azure"
DALLE_AZURE = "dalle_azure"
GPT_4_AZURE = "gpt_4_azure"
GPT_4_OPENAI = "gpt_4_openai"
ASST_AZURE = "asst_azure"

# Environment variable keys
ENV_AZURE_OPENAI_ENDPOINT = "AZ_OPENAI_ENDPOINT"
ENV_AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT = "AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT"
ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT = "AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT"
ENV_AZURE_OPENAI_SWEDENCENTRAL_KEY = "AZURE_OPENAI_SWEDENCENTRAL_KEY"
ENV_AZURE_OPENAI_SEARCH_ENDPOINT = "AZURE_OPENAI_SEARCH_ENDPOINT"
ENV_AZURE_OPENAI_SEARCH_INDEX = "AZURE_OPENAI_SEARCH_INDEX"

ENV_AZURE_OPENAI_COMPLETIONS_NAME = "gpt-35-turbo-instruct"
ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME = "gpt-35-turbo"
ENV_AZURE_OPENAI_EMBEDDINGS_NAME = "text-embedding-ada-002"
ENV_AZURE_OPENAI_AUDIO_NAME = "whisper"
ENV_AZURE_OPENAI_DALLE_NAME = "dall-e-3"
ENV_AZURE_OPENAI_CHAT_COMPLETIONS_GPT4_NAME = "gpt-4o-mini"
ENV_AZURE_OPENAI_REALTIME_NAME = "gpt-4o-mini-realtime-preview-1217"
ENV_AZURE_OPENAI_TTS_NAME = "tts"

ENV_OPENAI_KEY = "OPENAI_KEY"
ENV_OPENAI_COMPLETIONS_MODEL = "gpt-3.5-turbo-instruct"
ENV_OPENAI_CHAT_COMPLETIONS_MODEL = "gpt-3.5-turbo"
ENV_OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
ENV_OPENAI_AUDIO_MODEL = "whisper-1"
ENV_OPENAI_DALLE_MODEL = "dall-e-3"
ENV_OPENAI_CHAT_COMPLETIONS_GPT4_MODEL = "gpt-4o-mini-2024-07-18"
ENV_OPENAI_REALTIME_NAME = "gpt-4o-mini-realtime-preview-2024-10-01"
ENV_OPENAI_TTS_MODEL = "tts-1"


def skip_openai_test(api_type) -> bool:
    return in_ci() and "openai" in api_type and "tests-weekly" not in os.getenv("SYSTEM_DEFINITIONNAME", "")


@pytest.fixture
def client(api_type, api_version):
    if skip_openai_test(api_type):
        pytest.skip("Skipping openai tests - they only run on tests-weekly.")

    if api_type == "azure":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider(get_credential(), "https://cognitiveservices.azure.com/.default"),
            api_version=api_version,
        )
    elif api_type == "azure_key":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=api_version,
        )
    elif api_type in ["openai", "gpt_4_openai", "tts_openai"]:
        client = openai.OpenAI(
            api_key=os.getenv(ENV_OPENAI_KEY)
        )
    elif api_type in ["whisper_azure", "tts_azure"]:
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider(get_credential(), "https://cognitiveservices.azure.com/.default"),
            api_version=api_version,
        )
    elif api_type in ["dalle_azure", "gpt_4_azure", "asst_azure"]:
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider(get_credential(), "https://cognitiveservices.azure.com/.default"),
            api_version=api_version,
        )
    return client


@pytest.fixture
def client_async(api_type, api_version):
    if skip_openai_test(api_type):
        pytest.skip("Skipping openai tests - they only run on tests-weekly.")

    if api_type == "azure":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider_async(get_credential(is_async=True), "https://cognitiveservices.azure.com/.default"),
            api_version=api_version,
        )
    elif api_type == "azure_key":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=api_version,
        )
    elif api_type in ["openai", "gpt_4_openai", "tts_openai"]:
        client = openai.AsyncOpenAI(
            api_key=os.getenv(ENV_OPENAI_KEY)
        )
    elif api_type in ["whisper_azure", "tts_azure"]:
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_NORTHCENTRALUS_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider_async(get_credential(is_async=True), "https://cognitiveservices.azure.com/.default"),
            api_version=api_version,
        )
    elif api_type in ["dalle_azure", "gpt_4_azure", "asst_azure"]:
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_SWEDENCENTRAL_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider_async(get_credential(is_async=True), "https://cognitiveservices.azure.com/.default"),
            api_version=api_version,
        )
    return client


def build_kwargs(args, api_type):
    test_feature = args[0].qualified_test_name
    if test_feature.startswith("test_audio"):
        if api_type in ["whisper_azure"]:
            return {"model": ENV_AZURE_OPENAI_AUDIO_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_AUDIO_MODEL}
        elif api_type == "tts_openai":
            return {"model": ENV_OPENAI_TTS_MODEL}
        elif api_type in ["tts_azure"]:
            return {"model": ENV_AZURE_OPENAI_TTS_NAME}
    if test_feature.startswith(
        ("test_client", "test_models", "test_chat_completions",
         "test_assistants", "test_responses", "test_vector_stores")
    ):
        if api_type in ["azure", "azure_key", "asst_azure"]:
            return {"model": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_CHAT_COMPLETIONS_MODEL}
        elif api_type in ["gpt_4_azure"]:
            return {"model": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_GPT4_NAME}
        elif api_type == "gpt_4_openai":
            return {"model": ENV_OPENAI_CHAT_COMPLETIONS_GPT4_MODEL}
    if test_feature.startswith("test_completions"):
        if api_type == "azure":
            return {"model": ENV_AZURE_OPENAI_COMPLETIONS_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_COMPLETIONS_MODEL}
    if test_feature.startswith("test_embeddings"):
        if api_type == "azure":
            return {"model": ENV_AZURE_OPENAI_EMBEDDINGS_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_EMBEDDINGS_MODEL}
    if test_feature.startswith("test_dall_e"):
        if api_type in ["dalle_azure"]:
            return {"model": ENV_AZURE_OPENAI_DALLE_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_DALLE_MODEL}
    if test_feature.startswith("test_realtime"):
        if api_type in ["gpt_4_azure"]:
            return {"model": ENV_AZURE_OPENAI_REALTIME_NAME}
        elif api_type == "gpt_4_openai":
            return {"model": ENV_OPENAI_REALTIME_NAME}
    if test_feature.startswith(("test_module_client", "test_cli")):
        return {}
    raise ValueError(f"Test feature: {test_feature} needs to have its kwargs configured.")


def configure_async(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        api_version = kwargs.pop("api_version")
        client_async = kwargs.pop("client_async")
        kwargs = build_kwargs(args, api_type)
        try:
            return await f(*args, client_async=client_async, api_type=api_type, api_version=api_version, **kwargs)
        except openai.RateLimitError:
            pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Rate limit reached.")
        except openai.BadRequestError as e:
            if e.body.get("code") == "content_policy_violation":
                pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Triggered content filter.")
            raise

    return wrapper


def configure(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        api_version = kwargs.pop("api_version")
        client = kwargs.pop("client")
        kwargs = build_kwargs(args, api_type)
        try:
            return f(*args, client=client, api_type=api_type, api_version=api_version, **kwargs)
        except openai.RateLimitError:
            pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Rate limit reached.")
        except openai.BadRequestError as e:
            if e.body.get("code") == "content_policy_violation":
                pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Triggered content filter.")
            raise

    return wrapper



@contextlib.contextmanager
def reload():
    try:
        importlib.reload(openai)
        yield
    finally:
        importlib.reload(openai)
