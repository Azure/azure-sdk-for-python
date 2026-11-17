# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Pytest configuration for azure-mgmt-discovery tests.

Live recording (AZURE_TEST_RUN_LIVE=true) reads the target read-path resources
from environment variables; in playback these fall back to sanitizer
placeholders that match the recordings. To re-record the read tests live, set:
  AZURE_SUBSCRIPTION_ID, AZURE_RESOURCE_GROUP, and the resource names
  DISCOVERY_WORKSPACE_NAME, DISCOVERY_SUPERCOMPUTER_NAME, DISCOVERY_NODE_POOL_NAME,
  DISCOVERY_STORAGE_CONTAINER_NAME, DISCOVERY_STORAGE_ASSET_NAME,
  DISCOVERY_BOOKSHELF_NAME, DISCOVERY_PROJECT_NAME, DISCOVERY_DEPLOYMENT_NAME,
  DISCOVERY_TOOL_NAME.
The write (create/update/delete) tests are playback-only and never run live.
"""

import os
import re
import pytest
from dotenv import load_dotenv
from devtools_testutils import (
    test_proxy,
    add_general_regex_sanitizer,
    add_header_regex_sanitizer,
    add_body_key_sanitizer,
    is_live,
)
from .testcase import AZURE_SUBSCRIPTION_ID

load_dotenv()


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "playback_only: test is recording-driven and must never run live "
        "(live execution would create, modify, or delete real resources).",
    )


def pytest_collection_modifyitems(items):
    """Enforce playback-only execution for write tests.

    The create/update/delete tests are driven by recordings and are not
    self-provisioning; running them live would mutate real resources in the
    configured subscription. Skip any test marked ``playback_only`` whenever
    the suite is run in live mode.
    """
    if not is_live():
        return
    skip_live = pytest.mark.skip(reason="playback-only: live execution would create/modify/delete real resources")
    for item in items:
        # Explicit marker, plus a name-based backstop so any create/update/delete
        # test is protected even if the marker is ever omitted.
        if "playback_only" in item.keywords or any(op in item.name for op in ("_create_", "_update_", "_delete_")):
            item.add_marker(skip_live)


@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    """Add sanitizers to remove sensitive information from recordings."""
    # Subscription, tenant, client credentials from env vars
    subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", AZURE_SUBSCRIPTION_ID)
    tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    client_id = os.environ.get("AZURE_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")

    add_general_regex_sanitizer(regex=subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=client_secret, value="00000000-0000-0000-0000-000000000000")
    # Any subscription id embedded in URIs or response bodies (e.g. a backend
    # reference such as a tool's LOGP_ENDPOINT_ID) is replaced with zeros.
    add_general_regex_sanitizer(
        regex=r"/subscriptions/[0-9a-fA-F-]{36}",
        value="/subscriptions/00000000-0000-0000-0000-000000000000",
    )
    add_header_regex_sanitizer(key="Authorization", value="Sanitized")

    # Scrub real resource, dependency, and host names from request URIs and
    # response bodies. These run on both requests and responses so playback
    # still matches after the recorded names are replaced with placeholders.
    segment_sanitizers = {
        r"/[Rr]esource[Gg]roups/[A-Za-z0-9._()-]+": "/resourceGroups/rgname",
        r"/workspaces/[A-Za-z0-9._-]+": "/workspaces/sanitized-workspace",
        r"/supercomputers/[A-Za-z0-9._-]+": "/supercomputers/sanitized-supercomputer",
        r"/nodePools/[A-Za-z0-9._-]+": "/nodePools/sanitized-nodepool",
        r"/storageContainers/[A-Za-z0-9._-]+": "/storageContainers/sanitized-storagecontainer",
        r"/storageAssets/[A-Za-z0-9._-]+": "/storageAssets/sanitized-storageasset",
        r"/bookshelves/[A-Za-z0-9._-]+": "/bookshelves/sanitized-bookshelf",
        r"/projects/[A-Za-z0-9._-]+": "/projects/sanitized-project",
        r"/chatModelDeployments/[A-Za-z0-9._-]+": "/chatModelDeployments/sanitized-chatdeployment",
        r"/tools/[A-Za-z0-9._-]+": "/tools/sanitized-tool",
        r"/virtualNetworks/[A-Za-z0-9._-]+": "/virtualNetworks/sanitized-vnet",
        r"/subnets/[A-Za-z0-9._-]+": "/subnets/sanitized-subnet",
        r"/userAssignedIdentities/[A-Za-z0-9._-]+": "/userAssignedIdentities/sanitized-identity",
        r"/storageAccounts/[A-Za-z0-9._-]+": "/storageAccounts/sanitizedstorage",
        r"/clusters/[A-Za-z0-9._-]+": "/clusters/sanitized-cluster",
        r"/vaults/[A-Za-z0-9._-]+": "/vaults/sanitized-vault",
        r"[A-Za-z0-9-]+\.workspace-dev\.discovery\.azure\.com": "sanitized.workspace-dev.discovery.azure.com",
        r"[A-Za-z0-9-]+\.bookshelf-dev\.discovery\.azure\.com": "sanitized.bookshelf-dev.discovery.azure.com",
        r"[A-Za-z0-9-]+\.services\.ai\.azure\.com": "sanitized.services.ai.azure.com",
        r"[A-Za-z0-9-]+\.vault\.azure\.net": "sanitized.vault.azure.net",
    }
    for regex, value in segment_sanitizers.items():
        add_general_regex_sanitizer(regex=regex, value=value)

    # Exact-value sanitizers for the configured live resource identifiers (the
    # read-path resource group and resource names). Unlike the path-segment
    # regexes above, these scrub each value wherever it appears in a recording,
    # including standalone body fields such as "name". They only take effect when
    # the env vars are set (i.e. during live recording); in playback the test
    # code already uses the placeholder values.
    #
    # Ordering matters: the test-proxy applies these in insertion order, so a
    # shorter value that is a prefix of a longer one (e.g. workspace "foo" vs
    # project "foo-project") would pre-empt the longer match and record the
    # wrong placeholder. Apply them from the longest live value to the shortest.
    exact_value_env = {
        "AZURE_RESOURCE_GROUP": "rgname",
        "DISCOVERY_WORKSPACE_NAME": "sanitized-workspace",
        "DISCOVERY_SUPERCOMPUTER_NAME": "sanitized-supercomputer",
        "DISCOVERY_NODE_POOL_NAME": "sanitized-nodepool",
        "DISCOVERY_STORAGE_CONTAINER_NAME": "sanitized-storagecontainer",
        "DISCOVERY_STORAGE_ASSET_NAME": "sanitized-storageasset",
        "DISCOVERY_BOOKSHELF_NAME": "sanitized-bookshelf",
        "DISCOVERY_PROJECT_NAME": "sanitized-project",
        "DISCOVERY_DEPLOYMENT_NAME": "sanitized-chatdeployment",
        "DISCOVERY_TOOL_NAME": "sanitized-tool",
    }
    exact_value_pairs = [
        (os.environ[env_var], placeholder)
        for env_var, placeholder in exact_value_env.items()
        if os.environ.get(env_var)
    ]
    for live_value, placeholder in sorted(exact_value_pairs, key=lambda pair: len(pair[0]), reverse=True):
        add_general_regex_sanitizer(regex=re.escape(live_value), value=placeholder)

    # Identity ids and managed resource-group names in response bodies.
    add_general_regex_sanitizer(
        regex=r'"principalId":\s*"[0-9a-fA-F-]{36}"', value='"principalId": "00000000-0000-0000-0000-000000000000"'
    )
    add_general_regex_sanitizer(
        regex=r'"clientId":\s*"[0-9a-fA-F-]{36}"', value='"clientId": "00000000-0000-0000-0000-000000000000"'
    )
    add_general_regex_sanitizer(
        regex=r'"managedResourceGroup":\s*"[^"]*"', value='"managedResourceGroup": "sanitized-mrg"'
    )
    add_general_regex_sanitizer(regex=r"(mrg|mobr)-[A-Za-z0-9-]+", value="sanitized-mrg")

    # Scrub every standalone "name" field (any depth) in response bodies. ARM
    # returns resource names in a standalone "name" field in addition to the
    # resource id path; this ensures those are sanitized by resource type
    # without relying on the test-proxy's default sanitizers.
    add_body_key_sanitizer(json_path="$..name", value="Sanitized")
