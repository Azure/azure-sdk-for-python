from typing import Optional

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_workspace
from azure.ai.ml._restclient.v2024_07_01_preview.models import Workspace
from azure.ai.ml.constants._workspace import IsolationMode
from azure.ai.ml.entities import (
    ServerlessComputeSettings,
    Workspace,
)


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
            {"serverless_compute": {"custom_subnet": settings.custom_subnet, "no_public_ip": settings.no_public_ip}}
        ]

        workspace_override = load_workspace(
            "./tests/test_configs/workspace/workspace_serverless.yaml", params_override=params_override
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
