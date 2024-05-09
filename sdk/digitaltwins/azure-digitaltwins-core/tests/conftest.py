# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from devtools_testutils.sanitizers import (
    add_body_key_sanitizer,
    add_header_regex_sanitizer,
    add_oauth_response_sanitizer,
    add_remove_header_sanitizer,
    remove_batch_sanitizers,
)

# Environment variable keys
ENV_URL = "AZURE_DIGITALTWINS_URL"
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

# Fake values
TEST_URL = "https://fake.api.wcus.digitaltwins.azure.net"
TEST_ID = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_URL: TEST_URL,
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
        ENV_CLIENT_ID: TEST_ID,
        ENV_CLIENT_SECRET: TEST_ID
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_remove_header_sanitizer(headers="Telemetry-Source-Time, Message-Id")
    add_body_key_sanitizer(json_path="AccessToken", value="fake.eyJleHAiOjIxNDc0ODM2NDd9.fake")
    add_oauth_response_sanitizer()
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")

    # Remove the following sanitizers since certain fields are needed in tests and are non-sensitive:
    #  - AZSDK3430: $..id
    #  - AZSDK3493: $..name
    remove_batch_sanitizers(["AZSDK3430", "AZSDK3493"])


@pytest.fixture(scope="session")
def digitaltwin(environment_variables):
    yield {
        "endpoint": environment_variables.get(ENV_URL),
    }
