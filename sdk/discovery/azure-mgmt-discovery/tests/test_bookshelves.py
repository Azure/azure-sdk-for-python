# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Bookshelves operations."""
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP, AZURE_SUBSCRIPTION_ID


class TestBookshelves(DiscoveryMgmtTestCase):
    """Tests for Bookshelves operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = AZURE_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_bookshelves_by_subscription(self):
        """Test listing bookshelves in the subscription."""
        bookshelves = list(self.client.bookshelves.list_by_subscription())
        assert isinstance(bookshelves, list)

    @recorded_by_proxy
    def test_list_bookshelves_by_resource_group(self):
        """Test listing bookshelves in a resource group."""
        bookshelves = list(self.client.bookshelves.list_by_resource_group(self.resource_group))
        assert isinstance(bookshelves, list)

    @recorded_by_proxy
    def test_get_bookshelf(self):
        """Test getting a specific bookshelf by name."""
        bookshelf = self.client.bookshelves.get(self.resource_group, "test-bookshelf-python")
        assert bookshelf is not None
        assert hasattr(bookshelf, "name")
        assert hasattr(bookshelf, "location")

    @recorded_by_proxy
    def test_create_bookshelf(self):
        """Test creating a bookshelf."""
        mi_id = f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourcegroups/fixedrg-dev-uksouth1/providers/Microsoft.ManagedIdentity/userAssignedIdentities/dev-uksouth1-uami"
        bookshelf_data = models.Bookshelf(
            location="uksouth",
            properties=models.BookshelfProperties(
                workload_identities={mi_id: models.UserAssignedIdentity()},
                private_endpoint_subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/fixedrg-dev-uksouth1/providers/Microsoft.Network/virtualNetworks/vnet-dev-uksouth1/subnets/private-endpoint-subnet",
                search_subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/fixedrg-dev-uksouth1/providers/Microsoft.Network/virtualNetworks/vnet-dev-uksouth1/subnets/search-subnet",
            ),
        )
        operation = self.client.bookshelves.begin_create_or_update(
            resource_group_name="olawal",
            bookshelf_name="test-bookshelf-python",
            resource=bookshelf_data,
        )
        bookshelf = operation.result()
        assert bookshelf is not None

    @recorded_by_proxy
    def test_update_bookshelf(self):
        """Test updating a bookshelf."""
        bookshelf_data = models.Bookshelf(tags={"SkipAutoDeleteTill": "2026-12-31"}) # type: ignore
        operation = self.client.bookshelves.begin_update(
            resource_group_name="olawal",
            bookshelf_name="test-bookshelf-python",
            properties=bookshelf_data,
        )
        updated_bookshelf = operation.result()
        assert updated_bookshelf is not None

    @recorded_by_proxy
    def test_delete_bookshelf(self):
        """Test deleting a bookshelf."""
        operation = self.client.bookshelves.begin_delete(
            resource_group_name="olawal",
            bookshelf_name="test-bookshelf-python",
        )
        operation.result()
