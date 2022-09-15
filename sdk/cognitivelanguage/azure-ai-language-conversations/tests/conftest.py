# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from devtools_testutils.sanitizers import add_header_regex_sanitizer, add_oauth_response_sanitizer


# Environment variable keys
ENV_ENDPOINT = "AZURE_CONVERSATIONS_ENDPOINT"
ENV_KEY = "AZURE_CONVERSATIONS_KEY"
ENV_PROJECT_NAME = "AZURE_CONVERSATIONS_PROJECT_NAME"
ENV_DEPLOYMENT_NAME = "AZURE_CONVERSATIONS_DEPLOYMENT_NAME"
ENV_WORKFLOW_PROJECT_NAME = "AZURE_CONVERSATIONS_WORKFLOW_PROJECT_NAME"
ENV_WORKFLOW_DEPLOYMENT_NAME = "AZURE_CONVERSATIONS_WORKFLOW_DEPLOYMENT_NAME"
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

# Fake values
TEST_ENDPOINT = "https://test-resource.api.cognitive.microsoft.com/"
TEST_KEY = "0000000000000000"
TEST_CONV_PROJECT_NAME = "conv_test"
TEST_CONV_DEPLOYMENT_NAME = "dep_test"
TEST_ORCH_PROJECT_NAME = "orch_test"
TEST_ORCH_DEPLOYMENT_NAME = "dep_test"
TEST_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_ENDPOINT: TEST_ENDPOINT,
        ENV_KEY: TEST_KEY,
        ENV_PROJECT_NAME: TEST_CONV_PROJECT_NAME,
        ENV_DEPLOYMENT_NAME: TEST_CONV_DEPLOYMENT_NAME,
        ENV_WORKFLOW_PROJECT_NAME: TEST_ORCH_PROJECT_NAME,
        ENV_WORKFLOW_DEPLOYMENT_NAME: TEST_ORCH_DEPLOYMENT_NAME,
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
        ENV_CLIENT_ID: TEST_ID,
        ENV_CLIENT_SECRET: TEST_ID
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")


@pytest.fixture(scope="session")
def conversation_creds(environment_variables):
    yield {
        "endpoint": environment_variables.get(ENV_ENDPOINT).rstrip("/"),
        "key": environment_variables.get(ENV_KEY),
        "conv_project_name": environment_variables.get(ENV_PROJECT_NAME),
        "conv_deployment_name": environment_variables.get(ENV_DEPLOYMENT_NAME),
        "orch_project_name": environment_variables.get(ENV_WORKFLOW_PROJECT_NAME),
        "orch_deployment_name": environment_variables.get(ENV_WORKFLOW_DEPLOYMENT_NAME)
    }
