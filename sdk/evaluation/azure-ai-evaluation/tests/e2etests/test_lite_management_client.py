import pytest
import logging

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

    @pytest.mark.azuretest
    @pytest.mark.parametrize("include_credentials", [ False, True ])
    def test_workspace_get_default_store(self, project_scope, include_credentials: bool):
        client = LiteAzureManagementClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            logger=logging.getLogger(__name__)
        )

        store = client.workspace_get_default_datastore(
            workspace_name=project_scope["project_name"],
            include_credentials=include_credentials
        )

        assert store
        assert store.name == "workspaceblobstore"
        assert store.account_name == "pfevalsws4628243569"
        assert store.endpoint == "core.windows.net"
        assert store.container_name == "azureml-blobstore-36e33176-ada8-420e-890d-983e519a75b1"
        if include_credentials:
            assert isinstance(store.credential, AzureNamedKeyCredential) or isinstance(store.credential, AzureSasCredential)
        else:
            assert store.credential == None

    @pytest.mark.azuretest
    def test_workspace_get_info(self, project_scope):
        client = LiteAzureManagementClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            logger=logging.getLogger(__name__)
        )

        workspace = client.workspace_get_info(project_scope["project_name"])

        assert workspace
        assert workspace.name
        assert workspace.ml_flow_tracking_uri
