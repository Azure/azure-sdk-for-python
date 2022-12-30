from pathlib import Path

import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import load_workspace_connection
from azure.ai.ml._restclient.v2022_01_01_preview.models import ConnectionAuthType, ConnectionCategory
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import WorkspaceConnection
from azure.ai.ml.entities._credentials import PatTokenConfiguration


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestWorkspaceConnectionEntity:
    def test_workspace_connection_constructor(self):
        ws_connection = WorkspaceConnection(
            target="dummy_target",
            type=camel_to_snake(ConnectionCategory.PYTHON_FEED),
            credentials=PatTokenConfiguration(pat="dummy_pat"),
            name="dummy_connection",
            metadata=None,
        )

        assert ws_connection.name == "dummy_connection"
        assert ws_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.target == "dummy_target"
        assert ws_connection.metadata is None

    def test_workspace_connection_entity_load_and_dump(self):
        def simple_workspace_connection_validation(ws_connection):
            assert ws_connection.name == "test_ws_conn_git_pat"
            assert ws_connection.target == "https://test-git-feed.com"
            assert ws_connection.type == camel_to_snake(ConnectionCategory.GIT)
            assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
            assert ws_connection.credentials.pat == "dummy_pat"
            assert ws_connection.metadata is None

        verify_entity_load_and_dump(
            load_workspace_connection,
            simple_workspace_connection_validation,
            "./tests/test_configs/workspace_connection/git_pat.yaml",
        )

        ws_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/container_registry_managed_identity.yaml"
        )

        assert ws_connection.type == camel_to_snake(ConnectionCategory.CONTAINER_REGISTRY)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.MANAGED_IDENTITY)
        assert ws_connection.credentials.client_id == "client_id"
        assert ws_connection.credentials.resource_id == "resource_id"
        assert ws_connection.name == "test_ws_conn_cr_managed"
        assert ws_connection.target == "https://test-feed.com"
        assert ws_connection.metadata is None

        ws_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/python_feed_pat.yaml"
        )

        assert ws_connection.type == camel_to_snake(ConnectionCategory.PYTHON_FEED)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.PAT)
        assert ws_connection.credentials.pat == "dummy_pat"
        assert ws_connection.name == "test_ws_conn_python_pat"
        assert ws_connection.target == "https://test-feed.com"
        assert ws_connection.metadata is None

        ws_connection = load_workspace_connection(
            source="./tests/test_configs/workspace_connection/fs_service_principal.yaml"
        )

        assert ws_connection.name == "test_ws_conn_fs_sp"
        assert ws_connection.target == "azureml://featurestores/featurestore"
        assert ws_connection.type == camel_to_snake(ConnectionCategory.FEATURE_STORE)
        assert ws_connection.credentials.type == camel_to_snake(ConnectionAuthType.SERVICE_PRINCIPAL)
        assert ws_connection.credentials.client_id == "client_id"
        assert ws_connection.credentials.client_secret == "PasswordPlaceHolder"
        assert ws_connection.credentials.tenant_id == "tenant_id"
        assert ws_connection.metadata["name"] == "featurestore"
        assert ws_connection.metadata["description"] == "my featurestore"
        assert ws_connection.metadata["type"] == "feast"
        assert ws_connection.metadata["featurestore_config"]
        assert ws_connection.metadata["connection_config"]
