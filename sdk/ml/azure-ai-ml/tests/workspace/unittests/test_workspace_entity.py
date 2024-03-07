from typing import Optional

import pytest
from marshmallow.exceptions import ValidationError

from azure.ai.ml import load_workspace
from azure.ai.ml._restclient.v2023_08_01_preview.models import FqdnOutboundRule as RestFqdnOutboundRule
from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    ManagedNetworkProvisionStatus as RestManagedNetworkProvisionStatus,
)
from azure.ai.ml._restclient.v2023_08_01_preview.models import ManagedNetworkSettings as RestManagedNetwork
from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    PrivateEndpointDestination as RestPrivateEndpointOutboundRuleDestination,
)
from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    PrivateEndpointOutboundRule as RestPrivateEndpointOutboundRule,
)
from azure.ai.ml._restclient.v2023_08_01_preview.models import ServerlessComputeSettings
from azure.ai.ml._restclient.v2023_08_01_preview.models import (
    ServiceTagDestination as RestServiceTagOutboundRuleDestination,
)
from azure.ai.ml._restclient.v2023_08_01_preview.models import ServiceTagOutboundRule as RestServiceTagOutboundRule
from azure.ai.ml._restclient.v2023_08_01_preview.models import Workspace
from azure.ai.ml._restclient.v2023_08_01_preview.models import Workspace as RestWorkspace
from azure.ai.ml.constants._workspace import IsolationMode
from azure.ai.ml.entities import (
    FqdnDestination,
    PrivateEndpointDestination,
    ServerlessComputeSettings,
    ServiceTagDestination,
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
