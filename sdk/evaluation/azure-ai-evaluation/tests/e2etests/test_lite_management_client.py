import pytest
import logging

from devtools_testutils import AzureRecordedTestCase
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.ai.evaluation._promptflow.azure._lite_azure_management_client import LiteAzureManagementClient

@pytest.mark.usefixtures("model_config", "project_scope",
    # "recording_injection", "recorded_test"
)
class TestLiteAzureManagementClient(object):
    """End to end tests for the lite Azure management client."""

    @pytest.mark.azuretest
    def test_get_credential(self, project_scope):
        client = LiteAzureManagementClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            logger=logging.getLogger(__name__)
        )

        credential = client.get_credential()
        assert isinstance(credential, TokenCredential)

    @pytest.mark.azuretest
    def test_get_token(self, project_scope):
        client = LiteAzureManagementClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            logger=logging.getLogger(__name__)
        )

        token = client.get_token()
        assert isinstance(token, str) and len(token) > 0

    def test_workspace_get_default_store(self, project_scope):
        client = LiteAzureManagementClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            logger=logging.getLogger(__name__)
        )

        store = client.workspace_get_default_datastore(
            workspace_name=project_scope["project_name"]
        )

        assert store
        assert store.name
        assert store.account_name
        assert.store.endpoint
        assert store.container_name
        assert isinstance(store.credential, AzureSasCredential) or isinstance(store.credential, AzureNamedKeyCredential)