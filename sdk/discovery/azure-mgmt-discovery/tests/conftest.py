# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Pytest configuration for azure-mgmt-discovery tests.

Management SDK tests run as live-only tests (no recordings needed).
"""
import os
import pytest
from dotenv import load_dotenv
from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
)

load_dotenv()


# For security, please avoid recording sensitive identity information
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    """Add sanitizers to remove sensitive information."""
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    client_id = os.environ.get("AZURE_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_secret, value="00000000-0000-0000-0000-000000000000")
    add_header_regex_sanitizer(key="Authorization", value="Sanitized")
