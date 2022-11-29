# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import pytest

from devtools_testutils.sanitizers import add_header_regex_sanitizer


# Environment variable keys
ENV_METRICS_RESOURCE_ID = "METRICS_RESOURCE_ID"
ENV_SUBSCRIPTION_ID = "AZURE_SUBSCRIPTION_ID"
ENV_WORKSPACE_ID = "AZURE_MONITOR_WORKSPACE_ID"
ENV_SECONDARY_WORKSPACE_ID = "AZURE_MONITOR_SECONDARY_WORKSPACE_ID"
ENV_DCR_ID = "AZURE_MONITOR_DCR_ID"
ENV_TABLE_NAME = "AZURE_MONITOR_TABLE_NAME"
ENV_TENANT_ID = "AZURE_TENANT_ID"
ENV_CLIENT_ID = "AZURE_CLIENT_ID"
ENV_CLIENT_SECRET = "AZURE_CLIENT_SECRET"

# Fake values
TEST_ID = "00000000-0000-0000-0000-000000000000"
TEST_RESOURCE_ID = "/subscriptions/fake-subscription/resourceGroups/fake-resource"
TEST_TABLE_NAME = "test-table"


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy, environment_variables):
    sanitization_mapping = {
        ENV_METRICS_RESOURCE_ID: TEST_RESOURCE_ID,
        ENV_SUBSCRIPTION_ID: TEST_ID,
        ENV_WORKSPACE_ID: TEST_ID,
        ENV_SECONDARY_WORKSPACE_ID: TEST_ID,
        ENV_TENANT_ID: TEST_ID,
        ENV_CLIENT_ID: TEST_ID,
        ENV_CLIENT_SECRET: TEST_ID,
        ENV_TABLE_NAME: TEST_TABLE_NAME,
        ENV_DCR_ID: TEST_ID
    }
    environment_variables.sanitize_batch(sanitization_mapping)
    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")


@pytest.fixture(scope="session")
def monitor_info(environment_variables):
    yield {
        "metrics_resource_id": environment_variables.get(ENV_METRICS_RESOURCE_ID),
        "workspace_id": environment_variables.get(ENV_WORKSPACE_ID),
        "secondary_workspace_id": environment_variables.get(ENV_SECONDARY_WORKSPACE_ID),
        "table_name": environment_variables.get(ENV_TABLE_NAME),
        "client_id": environment_variables.get(ENV_CLIENT_ID),
        "tenant_id": environment_variables.get(ENV_TENANT_ID)
    }
