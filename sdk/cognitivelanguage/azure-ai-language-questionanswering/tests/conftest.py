# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils.sanitizers import (
    add_header_regex_sanitizer,
    add_oauth_response_sanitizer,
    remove_batch_sanitizers
)


# Environment variable keys
ENV_ENDPOINT = "AZURE_QUESTIONANSWERING_ENDPOINT"
ENV_KEY = "AZURE_QUESTIONANSWERING_KEY"
ENV_PROJECT = "AZURE_QUESTIONANSWERING_PROJECT"
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

# Fake values
TEST_ENDPOINT = "https://test-resource.api.cognitive.microsoft.com/"
TEST_KEY = "0000000000000000"
TEST_PROJECT = "test-project"
TEST_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_ENDPOINT: TEST_ENDPOINT,
        ENV_KEY: TEST_KEY,
        ENV_PROJECT: TEST_PROJECT,
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
        ENV_CLIENT_ID: TEST_ID,
        ENV_CLIENT_SECRET: TEST_ID
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    remove_batch_sanitizers(["AZSDK3430"])


@pytest.fixture(scope="session")
def qna_creds(environment_variables):
    yield {
        "qna_endpoint": environment_variables.get(ENV_ENDPOINT),
        "qna_key": environment_variables.get(ENV_KEY),
        "qna_project": environment_variables.get(ENV_PROJECT)
    }
