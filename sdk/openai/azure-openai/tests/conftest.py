# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
import requests
import aiohttp
import yarl
import functools
import openai
from devtools_testutils.sanitizers import add_header_regex_sanitizer, add_oauth_response_sanitizer
from azure.identity import DefaultAzureCredential


# for pytest.parametrize
ALL = ["azure", "azuread", "openai"]
AZURE = "azure"
OPENAI = "openai"
AZURE_AD = "azuread"

# Environment variable keys
ENV_AZURE_OPENAI_ENDPOINT = "AZURE_OPENAI_ENDPOINT"
ENV_AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
ENV_AZURE_OPENAI_WHISPER_ENDPOINT = "AZURE_OPENAI_WHISPER_ENDPOINT"
ENV_AZURE_OPENAI_WHISPER_KEY = "AZURE_OPENAI_WHISPER_KEY"
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"
ENV_AZURE_OPENAI_SEARCH_ENDPOINT = "AZURE_OPENAI_SEARCH_ENDPOINT"
ENV_AZURE_OPENAI_SEARCH_KEY = "AZURE_OPENAI_SEARCH_KEY"
ENV_AZURE_OPENAI_SEARCH_INDEX = "AZURE_OPENAI_SEARCH_INDEX"

ENV_AZURE_OPENAI_API_VERSION = "2023-09-01-preview"
ENV_AZURE_OPENAI_COMPLETIONS_NAME = "text-davinci-003"
ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME = "gpt-35-turbo-16k"
ENV_AZURE_OPENAI_EMBEDDINGS_NAME = "text-embedding-ada-002"
ENV_AZURE_OPENAI_AUDIO_NAME = "whisper-deployment"

ENV_OPENAI_KEY = "OPENAI_KEY"
ENV_OPENAI_COMPLETIONS_MODEL = "text-davinci-003"
ENV_OPENAI_CHAT_COMPLETIONS_MODEL = "gpt-3.5-turbo"
ENV_OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"
ENV_OPENAI_AUDIO_MODEL = "whisper-1"

# Fake values
TEST_ENDPOINT = "https://test-resource.openai.azure.com/"
TEST_KEY = "0000000000000000"
TEST_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_AZURE_OPENAI_ENDPOINT: TEST_ENDPOINT,
        ENV_AZURE_OPENAI_KEY: TEST_KEY,
        ENV_AZURE_OPENAI_WHISPER_ENDPOINT: TEST_ENDPOINT,
        ENV_AZURE_OPENAI_WHISPER_KEY: TEST_KEY,
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
    }


def configure_api_type(api_type, whisper=False, **kwargs):
    if api_type == "azure":
        if whisper:
            openai.api_base = os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT).rstrip("/")
            openai.api_key = os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY)
        else:
            openai.api_base = os.getenv(ENV_AZURE_OPENAI_ENDPOINT).rstrip("/")
            openai.api_key = os.getenv(ENV_AZURE_OPENAI_KEY)
        openai.api_type = "azure"
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION
    elif api_type == "azuread":
        if whisper:
            openai.api_base = os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT).rstrip("/")
        else:
            openai.api_base = os.getenv(ENV_AZURE_OPENAI_ENDPOINT).rstrip("/")
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        openai.api_type = "azuread"
        openai.api_key = token.token
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION
    elif api_type == "openai":
        openai.api_base = "https://api.openai.com/v1"
        openai.api_type = "openai"
        openai.api_key = os.getenv(ENV_OPENAI_KEY)
        openai.api_version = None


def configure_async(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        whisper = args[0].qualified_test_name.startswith("test_audio")
        configure_api_type(api_type, whisper=whisper, **kwargs)
        try:
            return await f(*args, api_type=api_type, **kwargs)
        except openai.error.RateLimitError:
            pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Rate limit reached.")

    return wrapper


def configure(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        whisper = args[0].qualified_test_name.startswith("test_audio")
        configure_api_type(api_type, whisper=whisper, **kwargs)
        try:
            return f(*args, api_type=api_type, **kwargs)
        except openai.error.RateLimitError:
            pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Rate limit reached.")

    return wrapper


def setup_adapter(deployment_id):

    class CustomAdapter(requests.adapters.HTTPAdapter):

        def send(self, request, **kwargs):
            request.url = f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}"
            return super().send(request, **kwargs)

    session = requests.Session()

    session.mount(
        prefix=f"{openai.api_base}/openai/deployments/{deployment_id}",
        adapter=CustomAdapter()
    )

    openai.requestssession = session


def setup_adapter_async(deployment_id):

    class CustomAdapterAsync(aiohttp.ClientRequest):

        async def send(self, conn) -> aiohttp.ClientResponse:
            self.url = yarl.URL(f"{openai.api_base}/openai/deployments/{deployment_id}/extensions/chat/completions?api-version={openai.api_version}")
            return await super().send(conn)
    
    session = aiohttp.ClientSession(request_class=CustomAdapterAsync)
    openai.aiosession.set(session)
