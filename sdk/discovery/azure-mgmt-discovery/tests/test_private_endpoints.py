# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Private Endpoint related operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase


# Resource group and resources for testing
WORKSPACE_RESOURCE_GROUP = "olawal"
WORKSPACE_NAME = "wrksptest44"
BOOKSHELF_NAME = "test-bookshelf"


class TestPrivateEndpoints(DiscoveryMgmtTestCase):
    """Tests for Private Endpoint related operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = WORKSPACE_RESOURCE_GROUP
        self.workspace_name = WORKSPACE_NAME
        self.bookshelf_name = BOOKSHELF_NAME

    # ============ Workspace Private Endpoint Connection Tests ============
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_list_workspace_private_endpoint_connections(self):
        """Test listing workspace private endpoint connections."""
        connections = list(
            self.client.workspace_private_endpoint_connections.list_by_workspace(
                self.resource_group, self.workspace_name
            )
        )
        assert isinstance(connections, list)
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_get_workspace_private_endpoint_connection(self):
        """Test getting a workspace private endpoint connection."""
        connection_name = "test-pe-connection"
        connection = self.client.workspace_private_endpoint_connections.get(
            self.resource_group, self.workspace_name, connection_name
        )
        assert connection is not None
        assert hasattr(connection, "name")
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_create_workspace_private_endpoint_connection(self):
        """Test creating a workspace private endpoint connection."""
        connection_name = "test-pe-connection"
        connection_data = {
            "properties": {
                "privateLinkServiceConnectionState": {
                    "status": "Approved"
                }
            }
        }
        operation = self.client.workspace_private_endpoint_connections.begin_create_or_update(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            private_endpoint_connection_name=connection_name,
            resource=connection_data,
        )
        connection = operation.result()
        assert connection is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_delete_workspace_private_endpoint_connection(self):
        """Test deleting a workspace private endpoint connection."""
        connection_name = "pe-conn-to-delete"
        operation = self.client.workspace_private_endpoint_connections.begin_delete(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            private_endpoint_connection_name=connection_name,
        )
        operation.result()

    # ============ Workspace Private Link Resource Tests ============
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_list_workspace_private_link_resources(self):
        """Test listing workspace private link resources."""
        link_resources = list(
            self.client.workspace_private_link_resources.list_by_workspace(self.resource_group, self.workspace_name)
        )
        assert isinstance(link_resources, list)
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_get_workspace_private_link_resource(self):
        """Test getting a workspace private link resource."""
        link_resource_name = "workspace"
        link_resource = self.client.workspace_private_link_resources.get(
            self.resource_group, self.workspace_name, link_resource_name
        )
        assert link_resource is not None

    # ============ Bookshelf Private Endpoint Connection Tests ============
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_list_bookshelf_private_endpoint_connections(self):
        """Test listing bookshelf private endpoint connections."""
        connections = list(
            self.client.bookshelf_private_endpoint_connections.list_by_bookshelf(
                self.resource_group, self.bookshelf_name
            )
        )
        assert isinstance(connections, list)
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_get_bookshelf_private_endpoint_connection(self):
        """Test getting a bookshelf private endpoint connection."""
        connection_name = "test-pe-connection"
        connection = self.client.bookshelf_private_endpoint_connections.get(
            self.resource_group, self.bookshelf_name, connection_name
        )
        assert connection is not None
        assert hasattr(connection, "name")
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_create_bookshelf_private_endpoint_connection(self):
        """Test creating a bookshelf private endpoint connection."""
        connection_name = "test-pe-connection"
        connection_data = {
            "properties": {
                "privateLinkServiceConnectionState": {
                    "status": "Approved"
                }
            }
        }
        operation = self.client.bookshelf_private_endpoint_connections.begin_create_or_update(
            resource_group_name=self.resource_group,
            bookshelf_name=self.bookshelf_name,
            private_endpoint_connection_name=connection_name,
            resource=connection_data,
        )
        connection = operation.result()
        assert connection is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_delete_bookshelf_private_endpoint_connection(self):
        """Test deleting a bookshelf private endpoint connection."""
        connection_name = "pe-conn-to-delete"
        operation = self.client.bookshelf_private_endpoint_connections.begin_delete(
            resource_group_name=self.resource_group,
            bookshelf_name=self.bookshelf_name,
            private_endpoint_connection_name=connection_name,
        )
        operation.result()

    # ============ Bookshelf Private Link Resource Tests ============
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_list_bookshelf_private_link_resources(self):
        """Test listing bookshelf private link resources."""
        link_resources = list(
            self.client.bookshelf_private_link_resources.list_by_bookshelf(self.resource_group, self.bookshelf_name)
        )
        assert isinstance(link_resources, list)
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_get_bookshelf_private_link_resource(self):
        """Test getting a bookshelf private link resource."""
        link_resource_name = "bookshelf"
        link_resource = self.client.bookshelf_private_link_resources.get(
            self.resource_group, self.bookshelf_name, link_resource_name
        )
        assert link_resource is not None
