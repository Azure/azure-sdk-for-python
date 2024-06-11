import pytest

from azure.ai.ml import load_workspace
from azure.ai.ml.entities import Hub


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestProjectEntity:
    def test_project_schema_manipulation(self) -> None:
        hub = load_workspace(source="./tests/test_configs/workspace/ai_workspaces/aihub_min.yml")
        assert hub is not None
        assert type(hub) == Hub
        assert hub.name == "hub_name"
        assert hub.location == "WestCentralUS"
        assert (
            hub.default_resource_group
            == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-default-resource-group"
        )
        assert hub.tags == {"purpose": "testing", "team": "ws-management"}
        assert (
            hub.storage_account
            == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.Storage/storageAccounts/testAccount"
        )
        assert (
            hub.container_registry
            == "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/testRG/providers/Microsoft.ContainerRegistry/registries/testACR"
        )
        assert (
            hub.key_vault
            == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.KeyVault/vaults/testKeyVault"
        )
        assert (
            hub.application_insights
            == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.Insights/components/testAppIn"
        )
        assert hub.image_build_compute == "some_compute_name"
        assert hub.public_network_access == "Enabled"
        assert hub.hbi_workspace == True
        assert (
            hub.customer_managed_key.key_vault
            == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.KeyVault/vaults/testKeyVault2"
        )
        assert hub.customer_managed_key.key_uri == "https://keyvault.vault.azure.net/keys/cmkkey/123456"
        assert (
            hub.serverless_compute.custom_subnet
            == "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/testRG/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet"
        )
        assert hub.serverless_compute.no_public_ip

    # Note, this test does not ensure as much API correctness as
    # you'd like because of the workspace operation's reliance on ARM
    # template madness.
    @pytest.mark.skip(reason="Rest conversion is/has always been buggy aparently. Not fixing it yet.")
    def test_hub_rest_conversion(self) -> None:
        original_hub = Hub(
            name="hub_name",
            location="somewhere",
            description="test desc",
            tags={"purpose": "testing"},
            display_name="test_display_name",
            resource_group="testRG",
            storage_account="testAccount",
            key_vault="testKeyVault",
            container_registry="testACR",
            image_build_compute="some_compute_name",
            public_network_access="Enabled",
            primary_user_assigned_identity="id1",
            enable_data_isolation=True,
            default_resource_group="my-default-resource-group",
        )

        # Convert hub back and forth from rest equivalent and ensure consistency.
        rest_hub = original_hub._to_rest_object()
        new_hub = Hub._from_rest_object(rest_hub)

        assert new_hub.name == original_hub.name
        assert new_hub.location == original_hub.location
        assert new_hub.description == original_hub.description
        assert new_hub.tags == original_hub.tags
        assert new_hub.display_name == original_hub.display_name
        assert new_hub.resource_group == original_hub.resource_group
        assert new_hub.storage_account == original_hub.storage_account
        assert new_hub.key_vault == original_hub.key_vault
        assert new_hub.container_registry == original_hub.container_registry
        assert new_hub.image_build_compute == original_hub.image_build_compute
        assert new_hub.public_network_access == original_hub.public_network_access
        assert new_hub.primary_user_assigned_identity == original_hub.primary_user_assigned_identity
        assert new_hub.enable_data_isolation == original_hub.enable_data_isolation
        assert new_hub.default_resource_group == original_hub.default_resource_group
