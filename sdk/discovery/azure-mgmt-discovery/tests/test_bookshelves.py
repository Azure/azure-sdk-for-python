# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Bookshelves operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP


class TestBookshelves(DiscoveryMgmtTestCase):
    """Tests for Bookshelves operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
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

    @pytest.mark.skip(reason="Requires existing bookshelf")
    @recorded_by_proxy
    def test_get_bookshelf(self):
        """Test getting a specific bookshelf by name."""
        # TODO: Replace with actual bookshelf name from test environment
        bookshelf = self.client.bookshelves.get(self.resource_group, "test-bookshelf")
        assert bookshelf is not None
        assert hasattr(bookshelf, "name")
        assert hasattr(bookshelf, "location")

    @pytest.mark.skip(reason="Requires proper setup with workload identities and managed resource group configuration")
    @recorded_by_proxy
    def test_create_bookshelf(self):
        """Test creating a bookshelf."""
        # TODO: Bookshelf creation may require additional configuration
        bookshelf_data = {"location": "centraluseuap"}
        operation = self.client.bookshelves.begin_create_or_update(
            resource_group_name=self.resource_group,
            bookshelf_name="test-bookshelf",
            resource=bookshelf_data,
        )
        bookshelf = operation.result()
        assert bookshelf is not None

    @pytest.mark.skip(reason="Requires existing bookshelf with properties that can be updated")
    @recorded_by_proxy
    def test_update_bookshelf(self):
        """Test updating a bookshelf."""
        # TODO: Get existing bookshelf and update
        bookshelf_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.bookshelves.begin_create_or_update(
            resource_group_name=self.resource_group,
            bookshelf_name="test-bookshelf",
            resource=bookshelf_data,
        )
        updated_bookshelf = operation.result()
        assert updated_bookshelf is not None

    @pytest.mark.skip(reason="Requires existing bookshelf to delete")
    @recorded_by_proxy
    def test_delete_bookshelf(self):
        """Test deleting a bookshelf."""
        operation = self.client.bookshelves.begin_delete(
            resource_group_name=self.resource_group,
            bookshelf_name="bookshelf-to-delete",
        )
        operation.result()
