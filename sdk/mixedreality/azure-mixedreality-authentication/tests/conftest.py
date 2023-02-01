# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import pytest

from azure.core.credentials import AzureKeyCredential
from devtools_testutils.sanitizers import add_body_key_sanitizer, add_remove_header_sanitizer


# Environment variable keys
ENV_ACCOUNT_DOMAIN = "MIXEDREALITY_ACCOUNT_DOMAIN"
ENV_ACCOUNT_ID = "MIXEDREALITY_ACCOUNT_ID"
ENV_ACCOUNT_KEY = "MIXEDREALITY_ACCOUNT_KEY"

# Fake values
TEST_ACCOUNT_DOMAIN = "mixedreality.azure.com"
TEST_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"
TEST_ACCOUNT_KEY = "fakekey"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_ACCOUNT_DOMAIN: TEST_ACCOUNT_DOMAIN,
        ENV_ACCOUNT_ID: TEST_ACCOUNT_ID,
        ENV_ACCOUNT_KEY: TEST_ACCOUNT_KEY
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_remove_header_sanitizer(headers="X-MRC-CV")
    # Replace AccessToken with fake JWT.
    add_body_key_sanitizer(json_path="AccessToken", value="fake.eyJleHAiOjIxNDc0ODM2NDd9.fake")


@pytest.fixture(scope="session")
def account_info(environment_variables):
    yield {
        "account_domain": environment_variables.get(ENV_ACCOUNT_DOMAIN),
        "account_id": environment_variables.get(ENV_ACCOUNT_ID),
        "key_credential": AzureKeyCredential(environment_variables.get(ENV_ACCOUNT_KEY))
    }
