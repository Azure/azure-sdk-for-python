from typing import Optional

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_workspace
from azure.ai.ml.entities import ServerlessComputeSettings, Workspace


@pytest.mark.unittest
@pytest.mark.core_sdk_test
class TestWorkspaceEntity:
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
