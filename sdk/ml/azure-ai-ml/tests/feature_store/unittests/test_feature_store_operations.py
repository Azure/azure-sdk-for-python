from unittest.mock import DEFAULT, Mock

import pytest
from marshmallow import ValidationError
from pytest_mock import MockFixture

from azure.ai.ml._scope_dependent_operations import OperationScope
from azure.ai.ml.entities import FeatureStore, Workspace
from azure.ai.ml.entities._feature_store._constants import (
    OFFLINE_MATERIALIZATION_STORE_TYPE,
    OFFLINE_STORE_CONNECTION_NAME,
    ONLINE_MATERIALIZATION_STORE_TYPE,
    ONLINE_STORE_CONNECTION_NAME,
)
from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore
from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings
from azure.ai.ml.operations._feature_store_operations import FeatureStoreOperations
from azure.core.polling import LROPoller

MOCK_MATERIALIZATION_STORE_TARGET = "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/test_storage/blobServices/default/containers/offlinestore"
MOCK_MATERIALIZATION_STORE_TARGET_INCOMPLETE = (
    "/subscriptions/sub/resourceGroups/rg/providers/Microsoft.Storage/storageAccounts/test_storage"
)


@pytest.fixture
def mock_credential() -> Mock:
    yield Mock()


@pytest.fixture
def mock_feature_store_operation(
    mock_workspace_scope: OperationScope,
    mock_aml_services_2023_08_01_preview: Mock,
    mock_machinelearning_client: Mock,
    mock_credential: Mock,
) -> FeatureStoreOperations:
    yield FeatureStoreOperations(
        operation_scope=mock_workspace_scope,
        service_client=mock_aml_services_2023_08_01_preview,
        all_operations=mock_machinelearning_client._operation_container,
        credentials=mock_credential,
    )


@pytest.mark.unittest
@pytest.mark.data_experiences_test
class TestFeatureStoreOperation:
    @pytest.mark.parametrize("arg", ["resource_group", "subscription", "other_rand_str"])
    def test_list(self, arg: str, mock_feature_store_operation: FeatureStoreOperations) -> None:
        mock_feature_store_operation.list(scope=arg)
        if arg == "subscription":
            mock_feature_store_operation._operation.list_by_subscription.assert_called_once()
        else:
            mock_feature_store_operation._operation.list_by_resource_group.assert_called_once()

    def test_get(self, mock_feature_store_operation: FeatureStoreOperations) -> None:
        def outgoing_get_call(rg, name):
            from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings

            ws = Workspace(name=name, kind="featurestore")
            ws._feature_store_settings = FeatureStoreSettings(
                offline_store_connection_name=OFFLINE_STORE_CONNECTION_NAME,
                online_store_connection_name=ONLINE_STORE_CONNECTION_NAME,
            )
            return ws._to_rest_object()

        mock_feature_store_operation._operation.get.side_effect = outgoing_get_call
        featurestore = mock_feature_store_operation.get(name="random_name", resource_group="rg")
        mock_feature_store_operation._operation.get.assert_called_once()

        assert featurestore._kind == "featurestore"
        assert featurestore._feature_store_settings.offline_store_connection_name == OFFLINE_STORE_CONNECTION_NAME
        assert featurestore._feature_store_settings.online_store_connection_name == ONLINE_STORE_CONNECTION_NAME

    def test_begin_create(
        self,
        mock_feature_store_operation: FeatureStoreOperations,
        mocker: MockFixture,
    ):
        from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration

        IDENTITY_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/test_rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/new_identity"

        def outgoing_get_call(rg, name):
            return Workspace(name=name, kind="featurestore")._to_rest_object()

        mocker.patch("azure.ai.ml.operations._feature_store_operations.FeatureStoreOperations.get", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._feature_store_operations.FeatureStoreOperations._populate_arm_parameters",
            return_value=({}, {}, {}),
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.WorkspaceOperationsBase.begin_create",
            return_value=None,
        )
        mocker.patch("azure.ai.ml._arm_deployments.ArmDeploymentExecutor.deploy_resource", return_value=LROPoller)

        # create
        mock_feature_store_operation._operation.get.side_effect = Exception()
        mock_feature_store_operation.begin_create(feature_store=FeatureStore(name="name"))
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.assert_called_once()

        # create, no materialization identity is allowed
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.reset_mock()
        mock_feature_store_operation.begin_create(
            feature_store=FeatureStore(
                name="name",
                offline_store=MaterializationStore(
                    type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET
                ),
            )
        )
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.assert_called_once()
        call_kwargs = super(
            type(mock_feature_store_operation), mock_feature_store_operation
        ).begin_create.call_args.kwargs
        # remove this condition check when test env python version >= 3.8
        if isinstance(call_kwargs, dict):
            feature_store = call_kwargs["workspace"]
            feature_store_settings = feature_store._feature_store_settings
            offline_store_connection_name = feature_store_settings.offline_store_connection_name
            online_store_connection_name = feature_store_settings.online_store_connection_name
            assert offline_store_connection_name.startswith(OFFLINE_STORE_CONNECTION_NAME + "-")
            assert online_store_connection_name == None

        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.reset_mock()
        mock_feature_store_operation.begin_create(
            feature_store=FeatureStore(
                name="name",
                online_store=MaterializationStore(
                    type=ONLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET
                ),
            )
        )
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.assert_called_once()
        call_kwargs = super(
            type(mock_feature_store_operation), mock_feature_store_operation
        ).begin_create.call_args.kwargs
        # remove this condition check when test env python version >= 3.8
        if isinstance(call_kwargs, dict):
            feature_store = call_kwargs["workspace"]
            feature_store_settings = feature_store._feature_store_settings
            offline_store_connection_name = feature_store_settings.offline_store_connection_name
            online_store_connection_name = feature_store_settings.online_store_connection_name
            assert offline_store_connection_name.startswith(OFFLINE_STORE_CONNECTION_NAME + "-")
            assert online_store_connection_name.startswith(ONLINE_STORE_CONNECTION_NAME + "-")

        # create, with materialization identity
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.reset_mock()
        mock_feature_store_operation.begin_create(
            feature_store=FeatureStore(
                name="name",
                online_store=MaterializationStore(
                    type=ONLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET
                ),
                offline_store=MaterializationStore(
                    type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET
                ),
                materialization_identity=ManagedIdentityConfiguration(resource_id=IDENTITY_RESOURCE_ID),
            )
        )
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.assert_called_once()
        call_kwargs = super(
            type(mock_feature_store_operation), mock_feature_store_operation
        ).begin_create.call_args.kwargs
        # remove this condition check when test env python version >= 3.8
        if isinstance(call_kwargs, dict):
            feature_store = call_kwargs["workspace"]
            feature_store_settings = feature_store._feature_store_settings
            offline_store_connection_name = feature_store_settings.offline_store_connection_name
            online_store_connection_name = feature_store_settings.online_store_connection_name
            assert offline_store_connection_name.startswith(OFFLINE_STORE_CONNECTION_NAME + "-")
            assert online_store_connection_name.startswith(ONLINE_STORE_CONNECTION_NAME + "-")

        # create, with name only
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.reset_mock()
        mock_feature_store_operation.begin_create(feature_store=FeatureStore(name="name"))
        super(type(mock_feature_store_operation), mock_feature_store_operation).begin_create.assert_called_once()
        call_kwargs = super(
            type(mock_feature_store_operation), mock_feature_store_operation
        ).begin_create.call_args.kwargs
        # remove this condition check when test env python version >= 3.8
        if isinstance(call_kwargs, dict):
            feature_store = call_kwargs["workspace"]
            feature_store_settings = feature_store._feature_store_settings
            offline_store_connection_name = feature_store_settings.offline_store_connection_name
            online_store_connection_name = feature_store_settings.online_store_connection_name
            assert offline_store_connection_name.startswith(OFFLINE_STORE_CONNECTION_NAME + "-")
            assert online_store_connection_name == None

        # double create call
        mock_feature_store_operation._operation.get.side_effect = outgoing_get_call
        mock_feature_store_operation._operation.begin_update.side_effect = None
        mock_feature_store_operation.begin_create(feature_store=FeatureStore(name="name"))
        mock_feature_store_operation._operation.begin_update.assert_called()

    def test_update(self, mock_feature_store_operation: FeatureStoreOperations) -> None:
        fs = FeatureStore(
            name="name",
            description="description",
        )

        def outgoing_get_call(rg, name):
            from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings

            ws = Workspace(name=name, kind="featurestore")
            ws._feature_store_settings = FeatureStoreSettings()
            return ws._to_rest_object()

        def outgoing_call(rg, name, params, polling, cls):
            assert rg == "test_resource_group"
            assert name == "name"
            assert params.description == "description"
            assert polling is True
            assert callable(cls)
            return DEFAULT

        mock_feature_store_operation._operation.get.side_effect = outgoing_get_call
        mock_feature_store_operation._operation.begin_update.side_effect = outgoing_call
        mock_feature_store_operation.begin_update(fs, update_dependent_resources=True)
        mock_feature_store_operation._operation.begin_update.assert_called()

        with pytest.raises(ValidationError):
            mock_feature_store_operation.begin_update(
                feature_store=FeatureStore(
                    name="name",
                    offline_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET
                    ),
                )
            )
        with pytest.raises(ValidationError):
            mock_feature_store_operation.begin_update(
                feature_store=FeatureStore(
                    name="name",
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET_INCOMPLETE
                    ),
                )
            )
        with pytest.raises(ValidationError):
            mock_feature_store_operation.begin_update(
                feature_store=FeatureStore(
                    name="name",
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET
                    ),
                )
            )
        with pytest.raises(ValidationError):
            mock_feature_store_operation.begin_update(
                feature_store=FeatureStore(
                    name="name",
                    online_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=MOCK_MATERIALIZATION_STORE_TARGET
                    ),
                )
            )

    def test_update_with_role_assignments(
        self, mock_feature_store_operation: FeatureStoreOperations, mocker: MockFixture
    ) -> None:
        from azure.ai.ml.entities._credentials import ManagedIdentityConfiguration
        from azure.ai.ml.entities._feature_store.materialization_store import MaterializationStore

        EXISTING_IDENTITY_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/test_rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/exist_identity"
        EXISTING_OFFLINE_STORE_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/test_rg/providers/Microsoft.Storage/storageAccounts/test_storage/blobServices/default/containers/exist"
        EXISTING_ONLINE_STORE_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/mdctest/providers/Microsoft.Cache/Redis/exist"
        OFFLINE_STORE_CONNECTION_NAME = "offlineStoreConnectionName"
        ONLINE_STORE_CONNECTION_NAME = "onlineStoreConnectionName"
        NEW_IDENTITY_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/test_rg/providers/Microsoft.ManagedIdentity/userAssignedIdentities/new_identity"
        NEW_OFFLINE_STORE_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/test_rg/providers/Microsoft.Storage/storageAccounts/test_storage/blobServices/default/containers/new"
        NEW_ONLINE_STORE_RESOURCE_ID = "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourceGroups/mdctest/providers/Microsoft.Cache/Redis/new"

        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.WorkspaceOperationsBase.begin_update",
            return_value=None,
        )
        mocker.patch(
            "azure.ai.ml.operations._workspace_connections_operations.WorkspaceConnectionsOperations.get",
            return_value=None,
        )

        def outgoing_get_call(rg, name):
            from azure.ai.ml._utils.utils import camel_to_snake
            from azure.ai.ml.constants import ManagedServiceIdentityType
            from azure.ai.ml.entities import IdentityConfiguration, ManagedIdentityConfiguration
            from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings

            ws = Workspace(
                name=name,
                kind="featurestore",
                identity=IdentityConfiguration(
                    type=camel_to_snake(ManagedServiceIdentityType.USER_ASSIGNED),
                    user_assigned_identities=[
                        ManagedIdentityConfiguration(resource_id=EXISTING_IDENTITY_RESOURCE_ID),
                    ],
                ),
            )
            ws._feature_store_settings = FeatureStoreSettings(
                offline_store_connection_name=f"{OFFLINE_STORE_CONNECTION_NAME}-existing",
                online_store_connection_name=f"{ONLINE_STORE_CONNECTION_NAME}-existing",
            )
            return ws._to_rest_object()

        def outgoing_workspace_connection_call(resource_group_name, workspace_name, connection_name):
            if connection_name.startswith(OFFLINE_STORE_CONNECTION_NAME):
                from azure.ai.ml._restclient.v2023_04_01_preview.models import (
                    WorkspaceConnectionPropertiesV2,
                    WorkspaceConnectionPropertiesV2BasicResource,
                )

                resource = WorkspaceConnectionPropertiesV2BasicResource(
                    properties=WorkspaceConnectionPropertiesV2(
                        category=OFFLINE_MATERIALIZATION_STORE_TYPE, target=EXISTING_OFFLINE_STORE_RESOURCE_ID
                    )
                )
                return resource
            elif connection_name.startswith(ONLINE_STORE_CONNECTION_NAME):
                from azure.ai.ml._restclient.v2023_04_01_preview.models import (
                    WorkspaceConnectionPropertiesV2,
                    WorkspaceConnectionPropertiesV2BasicResource,
                )

                resource = WorkspaceConnectionPropertiesV2BasicResource(
                    properties=WorkspaceConnectionPropertiesV2(
                        category=ONLINE_MATERIALIZATION_STORE_TYPE, target=EXISTING_ONLINE_STORE_RESOURCE_ID
                    )
                )
                return resource
            else:
                raise Exception("Invalid exception")

        def perform_tests(testcases, mock_feature_store_operation):
            for testcase in testcases:
                mock_feature_store_operation.begin_update(testcase[0], update_dependent_resources=True)
                super(
                    type(mock_feature_store_operation), mock_feature_store_operation
                ).begin_update.assert_called_once()
                call_kwargs = super(
                    type(mock_feature_store_operation), mock_feature_store_operation
                ).begin_update.call_args.kwargs

                # remove this condition check when test env python version >= 3.8
                if isinstance(call_kwargs, dict):
                    feature_store_settings = call_kwargs["feature_store_settings"]
                    offline_store_connection_name = feature_store_settings.offline_store_connection_name
                    online_store_connection_name = feature_store_settings.online_store_connection_name
                    assert call_kwargs["grant_materialization_permissions"] == True
                    assert call_kwargs["update_workspace_role_assignment"] == testcase[1][0]
                    assert call_kwargs["update_offline_store_role_assignment"] == testcase[1][1]
                    assert call_kwargs["update_online_store_role_assignment"] == testcase[1][2]
                    assert call_kwargs["materialization_identity_id"] == testcase[1][3]
                    assert call_kwargs["offline_store_target"] == testcase[1][4]
                    assert call_kwargs["online_store_target"] == testcase[1][5]
                    assert (f"{OFFLINE_STORE_CONNECTION_NAME}-existing" == offline_store_connection_name) == testcase[
                        1
                    ][6]
                    assert (f"{ONLINE_STORE_CONNECTION_NAME}-existing" == online_store_connection_name) == testcase[1][
                        7
                    ]

                print(f"passed test case: {testcase}")
                super(type(mock_feature_store_operation), mock_feature_store_operation).begin_update.reset_mock()

        mock_feature_store_operation._operation.get.side_effect = outgoing_get_call

        # existing stores
        mock_feature_store_operation._workspace_connection_operation.get.side_effect = (
            outgoing_workspace_connection_call
        )

        testcases1 = [
            (FeatureStore(name="name", description="description"), [False, False, False, None, None, None, True, True]),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    materialization_identity=ManagedIdentityConfiguration(resource_id=NEW_IDENTITY_RESOURCE_ID),
                ),
                [
                    True,
                    True,
                    True,
                    NEW_IDENTITY_RESOURCE_ID,
                    EXISTING_OFFLINE_STORE_RESOURCE_ID,
                    EXISTING_ONLINE_STORE_RESOURCE_ID,
                    True,
                    True,
                ],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=NEW_OFFLINE_STORE_RESOURCE_ID
                    ),
                ),
                [False, True, False, EXISTING_IDENTITY_RESOURCE_ID, NEW_OFFLINE_STORE_RESOURCE_ID, None, False, True],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    online_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=NEW_ONLINE_STORE_RESOURCE_ID
                    ),
                ),
                [False, False, True, EXISTING_IDENTITY_RESOURCE_ID, None, NEW_ONLINE_STORE_RESOURCE_ID, True, False],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    materialization_identity=ManagedIdentityConfiguration(resource_id=NEW_IDENTITY_RESOURCE_ID),
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=NEW_OFFLINE_STORE_RESOURCE_ID
                    ),
                    online_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=NEW_ONLINE_STORE_RESOURCE_ID
                    ),
                ),
                [
                    True,
                    True,
                    True,
                    NEW_IDENTITY_RESOURCE_ID,
                    NEW_OFFLINE_STORE_RESOURCE_ID,
                    NEW_ONLINE_STORE_RESOURCE_ID,
                    False,
                    False,
                ],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    materialization_identity=ManagedIdentityConfiguration(resource_id=NEW_IDENTITY_RESOURCE_ID),
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=EXISTING_OFFLINE_STORE_RESOURCE_ID
                    ),
                    online_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=EXISTING_ONLINE_STORE_RESOURCE_ID
                    ),
                ),
                [
                    True,
                    True,
                    True,
                    NEW_IDENTITY_RESOURCE_ID,
                    EXISTING_OFFLINE_STORE_RESOURCE_ID,
                    EXISTING_ONLINE_STORE_RESOURCE_ID,
                    True,
                    True,
                ],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    materialization_identity=ManagedIdentityConfiguration(resource_id=EXISTING_IDENTITY_RESOURCE_ID),
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=NEW_OFFLINE_STORE_RESOURCE_ID
                    ),
                    online_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=NEW_ONLINE_STORE_RESOURCE_ID
                    ),
                ),
                [
                    False,
                    True,
                    True,
                    EXISTING_IDENTITY_RESOURCE_ID,
                    NEW_OFFLINE_STORE_RESOURCE_ID,
                    NEW_ONLINE_STORE_RESOURCE_ID,
                    False,
                    False,
                ],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=EXISTING_OFFLINE_STORE_RESOURCE_ID
                    ),
                    online_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=EXISTING_ONLINE_STORE_RESOURCE_ID
                    ),
                ),
                [False, False, False, None, None, None, True, True],
            ),
        ]

        perform_tests(testcases1, mock_feature_store_operation)

        # non existing stores
        def outgoing_get_call_empty_no_workspace_connection(rg, name):
            from azure.ai.ml._utils.utils import camel_to_snake
            from azure.ai.ml.constants import ManagedServiceIdentityType
            from azure.ai.ml.entities import IdentityConfiguration, ManagedIdentityConfiguration
            from azure.ai.ml.entities._workspace.feature_store_settings import FeatureStoreSettings

            ws = Workspace(
                name=name,
                kind="featurestore",
                identity=IdentityConfiguration(
                    type=camel_to_snake(ManagedServiceIdentityType.USER_ASSIGNED),
                    user_assigned_identities=[
                        ManagedIdentityConfiguration(resource_id=EXISTING_IDENTITY_RESOURCE_ID),
                    ],
                ),
            )
            ws._feature_store_settings = FeatureStoreSettings(
                offline_store_connection_name=None,
                online_store_connection_name=None,
            )
            return ws._to_rest_object()

        mock_feature_store_operation._operation.get.side_effect = outgoing_get_call_empty_no_workspace_connection

        testcases2 = [
            (
                FeatureStore(name="name", description="description"),
                [False, False, False, None, None, None, False, False],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    materialization_identity=ManagedIdentityConfiguration(resource_id=NEW_IDENTITY_RESOURCE_ID),
                ),
                [True, False, False, NEW_IDENTITY_RESOURCE_ID, None, None, False, False],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    offline_store=MaterializationStore(
                        type=OFFLINE_MATERIALIZATION_STORE_TYPE, target=NEW_OFFLINE_STORE_RESOURCE_ID
                    ),
                    online_store=MaterializationStore(
                        type=ONLINE_MATERIALIZATION_STORE_TYPE, target=NEW_ONLINE_STORE_RESOURCE_ID
                    ),
                ),
                [
                    False,
                    True,
                    True,
                    EXISTING_IDENTITY_RESOURCE_ID,
                    NEW_OFFLINE_STORE_RESOURCE_ID,
                    NEW_ONLINE_STORE_RESOURCE_ID,
                    False,
                    False,
                ],
            ),
            (
                FeatureStore(
                    name="name",
                    description="description",
                    materialization_identity=ManagedIdentityConfiguration(resource_id=EXISTING_IDENTITY_RESOURCE_ID),
                ),
                [False, False, False, None, None, None, False, False],
            ),
        ]

        perform_tests(testcases2, mock_feature_store_operation)

    def test_begin_provision_network(self, mock_feature_store_operation: FeatureStoreOperations) -> None:
        def outgoing_call(name):
            return "testws"

        mock_feature_store_operation._operation.get.side_effect = outgoing_call
        mock_feature_store_operation.begin_provision_network(feature_store_name="testws")
        mock_feature_store_operation._provision_network_operation.begin_provision_managed_network.assert_called_once()

    def test_delete(self, mock_feature_store_operation: FeatureStoreOperations, mocker: MockFixture) -> None:
        def outgoing_call(rg, name):
            return Workspace(name=name, kind="featurestore")._to_rest_object()

        mock_feature_store_operation._operation.get.side_effect = outgoing_call
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        mocker.patch(
            "azure.ai.ml.operations._workspace_operations_base.get_generic_arm_resource_by_arm_id", return_value=None
        )
        mock_feature_store_operation.begin_delete("randstr", delete_dependent_resources=True)
        mock_feature_store_operation._operation.begin_delete.assert_called_once()

    def test_delete_non_feature_store_kind(
        self, mock_feature_store_operation: FeatureStoreOperations, mocker: MockFixture
    ) -> None:
        def outgoing_call(rg, name):
            return Workspace(name=name)._to_rest_object()

        mock_feature_store_operation._operation.get.side_effect = outgoing_call
        mocker.patch("azure.ai.ml.operations._workspace_operations_base.delete_resource_by_arm_id", return_value=None)
        with pytest.raises(Exception):
            mock_feature_store_operation.begin_delete("randstr", delete_dependent_resources=True)
