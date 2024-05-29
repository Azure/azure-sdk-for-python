from typing import Optional
from unittest.mock import DEFAULT, MagicMock, Mock, patch
from uuid import UUID, uuid4

import pytest
from pytest_mock import MockFixture

from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    EncryptionKeyVaultUpdateProperties,
    EncryptionUpdateProperties,
    ManagedNetworkSettings,
)
from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    ServerlessComputeSettings as RestServerlessComputeSettings,
)
from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.constants import ManagedServiceIdentityType
from azure.ai.ml.entities import (
    CustomerManagedKey,
    FeatureStore,
    FeatureStoreSettings,
    FqdnDestination,
    IdentityConfiguration,
    IsolationMode,
    ManagedIdentityConfiguration,
    ManagedNetwork,
    MaterializationStore,
    PrivateEndpointDestination,
    ServerlessComputeSettings,
    ServiceTagDestination,
    Workspace,
)
from azure.ai.ml.operations._workspace_operations_base import WorkspaceOperationsBase
from azure.core.polling import LROPoller


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_workspace_operation_base(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2023_06_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
    mock_aml_services_workspace_dataplane: Mock,
) -> WorkspaceOperationsBase:
    yield WorkspaceOperationsBase(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2023_06_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
        dataplane_client=mock_aml_services_workspace_dataplane,
        requests_pipeline=mock_machinelearning_client._requests_pipeline,
    )


@pytest.fixture
def mock_workspace_operation_base_aug_2023_preview(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2023_08_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> WorkspaceOperationsBase:
    yield WorkspaceOperationsBase(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2023_08_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
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
    def test_begin_create(
        self,
        mock_workspace_operation_base: WorkspaceOperationsBase,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.WorkspaceOperationsBase._populate_arm_parameters",
            return_value=({}, {}, {}),
        )
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation_base.begin_create(workspace=Workspace(name="name"))

    def test_begin_create_featurestore_kind(
        self,
        mock_workspace_operation_base: WorkspaceOperationsBase,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.WorkspaceOperationsBase._populate_arm_parameters",
            return_value=({}, {}, {}),
        )
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation_base.begin_create(workspace=Workspace(name="name", kind="FeatureStore"))

    def test_begin_create_with_resource_group(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
    ):
        ws = Workspace(
            name="name",
            resource_group="another_resource_group",
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.WorkspaceOperationsBase._populate_arm_parameters",
            return_value=({}, {}, {}),
        )
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)

        def outgoing_call(rg, name):
            assert rg == "another_resource_group"
            assert name == "name"
            return None

        mock_workspace_operation_base._operation.get.side_effect = outgoing_call
        mock_workspace_operation_base.begin_create(workspace=ws)
        mock_workspace_operation_base._operation.get.assert_called()

    def test_get(self, mock_workspace_operation_base: WorkspaceOperationsBase) -> None:
        def outgoing_get_call(rg, name):
            ws = Workspace(name=name)
            ws.managed_network = ManagedNetwork(
                isolation_mode=IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND,
                outbound_rules=[
                    FqdnDestination(name="fqdn-rule", destination="google.com"),
                    PrivateEndpointDestination(
                        name="perule", service_resource_id="/storageid", subresource_target="blob", spark_enabled=False
                    ),
                    ServiceTagDestination(
                        name="servicetag-rule", service_tag="sometag", protocol="*", port_ranges="1,2"
                    ),
                ],
            )
            return ws._to_rest_object()

        mock_workspace_operation_base._operation.get.side_effect = outgoing_get_call
        ws = mock_workspace_operation_base.get(name="random_name", resource_group="rg")
        mock_workspace_operation_base._operation.get.assert_called_once()

        assert ws.managed_network is not None
        assert ws.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND
        rules = ws.managed_network.outbound_rules
        assert isinstance(rules[0], FqdnDestination)
        assert rules[0].destination == "google.com"

        assert isinstance(rules[1], PrivateEndpointDestination)
        assert rules[1].service_resource_id == "/storageid"
        assert rules[1].spark_enabled == False
        assert rules[1].subresource_target == "blob"

        assert isinstance(rules[2], ServiceTagDestination)
        assert rules[2].service_tag == "sometag"
        assert rules[2].protocol == "*"
        assert rules[2].port_ranges == "1,2"

    def test_create_get_exception_swallow(
        self,
        mock_workspace_operation_base: WorkspaceOperationsBase,
        mocker: MockFixture,
    ):
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", side_effect=Exception)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.WorkspaceOperationsBase._populate_arm_parameters",
            return_value=({}, {}, {}),
        )
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation_base.begin_create(workspace=Workspace(name="name"))

    def test_begin_create_existing_ws(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
    ):
        def outgoing_call(rg, name, params, polling, cls):
            assert name == "name"
            return DEFAULT

        mock_workspace_operation_base._operation.begin_update.side_effect = outgoing_call
        mocker.patch("azure.ai.ml.operations.WorkspaceOperations.get", return_value=Workspace(name="name"))
        mock_workspace_operation_base.begin_create(workspace=Workspace(name="name"))
        mock_workspace_operation_base._operation.begin_update.assert_called()

    def test_update(self, mock_workspace_operation_base: WorkspaceOperationsBase) -> None:
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
            managed_network=ManagedNetwork(),
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
            assert params.managed_network.isolation_mode == "Disabled"
            assert params.managed_network.outbound_rules == {}
            assert polling is True
            assert callable(cls)
            return DEFAULT

        mock_workspace_operation_base._operation.begin_update.side_effect = outgoing_call
        mock_workspace_operation_base.begin_update(ws, update_dependent_resources=True)
        mock_workspace_operation_base._operation.begin_update.assert_called()

    def test_update_with_empty_property_values(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
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

        mock_workspace_operation_base._operation.begin_update.side_effect = outgoing_call
        mock_workspace_operation_base.begin_update(ws)
        mock_workspace_operation_base._operation.begin_update.assert_called()

    def test_delete_no_wait(self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_generic_arm_resource_by_arm_id", return_value=None
        )
        mock_workspace_operation_base.begin_delete("randstr", delete_dependent_resources=True)
        mock_workspace_operation_base._operation.begin_delete.assert_called_once()

    def test_delete_wait(self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture) -> None:
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_generic_arm_resource_by_arm_id", return_value=None
        )
        mocker.patch("azure.ai.ml._utils._azureml_polling.polling_wait", return_value=LROPoller)
        mock_workspace_operation_base.begin_delete("randstr", delete_dependent_resources=True)
        mock_workspace_operation_base._operation.begin_delete.assert_called_once()

    def test_delete_wait_exception(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
    ) -> None:
        patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        patch("azure.ai.ml._utils._azureml_polling.polling_wait", side_effect=Exception)
        with pytest.raises(Exception):
            mock_workspace_operation_base.begin_delete("randstr", delete_dependent_resources=True)
            mock_workspace_operation_base._operation.begin_delete.assert_called_once()

    def _populate_arm_parameters(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_resource_group_location", return_value="random_name"
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_log_analytics_arm_id",
            return_value=("random_id", True),
        )
        mock_workspace_operation_base._populate_arm_parameters(workspace=Workspace(name="name"))

    def test_populate_arm_parameters_other_branches(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_resource_group_location", return_value="random_name"
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_resource_and_group_name",
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
        mock_workspace_operation_base._populate_arm_parameters(workspace=ws)

    def test_populate_feature_store_arm_parameters(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_resource_group_location", return_value="random_name"
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_log_analytics_arm_id",
            return_value=("random_id", True),
        )

        # test create feature store
        feature_store = FeatureStore(name="name", resource_group="rg", location="eastus2euap")
        template, param, _ = mock_workspace_operation_base._populate_arm_parameters(
            workspace=feature_store, grant_materialization_permissions=True
        )

        assert param["kind"]["value"] == "featurestore"
        assert param["location"]["value"] == "eastus2euap"
        assert param["grant_materialization_permissions"]["value"] == "true"
        assert param["materializationIdentityOption"]["value"] == "new"
        assert param["materialization_identity_name"]["value"].startswith("materialization-uai-")
        assert param["materialization_identity_subscription_id"]["value"] == "test_subscription"
        assert param["materialization_identity_resource_group_name"]["value"] == "rg"
        assert param["offlineStoreStorageAccountOption"]["value"] == "new"
        assert param["offline_store_storage_account_name"]["value"] == param["storageAccountName"]["value"]
        assert param["offline_store_container_name"]["value"]
        assert param["offline_store_resource_group_name"]["value"] == "rg"
        assert param["offline_store_subscription_id"]["value"] == "test_subscription"
        assert param["offline_store_connection_name"]["value"] is None
        assert param["online_store_resource_id"]["value"] is None
        assert param["online_store_resource_group_name"]["value"] is None
        assert param["online_store_subscription_id"]["value"] is None
        assert param["online_store_connection_name"]["value"] is None

        # test create feature store with materialization identity
        mock_materialization_identity_resource_id = (
            "/subscriptions/sub/resourceGroups/rg1/providers/Microsoft.ManagedIdentity/userAssignedIdentities/uai"
        )
        feature_store = FeatureStore(
            name="name",
            resource_group="rg",
        )
        template, param, _ = mock_workspace_operation_base._populate_arm_parameters(
            workspace=feature_store,
            grant_materialization_permissions=False,
            materialization_identity=ManagedIdentityConfiguration(
                client_id="client_id", resource_id=mock_materialization_identity_resource_id
            ),
        )

        assert param["kind"]["value"] == "featurestore"
        assert param["grant_materialization_permissions"]["value"] == "false"
        assert param["materializationIdentityOption"]["value"] == "existing"
        assert param["materialization_identity_name"]["value"] == "uai"
        assert param["materialization_identity_resource_group_name"]["value"] == "rg1"
        assert param["materialization_identity_subscription_id"]["value"] == "sub"

        # test create feature store with offline store
        mock_offline_store_target = "/subscriptions/sub1/resourceGroups/rg1/providers/Microsoft.Storage/storageAccounts/offlinestorage/blobServices/default/containers/offlinestore"
        feature_store._feature_store_settings = FeatureStoreSettings(
            offline_store_connection_name="OfflineStoreConnectionName",
            online_store_connection_name="",
        )
        template, param, _ = mock_workspace_operation_base._populate_arm_parameters(
            workspace=feature_store, offline_store_target=mock_offline_store_target
        )
        assert param["kind"]["value"] == "featurestore"
        assert param["offlineStoreStorageAccountOption"]["value"] == "existing"
        assert param["offline_store_storage_account_name"]["value"] == "offlinestorage"
        assert param["offline_store_container_name"]["value"] == "offlinestore"
        assert param["offline_store_resource_group_name"]["value"] == "rg1"
        assert param["offline_store_subscription_id"]["value"] == "sub1"
        assert param["offline_store_connection_name"]["value"] == "OfflineStoreConnectionName"
        assert param["online_store_connection_name"]["value"] is None

        # offline store with provided storage account
        mock_storage_account = (
            "/subscriptions/sub2/resourceGroups/rg2/providers/Microsoft.Storage/storageAccounts/storage"
        )
        feature_store = FeatureStore(
            name="name",
            resource_group="rg",
            storage_account=mock_storage_account,
        )
        template, param, _ = mock_workspace_operation_base._populate_arm_parameters(
            workspace=feature_store, offline_store_target=mock_offline_store_target
        )
        assert param["kind"]["value"] == "featurestore"
        assert param["offlineStoreStorageAccountOption"]["value"] == "existing"
        assert param["offline_store_storage_account_name"]["value"] == "offlinestorage"
        assert param["offline_store_container_name"]["value"] == "offlinestore"
        assert param["offline_store_resource_group_name"]["value"] == "rg1"
        assert param["offline_store_subscription_id"]["value"] == "sub1"
        assert param["offline_store_connection_name"]["value"] is None

        template, param, _ = mock_workspace_operation_base._populate_arm_parameters(
            workspace=feature_store,
        )
        assert param["kind"]["value"] == "featurestore"
        assert param["offlineStoreStorageAccountOption"]["value"] == "new"
        assert param["offline_store_storage_account_name"]["value"]
        assert param["offline_store_storage_account_name"]["value"] != "storage"
        assert param["offline_store_container_name"]["value"]
        assert param["offline_store_resource_group_name"]["value"] == "rg"
        assert param["offline_store_subscription_id"]["value"] == "test_subscription"
        assert param["offline_store_connection_name"]["value"] is None

        # test create feature store with online store
        mock_online_store_target = "/subscriptions/sub3/resourceGroups/rg3/providers/Microsoft.Cache/Redis/onlinestore"
        feature_store = FeatureStore(name="name", resource_group="rg")
        feature_store._feature_store_settings = FeatureStoreSettings(
            offline_store_connection_name="OfflineStoreConnectionName",
            online_store_connection_name="OnlineStoreConnectionName",
        )
        template, param, _ = mock_workspace_operation_base._populate_arm_parameters(
            workspace=feature_store, online_store_target=mock_online_store_target
        )
        assert param["kind"]["value"] == "featurestore"
        assert param["online_store_resource_id"]["value"] == mock_online_store_target
        assert param["online_store_resource_group_name"]["value"] == "rg3"
        assert param["online_store_subscription_id"]["value"] == "sub3"
        assert param["offline_store_connection_name"]["value"] == "OfflineStoreConnectionName"
        assert param["online_store_connection_name"]["value"] == "OnlineStoreConnectionName"

    def test_generate_materialization_identity_name(self) -> None:
        from azure.ai.ml.operations._workspace_operations_base import _generate_materialization_identity

        # case1
        ws = Workspace(name="workspace_name", resource_group="rG", location="eastus")
        name = _generate_materialization_identity(workspace=ws, subscription_id="sUb", resources_being_deployed={})
        ws1 = Workspace(name="Workspace_Name", resource_group="Rg", location="eastus")
        name1 = _generate_materialization_identity(workspace=ws1, subscription_id="suB", resources_being_deployed={})
        assert name == name1

        # case2
        ws1 = Workspace(name="workspace_name", resource_group="rg", location="westus")
        name1 = _generate_materialization_identity(workspace=ws1, subscription_id="sub", resources_being_deployed={})
        assert name != name1

        # case3
        ws1 = Workspace(name="workspaceName", resource_group="rg", location="eastus")
        name1 = _generate_materialization_identity(workspace=ws1, subscription_id="sub", resources_being_deployed={})
        assert name != name1

        # case4
        ws = Workspace(name="longWorkspace-12Name345", resource_group="resourceGroup")
        name = _generate_materialization_identity(
            workspace=ws, subscription_id="Subscription", resources_being_deployed={}
        )
        assert name is not None

    def test_populate_feature_store_role_assignments_paramaters(
        self, mock_workspace_operation_base: WorkspaceOperationsBase, mocker: MockFixture
    ) -> None:
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_resource_group_location", return_value="random_name"
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_log_analytics_arm_id",
            return_value=("random_id", True),
        )
        template, param, _ = mock_workspace_operation_base._populate_feature_store_role_assignment_parameters(
            workspace=FeatureStore(name="name"),
            materialization_identity_id="/subscriptions/sub/resourcegroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity",
            offline_store_target="/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/test_storage/blobServices/default/containers/offlinestore",
            online_store_target="/subscriptions/sub1/resourceGroups/mdctest/providers/Microsoft.Cache/Redis/onlinestore",
            update_workspace_role_assignment=True,
            update_offline_store_role_assignment=True,
            update_online_store_role_assignment=True,
            location="eastus2euap",
        )

        assert template is not None
        assert param["location"] == {"value": "eastus2euap"}
        assert param["materialization_identity_resource_id"] == {
            "value": "/subscriptions/sub/resourcegroups/rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/identity"
        }
        assert param["offline_store_target"] == {
            "value": "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/test_storage/blobServices/default/containers/offlinestore"
        }
        assert param["offline_store_resource_group_name"] == {"value": "rg"}
        assert param["offline_store_subscription_id"] == {"value": "sub"}
        assert param["online_store_target"] == {
            "value": "/subscriptions/sub1/resourceGroups/mdctest/providers/Microsoft.Cache/Redis/onlinestore"
        }
        assert param["online_store_resource_group_name"] == {"value": "mdctest"}
        assert param["online_store_subscription_id"] == {"value": "sub1"}
        assert param["update_workspace_role_assignment"] == {"value": "true"}
        assert param["update_offline_store_role_assignment"] == {"value": "true"}
        assert param["update_online_store_role_assignment"] == {"value": "true"}

        # false case
        template, param, _ = mock_workspace_operation_base._populate_feature_store_role_assignment_parameters(
            workspace=FeatureStore(name="name"),
            materialization_identity_id="",
            offline_store_target="",
            online_store_target="",
            update_workspace_role_assignment=False,
            update_offline_store_role_assignment=False,
            update_online_store_role_assignment=False,
        )

        assert template is not None
        assert param["materialization_identity_resource_id"] == {"value": None}
        assert param["offline_store_target"] == {"value": None}
        assert param["offline_store_resource_group_name"] == {"value": None}
        assert param["offline_store_subscription_id"] == {"value": None}
        assert param["online_store_target"] == {"value": None}
        assert param["online_store_resource_group_name"] == {"value": None}
        assert param["online_store_subscription_id"] == {"value": None}
        assert param["update_workspace_role_assignment"] == {"value": "false"}
        assert param["update_offline_store_role_assignment"] == {"value": "false"}
        assert param["update_online_store_role_assignment"] == {"value": "false"}

    def test_check_workspace_name(self, mock_workspace_operation_base: WorkspaceOperationsBase):
        mock_workspace_operation_base._default_workspace_name = None
        with pytest.raises(Exception):
            mock_workspace_operation_base._check_workspace_name(None)

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
        mock_workspace_operation_base_aug_2023_preview: WorkspaceOperationsBase,
        mocker: MockFixture,
    ) -> None:
        ws = Workspace(name="name", location="test", serverless_compute=serverless_compute_settings)
        spy = mocker.spy(WorkspaceOperationsBase, "_populate_arm_parameters")

        mock_workspace_operation_base_aug_2023_preview._operation.get = MagicMock(return_value=None)
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)
        mock_workspace_operation_base_aug_2023_preview.begin_create(ws)
        (_, param, _) = spy.spy_return
        settings = param["serverless_compute_settings"]["value"]
        if serverless_compute_settings is None:
            # settings is an empty JSON REST object at this point
            assert len(settings) == 0
        else:
            RestServerlessComputeSettings.deserialize(settings) == serverless_compute_settings._to_rest_object()

    @pytest.mark.parametrize(
        "serverless_compute_settings",
        [
            None,
            ServerlessComputeSettings(custom_subnet=gen_subnet_name(vnet="testvnet", subnet_name="testsubnet")),
            ServerlessComputeSettings(custom_subnet=gen_subnet_name(subnet_name="npip"), no_public_ip=True),
        ],
    )
    def test_update_workspace_with_serverless_custom_vnet(
        self,
        serverless_compute_settings: ServerlessComputeSettings,
        mock_workspace_operation_base_aug_2023_preview: WorkspaceOperationsBase,
        mocker: MockFixture,
    ) -> None:
        ws = Workspace(name="name", location="test", serverless_compute=serverless_compute_settings)
        spy = mocker.spy(mock_workspace_operation_base_aug_2023_preview._operation, "begin_update")
        mock_workspace_operation_base_aug_2023_preview.begin_update(ws)
        if serverless_compute_settings is None:
            assert spy.call_args[0][2].serverless_compute_settings is None
        else:
            assert (
                ServerlessComputeSettings._from_rest_object(spy.call_args[0][2].serverless_compute_settings)
                == serverless_compute_settings
            )

    @pytest.mark.parametrize(
        "new_settings",
        [
            ServerlessComputeSettings(custom_subnet=gen_subnet_name(vnet="testvnet", subnet_name="testsubnet")),
            ServerlessComputeSettings(no_public_ip=True),
        ],
    )
    def test_can_perform_partial_update_of_serverless_compute_settings(
        self,
        new_settings: ServerlessComputeSettings,
        mock_workspace_operation_base_aug_2023_preview: WorkspaceOperationsBase,
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
        mock_workspace_operation_base_aug_2023_preview._operation.get = MagicMock(return_value=rest_workspace)
        spy = mocker.spy(mock_workspace_operation_base_aug_2023_preview._operation, "begin_update")
        mock_workspace_operation_base_aug_2023_preview.begin_update(ws)
        assert (
            ServerlessComputeSettings._from_rest_object(spy.call_args[0][2].serverless_compute_settings) == new_settings
        )
