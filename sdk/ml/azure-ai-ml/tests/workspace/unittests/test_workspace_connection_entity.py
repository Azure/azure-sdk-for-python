import pytest
from azure.ai.ml._restclient.v2022_01_01_preview.models import ConnectionCategory, ConnectionAuthType
from azure.ai.ml.entities import WorkspaceConnection
from azure.ai.ml.entities._workspace.connections.credentials import PatTokenCredentials
from azure.ai.ml import load_workspace_connection


@pytest.mark.unittest
class TestWorkspaceConnectionEntity:
    def test_workspace_connection_constructor(self):
        ws_connection = WorkspaceConnection(
            target="dummy_target",
            type=ConnectionCategory.PYTHON_FEED,
            credentials=PatTokenCredentials(pat="dummy_pat"),
            name="dummy_connection",
            metadata=None,
        )

        assert ws_connection.name == "dummy_connection"
        assert ws_connection.type == ConnectionCategory.PYTHON_FEED
        assert ws_connection.credentials.type == ConnectionAuthType.PAT
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.target == "dummy_target"
        assert ws_connection.metadata is None

    def test_workspace_connection_entity_load(self):
        ws_connection = load_workspace_connection(path="./tests/test_configs/workspace_connection/git_pat.yaml")

        assert ws_connection.name == "test_ws_conn_git_pat"
        assert ws_connection.target == "https://test-git-feed.com"
        assert ws_connection.type == ConnectionCategory.GIT
        assert ws_connection.credentials.type == ConnectionAuthType.PAT
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.metadata is None

        ws_connection = load_workspace_connection(
            path="./tests/test_configs/workspace_connection/container_registry_managed_identity.yaml"
        )

        assert ws_connection.type == ConnectionCategory.CONTAINER_REGISTRY
        assert ws_connection.credentials.type == ConnectionAuthType.MANAGED_IDENTITY
        assert ws_connection.credentials.client_id == "client_id"
        assert ws_connection.credentials.resource_id == "resource_id"
        assert ws_connection.name == "test_ws_conn_cr_managed"
        assert ws_connection.target == "https://test-feed.com"
        assert ws_connection.metadata is None

        ws_connection = load_workspace_connection(path="./tests/test_configs/workspace_connection/python_feed_pat.yaml")

        assert ws_connection.type == ConnectionCategory.PYTHON_FEED
        assert ws_connection.credentials.type == ConnectionAuthType.PAT
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.name == "test_ws_conn_python_pat"
        assert ws_connection.target == "https://test-feed.com"
        assert ws_connection.metadata is None

        ws_connection = load_workspace_connection(
            path="./tests/test_configs/workspace_connection/fs_service_principal.yaml"
        )

        assert ws_connection.name == "test_ws_conn_fs_sp"
        assert ws_connection.target == "azureml://featurestores/featurestore"
        assert ws_connection.type == ConnectionCategory.FEATURE_STORE
        assert ws_connection.credentials.type == ConnectionAuthType.SERVICE_PRINCIPAL
        assert ws_connection.credentials.client_id == "client_id"
        assert ws_connection.credentials.client_secret == "PasswordPlaceHolder"
        assert ws_connection.credentials.tenant_id == "tenant_id"
        assert ws_connection.metadata["name"] == "featurestore"
        assert ws_connection.metadata["description"] == "my featurestore"
        assert ws_connection.metadata["type"] == "feast"
        assert ws_connection.metadata["featurestore_config"]
        assert ws_connection.metadata["connection_config"]
