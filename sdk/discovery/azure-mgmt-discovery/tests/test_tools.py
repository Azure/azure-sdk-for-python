# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Tools operations."""
import uuid
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase, AZURE_RESOURCE_GROUP


# Known tool name in the test environment
TOOL_NAME = "test-tool-50d87c62"


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
    @recorded_by_proxy
    def test_create_tool(self):
        """Test creating a tool."""
        unique_name = f"test-tool-{uuid.uuid4().hex[:8]}"
        tool_data = {
            "location": "uksouth",
            "properties": {
                "version": "1.0.0",
                "definitionContent": {
                    "name": "molpredictor",
                    "description": "Molecular property prediction for single SMILES strings.",
                    "version": "1.0.0",
                    "category": "cheminformatics",
                    "license": "MIT",
                    "infra": [
                        {
                            "name": "worker",
                            "infra_type": "container",
                            "image": {
                                "acr": "demodiscoveryacr.azurecr.io/molpredictor:latest"
                            },
                            "compute": {
                                "min_resources": {
                                    "cpu": "1",
                                    "ram": "1Gi",
                                    "storage": "32",
                                    "gpu": "0"
                                },
                                "max_resources": {
                                    "cpu": "2",
                                    "ram": "1Gi",
                                    "storage": "64",
                                    "gpu": "0"
                                },
                                "recommended_sku": ["Standard_D4s_v6"],
                                "pool_type": "static",
                                "pool_size": 1
                            }
                        }
                    ],
                    "actions": [
                        {
                            "name": "predict",
                            "description": "Predict molecular properties for SMILES strings.",
                            "input_schema": {
                                "type": "object",
                                "properties": {
                                    "action": {
                                        "type": "string",
                                        "description": "The property to predict. Must be one of [log_p, boiling_point, solubility, density, critical_point]"
                                    }
                                },
                                "required": ["action"]
                            },
                            "command": "python molpredictor.py --action {{ action }}",
                            "infra_node": "worker"
                        }
                    ]
                }
            }
        }
        operation = self.client.tools.begin_create_or_update(
            resource_group_name="olawal",
            tool_name=unique_name,
            resource=tool_data,
        )
        tool = operation.result()
        assert tool is not None
    @pytest.mark.skip(reason="no recording")
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
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_delete_tool(self):
        """Test deleting a tool."""
        operation = self.client.tools.begin_delete(
            resource_group_name=self.resource_group,
            tool_name="tool-to-delete",
        )
        operation.result()
