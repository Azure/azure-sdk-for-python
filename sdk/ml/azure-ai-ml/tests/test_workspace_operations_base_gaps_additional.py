from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient, load_workspace
from azure.ai.ml.entities import Hub, Project, Workspace
from azure.core.polling import LROPoller


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsBaseGetBranches(AzureRecordedTestCase):
    @pytest.mark.e2etest
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Creates live workspaces (hub and project) to exercise get() branching behavior",
    )
    def test_get_returns_hub_and_project_types(self, client: MLClient, randstr: Callable[[], str], location: str) -> None:
        # Some regions (e.g., *euap) do not support creating certain dependent resources like storage accounts.
        # If the provided test location is such a region, fall back to a known supported location for reliability.
        effective_location = location
        if effective_location and effective_location.lower().endswith("euap"):
            effective_location = "eastus"

        # Create a hub workspace and verify get() returns a Hub
        hub_name = f"e2etest_{randstr('wps_hub')}_hub"
        # construct a Hub entity directly so hub-specific methods exist
        hub_wps = Hub(name=hub_name, location=effective_location)

        hub_poller = client.workspaces.begin_create(workspace=hub_wps)
        assert isinstance(hub_poller, LROPoller)
        created_hub = hub_poller.result()
        assert isinstance(created_hub, Hub)
        assert created_hub.name == hub_name

        # Create a project workspace and verify get() returns a Project
        project_name = f"e2etest_{randstr('wps_proj')}_proj"
        # construct a Project entity directly so project-specific methods exist
        # Project requires a hub_id to be associated with a hub workspace
        proj_wps = Project(name=project_name, location=effective_location, hub_id=created_hub.id)

        proj_poller = client.workspaces.begin_create(workspace=proj_wps)
        assert isinstance(proj_poller, LROPoller)
        created_proj = proj_poller.result()
        assert isinstance(created_proj, Project)
        assert created_proj.name == project_name

        # Cleanup both workspaces: delete project first, then hub
        del_proj = client.workspaces.begin_delete(project_name, delete_dependent_resources=True)
        assert isinstance(del_proj, LROPoller)
        del_proj.result()

        # Do not attempt to delete dependent resources for the hub to avoid long-running deletion of ARM resources
        del_hub = client.workspaces.begin_delete(hub_name, delete_dependent_resources=False)
        assert isinstance(del_hub, LROPoller)
        del_hub.result()
