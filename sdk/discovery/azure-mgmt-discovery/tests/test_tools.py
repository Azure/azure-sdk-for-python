# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Tools operations."""
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP


# Known tool name in the test environment
TOOL_NAME = "testtool"


class TestTools(DiscoveryMgmtTestCase):
    """Tests for Tools operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = AZURE_RESOURCE_GROUP

    @recorded_by_proxy
    def test_list_tools_by_subscription(self):
        """Test listing tools in the subscription."""
        tools = list(self.client.tools.list_by_subscription())
        assert isinstance(tools, list)

    @recorded_by_proxy
    def test_list_tools_by_resource_group(self):
        """Test listing tools in a resource group."""
        tools = list(self.client.tools.list_by_resource_group(self.resource_group))
        assert isinstance(tools, list)

    @recorded_by_proxy
    def test_get_tool(self):
        """Test getting a specific tool by name."""
        tool = self.client.tools.get(self.resource_group, TOOL_NAME)
        assert tool is not None
        # Don't assert on name since it may be sanitized in playback
        assert hasattr(tool, "name")
        assert hasattr(tool, "location")

    @pytest.mark.skip(reason="Requires ToolProperties with tool configuration")
    @recorded_by_proxy
    def test_create_tool(self):
        """Test creating a tool."""
        tool_data = {"location": "centraluseuap"}
        operation = self.client.tools.begin_create_or_update(
            resource_group_name=self.resource_group,
            tool_name="test-tool",
            resource=tool_data,
        )
        tool = operation.result()
        assert tool is not None

    @pytest.mark.skip(reason="Requires existing Tool to update")
    @recorded_by_proxy
    def test_update_tool(self):
        """Test updating a tool."""
        tool_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.tools.begin_create_or_update(
            resource_group_name=self.resource_group,
            tool_name=TOOL_NAME,
            resource=tool_data,
        )
        updated_tool = operation.result()
        assert updated_tool is not None

    @pytest.mark.skip(reason="Requires existing Tool to delete")
    @recorded_by_proxy
    def test_delete_tool(self):
        """Test deleting a tool."""
        operation = self.client.tools.begin_delete(
            resource_group_name=self.resource_group,
            tool_name="tool-to-delete",
        )
        operation.result()
