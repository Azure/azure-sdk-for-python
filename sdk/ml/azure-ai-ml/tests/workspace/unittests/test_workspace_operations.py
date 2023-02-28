from typing import Callable
from unittest.mock import DEFAULT, Mock, call, patch

import pytest
from pytest_mock import MockFixture

from azure.ai.ml import MLClient, load_workspace
from azure.ai.ml._restclient.v2022_12_01_preview.models import (
    EncryptionKeyVaultUpdateProperties,
    EncryptionUpdateProperties,
)
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml.entities import (
    CustomerManagedKey,
    IdentityConfiguration,
    ManagedIdentityConfiguration,
    Workspace,
    WorkspaceConnection,
)
from azure.ai.ml.operations import WorkspaceOperations
from azure.core.polling import LROPoller


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_operation(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2022_12_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> WorkspaceOperations:
    yield WorkspaceOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2022_12_01_preview,
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

    def test_begin_create_featurestore_kind(
        self,
        mock_workspace_operation: WorkspaceOperations,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=None)
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations._populate_arm_paramaters", return_value=({}, {}, {}))
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation.begin_create(workspace=Workspace(name="name", kind="FeatureStore"))

    def test_begin_create_with_resource_group(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture):
        ws = Workspace(
            name="name",
            resource_group="another_resource_group",
        )
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations._populate_arm_paramaters", return_value=({}, {}, {}))
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)

        def outgoing_call(rg, name):
            assert rg == "another_resource_group"
            assert name == "name"
            return None

        mock_workspace_operation._operation.get.side_effect = outgoing_call
        mock_workspace_operation.begin_create(workspace=ws)
        mock_workspace_operation._operation.get.assert_called()

    def test_create_get_exception_swallow(
        self,
        mock_workspace_operation: WorkspaceOperations,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", side_effect=Exception)
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations._populate_arm_paramaters", return_value=({}, {}, {}))
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation.begin_create(workspace=Workspace(name="name"))

    def test_begin_create_existing_ws(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture):
        def outgoing_call(rg, name, params, polling, cls):
            assert name == "name"
            return DEFAULT

        mock_workspace_operation._operation.begin_update.side_effect = outgoing_call
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=Workspace(name="name"))
        mock_workspace_operation.begin_create(workspace=Workspace(name="name"))
        mock_workspace_operation._operation.begin_update.assert_called()

    def test_update(self, mock_workspace_operation: WorkspaceOperations) -> None:
        ws = Workspace(
            name="name",
            tags={"key": "value"},
            description="description",
            display_name="friendly_name",
            image_build_compute="some_compute_name_to_update",
            public_network_access="Enabled",
            container_registry="foo_conntainer_registry",
            application_insights="foo_application_insights",
            identity=IdentityConfiguration(
                type=camel_to_snake(ManagedServiceIdentityType.USER_ASSIGNED),
                user_assigned_identities=[
                    ManagedIdentityConfiguration(resource_id="resource1"),
                    ManagedIdentityConfiguration(resource_id="resource2"),
                ],
            ),
            primary_user_assigned_identity="resource2",
            customer_managed_key=CustomerManagedKey(key_uri="new_cmk_uri"),
        )

        def outgoing_call(rg, name, params, polling, cls):
            assert rg == "test_resource_group"
            assert name == "name"
            assert params.description == "description"
            assert params.friendly_name == "friendly_name"
            assert params.image_build_compute == "some_compute_name_to_update"
            assert params.public_network_access == "Enabled"
            assert params.tags.get("key") == "value"
            assert params.container_registry == "foo_conntainer_registry"
            assert params.application_insights == "foo_application_insights"
            assert params.identity.type == ManagedServiceIdentityType.USER_ASSIGNED
            assert len(params.identity.user_assigned_identities) == 2
            assert params.primary_user_assigned_identity == "resource2"
            assert params.encryption == EncryptionUpdateProperties(
                key_vault_properties=EncryptionKeyVaultUpdateProperties(
                    key_identifier="new_cmk_uri",
                )
            )
            assert polling is True
            assert callable(cls)
            return DEFAULT

        mock_workspace_operation._operation.begin_update.side_effect = outgoing_call
        mock_workspace_operation.begin_update(ws, update_dependent_resources=True)
        mock_workspace_operation._operation.begin_update.assert_called()

    def test_update_with_empty_property_values(
        self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture
    ) -> None:
        ws = Workspace(name="name", description="", display_name="", image_build_compute="")
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=ws)

        def outgoing_call(rg, name, params, polling, cls):
            assert rg == "test_resource_group"
            assert name == "name"
            assert params.description == ""  # empty string is supported for description.
            assert params.friendly_name == ""  # empty string is supported for friendly name.
            assert params.image_build_compute == ""  # was set to empty string, for user to remove the property value.
            assert params.identity is None
            assert params.primary_user_assigned_identity is None
            assert (
                params.public_network_access is None
            )  # was not set for update, no change on service side for this property.
            assert polling is True
            assert callable(cls)
            return DEFAULT

        mock_workspace_operation._operation.begin_update.side_effect = outgoing_call
        mock_workspace_operation.begin_update(ws)
        mock_workspace_operation._operation.begin_update.assert_called()

    def test_delete_no_wait(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml.operations._workspace_operations.delete_resource_by_arm_id", return_value=None)
        mock_workspace_operation.begin_delete("randstr", delete_dependent_resources=True)
        mock_workspace_operation._operation.begin_delete.assert_called_once()

    def test_delete_wait(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml.operations._workspace_operations.delete_resource_by_arm_id", return_value=None)
        mocker.patch("azure.ai.ml._utils._azureml_polling.polling_wait", return_value=LROPoller)
        mock_workspace_operation.begin_delete("randstr", delete_dependent_resources=True)
        mock_workspace_operation._operation.begin_delete.assert_called_once()

    def test_delete_wait_exception(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        patch("azure.ai.ml.operations._workspace_operations.delete_resource_by_arm_id", return_value=None)
        patch("azure.ai.ml._utils._azureml_polling.polling_wait", side_effect=Exception)
        with pytest.raises(Exception):
            mock_workspace_operation.begin_delete("randstr", delete_dependent_resources=True)
            mock_workspace_operation._operation.begin_delete.assert_called_once()

    def test_begin_diagnose_no_wait(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mock_workspace_operation.begin_diagnose(name="random_name")
        mock_workspace_operation._operation.begin_diagnose.assert_called_once()
        mocker.patch("azure.ai.ml._restclient.v2022_10_01.models.DiagnoseRequestProperties", return_value=None)

    def test_begin_diagnose_wait(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mock_workspace_operation.begin_diagnose(name="random_name")
        mock_workspace_operation._operation.begin_diagnose.assert_called_once()
        mocker.patch("azure.ai.ml._restclient.v2022_10_01.models.DiagnoseRequestProperties", return_value=None)

    def test_populate_arm_paramaters(self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture) -> None:
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations.get_resource_group_location", return_value="random_name"
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations.get_default_log_analytics_arm_id",
            return_value=("random_id", True),
        )
        mock_workspace_operation._populate_arm_paramaters(workspace=Workspace(name="name"))

    def test_populate_arm_paramaters_other_branches(
        self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations.get_resource_group_location", return_value="random_name"
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations.get_resource_and_group_name",
            return_value=("resource_name", "group_name"),
        )
        ws = Workspace(name="name")
        ws.display_name = "display_name"
        ws.description = "description"
        ws.key_vault = "key_vault"
        ws.storage_account = "storage_account"
        ws.application_insights = "application_insights"
        ws.container_registry = "container_registry"
        ws.customer_managed_key = CustomerManagedKey("key", "url")
        ws.hbi_workspace = "hbi_workspace"
        ws.public_network_access = "public_network_access"
        ws.image_build_compute = "image_build_compute"
        ws.tags = {"k": "v"}
        ws.param = {"tagValues": {"value": {}}}
        mock_workspace_operation._populate_arm_paramaters(workspace=ws)

    def test_populate_arm_paramaters_feature_store(
        self, mock_workspace_operation: WorkspaceOperations, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations.get_resource_group_location", return_value="random_name"
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations.get_default_log_analytics_arm_id",
            return_value=("random_id", True),
        )
        setup_feature_store = True
        offline_store_connection = WorkspaceConnection(
            name="offline_connecttion",
            target="target",
            type="azure_data_lake_gen2",
            credentials=ManagedIdentityConfiguration(client_id="clientid", resource_id="resourceid"),
        )
        mock_workspace_operation._populate_arm_paramaters(
            workspace=Workspace(name="name"),
            setup_feature_store=setup_feature_store,
            offline_store_connection=offline_store_connection,
        )

    def test_check_workspace_name(self, mock_workspace_operation: WorkspaceOperations):
        mock_workspace_operation._default_workspace_name = None
        with pytest.raises(Exception):
            mock_workspace_operation._check_workspace_name(None)

    def test_load_uai_workspace_from_yaml(self, mock_workspace_operation: WorkspaceOperations):
        params_override = []
        wps = load_workspace("./tests/test_configs/workspace/workspace_uai.yaml", params_override=params_override)
        assert isinstance(wps.identity, IdentityConfiguration)
        assert isinstance(wps.identity.user_assigned_identities, list)
        assert isinstance(wps.identity.user_assigned_identities[0], ManagedIdentityConfiguration)
