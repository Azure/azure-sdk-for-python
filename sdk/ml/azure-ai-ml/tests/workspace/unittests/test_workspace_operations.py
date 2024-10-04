from typing import Optional
from unittest.mock import ANY, DEFAULT, MagicMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from pytest_mock import MockFixture

from azure.ai.ml import load_workspace
from azure.ai.ml._restclient.v2024_07_01_preview.models import (
    ServerlessComputeSettings as RestServerlessComputeSettings,
    Workspace as RestWorkspace,
)
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities import (
    CustomerManagedKey,
    IdentityConfiguration,
    ManagedIdentityConfiguration,
    ServerlessComputeSettings,
    Workspace,
)
from azure.ai.ml.operations import WorkspaceOperations
from azure.core.polling import LROPoller
import urllib.parse


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_operation(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2023_06_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
    mock_aml_services_workspace_dataplane: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2023_06_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
        dataplane_client=mock_aml_services_workspace_dataplane,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


@pytest.fixture
def mock_workspace_operation_aug_2023_preview(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2023_08_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
    mock_aml_services_workspace_dataplane: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2023_08_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
        dataplane_client=mock_aml_services_workspace_dataplane,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


def gen_subnet_name(
    subscription_id: Optional[UUID] = None,
    resource_group: Optional[str] = None,
    vnet: Optional[str] = None,
    subnet_name: Optional[str] = None,
) -> str:
    sub = subscription_id or uuid4()
    rg = resource_group or "test_resource_group"
    virtualnet = vnet or "testvnet"
    subnet = subnet_name or "testsubnet"
    return f"/subscriptions/{sub}/resourceGroups/{rg}/providers/Microsoft.Network/virtualNetworks/{virtualnet}/subnets/{subnet}"


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

    def test_get(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("urllib.parse.urlparse")
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
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations._populate_arm_parameters", return_value=({}, {}, {}))
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation.begin_create(workspace=Workspace(name="name"))

    def test_update(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("urllib.parse.urlparse")
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

    def test_update_with_role_assignemnt(
        self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture
    ) -> None:
        mocker.patch("urllib.parse.urlparse")
        mocker.patch(
            "azure.ai.ml.operations.WorkspaceOperations._populate_feature_store_role_assignment_parameters",
            return_value=({}, {}, {}),
        )
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)

        ws = Workspace(name="name", description="description", kind="featurestore")

        def outgoing_call(rg, name, params, polling, cls):
            assert rg == "test_resource_group"
            assert name == "name"
            assert params.description == "description"
            assert polling is True
            assert callable(cls)
            return DEFAULT

        mock_workspace_operation._operation.begin_update.side_effect = outgoing_call
        mock_workspace_operation.begin_update(
            ws,
            update_dependent_resources=True,
            grant_materialization_identity_permission=True,
            update_workspace_role_assignment=True,
            update_offline_store_role_assignment=True,
            update_online_store_role_assignment=True,
        )
        mock_workspace_operation._operation.begin_update.assert_called()

    def test_delete(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("urllib.parse.urlparse")
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_generic_arm_resource_by_arm_id", return_value=None
        )
        mock_workspace_operation.begin_delete("randstr", delete_dependent_resources=True)
        mock_workspace_operation._operation.begin_delete.assert_called_once()

    def test_purge(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("urllib.parse.urlparse")
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_generic_arm_resource_by_arm_id", return_value=None
        )
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

    @pytest.mark.parametrize(
        "serverless_compute_settings",
        [
            None,
            ServerlessComputeSettings(custom_subnet=gen_subnet_name(vnet="testvnet", subnet_name="testsubnet")),
            ServerlessComputeSettings(custom_subnet=gen_subnet_name(subnet_name="npip"), no_public_ip=True),
        ],
    )
    def test_create_workspace_with_serverless_custom_vnet(
        self,
        serverless_compute_settings: ServerlessComputeSettings,
        mock_workspace_operation_aug_2023_preview: WorkspaceOperations,
        mocker: MockFixture,
    ) -> None:
        ws = Workspace(name="name", location="test", serverless_compute=serverless_compute_settings)
        spy = mocker.spy(WorkspaceOperations, "_populate_arm_parameters")

        mock_workspace_operation_aug_2023_preview._operation.get = MagicMock(return_value=None)
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation_aug_2023_preview.begin_create(ws)
        (_, param, _) = spy.spy_return
        settings = param["serverless_compute_settings"]["value"]
        if serverless_compute_settings is None:
            # Will return empty dict if serverless_compute_settings is None
            assert len(settings) == 0
        else:
            RestServerlessComputeSettings.deserialize(settings) == serverless_compute_settings._to_rest_object()

    @pytest.mark.parametrize(
        "new_settings",
        [
            ServerlessComputeSettings(
                custom_subnet=gen_subnet_name(vnet="testvnet", subnet_name="testsubnet"), no_public_ip=False
            ),
            ServerlessComputeSettings(
                custom_subnet=gen_subnet_name(vnet="testvnet", subnet_name="testsubnet"), no_public_ip=True
            ),
        ],
    )
    def test_can_update_of_serverless_compute_settings(
        self,
        new_settings: ServerlessComputeSettings,
        mock_workspace_operation_aug_2023_preview: WorkspaceOperations,
        mocker: MockFixture,
    ) -> None:
        original_settings = ServerlessComputeSettings(
            custom_subnet=gen_subnet_name(vnet="testvnet", subnet_name="default"), no_public_ip=False
        )
        wsname = "fake"
        ws = Workspace(name=wsname, location="test", serverless_compute=new_settings)

        key = CustomerManagedKey()
        original_workspace = Workspace(
            name=wsname,
            location="test",
            serverless_compute=original_settings,
            customer_managed_key=key,
        )
        rest_workspace: RestWorkspace = original_workspace._to_rest_object()  # pylint: disable=protected-access
        mock_workspace_operation_aug_2023_preview._operation.get = MagicMock(return_value=rest_workspace)
        spy = mocker.spy(mock_workspace_operation_aug_2023_preview._operation, "begin_update")
        mock_workspace_operation_aug_2023_preview.begin_update(ws)
        assert (
            ServerlessComputeSettings._from_rest_object(spy.call_args[0][2].serverless_compute_settings) == new_settings
        )

    def test_can_remove_serverless_compute_settings_via_none_subnet_and_false_npip(
        self, mock_workspace_operation_aug_2023_preview: WorkspaceOperations, mocker: MockFixture
    ) -> None:
        original_settings = ServerlessComputeSettings(
            custom_subnet=gen_subnet_name(vnet="testvnet", subnet_name="default"), no_public_ip=False
        )
        removal_settings = ServerlessComputeSettings(custom_subnet=None, no_public_ip=False)
        wsname = "fake"
        ws = Workspace(name=wsname, location="test", serverless_compute=removal_settings)

        key = CustomerManagedKey()
        original_workspace = Workspace(
            name=wsname,
            location="test",
            serverless_compute=original_settings,
            customer_managed_key=key,
        )
        rest_workspace: RestWorkspace = original_workspace._to_rest_object()  # pylint: disable=protected-access
        mock_workspace_operation_aug_2023_preview._operation.get = MagicMock(return_value=rest_workspace)
        spy = mocker.spy(mock_workspace_operation_aug_2023_preview._operation, "begin_update")
        mock_workspace_operation_aug_2023_preview.begin_update(ws)
        assert (
            ServerlessComputeSettings._from_rest_object(spy.call_args[0][2].serverless_compute_settings)
            == ServerlessComputeSettings()
        )

    def test_can_remove_via_file(
        self, mock_workspace_operation_aug_2023_preview: WorkspaceOperations, mocker: MockFixture
    ) -> None:
        import os

        removal_settings = ServerlessComputeSettings(custom_subnet=None, no_public_ip=False)
        wsname = "fake"
        config_dir = os.path.join("tests", "test_configs", "workspace")
        default_source = os.path.join(config_dir, "workspace_min_with_serverless.yaml")
        ws = load_workspace(source=default_source)
        assert ws.serverless_compute.custom_subnet is not None
        assert ws.serverless_compute.no_public_ip
        rest_workspace = ws._to_rest_object()  # pylint: disable=protected-access
        mock_workspace_operation_aug_2023_preview._operation.get = MagicMock(return_value=rest_workspace)
        spy = mocker.spy(mock_workspace_operation_aug_2023_preview._operation, "begin_update")
        ws_update = load_workspace(source=os.path.join(config_dir, "workspace_removing_serverless.yaml"))
        mock_workspace_operation_aug_2023_preview.begin_update(ws_update)
        assert (
            ServerlessComputeSettings._from_rest_object(spy.call_args[0][2].serverless_compute_settings)
            == ServerlessComputeSettings()
        )
