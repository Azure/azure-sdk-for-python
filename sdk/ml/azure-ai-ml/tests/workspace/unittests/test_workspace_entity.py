from typing import Optional

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_workspace
from azure.ai.ml.entities import ServerlessComputeSettings, Workspace, FqdnDestination, ServiceTagDestination, PrivateEndpointDestination

from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    Workspace as RestWorkspace,
    ManagedNetworkSettings as RestManagedNetwork,
    FqdnOutboundRule as RestFqdnOutboundRule,
    PrivateEndpointOutboundRule as RestPrivateEndpointOutboundRule,
    PrivateEndpointDestination as RestPrivateEndpointOutboundRuleDestination,
    ServiceTagOutboundRule as RestServiceTagOutboundRule,
    ServiceTagDestination as RestServiceTagOutboundRuleDestination,
    ManagedNetworkProvisionStatus as RestManagedNetworkProvisionStatus,
)

from azure.ai.ml.constants._workspace import IsolationMode

@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestWorkspaceEntity:
    def test_workspace_entity_from_rest_object_managednetwork_restclient_versions_match(self):
        rest_mvnet = RestManagedNetwork(
            isolation_mode=IsolationMode.ALLOW_ONLY_APPROVED_OUTBOUND,
            outbound_rules={
                "fqdn-rule": RestFqdnOutboundRule(destination="google.com"),
                "pe-rule": RestPrivateEndpointOutboundRule(destination=RestPrivateEndpointOutboundRuleDestination(service_resource_id="/somestorageid", spark_enabled=False, subresource_target="blob")),
                "servicetag-rule": RestServiceTagOutboundRule(destination=RestServiceTagOutboundRuleDestination(service_tag="sometag", protocol="*", port_ranges="1,2")),
                },
            status=RestManagedNetworkProvisionStatus(status="Active", spark_ready=False))
        rest_ws = RestWorkspace(managed_network=rest_mvnet)

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

        assert isinstance(rules[2], ServiceTagDestination)
        assert rules[2].service_tag == "sometag"
        assert rules[2].protocol == "*"
        assert rules[2].port_ranges == "1,2"


    @pytest.mark.parametrize(
        "settings",
        [
            None,
            ServerlessComputeSettings(None, False),
            ServerlessComputeSettings(
                "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet",
                False,
            ),
            ServerlessComputeSettings(
                "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnetnpip",
                True,
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

    def test_serverless_compute_settings_subnet_name_must_be_an_arm_id(self) -> None:
        with pytest.raises(ValidationError):
            ServerlessComputeSettings("justaname", True)

    @pytest.mark.parametrize(
        "settings",
        [
            ServerlessComputeSettings(
                "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/default",
                True,
            ),  # Override but using same value
            ServerlessComputeSettings(
                "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet",
                True,
            ),
            ServerlessComputeSettings(
                "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/default",
                False,
            ),
            ServerlessComputeSettings(
                "/subscriptions/b17253fa-f327-42d6-9686-f3e553e24763/resourcegroups/static_resources_cli_v2_e2e_tests_resources/providers/Microsoft.Network/virtualNetworks/testwsvnet/subnets/testsubnet",
                False,
            ),
        ],
    )
    def test_workspace_load_override_serverless(self, settings: ServerlessComputeSettings) -> None:
        params_override = [
            {"serverless_compute": {"custom_subnet": settings.custom_subnet, "no_public_ip": settings.no_public_ip}}
        ]

        workspace_override = load_workspace(
            "./tests/test_configs/workspace/workspace_serverless.yaml", params_override=params_override
        )
        assert workspace_override.serverless_compute == settings
