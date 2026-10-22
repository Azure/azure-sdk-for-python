from unittest.mock import DEFAULT, Mock

import pytest
from pytest_mock import MockFixture

from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities import (
    Hub,
)
from azure.ai.ml.operations import WorkspaceOperations
from azure.core.polling import LROPoller


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_hub_operation(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2023_06_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2023_06_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestMockedOperations:
    @pytest.mark.parametrize("arg", ["resource_group", "subscription", "other_rand_str"])
    def test_list(self, arg: str, mock_hub_operation: WorkspaceOperations) -> None:
        mock_hub_operation.list(scope=arg)
        if arg == "subscription":
            mock_hub_operation._operation.list_by_subscription.assert_called_once()
        else:
            mock_hub_operation._operation.list_by_resource_group.assert_called_once()

    def test_get(self, mock_hub_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("urllib.parse.urlparse")
        mock_hub_operation.get(name="random_name")
        mock_hub_operation._operation.get.assert_called_once()

    def test_begin_create(
        self,
        mock_hub_operation: WorkspaceOperations,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=None)
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations._populate_arm_parameters", return_value=({}, {}, {}))
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_hub_operation.begin_create(workspace=Hub(name="name"))

    def test_update(self, mock_hub_operation: WorkspaceOperations) -> None:
        hub = Hub(
            name="name",
            description="description",
        )

        def outgoing_call(rg, name, params, polling, cls):
            assert rg == "test_resource_group"
            assert name == "name"
            assert params.description == "description"
            assert polling is True
            assert callable(cls)
            return DEFAULT

        def outgoing_get_call(rg, name):
            return Hub(name=name)._to_rest_object()

        mock_hub_operation._operation.get.side_effect = outgoing_get_call
        mock_hub_operation._operation.begin_update.side_effect = outgoing_call
        mock_hub_operation.begin_update(workspace=hub, update_dependent_resources=True)
        mock_hub_operation._operation.begin_update.assert_called()

    def test_delete(self, mock_hub_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        def outgoing_call(rg, name):
            return Hub(name=name)._to_rest_object()

        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_generic_arm_resource_by_arm_id", return_value=None
        )
        mock_hub_operation._operation.get.side_effect = outgoing_call
        mock_hub_operation.begin_delete("randstr", delete_dependent_resources=True)
        mock_hub_operation._operation.begin_delete.assert_called_once()
