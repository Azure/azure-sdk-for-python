# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Pytest configuration for azure-ai-discovery tests.

This module configures the test environment for both recorded (playback) and live tests.
Uses devtools_testutils for Azure SDK test infrastructure.
"""
import os
import pytest
from dotenv import load_dotenv

load_dotenv()


# Recorded test infrastructure imports
from devtools_testutils import (
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    add_body_key_sanitizer,
    remove_batch_sanitizers,
    test_proxy,
)


# Environment Variables for test configuration
# Set AZURE_TEST_RUN_LIVE=true to run live tests
# Otherwise tests run in playback mode using recorded responses


# Add sanitizers to remove sensitive information from recordings
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    """Add sanitizers to remove sensitive information from recordings."""
    # Sanitize subscription IDs
    add_general_regex_sanitizer(
        regex=r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        value="00000000-0000-0000-0000-000000000000",
    )
    # Sanitize authorization headers
    add_header_regex_sanitizer(key="Authorization", value="Bearer [REDACTED]")
    # Sanitize x-ms-client-request-id
    add_header_regex_sanitizer(key="x-ms-client-request-id", value="00000000-0000-0000-0000-000000000000")
    # Sanitize workspace endpoints in URLs
    add_general_regex_sanitizer(
        regex=r"https://[a-zA-Z0-9-]+\.workspace[a-zA-Z0-9-]*\.discovery\.azure\.com",
        value="https://test-workspace.workspace.discovery.azure.com",
    )
    # Sanitize bookshelf endpoints in URLs
    add_general_regex_sanitizer(
        regex=r"https://[a-zA-Z0-9-]+\.bookshelf[a-zA-Z0-9-]*\.discovery\.azure\.com",
        value="https://test-bookshelf.bookshelf.discovery.azure.com",
    )
    # Sanitize bogus Location header (service returns https://example.com for LROs)
    # Replace with empty string so the LRO poller uses operation-location instead
    add_header_regex_sanitizer(key="Location", regex=r"^https://example\.com$", value="")
    # Remove the default body key sanitizer for "$..name" (AZSDK3493).
    # It replaces name values with "Sanitized", conflicting with the UUID regex
    # sanitizer that already handles name fields containing UUIDs in URLs.
    remove_batch_sanitizers(["AZSDK3493"])


@pytest.fixture(scope="session")
def subscription_id():
    """Get subscription ID from environment or use default test subscription."""
    return os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")


@pytest.fixture(scope="session")
def resource_group():
    """Get resource group from environment or use default test resource group."""
    return os.environ.get("AZURE_DISCOVERY_RESOURCE_GROUP", "test-rg")


@pytest.fixture(scope="session")
def workspace_name():
    """Get workspace name from environment or use default test workspace."""
    return os.environ.get("AZURE_DISCOVERY_WORKSPACE_NAME", "test-workspace")


@pytest.fixture(scope="session")
def project_name():
    """Get project name from environment or use default test project."""
    return os.environ.get("AZURE_DISCOVERY_PROJECT_NAME", "test-project")


@pytest.fixture(scope="session")
def bookshelf_name():
    """Provide Discovery bookshelf name."""
    return os.environ.get("AZURE_DISCOVERY_BOOKSHELF_NAME", "test-bookshelf")
