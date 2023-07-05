# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import pytest
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
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

ENV_AZURE_OPENAI_API_VERSION = "2023-06-01-preview"
ENV_AZURE_OPENAI_COMPLETIONS_NAME = "text-davinci-003"
ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME = "gpt-35-turbo"
ENV_AZURE_OPENAI_EMBEDDINGS_NAME = "text-embedding-ada-002"

ENV_OPENAI_KEY = "OPENAI_KEY"
ENV_OPENAI_COMPLETIONS_MODEL = "text-davinci-003"
ENV_OPENAI_CHAT_COMPLETIONS_MODEL = "gpt-3.5-turbo"
ENV_OPENAI_EMBEDDINGS_MODEL = "text-embedding-ada-002"

# Fake values
TEST_ENDPOINT = "https://test-resource.openai.azure.com/"
TEST_KEY = "0000000000000000"
TEST_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_AZURE_OPENAI_ENDPOINT: TEST_ENDPOINT,
        ENV_AZURE_OPENAI_KEY: TEST_KEY,
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
        ENV_CLIENT_ID: TEST_ID,
        ENV_CLIENT_SECRET: TEST_ID,
        ENV_OPENAI_KEY: TEST_KEY
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
    }


def configure(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        api_type = kwargs.pop("api_type")
        if api_type == "azure":
            openai.api_base = os.getenv(ENV_AZURE_OPENAI_ENDPOINT).rstrip("/")
            openai.api_type = "azure"
            openai.api_key = os.getenv(ENV_AZURE_OPENAI_KEY)
            openai.api_version = ENV_AZURE_OPENAI_API_VERSION
        elif api_type == "azuread":
            credential = DefaultAzureCredential()
            token = credential.get_token("https://cognitiveservices.azure.com/.default")
            openai.api_base = os.getenv(ENV_AZURE_OPENAI_ENDPOINT).rstrip("/")
            openai.api_type = "azuread"
            openai.api_key = token.token
            openai.api_version = ENV_AZURE_OPENAI_API_VERSION
        elif api_type == "openai":
            openai.api_base = "https://api.openai.com/v1"
            openai.api_type = "openai"
            openai.api_key = os.getenv(ENV_OPENAI_KEY)
            openai.api_version = None

        return f(*args, api_type=api_type, **kwargs)

    return wrapper
