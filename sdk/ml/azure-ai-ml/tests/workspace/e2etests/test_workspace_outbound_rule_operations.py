# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import MLClient, load_workspace
from azure.ai.ml._utils.utils import camel_to_snake
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.ai.ml.entities._workspace.networking import (
    FqdnDestination,
    PrivateEndpointDestination,
    ServiceTagDestination,
)
from azure.core.paging import ItemPaged
from azure.ai.ml.constants._workspace import IsolationMode, OutboundRuleCategory, OutboundRuleType
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
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        # resource name key word
        wps_name = f"e2etest_{randstr('wps_name')}_mvnet"

        wps_description = f"{wps_name} description"
        wps_display_name = f"{wps_name} display name"
        params_override = [
            {"name": wps_name},
            # {"location": location}, # using master for now
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
        # assert workspace.location == location # using master for now
        assert workspace.description == wps_description
        assert workspace.display_name == wps_display_name
        assert workspace.managed_network.isolation_mode == IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND

        # test list outbound rules
        rules = client._workspace_outbound_rules.list(client.resource_group_name, wps_name)
        rules_dict = {}
        for rule in rules:
            rules_dict[rule.rule_name] = rule

        assert "my-service" in rules_dict.keys()
        assert isinstance(rules_dict["my-service"], ServiceTagDestination)
        assert rules_dict["my-service"].category == OutboundRuleCategory.USER_DEFINED
        assert rules_dict["my-service"].port_ranges == "80, 8080-8089"
        assert rules_dict["my-service"].protocol == "TCP"
        assert rules_dict["my-service"].service_tag == "DataFactory"

        assert "my-storage" in rules_dict.keys()
        assert isinstance(rules_dict["my-storage"], PrivateEndpointDestination)
        assert rules_dict["my-storage"].category == OutboundRuleCategory.USER_DEFINED
        assert "storageAccounts/mvnetstorage1" in rules_dict["my-storage"].service_resource_id
        assert rules_dict["my-storage"].spark_enabled == False
        assert rules_dict["my-storage"].subresource_target == "blob"

        assert "pytorch" in rules_dict.keys()
        assert isinstance(rules_dict["pytorch"], FqdnDestination)
        assert rules_dict["pytorch"].category == OutboundRuleCategory.USER_DEFINED
        assert rules_dict["pytorch"].destination == "*.pytorch.org"

        # test adding outbound rules with workspace update
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
        rule = client._workspace_outbound_rules.get(client.resource_group_name, wps_name, "added-fqdnrule")
        assert isinstance(rule, FqdnDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert rule.destination == "test.com"
        # ServiceTag rule
        rule = client._workspace_outbound_rules.get(client.resource_group_name, wps_name, "added-servicetagrule")
        assert isinstance(rule, ServiceTagDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert rule.service_tag == "DataFactory"
        assert rule.protocol == "TCP"
        assert rule.port_ranges == "80, 8080-8089"
        # PrivateEndpoint rule
        rule = client._workspace_outbound_rules.get(client.resource_group_name, wps_name, "added-perule")
        assert isinstance(rule, PrivateEndpointDestination)
        assert rule.category == OutboundRuleCategory.USER_DEFINED
        assert "storageAccounts/mvnetstorage2" in rule.service_resource_id
        assert rule.subresource_target == "blob"
        assert rule.spark_enabled == True

        # assert update did not remove existing outbound rules
        rules = client._workspace_outbound_rules.list(client.resource_group_name, wps_name)
        rule_names = [rule.rule_name for rule in rules]
        assert "pytorch" in rule_names
        assert "my-service" in rule_names
        assert "my-storage" in rule_names

        # test remove outbound rule
        rule_poller = client._workspace_outbound_rules.begin_remove(client.resource_group_name, wps_name, "pytorch")
        assert isinstance(rule_poller, LROPoller)
        rule_poller.result()

        rule_poller = client._workspace_outbound_rules.begin_remove(client.resource_group_name, wps_name, "my-service")
        assert isinstance(rule_poller, LROPoller)
        rule_poller.result()

        rule_poller = client._workspace_outbound_rules.begin_remove(client.resource_group_name, wps_name, "my-storage")
        assert isinstance(rule_poller, LROPoller)
        rule_poller.result()

        # assert remove worked removed the outbound rules
        rules = client._workspace_outbound_rules.list(client.resource_group_name, wps_name)
        rule_names = [rule.rule_name for rule in rules]
        assert "pytorch" not in rule_names
        assert "my-service" not in rule_names
        assert "my-storage" not in rule_names

        # test workspace deletion
        poller = client.workspaces.begin_delete(wps_name, delete_dependent_resources=True)
        # verify that request was accepted by checking if poller is returned
        assert poller
        assert isinstance(poller, LROPoller)
