# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: ml_samples_workspace.py
DESCRIPTION:
    These samples demonstrate different ways to configure Workspace and related objects.
USAGE:
    python ml_samples_workspace.py

"""

import os
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from ml_samples_compute import handle_resource_exists_error

subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
resource_group = os.environ["RESOURCE_GROUP_NAME"]
credential = DefaultAzureCredential()
ml_client = MLClient(credential, subscription_id, resource_group)
ml_client_ws = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws1")


class WorkspaceConfigurationOptions(object):
    def ml_workspace_config_sample_snippets_entities(self):
        # [START load_workspace]
        from azure.ai.ml import load_workspace

        ws = load_workspace(
            "../tests/test_configs/workspace/workspace_min.yaml",
            params_override=[{"description": "loaded from workspace_min.yaml"}],
        )
        # [END load_workspace]

        # [START load_hub]
        from azure.ai.ml import load_hub

        hub = load_hub(
            "../tests/test_configs/workspace/workspacehub_min.yaml",
            params_override=[{"description": "loaded from workspacehub_min.yaml"}],
        )
        # [END load_hub]

        # [START load_workspace_connection]
        from azure.ai.ml import load_connection

        wps_connection = load_connection(source="../tests/test_configs/connection/snowflake_user_pwd.yaml")
        # [END load_workspace_connection]

        # [START customermanagedkey]
        from azure.ai.ml.entities import CustomerManagedKey, Workspace

        cmk = CustomerManagedKey(
            key_vault="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.KeyVault/vaults/vault-name",
            key_uri="https://vault-name.vault.azure.net/keys/key-name/key-version",
        )

        # special bring your own scenario
        byo_cmk = CustomerManagedKey(
            key_vault="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.KeyVault/vaults/vault-name",
            key_uri="https://vault-name.vault.azure.net/keys/key-name/key-version",
            cosmosdb_id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-name",
            storage_id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/storage-name",
            search_id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.Search/searchServices/search-name",
        )

        ws = Workspace(name="ws-name", location="eastus", display_name="My workspace", customer_managed_key=cmk)
        # [END customermanagedkey]

        # [START workspace_managed_network]
        from azure.ai.ml.entities import (
            Workspace,
            ManagedNetwork,
            IsolationMode,
            ServiceTagDestination,
            PrivateEndpointDestination,
            FqdnDestination,
        )

        # Example private endpoint outbound to a blob
        blobrule = PrivateEndpointDestination(
            name="blobrule",
            service_resource_id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/storage-name",
            subresource_target="blob",
            spark_enabled=False,
        )

        # Example service tag rule
        datafactoryrule = ServiceTagDestination(
            name="datafactory", service_tag="DataFactory", protocol="TCP", port_ranges="80, 8080-8089"
        )

        # Example FQDN rule
        pypirule = FqdnDestination(name="pypirule", destination="pypi.org")

        network = ManagedNetwork(
            isolation_mode=IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND,
            outbound_rules=[blobrule, datafactoryrule, pypirule],
        )

        # Workspace configuration
        ws = Workspace(name="ws-name", location="eastus", managed_network=network)
        # [END workspace_managed_network]

        # [START fqdn_outboundrule]
        from azure.ai.ml.entities import FqdnDestination

        # Example FQDN rule
        pypirule = FqdnDestination(name="rulename", destination="pypi.org")
        # [END fqdn_outboundrule]

        # [START private_endpoint_outboundrule]
        from azure.ai.ml.entities import PrivateEndpointDestination

        # Example private endpoint outbound to a blob
        blobrule = PrivateEndpointDestination(
            name="blobrule",
            service_resource_id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/storage-name",
            subresource_target="blob",
            spark_enabled=False,
        )

        # Example private endpoint outbound to an application gateway
        appGwRule = PrivateEndpointDestination(
            name="appGwRule",
            service_resource_id="/subscriptions/00000000-1111-2222-3333-444444444444/resourceGroups/test-rg/providers/Microsoft.Network/applicationGateways/appgw-name",  # cspell:disable-line
            subresource_target="appGwPrivateFrontendIpIPv4",
            spark_enabled=False,
            fqdns=["contoso.com", "contoso2.com"],
        )
        # [END private_endpoint_outboundrule]

        # [START service_tag_outboundrule]
        from azure.ai.ml.entities import ServiceTagDestination

        # Example service tag rule
        datafactoryrule = ServiceTagDestination(
            name="datafactory", service_tag="DataFactory", protocol="TCP", port_ranges="80, 8080-8089"
        )

        # Example service tag rule using custom address prefixes
        customAddressPrefixesRule = ServiceTagDestination(
            name="customAddressPrefixesRule",
            address_prefixes=["168.63.129.16", "10.0.0.0/24"],
            protocol="TCP",
            port_ranges="80, 443, 8080-8089",
        )
        # [END service_tag_outboundrule]

        # [START workspace]
        from azure.ai.ml.entities import Workspace

        ws = Workspace(name="sample-ws", location="eastus", description="a sample workspace object")
        # [END workspace]

        # [START workspace_hub]
        from azure.ai.ml.entities import Hub

        ws = Hub(name="sample-ws", location="eastus", description="a sample workspace hub object")
        # [END workspace_hub]

    @handle_resource_exists_error
    def ml_workspace_config_sample_snippets_operations(self):
        # [START workspace_list]
        from azure.ai.ml.constants import Scope

        # list workspaces in the resource group set in ml_client
        workspaces = ml_client.workspaces.list()
        workspaces = ml_client.workspaces.list(scope=Scope.RESOURCE_GROUP)

        # list workspaces in the subscription set in ml_client
        workspaces = ml_client.workspaces.list(scope=Scope.SUBSCRIPTION)
        # [END workspace_list]

        # [START workspace_get]
        workspace = ml_client.workspaces.get(name="test-ws1")
        # [END workspace_get]

        # [START workspace_get_keys]
        ws_keys = ml_client.workspaces.get_keys(name="test-ws1")
        # [END workspace_get_keys]

        # [START workspace_sync_keys]
        ml_client.workspaces.begin_sync_keys(name="test-ws1")
        # [END workspace_sync_keys]

        # [START workspace_provision_network]
        ml_client.workspaces.begin_provision_network(workspace_name="test-ws1", include_spark=False)
        # [END workspace_provision_network]

        # [START workspace_begin_create]
        from azure.ai.ml.entities import Workspace

        ws = Workspace(
            name="test-ws1",
            description="a test workspace",
            tags={"purpose": "demo"},
            location="eastus",
            resource_group=resource_group,
        )
        ws = ml_client.workspaces.begin_create(workspace=ws).result()
        # [END workspace_begin_create]

        # [START workspace_begin_update]
        ws = ml_client.workspaces.get(name="test-ws1")
        ws.description = "a different description"
        ws = ml_client.workspaces.begin_update(workspace=ws).result()
        # [END workspace_begin_update]

        # [START workspace_begin_delete]
        ml_client.workspaces.begin_delete(name="test-ws", delete_dependent_resources=True, permanently_delete=True)
        # [END workspace_begin_delete]

        # [START workspace_begin_diagnose]
        diagnose_result = ml_client.workspaces.begin_diagnose(name="test-ws1").result()
        # [END workspace_begin_diagnose]

        # [START get_connection]
        from azure.ai.ml import MLClient

        ml_client_ws = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws1")
        connection = ml_client.connections.get(name="test-ws1")
        # [END get_connection]

        # [START create_or_update_connection]
        from azure.ai.ml import MLClient
        from azure.ai.ml.entities import WorkspaceConnection
        from azure.ai.ml.entities import UsernamePasswordConfiguration

        ml_client_ws = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws")
        wps_connection = WorkspaceConnection(
            name="connection-1",
            type="snowflake",
            target="jdbc:snowflake://<myaccount>.snowflakecomputing.com/?db=<mydb>&warehouse=<mywarehouse>&role=<myrole>",  # cspell:disable-line
            credentials=UsernamePasswordConfiguration(username="XXXXX", password="XXXXXX"),
        )
        connection = ml_client_ws.connections.create_or_update(workspace_connection=wps_connection)
        # [END create_or_update_connection]

        # [START delete_connection]
        from azure.ai.ml import MLClient

        ml_client_ws = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws")
        ml_client_ws.connections.delete(name="connection-1")
        # [END delete_connection]

        # [START list_connection]
        from azure.ai.ml import MLClient

        ml_client_ws = MLClient(credential, subscription_id, resource_group, workspace_name="test-ws")
        ml_client_ws.connections.list(connection_type="git")
        # [END list_connection]

        # [START hub_list]
        from azure.ai.ml.constants import Scope

        # list workspaces in the resource group set in ml_client
        hubs = ml_client.workspace_hubs.list()
        hubs = ml_client.workspace_hubs.list(scope=Scope.RESOURCE_GROUP)

        # list workspaces in the subscription set in ml_client
        hubs = ml_client.workspace_hubs.list(scope=Scope.SUBSCRIPTION)
        # [END hub_list]

        # [START hub_get]
        workspace = ml_client.workspace_hubs.get(name="test-hub1")
        # [END hub_get]

        # [START hub_begin_create]
        from azure.ai.ml.entities import Hub

        hub = Hub(
            name="test-hub1",
            description="a test hub",
            tags={"purpose": "demo"},
            location="eastus",
            resource_group=resource_group,
        )
        hub = ml_client.workspace_hubs.begin_create(workspace_hub=hub).result()
        # [END hub_begin_create]

        # [START hub_begin_update]
        hub = ml_client.workspace_hubs.get(name="test-hub1")
        hub.description = "a different description"
        hub = ml_client.workspace_hubs.begin_update(workspace_hub=hub).result()
        # [END hub_begin_update]

        # [START hub_begin_delete]
        ml_client.workspace_hubs.begin_delete(
            name="test-hub1", delete_dependent_resources=True, permanently_delete=True
        )
        # [END hub_begin_delete]

        # [START outbound_rule_list]
        rules = ml_client.workspace_outbound_rules.list(workspace_name="test-ws")
        # [END outbound_rule_list]

        # [START outbound_rule_get]
        rule = ml_client.workspace_outbound_rules.get(workspace_name="test-ws", outbound_rule_name="sample-rule")
        # [END outbound_rule_get]

        # [START outbound_rule_begin_create]
        from azure.ai.ml.entities import FqdnDestination

        fqdn_rule = FqdnDestination(name="rulename", destination="google.com")
        rule = ml_client.workspace_outbound_rules.begin_create(workspace_name="test-ws", rule=fqdn_rule).result()
        # [END outbound_rule_begin_create]

        # [START outbound_rule_begin_update]
        from azure.ai.ml.entities import FqdnDestination

        fqdn_rule = FqdnDestination(name="rulename", destination="linkedin.com")
        rule = ml_client.workspace_outbound_rules.begin_update(workspace_name="test-ws", rule=fqdn_rule).result()
        # [END outbound_rule_begin_update]

        # [START outbound_rule_begin_remove]
        ml_client.workspace_outbound_rules.begin_remove(workspace_name="test-ws", outbound_rule_name="rulename")
        # [END outbound_rule_begin_remove]


if __name__ == "__main__":
    sample = WorkspaceConfigurationOptions()
    sample.ml_workspace_config_sample_snippets_entities()
    sample.ml_workspace_config_sample_snippets_operations()
