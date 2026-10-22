# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from devtools_testutils.sanitizers import add_header_regex_sanitizer


# Environment variable keys
ENV_METRICS_RESOURCE_ID = "METRICS_RESOURCE_ID"
ENV_SUBSCRIPTION_ID = "MONITOR_SUBSCRIPTION_ID"
ENV_TENANT_ID = "AZURE_MONITOR_TENANT_ID"

# Fake values
TEST_ID = "00000000-0000-0000-0000-000000000000"
TEST_RESOURCE_ID = "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/fake-resource"
TEST_TABLE_NAME = "test-table"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_METRICS_RESOURCE_ID: TEST_RESOURCE_ID,
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")


@pytest.fixture(scope="session")
def monitor_info(environment_variables):
    yield {
        "metrics_resource_id": environment_variables.get(ENV_METRICS_RESOURCE_ID),
    }
