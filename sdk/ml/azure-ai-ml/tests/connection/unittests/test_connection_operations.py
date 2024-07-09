from typing import Callable
from unittest.mock import Mock, patch

import pytest

from azure.ai.ml import load_connection
from azure.ai.ml._restclient.v2022_01_01_preview.models import ConnectionCategory
from azure.ai.ml._scope_dependent_operations import OperationConfig, OperationScope
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities import PatTokenConfiguration, WorkspaceConnection
from azure.ai.ml.operations import WorkspaceConnectionsOperations


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_connection_operation(
    mock_workspace_scope: OperationScope,
    mock_operation_config: OperationConfig,
    mock_aml_services_2022_01_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> WorkspaceConnectionsOperations:
    yield WorkspaceConnectionsOperations(
        operation_scope=mock_workspace_scope,
        operation_config=mock_operation_config,
        service_client=mock_aml_services_2022_01_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
@pytest.mark.core_sdk_test
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
    ) -> None:
        mock_from_rest.return_value = WorkspaceConnection(
            target="dummy_target",
            type=ConnectionCategory.PYTHON_FEED,
            credentials=PatTokenConfiguration(pat="dummy_pat"),
            name="dummy_connection",
        )
        mock_workspace_connection_operation.get("random_name")
        mock_workspace_connection_operation._operation.get.assert_called_once()

    @patch.object(WorkspaceConnection, "_from_rest_object")
    def test_create_or_update(
        self,
        mock_from_rest,
        mock_workspace_connection_operation: WorkspaceConnectionsOperations,
    ):
        mock_from_rest.return_value = WorkspaceConnection(
            target="dummy_target",
            type=camel_to_snake(ConnectionCategory.PYTHON_FEED),
            credentials=PatTokenConfiguration(pat="dummy_pat"),
            name="dummy_connection",
        )
        workspace_connection = load_connection(source="./tests/test_configs/connection/python_feed_pat.yaml")

        mock_workspace_connection_operation.create_or_update(workspace_connection=workspace_connection)
        mock_workspace_connection_operation._operation.create.assert_called_once()

    def test_delete(
        self,
        mock_workspace_connection_operation: WorkspaceConnectionsOperations,
    ) -> None:
        mock_workspace_connection_operation.delete("randstr")
        mock_workspace_connection_operation._operation.delete.assert_called_once()
