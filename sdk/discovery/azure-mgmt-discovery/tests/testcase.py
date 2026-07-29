# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Base test class for azure-mgmt-discovery tests.

Management SDK tests use AzureMgmtRecordedTestCase against the GA API
version 2026-06-01 on the public ARM endpoint.
"""

import os
from devtools_testutils import AzureMgmtRecordedTestCase

# Public ARM endpoint for the GA API version 2026-06-01.
AZURE_ARM_ENDPOINT = os.environ.get("AZURE_ARM_ENDPOINT", "https://management.azure.com")
AZURE_LOCATION = os.environ.get("AZURE_LOCATION", "uksouth")

# Test subscription and resource group
AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
AZURE_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")


class DiscoveryMgmtTestCase(AzureMgmtRecordedTestCase):
    """Base test class for Discovery management SDK tests."""

    def create_discovery_client(self, client_class):
        """Create a Discovery management client for the public ARM endpoint."""
        # Use environment variable for subscription or default
        subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", AZURE_SUBSCRIPTION_ID)
        credential = self.get_credential(client_class)
        return client_class(credential=credential, subscription_id=subscription_id, base_url=AZURE_ARM_ENDPOINT)
