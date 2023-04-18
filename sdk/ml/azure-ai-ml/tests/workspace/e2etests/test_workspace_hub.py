# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live
from test_utilities.utils import verify_entity_load_and_dump

from azure.ai.ml import MLClient, load_workspace_hub
from azure.ai.ml.constants._common import PublicNetworkAccess
from azure.ai.ml.entities._hub.hub import WorkspaceHub
from azure.core.paging import ItemPaged
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.core_sdk_test
@pytest.mark.usefixtures(
    "recorded_test", "mock_workspace_arm_template_deployment_name", "mock_workspace_dependent_resource_name_generator"
)
class TestWorkspace(AzureRecordedTestCase):
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    def test_hub_create_update_and_delete(self, client: MLClient, randstr: Callable[[], str], location: str) -> None:
        hub_name = f"e2etest_{randstr('hub_name')}"
        hub_description = f"{hub_name} description"
        hub_display_name = f"{hub_name} display name"
        params_override = [
            {"name": hub_name},
            {"location": location},
            {"description": hub_description},
            {"display_name": hub_display_name},
        ]

        def workspace_validation(hubs):
            workspace_poller = client.hubs.begin_create(workspace_hub=hubs)
            assert isinstance(workspace_poller, LROPoller)
            workspace_hub = workspace_poller.result()
            assert isinstance(workspace_hub, WorkspaceHub)
            assert workspace_hub.name == hub_name
            assert workspace_hub.location == location
            assert workspace_hub.description == hub_description
            assert workspace_hub.display_name == hub_display_name
            assert workspace_hub.public_network_access == PublicNetworkAccess.ENABLED

        workspace_hub = verify_entity_load_and_dump(
            load_workspace_hub,
            workspace_validation,
            "./tests/test_configs/workspace/workspacehub_min.yaml",
            params_override=params_override,
        )[0]

        hub_list = client.hubs.list()
        assert isinstance(hub_list, ItemPaged)
        workspace_hub = client.hubs.get(hub_name)
        assert isinstance(workspace_hub, WorkspaceHub)
        assert workspace_hub.name == hub_name

        param_display_name = "Test display name"
        param_description = "Test description"
        param_tags = {"k1": "v1", "k2": "v2"}
        workspace_poller = client.hubs.begin_update(
            workspace_hub,
            display_name=param_display_name,
            description=param_description,
            public_network_access=PublicNetworkAccess.DISABLED,
            update_dependent_resources=True,
            tags=param_tags,
        )
        assert isinstance(workspace_poller, LROPoller)
        workspace_hub = workspace_poller.result()
        assert isinstance(workspace_hub, WorkspaceHub)
        assert workspace_hub.display_name == param_display_name
        assert workspace_hub.description == param_description
        assert workspace_hub.public_network_access == PublicNetworkAccess.DISABLED
        assert workspace_hub.tags == param_tags
        assert workspace_hub.storage_accounts.count != 0
        assert workspace_hub.key_vaults.count != 0

        poller = client.hubs.begin_delete(hub_name, delete_dependent_resources=True)
        # verify that request was accepted by checking if poller is returned
        assert poller
        assert isinstance(poller, LROPoller)
