# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Bookshelves operations."""

import os
import pytest
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP, AZURE_SUBSCRIPTION_ID

# Live resources for read-only tests (read, never mutated)
READ_RESOURCE_GROUP = os.environ.get("AZURE_RESOURCE_GROUP", "rgname")
READ_BOOKSHELF_NAME = os.environ.get("DISCOVERY_BOOKSHELF_NAME", "sanitized-bookshelf")


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
        bookshelves = list(self.client.bookshelves.list_by_resource_group(READ_RESOURCE_GROUP))
        assert isinstance(bookshelves, list)

    @recorded_by_proxy
    def test_get_bookshelf(self):
        """Test getting a specific bookshelf by name."""
        bookshelf = self.client.bookshelves.get(READ_RESOURCE_GROUP, READ_BOOKSHELF_NAME)
        assert bookshelf is not None
        assert hasattr(bookshelf, "name")
        assert hasattr(bookshelf, "location")

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_create_bookshelf(self):
        """Test creating a bookshelf."""
        mi_id = f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.ManagedIdentity/userAssignedIdentities/sanitized-identity"
        bookshelf_data = models.Bookshelf(
            location="uksouth",
            properties=models.BookshelfProperties(
                workload_identities={mi_id: models.UserAssignedIdentity()},
                private_endpoint_subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/sanitized-vnet/subnets/sanitized-subnet",
                search_subnet_id=f"/subscriptions/{AZURE_SUBSCRIPTION_ID}/resourceGroups/rgname/providers/Microsoft.Network/virtualNetworks/sanitized-vnet/subnets/sanitized-subnet",
            ),
        )
        operation = self.client.bookshelves.begin_create_or_update(
            resource_group_name="rgname",
            bookshelf_name="sanitized-bookshelf",
            resource=bookshelf_data,
        )
        bookshelf = operation.result()
        assert bookshelf is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_update_bookshelf(self):
        """Test updating a bookshelf."""
        bookshelf_data = models.Bookshelf(tags={"SkipAutoDeleteTill": "2026-12-31"})  # type: ignore
        operation = self.client.bookshelves.begin_update(
            resource_group_name="rgname",
            bookshelf_name="sanitized-bookshelf",
            properties=bookshelf_data,
        )
        updated_bookshelf = operation.result()
        assert updated_bookshelf is not None

    @pytest.mark.playback_only
    @recorded_by_proxy
    def test_delete_bookshelf(self):
        """Test deleting a bookshelf."""
        operation = self.client.bookshelves.begin_delete(
            resource_group_name="rgname",
            bookshelf_name="sanitized-bookshelf",
        )
        operation.result()
