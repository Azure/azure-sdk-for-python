# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for ChatModelDeployments operations."""
from azure.mgmt.discovery import DiscoveryMgmtClient, models
from devtools_testutils import recorded_by_proxy

from .testcase import DiscoveryMgmtTestCase


# Resource group that has a workspace
WORKSPACE_RESOURCE_GROUP = "olawal"
WORKSPACE_NAME = "test-wrksp-create01"


class TestChatModelDeployments(DiscoveryMgmtTestCase):
    """Tests for ChatModelDeployments operations."""

    def setup_method(self, method):
        self.client = self.create_discovery_client(DiscoveryMgmtClient)
        self.resource_group = WORKSPACE_RESOURCE_GROUP
        self.workspace_name = WORKSPACE_NAME

    @recorded_by_proxy
    def test_list_chat_model_deployments_by_workspace(self):
        """Test listing chat model deployments in a workspace."""
        deployments = list(
            self.client.chat_model_deployments.list_by_workspace(self.resource_group, self.workspace_name)
        )
        assert isinstance(deployments, list)

    @recorded_by_proxy
    def test_get_chat_model_deployment(self):
        """Test getting a specific chat model deployment by name."""
        deployment = self.client.chat_model_deployments.get(
            self.resource_group, self.workspace_name, "test-deploy-chatmodel01"
        )
        assert deployment is not None
        assert hasattr(deployment, "name")

    @recorded_by_proxy
    def test_create_chat_model_deployment(self):
        """Test creating a chat model deployment."""
        deployment_data = models.ChatModelDeployment(
            location="uksouth",
            properties=models.ChatModelDeploymentProperties(
                model_format="OpenAI",
                model_name="gpt-4o",
            ),
        )
        operation = self.client.chat_model_deployments.begin_create_or_update(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            chat_model_deployment_name="test-deploy-chatmodel01",
            resource=deployment_data,
        )
        deployment = operation.result()
        assert deployment is not None

    @recorded_by_proxy
    def test_update_chat_model_deployment(self):
        """Test updating a chat model deployment tags."""
        deployment_data = models.ChatModelDeployment(
            tags={"SkipAutoDeleteTill": "2026-12-31"},
        )
        operation = self.client.chat_model_deployments.begin_update(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            chat_model_deployment_name="test-deploy-chatmodel01",
            properties=deployment_data,
        )
        updated_deployment = operation.result()
        assert updated_deployment is not None

    @recorded_by_proxy
    def test_delete_chat_model_deployment(self):
        """Test deleting a chat model deployment."""
        operation = self.client.chat_model_deployments.begin_delete(
            resource_group_name=self.resource_group,
            workspace_name=self.workspace_name,
            chat_model_deployment_name="test-deploy-chatmodel01",
        )
        operation.result()
