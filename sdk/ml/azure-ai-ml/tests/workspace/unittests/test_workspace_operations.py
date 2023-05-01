from unittest.mock import DEFAULT, Mock

import pytest
from pytest_mock import MockFixture

from azure.ai.ml import load_workspace
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities import (
    IdentityConfiguration,
    ManagedIdentityConfiguration,
    Workspace,
)
from azure.ai.ml.operations import WorkspaceOperations
from azure.core.polling import LROPoller


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_operation(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2023_04_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2023_04_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestWorkspaceOperation:
    @pytest.mark.parametrize("arg", ["resource_group", "subscription", "other_rand_str"])
    def test_list(self, arg: str, mock_workspace_operation: WorkspaceOperations) -> None:
        mock_workspace_operation.list(scope=arg)
        if arg == "subscription":
            mock_workspace_operation._operation.list_by_subscription.assert_called_once()
        else:
            mock_workspace_operation._operation.list_by_resource_group.assert_called_once()

    def test_get(self, mock_workspace_operation: WorkspaceOperations) -> None:
        mock_workspace_operation.get("random_name")
        mock_workspace_operation._operation.get.assert_called_once()

    def test_list_keys(self, mock_workspace_operation: WorkspaceOperations) -> None:
        mock_workspace_operation.get_keys("random_name")
        mock_workspace_operation._operation.list_keys.assert_called_once()

    def test_begin_sync_keys_no_wait(self, mock_workspace_operation: WorkspaceOperations) -> None:
        mock_workspace_operation.begin_sync_keys(name="random_name")
        mock_workspace_operation._operation.begin_resync_keys.assert_called_once()

    def test_begin_sync_keys_wait(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml._utils._azureml_polling.polling_wait", return_value=LROPoller)
        mock_workspace_operation.begin_sync_keys(name="random_name")
        mock_workspace_operation._operation.begin_resync_keys.assert_called_once()

    def test_begin_create(
        self,
        mock_workspace_operation: WorkspaceOperations,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=None)
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations._populate_arm_paramaters", return_value=({}, {}, {}))
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation.begin_create(workspace=Workspace(name="name"))

    def test_update(self, mock_workspace_operation: WorkspaceOperations) -> None:
        ws = Workspace(
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

        mock_workspace_operation._operation.begin_update.side_effect = outgoing_call
        mock_workspace_operation.begin_update(ws, update_dependent_resources=True)
        mock_workspace_operation._operation.begin_update.assert_called()

    def test_delete(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mock_workspace_operation.begin_delete("randstr", delete_dependent_resources=True)
        mock_workspace_operation._operation.begin_delete.assert_called_once()

    def test_purge(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mock_workspace_operation.begin_delete("randstr", delete_dependent_resources=True, permanently_delete=True)
        mock_workspace_operation._operation.begin_delete.assert_called_once()

    def test_begin_diagnose_no_wait(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mock_workspace_operation.begin_diagnose(name="random_name")
        mock_workspace_operation._operation.begin_diagnose.assert_called_once()
        mocker.patch("azure.ai.ml._restclient.v2022_10_01.models.DiagnoseRequestProperties", return_value=None)

    def test_begin_diagnose_wait(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mock_workspace_operation.begin_diagnose(name="random_name")
        mock_workspace_operation._operation.begin_diagnose.assert_called_once()
        mocker.patch("azure.ai.ml._restclient.v2022_10_01.models.DiagnoseRequestProperties", return_value=None)

    def test_load_uai_workspace_from_yaml(self, mock_workspace_operation: WorkspaceOperations):
        params_override = []
        wps = load_workspace("./tests/test_configs/workspace/workspace_uai.yaml", params_override=params_override)
        assert isinstance(wps.identity, IdentityConfiguration)
        assert isinstance(wps.identity.user_assigned_identities, list)
        assert isinstance(wps.identity.user_assigned_identities[0], ManagedIdentityConfiguration)
