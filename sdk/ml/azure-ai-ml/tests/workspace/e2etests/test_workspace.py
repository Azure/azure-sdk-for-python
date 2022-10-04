# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import MLClient, load_workspace
from azure.ai.ml.constants._common import PublicNetworkAccess
from azure.ai.ml.constants._workspace import ManagedServiceIdentityType
from azure.core.paging import ItemPaged
from azure.mgmt.msi._managed_service_identity_client import ManagedServiceIdentityClient

from devtools_testutils import AzureRecordedTestCase, is_live


@pytest.mark.e2etest
@pytest.mark.mlc
@pytest.mark.usefixtures(
    "recorded_test", "mock_workspace_arm_template_deployment_name", "mock_workspace_dependent_resource_name_generator"
)
class TestWorkspace(AzureRecordedTestCase):
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    def test_workspace_create_update_and_delete(
        self, client: MLClient, randstr: Callable[[], str], location: str
    ) -> None:
        wps_name = f"e2etest_{randstr('wps_name')}"
        wps_description = f"{wps_name} description"
        wps_display_name = f"{wps_name} display name"
        params_override = [
            {"name": wps_name},
            {"location": location},
            {"description": wps_description},
            {"display_name": wps_display_name},
        ]

        # only test simple aspects of both a pointer and path-loaded workspace
        # save actual service calls for a single object (below).
        def workspace_validation(wps):
            workspace = client.workspaces.begin_create(workspace=wps)
            assert workspace.name == wps_name
            assert workspace.location == location
            assert workspace.description == wps_description
            assert workspace.display_name == wps_display_name
            assert workspace.public_network_access == PublicNetworkAccess.ENABLED

        workspace = verify_entity_load_and_dump(
            load_workspace,
            workspace_validation,
            "./tests/test_configs/workspace/workspace_min.yaml",
            params_override=params_override,
        )[0]

        workspace_list = client.workspaces.list()
        assert isinstance(workspace_list, ItemPaged)
        workspace = client.workspaces.get(wps_name)
        assert workspace.name == wps_name
        assert workspace.container_registry is None

        workspace = client.workspaces.begin_update(
            workspace,
            image_build_compute="compute",
            public_network_access=PublicNetworkAccess.DISABLED,
            container_regristry=workspace.container_registry,
            application_insights=workspace.application_insights,
            update_dependent_resources=True,
        )
        assert workspace.image_build_compute == "compute"
        assert workspace.public_network_access == PublicNetworkAccess.DISABLED
        # verify updating acr
        # TODO (1412559): Disabling this logic as it is deleting the main test workspace container registry
        # static_acr: str = client.workspaces.get(client._operation_scope.workspace_name).container_registry
        # workspace = client.workspaces.begin_update_dependencies(
        #     workspace_name=workspace.name, container_registry=static_acr, force=True
        # )
        # assert workspace.container_registry.lower() == static_acr.lower()

        poller = client.workspaces.begin_delete(wps_name, delete_dependent_resources=True, no_wait=True)
        # verify that request was accepted by checking if poller is returned
        assert poller

    def test_workspace_diagnosis(self, client: MLClient, randstr: Callable[[], str]) -> None:
        diagnose_result = client.workspaces.begin_diagnose(client._operation_scope.workspace_name)
        assert len(diagnose_result["container_registry_results"]) >= 0
        assert len(diagnose_result["dns_resolution_results"]) >= 0
        assert len(diagnose_result["key_vault_results"]) >= 0
        assert len(diagnose_result["network_security_rule_results"]) >= 0
        assert len(diagnose_result["other_results"]) >= 0
        assert len(diagnose_result["resource_lock_results"]) >= 0
        assert len(diagnose_result["storage_account_results"]) >= 0
        assert len(diagnose_result["user_defined_route_results"]) >= 0

    @pytest.mark.skip("Testing CMK workspace needs complicated setup, created TASK 1063112 to address that later")
    def test_workspace_cmk_create_and_delete(self, client: MLClient, randstr: Callable[[], str]) -> None:
        wps_name = f"e2etest_{randstr('wps_name')}"
        params_override = [{"name": wps_name}]
        wps = load_workspace(
            source="./tests/test_configs/workspace/workspace_cmk.yaml", params_override=params_override
        )

        # the kv name "ws-e2e-test-cmk" is not in the ARM template since it causes name collision when re-creating a WS. Add it back when re-enabling this test.
        wps.customer_managed_key.key_vault = f"/subscriptions/{client._operation_scope.subscription_id}/resourceGroups/{client._operation_scope.resource_group_name}/providers/Microsoft.KeyVault/vaults/ws-e2e-test-cmk"

        workspace = client.workspaces.begin_create(workspace=wps)
        assert workspace.name == wps_name
        assert workspace.customer_managed_key.key_vault == wps.customer_managed_key.key_vault
        client.workspaces.begin_delete(workspace_name=wps_name, delete_dependent_resources=True, no_wait=False)
        with pytest.raises(Exception) as e:
            client.workspaces.get(name=wps_name)
        assert e is not None

    @pytest.mark.e2etest
    @pytest.mark.mlc
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    def test_uai_workspace_create_update_and_delete(
        self, client: MLClient, randstr: Callable[[], str], location: str
    ) -> None:
        # resource name key word
        wps_name = f"e2etest_{randstr()}"

        # uai creation
        msi_client = ManagedServiceIdentityClient(
            credential=client._credential, subscription_id=client._operation_scope.subscription_id
        )
        user_assigned_identity = msi_client.user_assigned_identities.get(
            resource_group_name="rg-mhe-e2e-test-dont-remove",
            resource_name="uai-mhe",
        )
        user_assigned_identity2 = msi_client.user_assigned_identities.get(
            resource_group_name="rg-mhe-e2e-test-dont-remove",
            resource_name="uai-mhe2",
        )

        wps_description = f"{wps_name} description"
        wps_display_name = f"{wps_name} display name"
        params_override = [
            {"name": wps_name},
            {"location": location},
            {"description": wps_description},
            {"display_name": wps_display_name},
            {
                "identity": {
                    "type": "user_assigned",
                    "user_assigned_identities": {
                        user_assigned_identity.id: {
                            "principal_id": user_assigned_identity.principal_id,
                            "client_id": user_assigned_identity.client_id,
                        },
                        user_assigned_identity2.id: {
                            "principal_id": user_assigned_identity2.principal_id,
                            "client_id": user_assigned_identity2.client_id,
                        },
                    },
                }
            },
            {"primary_user_assigned_identity": user_assigned_identity.id},
        ]
        wps = load_workspace("./tests/test_configs/workspace/workspace_min.yaml", params_override=params_override)
        workspace = client.workspaces.begin_create(workspace=wps)
        assert workspace.name == wps_name
        assert workspace.location == location
        assert workspace.description == wps_description
        assert workspace.display_name == wps_display_name
        assert workspace.public_network_access == PublicNetworkAccess.ENABLED
        assert workspace.identity.type == ManagedServiceIdentityType.USER_ASSIGNED
        assert len(workspace.identity.user_assigned_identities) == 2
        assert workspace.primary_user_assigned_identity == user_assigned_identity.id

        workspace_list = client.workspaces.list()
        assert isinstance(workspace_list, ItemPaged)

        workspace = client.workspaces.get(name=wps_name)
        assert workspace.name == wps_name
        assert workspace.container_registry is None
        assert workspace.identity.type == ManagedServiceIdentityType.USER_ASSIGNED
        assert len(workspace.identity.user_assigned_identities) == 2
        assert workspace.primary_user_assigned_identity == user_assigned_identity.id

        workspace = client.workspaces.begin_update(
            workspace,
            primary_user_assigned_identity=user_assigned_identity2.id,
        )
        assert workspace.primary_user_assigned_identity == user_assigned_identity2.id
        poller = client.workspaces.begin_delete(wps_name, delete_dependent_resources=True, no_wait=True)
        # verify that request was accepted by checking if poller is returned
        assert poller
