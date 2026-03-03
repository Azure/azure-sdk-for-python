# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for ChatModelDeployments operations."""
import uuid
import pytest
from azure.mgmt.discovery import DiscoveryClient
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase


# Resource group that has a workspace
WORKSPACE_RESOURCE_GROUP = "olawal"
WORKSPACE_NAME = "wrksptest44"


class TestChatModelDeployments(DiscoveryMgmtTestCase):
    """Tests for ChatModelDeployments operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryClient)
        self.resource_group = WORKSPACE_RESOURCE_GROUP
        self.workspace_name = WORKSPACE_NAME

    @recorded_by_proxy
    def test_list_chat_model_deployments_by_workspace(self):
        """Test listing chat model deployments in a workspace."""
        deployments = list(
            self.client.chat_model_deployments.list_by_workspace(self.resource_group, self.workspace_name)
        )
        assert isinstance(deployments, list)
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_get_chat_model_deployment(self):
        """Test getting a specific chat model deployment by name."""
        # TODO: Replace with actual deployment name from test environment
        deployment = self.client.chat_model_deployments.get(self.resource_group, self.workspace_name, "test-deployment")
        assert deployment is not None
        assert hasattr(deployment, "name")
    @recorded_by_proxy
    def test_create_chat_model_deployment(self):
        """Test creating a chat model deployment."""
        unique_name = f"test-deploy-{uuid.uuid4().hex[:8]}"
        deployment_data = {
            "location": "uksouth",
            "properties": {
                "modelFormat": "OpenAI",
                "modelName": "gpt-4"
            }
        }
        operation = self.client.chat_model_deployments.begin_create_or_update(
            resource_group_name="olawal",
            workspace_name=self.workspace_name,
            chat_model_deployment_name=unique_name,
            resource=deployment_data,
        )
        deployment = operation.result()
        assert deployment is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_update_chat_model_deployment(self):
        """Test updating a chat model deployment."""
        deployment_data = {
            "location": "centraluseuap",
            "tags": {"updated": "true"},
        }
        operation = self.client.chat_model_deployments.begin_create_or_update(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            chat_model_deployment_name="test-deployment",
            resource=deployment_data,
        )
        updated_deployment = operation.result()
        assert updated_deployment is not None
    @pytest.mark.skip(reason="no recording")
    @recorded_by_proxy
    def test_delete_chat_model_deployment(self):
        """Test deleting a chat model deployment."""
        operation = self.client.chat_model_deployments.begin_delete(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            chat_model_deployment_name="deployment-to-delete",
        )
        operation.result()
