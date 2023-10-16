from typing import Optional, Tuple

import pytest
from marshmallow.exceptions import ValidationError

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

    @pytest.mark.parametrize("subnet_name", ["just_the_subnet_name", "", None])
    def test_serverless_compute_settings_subnet_must_be_specified_if_no_public_ip_is_true(
        self, subnet_name: str
    ) -> None:
        with pytest.raises(ValidationError):
            ServerlessComputeSettings(subnet_name, True)
