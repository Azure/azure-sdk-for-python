from typing import Optional

import pytest
import json
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_workspace
from azure.ai.ml._restclient.v2024_10_01_preview.models import (
    Workspace as RestWorkspace,
)
from azure.ai.ml.constants._workspace import FirewallSku, IsolationMode
from azure.ai.ml.entities import ServerlessComputeSettings, Workspace


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestWorkspaceEntity:
    @pytest.mark.parametrize(
        "settings",
        [
            None,
            ServerlessComputeSettings(custom_subnet=None, no_public_ip=False),
            ServerlessComputeSettings(
                custom_subnet="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet",
                no_public_ip=False,
            ),
            ServerlessComputeSettings(
                custom_subnet="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnetnpip",
                no_public_ip=True,
            ),
        ],
    )
    def test_serverless_compute_settings_loaded_from_rest_object(
        self, settings: Optional[ServerlessComputeSettings]
    ) -> None:
        workspace = Workspace(name="test_workspace", location="test_location", serverless_compute=settings)
        rest_object = workspace._to_rest_object()
        assert rest_object is not None
        if settings is None:
            assert rest_object.serverless_compute_settings is None
        else:
            assert ServerlessComputeSettings._from_rest_object(rest_object.serverless_compute_settings) == settings

    def test_from_rest_object(self) -> None:
        with open("./tests/test_configs/workspace/workspace_full_rest_response.json", "r") as f:
            rest_object = RestWorkspace.deserialize(json.load(f))

        workspace = Workspace._from_rest_object(rest_object)

        assert (
            workspace.id
            == "/subscriptions/sub-id/test_workspace/providers/Microsoft.Storage/storageAccounts/storage-account-name"
        )
        assert workspace.name == "test_workspace"
        assert workspace.location == "test_location"
        assert workspace.description == "test_description"
        assert workspace.tags == {"test_tag": "test_value"}
        assert workspace.display_name == "test_friendly_name"
        assert workspace.discovery_url == "test_discovery_url"
        assert workspace.resource_group == "providers"
        assert workspace.storage_account == "test_storage_account"
        assert workspace.key_vault == "test_key_vault"
        assert workspace.application_insights == "test_application_insights"
        assert workspace.container_registry == "test_container_registry"
        assert workspace.customer_managed_key.key_uri == "key_identifier"
        assert workspace.customer_managed_key.key_vault == "key_vault_arm_id"
        assert workspace.hbi_workspace is True
        assert workspace.public_network_access == "Enabled"
        assert workspace.image_build_compute == "test_image_build_compute"
        assert workspace.discovery_url == "test_discovery_url"
        assert workspace.mlflow_tracking_uri == "ml_flow_tracking_uri"
        assert workspace.primary_user_assigned_identity == "test_primary_user_assigned_identity"
        assert workspace.system_datastores_auth_mode == "AccessKey"
        assert workspace.enable_data_isolation == True
        assert workspace.allow_roleassignment_on_rg == True
        assert workspace._hub_id == "hub_resource_id"
        assert workspace._kind == "project"
        assert workspace._workspace_id == "workspace_id"
        assert workspace.identity is not None
        assert workspace.managed_network is not None
        assert workspace._feature_store_settings is not None
        assert workspace.network_acls is not None
        assert workspace.provision_network_now == True
        assert workspace.serverless_compute is not None
        assert workspace.network_acls is not None

    def test_from_rest_object_for_attributes_none(self) -> None:
        with open("./tests/test_configs/workspace/workspace_full_rest_response.json", "r") as f:
            rest_json = json.load(f)
            del rest_json["properties"]["managedNetwork"]
            del rest_json["properties"]["encryption"]
            rest_json["id"] = "/subscriptions/sub-id"
            del rest_json["identity"]
            del rest_json["properties"]["featureStoreSettings"]
            del rest_json["properties"]["serverlessComputeSettings"]
            del rest_json["properties"]["networkAcls"]
            rest_object = RestWorkspace.deserialize(rest_json)

        workspace = Workspace._from_rest_object(rest_object)

        assert workspace.id == "/subscriptions/sub-id"
        assert workspace.name == "test_workspace"
        assert workspace.location == "test_location"
        assert workspace.description == "test_description"
        assert workspace.tags == {"test_tag": "test_value"}
        assert workspace.display_name == "test_friendly_name"
        assert workspace.discovery_url == "test_discovery_url"
        assert workspace.resource_group is None
        assert workspace.storage_account == "test_storage_account"
        assert workspace.key_vault == "test_key_vault"
        assert workspace.application_insights == "test_application_insights"
        assert workspace.container_registry == "test_container_registry"
        assert workspace.customer_managed_key is None
        assert workspace.hbi_workspace is True
        assert workspace.public_network_access == "Enabled"
        assert workspace.image_build_compute == "test_image_build_compute"
        assert workspace.discovery_url == "test_discovery_url"
        assert workspace.mlflow_tracking_uri == "ml_flow_tracking_uri"
        assert workspace.primary_user_assigned_identity == "test_primary_user_assigned_identity"
        assert workspace.system_datastores_auth_mode == "AccessKey"
        assert workspace.enable_data_isolation == True
        assert workspace.allow_roleassignment_on_rg == True
        assert workspace._hub_id == "hub_resource_id"
        assert workspace._kind == "project"
        assert workspace._workspace_id == "workspace_id"
        assert workspace.identity is None
        assert workspace.managed_network is None
        assert workspace._feature_store_settings is None
        assert workspace.network_acls is None
        assert workspace.provision_network_now == True
        assert workspace.serverless_compute is None

    def test_serverless_compute_settings_subnet_name_must_be_an_arm_id(self) -> None:
        with pytest.raises(ValidationError):
            ServerlessComputeSettings(custom_subnet="justaname", no_public_ip=True)

    @pytest.mark.parametrize(
        "settings",
        [
            ServerlessComputeSettings(
                custom_subnet="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/default",
                no_public_ip=True,
            ),  # Override but using same value
            ServerlessComputeSettings(
                custom_subnet="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet",
                no_public_ip=True,
            ),
            ServerlessComputeSettings(
                custom_subnet="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/default",
                no_public_ip=False,
            ),
            ServerlessComputeSettings(
                custom_subnet="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet",
                no_public_ip=False,
            ),
        ],
    )
    def test_workspace_load_override_serverless(self, settings: ServerlessComputeSettings) -> None:
        params_override = [
            {
                "serverless_compute": {
                    "custom_subnet": settings.custom_subnet,
                    "no_public_ip": settings.no_public_ip,
                }
            }
        ]

        workspace_override = load_workspace(
            "./tests/test_configs/workspace/workspace_serverless.yaml",
            params_override=params_override,
        )
        assert workspace_override.serverless_compute == settings

    def test_workspace_load_yamls_to_test_outbound_rule_load(self):
        workspace = load_workspace("./tests/test_configs/workspace/workspace_many_ob_rules.yaml")

        assert workspace.managed_network is not None
        assert workspace.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND

        rules = workspace.managed_network.outbound_rules
        assert rules[0].name == "microsoft"
        assert rules[0].destination == "microsoft.com"

        assert rules[1].name == "appGwRule"
        assert rules[1].service_resource_id == "/someappgwid"
        assert rules[1].spark_enabled == False
        assert rules[1].subresource_target == "appGwPrivateFrontendIpIPv4"
        assert "contoso.com" in rules[1].fqdns
        assert "contoso2.com" in rules[1].fqdns

        assert rules[2].name == "servicetag-w-prefixes"
        assert rules[2].service_tag == "sometag"
        assert rules[2].protocol == "TCP"
        assert rules[2].port_ranges == "80, 8080-8089"
        assert "168.63.129.16" in rules[2].address_prefixes
        assert "10.0.0.0/24" in rules[2].address_prefixes

    def test_workspace_load_yamls_to_test_firewallsku_load(self):
        workspace = load_workspace("./tests/test_configs/workspace/workspace_mvnet_with_firewallsku.yaml")

        assert workspace.managed_network is not None
        assert workspace.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND
        rules = workspace.managed_network.outbound_rules

        assert workspace.managed_network.firewall_sku == "Basic"

        assert rules[0].name == "microsoft"
        assert rules[0].destination == "microsoft.com"

        assert rules[1].name == "appGwRule"
        assert rules[1].service_resource_id == "/someappgwid"
        assert rules[1].spark_enabled == False
        assert rules[1].subresource_target == "appGwPrivateFrontendIpIPv4"
        assert "contoso.com" in rules[1].fqdns
        assert "contoso2.com" in rules[1].fqdns

        assert rules[2].name == "pytorch"
        assert rules[2].destination == "*.pytorch.org"

    def test_workspace_load_yaml_to_test_network_acls_load(self):
        workspace = load_workspace("./tests/test_configs/workspace/ai_workspaces/workspacehub_with_networkacls.yaml")

        assert workspace.network_acls is not None
        assert len(workspace.network_acls.ip_rules) == 2
        assert workspace.network_acls.default_action == "Deny"
        assert workspace.public_network_access == "Enabled"
        ip_rules = workspace.network_acls.ip_rules

        assert ip_rules[0].value == "103.248.19.87"
        assert ip_rules[1].value == "103.248.19.86/32"
