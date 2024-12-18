# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient, load_workspace
from azure.ai.ml.constants._workspace import IsolationMode, OutboundRuleCategory
from azure.ai.ml.entities._workspace.networking import (
    FqdnDestination,
    ManagedNetwork,
    PrivateEndpointDestination,
    ServiceTagDestination,
)
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.core_sdk_test
@pytest.mark.usefixtures(
    "recorded_test", "mock_workspace_arm_template_deployment_name", "mock_workspace_dependent_resource_name_generator"
)
class TestWorkspaceOutboundRules(AzureRecordedTestCase):
    @pytest.mark.e2etest
    @pytest.mark.mlc
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    def test_workspace_create_with_managed_network_list_show_remove_rules(
        self, client: MLClient, randstr: Callable[[], str], location: str
    ) -> None:
        # resource name key word
        wps_name = f"e2etest_{randstr('wps_name')}_mvnet"

        wps_description = f"{wps_name} description"
        wps_display_name = f"{wps_name} display name"
        params_override = [
            {"name": wps_name},
            {"location": location},
            {"description": wps_description},
            {"display_name": wps_display_name},
        ]
        wps = load_workspace("./tests/test_configs/workspace/workspace_mvnet.yaml", params_override=params_override)

        # test creation
        workspace_poller = client.workspaces.begin_create(workspace=wps)
        assert isinstance(workspace_poller, LROPoller)
        workspace = workspace_poller.result()
        assert isinstance(workspace, Workspace)
        assert workspace.name == wps_name
        assert workspace.location == location
        assert workspace.description == wps_description
        assert workspace.display_name == wps_display_name
        assert workspace.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND

        # test list outbound rules
        rules = client.workspace_outbound_rules.list(workspace_name=wps_name)
        rules_dict = {}
        for rule in rules:
            rules_dict[rule.name] = rule

        assert "my-service" in rules_dict.keys()
        assert isinstance(rules_dict["my-service"], ServiceTagDestination)
        assert rules_dict["my-service"].category == OutboundRuleCategory.USER_DEFINED
        assert rules_dict["my-service"].port_ranges == "80, 8080-8089"
        assert rules_dict["my-service"].protocol == "TCP"
        assert rules_dict["my-service"].service_tag == "DataFactory"

        assert "my-storage" in rules_dict.keys()
        assert isinstance(rules_dict["my-storage"], PrivateEndpointDestination)
        assert rules_dict["my-storage"].category == OutboundRuleCategory.USER_DEFINED
        assert "storageAccounts/mvnetteststorage" in rules_dict["my-storage"].service_resource_id
        assert rules_dict["my-storage"].spark_enabled == False
        assert rules_dict["my-storage"].subresource_target == "blob"

        assert "pytorch" in rules_dict.keys()
        assert isinstance(rules_dict["pytorch"], FqdnDestination)
        assert rules_dict["pytorch"].category == OutboundRuleCategory.USER_DEFINED
        assert rules_dict["pytorch"].destination == "*.pytorch.org"

        # test service tag rule creation that uses address prefixes properties
        assert "custom-address-prefixes-rule" in rules_dict.keys()
        custom_address_prefixes_rule = rules_dict["custom-address-prefixes-rule"]
        assert isinstance(custom_address_prefixes_rule, ServiceTagDestination)
        assert custom_address_prefixes_rule.category == OutboundRuleCategory.USER_DEFINED
        assert custom_address_prefixes_rule.port_ranges == "10,20-30"
        assert custom_address_prefixes_rule.protocol == "TCP"
        assert custom_address_prefixes_rule.service_tag == "AzureMonitor"
        assert "10.0.0.0/24" in custom_address_prefixes_rule.address_prefixes

        # test private endpoint rule creation that uses fqdns properties
        assert "app-gw-pe-rule" in rules_dict.keys()
        app_gw_pe_rule = rules_dict["app-gw-pe-rule"]
        assert isinstance(app_gw_pe_rule, PrivateEndpointDestination)
        assert app_gw_pe_rule.category == OutboundRuleCategory.USER_DEFINED
        assert "applicationGateways/mvnettestappgw" in app_gw_pe_rule.service_resource_id
        assert app_gw_pe_rule.spark_enabled == False
        assert app_gw_pe_rule.subresource_target == "appGwPrivateFrontendIpIPv4"
        assert "test.1.fake.com" in app_gw_pe_rule.fqdns
        assert "test.2.fake.com" in app_gw_pe_rule.fqdns

        # test adding outbound rules with workspace update from yaml
        params_override = [
            {"name": wps_name},
        ]
        wps_update = load_workspace(
            "./tests/test_configs/workspace/workspace_update_mvnet.yaml", params_override=params_override
        )

        workspace_poller = client.workspaces.begin_update(workspace=wps_update)
        assert isinstance(workspace_poller, LROPoller)
        workspace = workspace_poller.result()
        assert isinstance(workspace, Workspace)
        assert workspace.name == wps_name

        # test show rules added
        # FQDN rule
        rule = client.workspace_outbound_rules.get(workspace_name=wps_name, outbound_rule_name="added-fqdnrule")
        assert isinstance(rule, FqdnDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert rule.destination == "test.com"
        # ServiceTag rule
        rule = client.workspace_outbound_rules.get(workspace_name=wps_name, outbound_rule_name="added-servicetagrule")
        assert isinstance(rule, ServiceTagDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert rule.service_tag == "DataFactory"
        assert rule.protocol == "TCP"
        assert rule.port_ranges == "80, 8080-8089"
        # PrivateEndpoint rule
        rule = client.workspace_outbound_rules.get(workspace_name=wps_name, outbound_rule_name="added-perule")
        assert isinstance(rule, PrivateEndpointDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert "storageAccounts/mvnetteststorage2" in rule.service_resource_id
        assert rule.subresource_target == "blob"
        assert rule.spark_enabled == True

        # assert update did not remove existing outbound rules
        rules = client.workspace_outbound_rules.list(workspace_name=wps_name)
        rule_names = [rule.name for rule in rules]
        assert "pytorch" in rule_names
        assert "my-service" in rule_names
        assert "my-storage" in rule_names

        # test outbound rules create with outbound rule operation
        fqdn_rule = FqdnDestination(name="anotherfqdn", destination="google.com")
        rule_poller = client.workspace_outbound_rules.begin_create(workspace_name=wps_name, rule=fqdn_rule)
        assert isinstance(rule_poller, LROPoller)
        rule = rule_poller.result()
        assert isinstance(rule, FqdnDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert rule.destination == "google.com"

        # test outbound rules update with outbound rule operation
        fqdn_rule = FqdnDestination(name="anotherfqdn", destination="adifffqdn.com")
        rule_poller = client.workspace_outbound_rules.begin_create(workspace_name=wps_name, rule=fqdn_rule)
        assert isinstance(rule_poller, LROPoller)
        rule = rule_poller.result()
        assert isinstance(rule, FqdnDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert rule.destination == "adifffqdn.com"

        # test remove outbound rule
        rule_poller = client.workspace_outbound_rules.begin_remove(
            workspace_name=wps_name, outbound_rule_name="pytorch"
        )
        assert isinstance(rule_poller, LROPoller)
        rule_poller.result()

        rule_poller = client.workspace_outbound_rules.begin_remove(
            workspace_name=wps_name, outbound_rule_name="my-service"
        )
        assert isinstance(rule_poller, LROPoller)
        rule_poller.result()

        rule_poller = client.workspace_outbound_rules.begin_remove(
            workspace_name=wps_name, outbound_rule_name="my-storage"
        )
        assert isinstance(rule_poller, LROPoller)
        rule_poller.result()

        # assert remove worked removed the outbound rules
        rules = client.workspace_outbound_rules.list(workspace_name=wps_name)
        rule_names = [rule.name for rule in rules]
        assert "pytorch" not in rule_names
        assert "my-service" not in rule_names
        assert "my-storage" not in rule_names

        # test workspace deletion
        poller = client.workspaces.begin_delete(wps_name, delete_dependent_resources=True)
        # verify that request was accepted by checking if poller is returned
        assert poller
        assert isinstance(poller, LROPoller)

    @pytest.mark.e2etest
    @pytest.mark.mlc
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    def test_workspace_create_with_managed_network_provision_network(
        self, client: MLClient, randstr: Callable[[], str], location: str
    ) -> None:
        # resource name key word
        wps_name = f"e2etest_{randstr('wps_name')}_mvnet"

        wps_description = f"{wps_name} description"
        wps_display_name = f"{wps_name} display name"
        params_override = [
            {"name": wps_name},
            {"location": location},
            {"description": wps_description},
            {"display_name": wps_display_name},
        ]
        wps = load_workspace(None, params_override=params_override)
        wps.managed_network = ManagedNetwork(isolation_mode=IsolationMode.ALLOW_INTERNET_OUTBOUND)

        # test creation
        workspace_poller = client.workspaces.begin_create(workspace=wps)
        assert isinstance(workspace_poller, LROPoller)
        workspace = workspace_poller.result()
        assert isinstance(workspace, Workspace)
        assert workspace.name == wps_name
        assert workspace.location == location
        assert workspace.description == wps_description
        assert workspace.display_name == wps_display_name
        assert workspace.managed_network.isolation_mode == IsolationMode.ALLOW_INTERNET_OUTBOUND

        provisioning_output = client.workspaces.begin_provision_network(
            workspace_name=workspace.name, include_spark=False
        ).result()
        assert provisioning_output.status == "Active"
        assert provisioning_output.spark_ready == False
