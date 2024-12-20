import pytest
import logging
from azure.core.credentials import AzureNamedKeyCredential, AzureSasCredential, TokenCredential
from azure.ai.evaluation._azure._clients import LiteMLClient


@pytest.mark.usefixtures("model_config", "project_scope", "recording_injection", "recorded_test")
class TestLiteAzureManagementClient(object):
    """End to end tests for the lite Azure management client."""

    @pytest.mark.azuretest
    def test_get_credential(self, project_scope, azure_cred):
        client = LiteMLClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            credential=azure_cred,
            logger=logging.getLogger(__name__),
        )

        credential = client.get_credential()
        assert isinstance(credential, TokenCredential)

    @pytest.mark.azuretest
    def test_get_token(self, project_scope, azure_cred):
        client = LiteMLClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            credential=azure_cred,
            logger=logging.getLogger(__name__),
        )

        token = client.get_token()
        assert isinstance(token, str) and len(token) > 0

    @pytest.mark.azuretest
    @pytest.mark.parametrize("include_credentials", [False, True])
    def test_workspace_get_default_store(self, project_scope, azure_cred, include_credentials: bool):
        client = LiteMLClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            credential=azure_cred,
            logger=logging.getLogger(__name__),
        )

        store = client.workspace_get_default_datastore(
            workspace_name=project_scope["project_name"], include_credentials=include_credentials
        )

        assert store
        assert store.name
        assert store.account_name
        assert store.endpoint
        assert store.container_name
        if include_credentials:
            assert isinstance(store.credential, str) or isinstance(store.credential, AzureSasCredential)
        else:
            assert store.credential == None

    @pytest.mark.azuretest
    def test_workspace_get_info(self, project_scope, azure_cred):
        client = LiteMLClient(
            subscription_id=project_scope["subscription_id"],
            resource_group=project_scope["resource_group_name"],
            credential=azure_cred,
            logger=logging.getLogger(__name__),
        )

        workspace = client.workspace_get_info(project_scope["project_name"])

        assert workspace
        assert workspace.name
        assert workspace.ml_flow_tracking_uri
