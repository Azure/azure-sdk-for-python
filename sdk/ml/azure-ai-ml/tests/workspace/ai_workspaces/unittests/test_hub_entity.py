from typing import Optional

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_hub


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestProjectEntity:
    def test_project_schema_manipulation(self) -> None:
      hub = load_hub(
            source="./tests/test_configs/workspace/ai_workspaces/aihub_min.yml"
        )
      assert hub.name == "hub_name"
      assert hub.location == "WestCentralUS"
      assert hub.additional_workspace_storage_accounts == ["/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.Storage/storageAccounts/extra-storage-account"]
      assert hub.default_workspace_resource_group == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/my-default-resource-group"
      assert hub.tags == {"purpose": "testing", "team": "ws-management"}
      assert hub.storage_account == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.Storage/storageAccounts/testAccount"
      assert hub.container_registry == "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/testRG/providers/Microsoft.ContainerRegistry/registries/testACR"
      assert hub.key_vault == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.KeyVault/vaults/testKeyVault"
      assert hub.application_insights == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.Insights/components/testAppIn"
      assert hub.image_build_compute == "some_compute_name"
      assert hub.public_network_access == "Enabled"
      assert hub.hbi_workspace == True
      assert hub.customer_managed_key.key_vault == "/subscriptions/00000000-0000-0000-0000-000000000000/resourceGroups/testRG/providers/Microsoft.KeyVault/vaults/testKeyVault2" 
      assert hub.customer_managed_key.key_uri == "https://keyvault.vault.azure.net/keys/cmkkey/123456"
      assert hub.serverless_compute.custom_subnet == "/subscriptions/00000000-0000-0000-0000-000000000000/resourcegroups/testRG/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet"
      assert hub.serverless_compute.no_public_ip

