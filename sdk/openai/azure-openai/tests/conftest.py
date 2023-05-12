# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils.sanitizers import add_header_regex_sanitizer, add_oauth_response_sanitizer


# Environment variable keys
ENV_AZURE_OPENAI_ENDPOINT = "AZURE_OPENAI_ENDPOINT"
ENV_AZURE_OPENAI_KEY = "AZURE_OPENAI_KEY"
ENV_AZURE_OPENAI_API_VERSION = "AZURE_OPENAI_API_VERSION"
ENV_AZURE_OPENAI_COMPLETIONS_NAME = "AZURE_OPENAI_COMPLETIONS_NAME"
ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME = "AZURE_OPENAI_CHAT_COMPLETIONS_NAME"
ENV_AZURE_OPENAI_EMBEDDINGS_NAME = "AZURE_OPENAI_EMBEDDINGS_NAME"
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

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
        ENV_CLIENT_SECRET: TEST_ID
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")


@pytest.fixture(scope="session")
def azure_openai_creds(environment_variables):
    yield {
        "endpoint": environment_variables.get(ENV_AZURE_OPENAI_ENDPOINT).rstrip("/"),
        "key": environment_variables.get(ENV_AZURE_OPENAI_KEY),
        "api_version": environment_variables.get(ENV_AZURE_OPENAI_API_VERSION),
        "completions_name": environment_variables.get(ENV_AZURE_OPENAI_COMPLETIONS_NAME),
        "chat_completions_name": environment_variables.get(ENV_AZURE_OPENAI_CHAT_COMPLETIONS_NAME),
        "embeddings_name": environment_variables.get(ENV_AZURE_OPENAI_EMBEDDINGS_NAME),
    }
