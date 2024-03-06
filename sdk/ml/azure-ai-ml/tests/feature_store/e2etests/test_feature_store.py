# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.constants._workspace import IsolationMode
from azure.ai.ml.entities import FeatureStore, ManagedNetwork, PrivateEndpointDestination
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.data_experiences_test
@pytest.mark.usefixtures(
    "mock_workspace_arm_template_deployment_name",
    "mock_workspace_dependent_resource_name_generator",
)
class TestFeatureStore(AzureRecordedTestCase):
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    @pytest.mark.nofixdeploymentname
    @pytest.mark.nofixresourcename
    def test_feature_store_create_and_delete(
        self,
        client: MLClient,
        randstr: Callable[[], str],
        location: str,
        online_store_target: str,
        offline_store_target: str,
        materialization_identity_resource_id: str,
        materialization_identity_client_id: str,
        default_storage_account: str,
    ) -> None:
        from azure.ai.ml.entities import ManagedIdentityConfiguration, MaterializationStore

        if not online_store_target:
            print("Feature store create e2e test: online store target is not provided, use default target")
            online_store_target = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.Cache/Redis/runhli-test"

        if not offline_store_target:
            print("Feature store create e2e test: offline store target is not provided, use default target")

        if not materialization_identity_client_id or not materialization_identity_resource_id:
            print("Feature store create e2e test: materialization identity is not provided, use default identity")

        if not default_storage_account:
            print("Feature store ceate e2e test: storage account is not provided, use default storage account")

        fs_name = f"e2etest_fs_{randstr('fs')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        # provision with no store and identity
        fs = FeatureStore(name=fs_name, description=fs_description, display_name=fs_display_name, location=location)
        fs_poller = client.feature_stores.begin_create(feature_store=fs)
        assert isinstance(fs_poller, LROPoller)

        create_fs = fs_poller.result()
        assert isinstance(create_fs, FeatureStore)
        assert create_fs.materialization_identity.resource_id
        assert not create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        assert create_fs.offline_store.target
        assert create_fs.offline_store.target.startswith(create_fs.storage_account)

        if not materialization_identity_client_id or not materialization_identity_resource_id:
            materialization_identity_client_id = create_fs.materialization_identity.client_id
            materialization_identity_resource_id = create_fs.materialization_identity.resource_id

        if not offline_store_target:
            offline_store_target = create_fs.offline_store.target

        if not default_storage_account:
            default_storage_account = create_fs.storage_account

        # provision with online store
        fs_name = f"e2etest_fs1_{randstr('fs1')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        fs1 = FeatureStore(
            name=fs_name,
            online_store=MaterializationStore(type="redis", target=online_store_target),
            description=fs_description,
            display_name=fs_display_name,
            location=location,
        )
        fs_poller = client.feature_stores.begin_create(feature_store=fs1)

        create_fs = fs_poller.result()
        assert isinstance(create_fs, FeatureStore)
        assert create_fs.materialization_identity.resource_id
        assert create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        assert create_fs.offline_store.target
        assert create_fs.online_store.target == online_store_target

        fs_poller = client.feature_stores.begin_delete(name=fs1.name, delete_dependent_resources=True)
        fs_poller.result()

        # provisioned with offline store
        fs_name = f"e2etest_fs2_{randstr('fs2')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        fs2 = FeatureStore(
            name=fs_name,
            offline_store=MaterializationStore(type="azure_data_lake_gen2", target=offline_store_target),
            description=fs_description,
            display_name=fs_display_name,
            location=location,
        )
        fs_poller = client.feature_stores.begin_create(feature_store=fs2)

        create_fs = fs_poller.result()
        assert isinstance(create_fs, FeatureStore)
        assert create_fs.materialization_identity.resource_id
        assert not create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        assert create_fs.offline_store.target == offline_store_target
        assert not offline_store_target.startswith(create_fs.storage_account)

        fs_poller = client.feature_stores.begin_delete(name=fs2.name, delete_dependent_resources=True)
        fs_poller.result()

        # provisioned with materialization identity
        fs_name = f"e2etest_fs3_{randstr('fs3')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        fs3 = FeatureStore(
            name=fs_name,
            materialization_identity=ManagedIdentityConfiguration(
                client_id=materialization_identity_client_id,
                resource_id=materialization_identity_resource_id,
            ),
            description=fs_description,
            display_name=fs_display_name,
            location=location,
        )
        fs_poller = client.feature_stores.begin_create(feature_store=fs3)

        create_fs = fs_poller.result()
        assert isinstance(create_fs, FeatureStore)
        assert create_fs.materialization_identity.resource_id.lower() == materialization_identity_resource_id.lower()
        assert not create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        assert create_fs.offline_store.target.startswith(create_fs.storage_account)

        fs_poller = client.feature_stores.begin_delete(name=fs3.name, delete_dependent_resources=True)
        fs_poller.result()

        fs_name = f"e2etest_fs4_{randstr('fs4')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        fs4 = FeatureStore(
            name=fs_name,
            materialization_identity=ManagedIdentityConfiguration(
                client_id=materialization_identity_client_id,
                resource_id=materialization_identity_resource_id,
            ),
            offline_store=MaterializationStore(type="azure_data_lake_gen2", target=offline_store_target),
            online_store=MaterializationStore(type="redis", target=online_store_target),
            description=fs_description,
            display_name=fs_display_name,
            location=location,
        )
        fs_poller = client.feature_stores.begin_create(feature_store=fs4)

        create_fs = fs_poller.result()
        assert isinstance(create_fs, FeatureStore)
        assert create_fs.materialization_identity.resource_id.lower() == materialization_identity_resource_id.lower()
        assert create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        assert create_fs.online_store.target == online_store_target
        assert create_fs.offline_store.target == offline_store_target

        fs_poller = client.feature_stores.begin_delete(name=fs4.name, delete_dependent_resources=True)
        fs_poller.result()

        # provision with storage account
        fs_name = f"e2etest_fs5_{randstr('fs5')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        fs5 = FeatureStore(
            name=fs_name,
            materialization_identity=ManagedIdentityConfiguration(
                client_id=materialization_identity_client_id,
                resource_id=materialization_identity_resource_id,
            ),
            storage_account=default_storage_account,
            offline_store=MaterializationStore(type="azure_data_lake_gen2", target=offline_store_target),
            description=fs_description,
            display_name=fs_display_name,
            location=location,
        )
        fs_poller = client.feature_stores.begin_create(feature_store=fs5)

        create_fs = fs_poller.result()
        assert create_fs.materialization_identity.resource_id.lower() == materialization_identity_resource_id.lower()
        assert create_fs.storage_account == default_storage_account
        assert not create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        assert create_fs.offline_store.target == offline_store_target

        fs_name = f"e2etest_fs6_{randstr('fs6')}"
        fs_description = f"{fs_name} description"
        fs_display_name = f"{fs_name} display name"

        fs6 = FeatureStore(
            name=fs_name,
            materialization_identity=ManagedIdentityConfiguration(
                client_id=materialization_identity_client_id,
                resource_id=materialization_identity_resource_id,
            ),
            storage_account=default_storage_account,
            description=fs_description,
            display_name=fs_display_name,
            location=location,
        )
        fs_poller = client.feature_stores.begin_create(feature_store=fs6)

        create_fs = fs_poller.result()
        assert create_fs.materialization_identity.resource_id.lower() == materialization_identity_resource_id.lower()
        assert create_fs.storage_account == default_storage_account
        assert not create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        assert create_fs.offline_store.target
        assert not create_fs.offline_store.target.startswith(default_storage_account)

        fs_poller = client.feature_stores.begin_delete(name=fs5.name, delete_dependent_resources=True)
        fs_poller.result()
        fs_poller = client.feature_stores.begin_delete(name=fs6.name, delete_dependent_resources=True)
        fs_poller.result()
        fs_poller = client.feature_stores.begin_delete(name=fs.name, delete_dependent_resources=True)
        fs_poller.result()

        # delete test
        with pytest.raises(Exception):
            client.feature_stores.get(fs.name)

        # normal workspace create
        from azure.ai.ml.entities import Workspace

        ws_name = f"e2etest_ws_{randstr('ws')}"

        ws = Workspace(name=ws_name, location=location)
        ws_poller = client.workspaces.begin_create(workspace=ws)
        create_ws = ws_poller.result()
        provisioned_storage_account = create_ws.storage_account

        assert isinstance(create_ws, Workspace)
        assert create_ws.name == ws_name

        ws1_name = f"e2etest_ws1_{randstr('ws1')}"
        ws1 = Workspace(name=ws1_name, storage_account=provisioned_storage_account, location=location)
        ws_poller = client.workspaces.begin_create(workspace=ws1)
        create_ws = ws_poller.result()

        assert isinstance(create_ws, Workspace)
        assert create_ws.name == ws1_name
        assert create_ws.storage_account == provisioned_storage_account

        ws_poller = client.workspaces.begin_delete(
            name=ws.name, delete_dependent_resources=True, permanently_delete=True
        )
        ws_poller.result()
        ws_poller = client.workspaces.begin_delete(
            name=ws1.name, delete_dependent_resources=True, permanently_delete=True
        )
        ws_poller.result()

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    @pytest.mark.nofixdeploymentname
    @pytest.mark.nofixresourcename
    def test_feature_store_update_delete(
        self,
        client: MLClient,
        randstr: Callable[[], str],
        location: str,
        online_store_target: str,
        offline_store_target: str,
        materialization_identity_resource_id: str,
        materialization_identity_client_id: str,
    ) -> None:
        if not online_store_target:
            print("Feature store update and delete e2e test: online store target is not provided, use default target")
            online_store_target = "/subscriptions/1aefdc5e-3a7c-4d71-a9f9-f5d3b03be19a/resourceGroups/mdctest/providers/Microsoft.Cache/Redis/runhli-test"

        if not offline_store_target:
            print("Feature store update and delete e2e test: offline store target is not provided, use default target")

        if not materialization_identity_client_id or not materialization_identity_resource_id:
            print(
                "Feature store update and delete e2e test: materialization identity is not provided, use default identity"
            )

        alt_fs_name = None
        if (
            not offline_store_target
            or not materialization_identity_client_id
            or not materialization_identity_resource_id
        ):
            alt_fs_name = f"alt_fs_{randstr('alt_fs')}"
            alt_fs_description = f"{alt_fs_name} description"
            alt_fs = FeatureStore(name=alt_fs_name, description=alt_fs_description, location=location)
            fs_poller = client.feature_stores.begin_create(feature_store=alt_fs)
            create_fs = fs_poller.result()
            offline_store_target = create_fs.offline_store.target
            materialization_identity_client_id = create_fs.materialization_identity.client_id
            materialization_identity_resource_id = create_fs.materialization_identity.resource_id

        fs_name = f"e2etest_fs_{randstr('fs_to_update')}"
        fs_description = f"{fs_name} description"
        fs_updated_description = f"{fs_name} updated description"
        fs_display_name = f"{fs_name} display name"

        fs = FeatureStore(name=fs_name, description=fs_description, display_name=fs_display_name, location=location)
        fs_poller = client.feature_stores.begin_create(feature_store=fs)

        create_fs = fs_poller.result()
        assert isinstance(create_fs, FeatureStore)

        assert create_fs.materialization_identity.resource_id
        assert create_fs.offline_store.target
        assert not create_fs._feature_store_settings.online_store_connection_name
        assert create_fs._feature_store_settings.offline_store_connection_name
        provisioned_offline_store_resource_id = create_fs.offline_store.target
        provisioned_materialization_identity = create_fs.materialization_identity

        fs_result = client.feature_stores.get(fs_name)
        assert isinstance(fs_result, FeatureStore)
        assert fs_result.name == fs_name

        fs_list = client.feature_stores.list()
        assert any(fs_name == fs.name for fs in fs_list)

        updated_fs = FeatureStore(name=fs_name, description=fs_updated_description, display_name=fs_display_name)
        fs_poller = client.feature_stores.begin_update(feature_store=updated_fs)

        updated_fs = fs_poller.result()
        assert isinstance(updated_fs, FeatureStore)
        assert not updated_fs._feature_store_settings.online_store_connection_name
        assert updated_fs._feature_store_settings.offline_store_connection_name
        assert updated_fs.name == fs_name
        assert updated_fs.description == fs_updated_description

        from azure.ai.ml.entities import ManagedIdentityConfiguration, MaterializationStore

        # online store update
        online_fs = FeatureStore(
            name=fs_name,
            online_store=MaterializationStore(type="redis", target=online_store_target),
        )
        fs_poller = client.feature_stores.begin_update(feature_store=online_fs)

        online_fs = fs_poller.result()
        assert isinstance(online_fs, FeatureStore)
        assert online_fs._feature_store_settings.online_store_connection_name
        assert online_fs._feature_store_settings.offline_store_connection_name
        assert online_fs.materialization_identity.resource_id == provisioned_materialization_identity.resource_id
        assert online_fs.offline_store.target == provisioned_offline_store_resource_id
        assert online_fs.online_store.target == online_store_target

        # offline store update
        offline_fs = FeatureStore(
            name=fs_name,
            offline_store=MaterializationStore(type="azure_data_lake_gen2", target=offline_store_target),
        )
        fs_poller = client.feature_stores.begin_update(feature_store=offline_fs)
        offline_fs = fs_poller.result()
        assert isinstance(offline_fs, FeatureStore)
        assert offline_fs.materialization_identity.resource_id == provisioned_materialization_identity.resource_id
        assert offline_fs._feature_store_settings.online_store_connection_name
        assert offline_fs._feature_store_settings.offline_store_connection_name
        assert (
            offline_fs._feature_store_settings.offline_store_connection_name
            != online_fs._feature_store_settings.offline_store_connection_name
        )
        assert offline_fs.offline_store.target == offline_store_target
        assert online_fs.online_store.target == online_store_target

        # identity update
        identity_fs = FeatureStore(
            name=fs_name,
            materialization_identity=ManagedIdentityConfiguration(
                client_id=materialization_identity_client_id, resource_id=materialization_identity_resource_id
            ),
        )
        fs_poller = client.feature_stores.begin_update(feature_store=identity_fs)
        identity_fs = fs_poller.result()
        assert isinstance(identity_fs, FeatureStore)
        assert identity_fs.materialization_identity.client_id == materialization_identity_client_id
        assert identity_fs.materialization_identity.resource_id.lower() == materialization_identity_resource_id.lower()
        assert (
            identity_fs._feature_store_settings.online_store_connection_name
            == online_fs._feature_store_settings.online_store_connection_name
        )
        assert (
            identity_fs._feature_store_settings.offline_store_connection_name
            == offline_fs._feature_store_settings.offline_store_connection_name
        )

        identity_fs = FeatureStore(
            name=fs_name,
            materialization_identity=ManagedIdentityConfiguration(
                client_id=provisioned_materialization_identity.client_id,
                resource_id=provisioned_materialization_identity.resource_id,
            ),
            offline_store=MaterializationStore(type="azure_data_lake_gen2", target=offline_store_target),
        )
        fs_poller = client.feature_stores.begin_update(feature_store=identity_fs)
        identity_fs = fs_poller.result()
        assert isinstance(offline_fs, FeatureStore)
        assert identity_fs.materialization_identity.client_id == provisioned_materialization_identity.client_id
        assert (
            identity_fs.materialization_identity.resource_id.lower()
            == provisioned_materialization_identity.resource_id.lower()
        )
        assert identity_fs.offline_store.target == offline_store_target
        assert identity_fs.online_store.target == online_store_target
        assert (
            identity_fs._feature_store_settings.online_store_connection_name
            == online_fs._feature_store_settings.online_store_connection_name
        )
        assert (
            identity_fs._feature_store_settings.offline_store_connection_name
            == offline_fs._feature_store_settings.offline_store_connection_name
        )

        # test update and provision managed network interface
        managed_network_fs = FeatureStore(
            name=fs_name,
            public_network_access="disabled",
            managed_network=ManagedNetwork(
                isolation_mode=IsolationMode.ALLOW_INTERNET_OUTBOUND,
                outbound_rules=[
                    PrivateEndpointDestination(
                        name="sourcerulefs",
                        service_resource_id=create_fs.storage_account,
                        subresource_target="dfs",
                        spark_enabled="true",
                    ),
                    PrivateEndpointDestination(
                        name="defaultkeyvault",
                        service_resource_id=create_fs.key_vault,
                        subresource_target="vault",
                        spark_enabled="true",
                    ),
                ],
            ),
        )
        fs_poller = client.feature_stores.begin_update(feature_store=managed_network_fs)
        fs_poller.result()
        status_poller = client.feature_stores.begin_provision_network(feature_store_name=fs_name)
        assert isinstance(status_poller, LROPoller)

        fs_poller = client.feature_stores.begin_delete(name=fs.name, delete_dependent_resources=True)
        if alt_fs_name:
            fs_poller = client.feature_stores.begin_delete(name=alt_fs_name, delete_dependent_resources=True)
