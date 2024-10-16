from typing import Optional

import pytest
from azure.ai.ml.entities import (
    Workspace,
    FqdnDestination,
    ServiceTagDestination,
    PrivateEndpointDestination,
    FeatureStore,
    Hub,
)

from azure.ai.ml._restclient.v2024_07_01_preview.models import (
    Workspace as RestWorkspace,
    ManagedNetworkSettings as RestManagedNetwork,
    FqdnOutboundRule as RestFqdnOutboundRule,
    PrivateEndpointOutboundRule as RestPrivateEndpointOutboundRule,
    PrivateEndpointDestination as RestPrivateEndpointOutboundRuleDestination,
    ServiceTagOutboundRule as RestServiceTagOutboundRule,
    ServiceTagDestination as RestServiceTagOutboundRuleDestination,
    ManagedNetworkProvisionStatus as RestManagedNetworkProvisionStatus,
    FeatureStoreSettings as RestFeatureStoreSettings,
    ManagedServiceIdentity as RestManagedServiceIdentity,
    ServerlessComputeSettings as RestServerlessComputeSettings,
    UserAssignedIdentity,
    # this one only for workspace hubs
    WorkspaceHubConfig as RestWorkspaceHubConfig,
)
from azure.ai.ml._restclient.v2024_07_01_preview.operations import (
    WorkspacesOperations as RestClientWorkspacesOperations,
    ManagedNetworkSettingsRuleOperations as RestClientManagedNetworkSettingsRuleOperations,
)

from azure.ai.ml.constants._workspace import IsolationMode
from azure.ai.ml import (
    MLClient,
)
from azure.identity import DefaultAzureCredential


def get_test_rest_workspace_with_all_details() -> RestWorkspace:
    rest_managed_network = RestManagedNetwork(
        isolation_mode=IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND,
        outbound_rules={
            "fqdn-rule": RestFqdnOutboundRule(destination="google.com"),
            "pe-rule": RestPrivateEndpointOutboundRule(
                fqdns=["contoso.com", "contoso2.com"],
                destination=RestPrivateEndpointOutboundRuleDestination(
                    service_resource_id="/somestorageid", spark_enabled=False, subresource_target="blob"
                ),
            ),
            "servicetag-rule": RestServiceTagOutboundRule(
                destination=RestServiceTagOutboundRuleDestination(
                    service_tag="sometag",
                    protocol="*",
                    port_ranges="1,2",
                    address_prefixes=["168.63.129.16", "10.0.0.0/24"],
                )
            ),
        },
        status=RestManagedNetworkProvisionStatus(status="Active", spark_ready=False),
    )
    rest_hub_config = RestWorkspaceHubConfig(default_workspace_resource_group="somerg")
    rest_feature_store_settings = RestFeatureStoreSettings(
        offline_store_connection_name="somevalue1", online_store_connection_name="somevalue2"
    )
    rest_managed_service_identity = RestManagedServiceIdentity(
        type="SystemAssigned", user_assigned_identities={"id1": UserAssignedIdentity()}
    )
    rest_serverless_compute = RestServerlessComputeSettings(
        serverless_compute_custom_subnet="/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet",
        serverless_compute_no_public_ip=True,
    )
    return RestWorkspace(
        managed_network=rest_managed_network,
        workspace_hub_config=rest_hub_config,
        feature_store_settings=rest_feature_store_settings,
        identity=rest_managed_service_identity,
        serverless_compute_settings=rest_serverless_compute,
    )


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestWorkspaceEntity:
    """
    test description:
    the purpose of the tests in this file is to ensure _restclient version is correct for
    marshalling and unmarshalling between REST and SDK client objects.

    if you will update the restclient version for anything that is using workspace object
    and related operations (currently: workspace entities, hub entities, network entities,
    WorkspaceOperations, WorkspaceOutboundRuleOperations, FeatureStoreOperations)
    then you will also need to update the restclient version to match in all these locations to avoid
    issues when unmarshalling.
    """

    def test_workspace_related_operations_and_entities_match_restclient_versions(self):
        client = MLClient(
            credential=DefaultAzureCredential(),
            subscription_id="fake-sub-id",
            resource_group_name="fake-rg-name",
        )

        assert "fake-sub-id" == client.subscription_id
        assert "fake-rg-name" == client.resource_group_name

        assert isinstance(
            client._workspace_outbound_rules._rule_operation, RestClientManagedNetworkSettingsRuleOperations
        )
        assert isinstance(client.workspaces._operation, RestClientWorkspacesOperations)
        assert isinstance(client.feature_stores._operation, RestClientWorkspacesOperations)

    def test_workspace_entity_from_rest_object_managednetwork_restclient_versions_match(self):
        rest_ws = get_test_rest_workspace_with_all_details()

        sdk_ws = Workspace._from_rest_object(rest_ws)
        assert sdk_ws.managed_network is not None
        assert sdk_ws.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND
        rules = sdk_ws.managed_network.outbound_rules
        assert isinstance(rules[0], FqdnDestination)
        assert rules[0].destination == "google.com"

        assert isinstance(rules[1], PrivateEndpointDestination)
        assert rules[1].service_resource_id == "/somestorageid"
        assert rules[1].spark_enabled == False
        assert rules[1].subresource_target == "blob"
        assert "contoso.com" in rules[1].fqdns
        assert "contoso2.com" in rules[1].fqdns

        assert isinstance(rules[2], ServiceTagDestination)
        assert rules[2].service_tag == "sometag"
        assert rules[2].protocol == "*"
        assert rules[2].port_ranges == "1,2"
        assert "168.63.129.16" in rules[2].address_prefixes
        assert "10.0.0.0/24" in rules[2].address_prefixes

        assert sdk_ws.identity.user_assigned_identities[0] is not None
        assert sdk_ws.identity.type == "system_assigned"

        # currently it seems serverless_compute is only attribute on basic workspace (not hub/FS)
        assert (
            sdk_ws.serverless_compute.custom_subnet
            == "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet"
        )
        assert sdk_ws.serverless_compute.no_public_ip == True

    def test_workspace_hub_entity_from_rest_to_ensure_restclient_versions_match(self):
        rest_ws = get_test_rest_workspace_with_all_details()

        sdk_hub = Hub._from_rest_object(rest_ws)
        assert sdk_hub.managed_network is not None
        assert sdk_hub.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND
        rules = sdk_hub.managed_network.outbound_rules
        assert isinstance(rules[0], FqdnDestination)
        assert rules[0].destination == "google.com"

        assert isinstance(rules[1], PrivateEndpointDestination)
        assert rules[1].service_resource_id == "/somestorageid"
        assert rules[1].spark_enabled == False
        assert rules[1].subresource_target == "blob"
        assert "contoso.com" in rules[1].fqdns
        assert "contoso2.com" in rules[1].fqdns

        assert isinstance(rules[2], ServiceTagDestination)
        assert rules[2].service_tag == "sometag"
        assert rules[2].protocol == "*"
        assert rules[2].port_ranges == "1,2"
        assert "168.63.129.16" in rules[2].address_prefixes
        assert "10.0.0.0/24" in rules[2].address_prefixes

        assert sdk_hub.identity.user_assigned_identities[0] is not None
        assert sdk_hub.identity.type == "system_assigned"

        # specific to hub
        assert sdk_hub.default_resource_group == "somerg"

    def test_feature_store_entity_from_rest_to_ensure_restclient_versions_match(self):
        rest_ws = get_test_rest_workspace_with_all_details()

        sdk_featurestore = FeatureStore._from_rest_object(rest_ws)
        assert sdk_featurestore.managed_network is not None
        assert sdk_featurestore.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND
        rules = sdk_featurestore.managed_network.outbound_rules
        assert isinstance(rules[0], FqdnDestination)
        assert rules[0].destination == "google.com"

        assert isinstance(rules[1], PrivateEndpointDestination)
        assert rules[1].service_resource_id == "/somestorageid"
        assert rules[1].spark_enabled == False
        assert rules[1].subresource_target == "blob"
        assert "contoso.com" in rules[1].fqdns
        assert "contoso2.com" in rules[1].fqdns

        assert isinstance(rules[2], ServiceTagDestination)
        assert rules[2].service_tag == "sometag"
        assert rules[2].protocol == "*"
        assert rules[2].port_ranges == "1,2"
        assert "168.63.129.16" in rules[2].address_prefixes
        assert "10.0.0.0/24" in rules[2].address_prefixes

        assert sdk_featurestore.identity.user_assigned_identities[0] is not None
        assert sdk_featurestore.identity.type == "system_assigned"

        # specific to feature store
        assert sdk_featurestore._feature_store_settings.offline_store_connection_name == "somevalue1"
        assert sdk_featurestore._feature_store_settings.online_store_connection_name == "somevalue2"
