from typing import Callable


import pytest
from unittest.mock import Mock, patch
from azure.ai.ml.operations import WorkspaceConnectionsOperations
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._restclient.v2022_01_01_preview.models import ConnectionCategory
from azure.ai.ml.entities import WorkspaceConnection
from azure.ai.ml.entities._workspace.connections.credentials import PatTokenCredentials


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_connection_operation(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_01_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> WorkspaceConnectionsOperations:
    yield WorkspaceConnectionsOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_01_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
class TestWorkspaceConnectionsOperation:
    @pytest.mark.parametrize(
        "arg", [ConnectionCategory.GIT, ConnectionCategory.PYTHON_FEED, ConnectionCategory.CONTAINER_REGISTRY]
    )
    def test_list(self, arg: str, mock_workspace_connection_operation: WorkspaceConnectionsOperations) -> None:
        mock_workspace_connection_operation.list(connection_type=arg)
        mock_workspace_connection_operation._operation.list.assert_called_once()

    @patch.object(WorkspaceConnection, "_from_rest_object")
    def test_get(
        self,
        mock_from_rest,
        mock_workspace_connection_operation: WorkspaceConnectionsOperations,
        randstr: Callable[[], str],
    ) -> None:
        mock_from_rest.return_value = WorkspaceConnection(
            target="dummy_target",
            type=ConnectionCategory.PYTHON_FEED,
            credentials=PatTokenCredentials(pat="dummy_pat"),
            name="dummy_connection",
        )
        mock_workspace_connection_operation.get(randstr())
        mock_workspace_connection_operation._operation.get.assert_called_once()

    @patch.object(WorkspaceConnection, "_from_rest_object")
    def test_create_or_update(
        self,
        mock_from_rest,
        mock_workspace_connection_operation: WorkspaceConnectionsOperations,
    ):
        mock_from_rest.return_value = WorkspaceConnection(
            target="dummy_target",
            type=ConnectionCategory.PYTHON_FEED,
            credentials=PatTokenCredentials(pat="dummy_pat"),
            name="dummy_connection",
            metadata=None,
        )
        workspace_connection = WorkspaceConnection.load(
            path="./tests/test_configs/workspace_connection/python_feed_pat.yaml"
        )
        mock_workspace_connection_operation.create_or_update(workspace_connection=workspace_connection)
        mock_workspace_connection_operation._operation.create.assert_called_once()

    def test_delete(
        self,
        mock_workspace_connection_operation: WorkspaceConnectionsOperations,
    ) -> None:
        mock_workspace_connection_operation.delete("randstr")
        mock_workspace_connection_operation._operation.delete.assert_called_once()
