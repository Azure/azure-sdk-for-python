# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Supercomputers operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP


class TestSupercomputers(DiscoveryMgmtTestCase):
    """Tests for Supercomputers operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = AZURE_RESOURCE_GROUP

    @pytest.mark.skip(reason="Backend unstable - centraluseuap region doesn't consistently support 2026-02-01-preview")
    @recorded_by_proxy
    def test_list_supercomputers_by_resource_group(self):
        """Test listing supercomputers in a resource group."""
        supercomputers = list(self.client.supercomputers.list_by_resource_group(self.resource_group))
        assert isinstance(supercomputers, list)

    @pytest.mark.skip(reason="Backend unstable - centraluseuap region doesn't consistently support 2026-02-01-preview")
    @recorded_by_proxy
    def test_list_supercomputers_by_subscription(self):
        """Test listing supercomputers in the subscription."""
        supercomputers = list(self.client.supercomputers.list_by_subscription())
        assert isinstance(supercomputers, list)

    @pytest.mark.skip(reason="Requires existing supercomputer")
    @recorded_by_proxy
    def test_get_supercomputer(self):
        """Test getting a specific supercomputer by name."""
        # TODO: Replace with actual supercomputer name from test environment
        supercomputer = self.client.supercomputers.get(self.resource_group, "test-supercomputer")
        assert supercomputer is not None
        assert hasattr(supercomputer, "name")
        assert hasattr(supercomputer, "location")

    @pytest.mark.skip(reason="Requires SupercomputerProperties with SupercomputerIdentities and network configuration")
    @recorded_by_proxy
    def test_create_supercomputer(self):
        """Test creating a supercomputer."""
        supercomputer_data = {"location": "centraluseuap"}
        operation = self.client.supercomputers.begin_create_or_update(
            resource_group_name=self.resource_group,
            supercomputer_name="test-supercomputer",
            resource=supercomputer_data,
        )
        supercomputer = operation.result()
        assert supercomputer is not None

    @pytest.mark.skip(reason="Requires existing supercomputer with properties that can be updated")
    @recorded_by_proxy
    def test_update_supercomputer(self):
        """Test updating a supercomputer."""
        supercomputer_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.supercomputers.begin_create_or_update(
            resource_group_name=self.resource_group,
            supercomputer_name="test-supercomputer",
            resource=supercomputer_data,
        )
        updated_supercomputer = operation.result()
        assert updated_supercomputer is not None

    @pytest.mark.skip(reason="Requires existing supercomputer to delete")
    @recorded_by_proxy
    def test_delete_supercomputer(self):
        """Test deleting a supercomputer."""
        operation = self.client.supercomputers.begin_delete(
            resource_group_name=self.resource_group,
            supercomputer_name="supercomputer-to-delete",
        )
        operation.result()
