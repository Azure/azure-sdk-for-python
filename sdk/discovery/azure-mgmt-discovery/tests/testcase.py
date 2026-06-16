# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Base test class for azure-mgmt-discovery tests.

Management SDK tests use AzureMgmtRecordedTestCase.
The 2026-02-01-preview API is currently behind a feature flag and requires
the EUAP (Early Update Access Program) endpoint.
"""
import os
from azure.identity import DefaultAzureCredential
from devtools_testutils import AzureMgmtRecordedTestCase


# EUAP endpoint required for 2026-02-01-preview API (feature-flagged)
AZURE_ARM_ENDPOINT = os.environ.get("AZURE_ARM_ENDPOINT", "https://eastus2euap.management.azure.com")
AZURE_LOCATION = os.environ.get("AZURE_LOCATION", "centraluseuap")

# Test subscription and resource group with the feature flag enabled
AZURE_SUBSCRIPTION_ID = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
AZURE_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "olawal")


class DiscoveryMgmtTestCase(AzureMgmtRecordedTestCase):
    """Base test class for Discovery management SDK tests.

    Configures the client to use the EUAP endpoint for the feature-flagged API.
    """

    def create_discovery_client(self, client_class):
        """Create a Discovery client configured for the EUAP endpoint."""
        # Use environment variable for subscription or default
        subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", AZURE_SUBSCRIPTION_ID)
        credential = self.get_credential(client_class)
        return client_class(credential=credential, subscription_id=subscription_id, base_url=AZURE_ARM_ENDPOINT)
