# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import time
import asyncio
import json
import httpx
import os
import pytest
import importlib
import contextlib
import requests
import aiohttp
import yarl
import functools
import openai
from devtools_testutils.sanitizers import add_header_regex_sanitizer, add_oauth_response_sanitizer
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.identity.aio import (
    DefaultAzureCredential as AsyncDefaultAzureCredential,
    get_bearer_token_provider as get_bearer_token_provider_async,
)

# controls whether we run tests against v0 or v1. Options: v0 or v1. Default: v1
ENV_OPENAI_TEST_MODE = "OPENAI_TEST_MODE"

# for pytest.parametrize
ALL = ["azure", "azuread", "openai"]
AZURE = "azure"
OPENAI = "openai"
AZURE_AD = "azuread"
WHISPER_AZURE = "whisper_azure"
WHISPER_AZURE_AD = "whisper_azuread"
WHISPER_ALL = ["whisper_azure", "whisper_azuread", "openai"]
DALLE_AZURE = "dalle_azure"

# Environment variable keys
ENV_AZURE_OPENAI_ENDPOINT = "AZ_OPENAI_ENDPOINT"
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
ENV_AZURE_OPENAI_AUDIO_NAME = "whisper"

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

# openai>=1.0.0 ---------------------------------------------------------------------------

class CustomHTTPTransport(httpx.HTTPTransport):
    """Temp stop-gap support for DALL-E"""
    def handle_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        if "images/generations" in request.url.path and request.url.params[
            "api-version"
        ] in [
            "2023-06-01-preview",
            "2023-07-01-preview",
            "2023-08-01-preview",
            "2023-09-01-preview",
            "2023-10-01-preview",
        ]:
            request.url = request.url.copy_with(path="/openai/images/generations:submit")
            response = super().handle_request(request)
            operation_location_url = response.headers["operation-location"]
            request.url = httpx.URL(operation_location_url)
            request.method = "GET"
            response = super().handle_request(request)
            response.read()

            timeout_secs: int = 120
            start_time = time.time()
            while response.json()["status"] not in ["succeeded", "failed"]:
                if time.time() - start_time > timeout_secs:
                    timeout = {"error": {"code": "Timeout", "message": "Operation polling timed out."}}
                    return httpx.Response(
                        status_code=400,
                        headers=response.headers,
                        content=json.dumps(timeout).encode("utf-8"),
                        request=request,
                    )

                time.sleep(int(response.headers.get("retry-after")) or 10)
                response = super().handle_request(request)
                response.read()

            if response.json()["status"] == "failed":
                error_data = response.json()
                return httpx.Response(
                    status_code=400,
                    headers=response.headers,
                    content=json.dumps(error_data).encode("utf-8"),
                    request=request,
                )

            result = response.json()["result"]
            return httpx.Response(
                status_code=200,
                headers=response.headers,
                content=json.dumps(result).encode("utf-8"),
                request=request,
            )
        return super().handle_request(request)


class AsyncCustomHTTPTransport(httpx.AsyncHTTPTransport):
    """Temp stop-gap support for DALL-E"""
    async def handle_async_request(
        self,
        request: httpx.Request,
    ) -> httpx.Response:
        if "images/generations" in request.url.path and request.url.params[
            "api-version"
        ] in [
            "2023-06-01-preview",
            "2023-07-01-preview",
            "2023-08-01-preview",
            "2023-09-01-preview",
            "2023-10-01-preview",
        ]:
            request.url = request.url.copy_with(path="/openai/images/generations:submit")
            response = await super().handle_async_request(request)
            operation_location_url = response.headers["operation-location"]
            request.url = httpx.URL(operation_location_url)
            request.method = "GET"
            response = await super().handle_async_request(request)
            await response.aread()

            timeout_secs: int = 120
            start_time = time.time()
            while response.json()["status"] not in ["succeeded", "failed"]:
                if time.time() - start_time > timeout_secs:
                    timeout = {"error": {"code": "Timeout", "message": "Operation polling timed out."}}
                    return httpx.Response(
                        status_code=400,
                        headers=response.headers,
                        content=json.dumps(timeout).encode("utf-8"),
                        request=request,
                    )

                await asyncio.sleep(int(response.headers.get("retry-after")) or 10)
                response = await super().handle_async_request(request)
                await response.aread()

            if response.json()["status"] == "failed":
                error_data = response.json()
                return httpx.Response(
                    status_code=400,
                    headers=response.headers,
                    content=json.dumps(error_data).encode("utf-8"),
                    request=request,
                )

            result = response.json()["result"]
            return httpx.Response(
                status_code=200,
                headers=response.headers,
                content=json.dumps(result).encode("utf-8"),
                request=request,
            )
        return await super().handle_async_request(request)

@pytest.fixture
def client(api_type):
    if os.getenv(ENV_OPENAI_TEST_MODE, "v1") != "v1":
        pytest.skip("Skipping - tests set to run against v1.")
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
    elif api_type == "openai":
        client = openai.OpenAI(
            api_key=os.getenv(ENV_OPENAI_KEY)
        )
    elif api_type == "whisper_azure":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type == "whisper_azuread":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider(DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type == "dalle_azure":
        client = openai.AzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
            http_client=httpx.Client(transport=CustomHTTPTransport())
        )

    return client


@pytest.fixture
def client_async(api_type):
    if os.getenv(ENV_OPENAI_TEST_MODE, "v1") != "v1":
        pytest.skip("Skipping - tests set to run against v1.")
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
    elif api_type == "openai":
        client = openai.AsyncOpenAI(
            api_key=os.getenv(ENV_OPENAI_KEY)
        )
    elif api_type == "whisper_azure":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type == "whisper_azuread":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT),
            azure_ad_token_provider=get_bearer_token_provider_async(AsyncDefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
        )
    elif api_type == "dalle_azure":
        client = openai.AsyncAzureOpenAI(
            azure_endpoint=os.getenv(ENV_AZURE_OPENAI_ENDPOINT),
            api_key=os.getenv(ENV_AZURE_OPENAI_KEY),
            api_version=ENV_AZURE_OPENAI_API_VERSION,
            http_client=httpx.AsyncClient(transport=AsyncCustomHTTPTransport())
        )

    return client


def build_kwargs(args, api_type):
    test_feature = args[0].qualified_test_name
    if test_feature.startswith("test_audio"):
        if api_type in ["whisper_azure", "whisper_azuread"]:
            return {"model": ENV_AZURE_OPENAI_AUDIO_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_AUDIO_MODEL}
    if test_feature.startswith("test_chat_completions") \
        or test_feature.startswith(("test_client", "test_models")):
        if api_type in ["azure", "azuread"]:
            return {"model": ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME}
        elif api_type == "openai":
            return {"model": ENV_OPENAI_CHAT_COMPLETIONS_MODEL}
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
    if test_feature.startswith(("test_dall_e", "test_module_client", "test_cli")):
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


# openai<1.0.0 ---------------------------------------------------------------------------

@pytest.fixture
def set_vars(api_type):
    if os.getenv(ENV_OPENAI_TEST_MODE, "v1") != "v0":
        pytest.skip("Skipping - tests set to run against v0.")

    if api_type == "azure":
        openai.api_base = os.getenv(ENV_AZURE_OPENAI_ENDPOINT).rstrip("/")
        openai.api_key = os.getenv(ENV_AZURE_OPENAI_KEY)
        openai.api_type = "azure"
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION
    elif api_type == "azuread":
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
    elif api_type == "whisper_azure":
        openai.api_base = os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT).rstrip("/")
        openai.api_key = os.getenv(ENV_AZURE_OPENAI_WHISPER_KEY)
        openai.api_type = "azure"
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION
    elif api_type == "whisper_azuread":
        openai.api_base = os.getenv(ENV_AZURE_OPENAI_WHISPER_ENDPOINT).rstrip("/")
        credential = DefaultAzureCredential()
        token = credential.get_token("https://cognitiveservices.azure.com/.default")
        openai.api_type = "azuread"
        openai.api_key = token.token
        openai.api_version = ENV_AZURE_OPENAI_API_VERSION


def configure_v0_async(f):
    @functools.wraps(f)
    async def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        set_vars = kwargs.pop("set_vars")
        azure_openai_creds = kwargs.pop("azure_openai_creds")
        try:
            return await f(*args, set_vars=set_vars, azure_openai_creds=azure_openai_creds, api_type=api_type, **kwargs)
        except openai.error.RateLimitError:
            pytest.skip(f"{str(f).split(' ')[1]}[{api_type}]: Skipping - Rate limit reached.")

    return wrapper


def configure_v0(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        set_vars = kwargs.pop("set_vars")
        azure_openai_creds = kwargs.pop("azure_openai_creds")
        try:
            return f(*args, set_vars=set_vars, azure_openai_creds=azure_openai_creds, api_type=api_type, **kwargs)
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
