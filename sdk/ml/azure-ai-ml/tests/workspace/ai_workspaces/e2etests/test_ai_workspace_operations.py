# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable, List

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Hub, Project, Workspace
from azure.core.polling import LROPoller
from azure.ai.ml.constants._common import WorkspaceType


@pytest.mark.e2etest
@pytest.mark.core_sdk_test
@pytest.mark.usefixtures(
    "recorded_test", "mock_workspace_arm_template_deployment_name", "mock_workspace_dependent_resource_name_generator"
)
class TestWorkspace(AzureRecordedTestCase):
    def compare_hub(self, hub1: Hub, hub2: Hub):
        assert hub1 is not None
        assert hub2 is not None
        assert hub1.name == hub2.name
        assert hub1.location == hub2.location
        assert hub1.description == hub2.description
        assert hub1.display_name == hub2.display_name
        assert hub1.default_workspace_resource_group in hub2.default_workspace_resource_group

    def compare_project(self, project1: Project, project2: Project):
        assert project1 is not None
        assert project2 is not None
        assert project1.name == project2.name
        assert project1.location == project2.location
        assert project1.description == project2.description
        assert project1.display_name == project2.display_name
        assert project1.hub_id == project2.hub_id

    def check_listed_workspaces(self, expected_workspaces: List[Workspace], listed_workspaces: List[Workspace]):
        target_names = [ws.name for ws in expected_workspaces]
        matches_found = 0
        for ws in listed_workspaces:
            if ws.name in target_names:
                matches_found += 1
        assert matches_found == len(expected_workspaces)

    @pytest.mark.skipif(
        condition=not is_live(),
        reason="ARM template makes playback complex, so the test is flaky when run against recording",
    )
    def test_ai_workspace_operations(self, client: MLClient, randstr: Callable[[], str], location: str) -> None:
        # declare values for finally-block cleanup
        created_hub = None
        created_project1 = None
        created_project2 = None
        try:
            # Create hub with 2 child projects
            local_hub = Hub(
                name=f"test_hub_{randstr('hub_name')}",
                description="hub description",
                display_name="hub display name",
                location="westus2",
                default_workspace_resource_group=client.resource_group_name,
            )
            created_hub = client.workspaces.begin_create(workspace=local_hub).result()
            assert created_hub.associated_workspaces is None

            local_project1 = Project(
                name=f"test_proj_1_{randstr('project_1_name')}",
                hub_id=created_hub.id,
                description="project1 description",
                display_name="project1 display name",
                location="westus2",
            )
            created_project1 = client.workspaces.begin_create(workspace=local_project1).result()

            local_project2 = Project(
                name=f"test_proj_2_{randstr('project_2_name')}",
                hub_id=created_hub.id,
                description="project2 description",
                display_name="project2 display name",
                location="westus2",
            )
            created_project2 = client.workspaces.begin_create(workspace=local_project2).result()

            project_ids = [created_project1.id, created_project2.id]

            # Validate created hub and projects against local originals
            self.compare_hub(local_hub, created_hub)
            self.compare_project(local_project1, created_project1)
            self.compare_project(local_project2, created_project2)

            # Get created hub and projects
            gotten_hub = client.workspaces.get(local_hub.name)
            # Now that we've created projects, the hub should have them listed within itself as
            # associated workspaces.
            assert all(id in gotten_hub.associated_workspaces for id in project_ids)
            gotten_project1 = client.workspaces.get(local_project1.name)
            gotten_project2 = client.workspaces.get(local_project2.name)
            # Compare gotten hub and projects against local originals
            self.compare_hub(local_hub, gotten_hub)
            self.compare_project(local_project1, gotten_project1)
            self.compare_project(local_project2, gotten_project2)

            # Get various permutations of listed workspaces.
            listed_hubs = [hub for hub in client.workspaces.list(kind=WorkspaceType.HUB)]
            listed_projects = [project for project in client.workspaces.list(kind=WorkspaceType.PROJECT)]
            listed_projects2 = [
                project for project in client.workspaces.list(kind=WorkspaceType.PROJECT, scope="subscription")
            ]
            listed_projects_and_hubs = [
                stuff for stuff in client.workspaces.list(kind=[WorkspaceType.HUB, WorkspaceType.PROJECT])
            ]
            listed_workspaces = [workspace for workspace in client.workspaces.list(kind=[WorkspaceType.DEFAULT])]
            normal_list = [stuff for stuff in client.workspaces.list()]

            # Ensure that each list contains the expected subset.
            self.check_listed_workspaces([local_hub], listed_hubs)
            self.check_listed_workspaces([local_project1, local_project2], listed_projects)
            self.check_listed_workspaces([local_project1, local_project2], listed_projects2)
            self.check_listed_workspaces([local_hub, local_project1, local_project2], listed_projects_and_hubs)
            self.check_listed_workspaces([], listed_workspaces)
            self.check_listed_workspaces([local_hub, local_project1, local_project2], normal_list)
        finally:
            # Delete both projects and the hub.
            if created_project1 is not None:
                poller = client.workspaces.begin_delete(created_project1.name, delete_dependent_resources=True)
                assert poller
                assert isinstance(poller, LROPoller)
                poller.wait()  # Need to wait for projects to be cleaned before deleting parent hub.

            if created_project2 is not None:
                poller = client.workspaces.begin_delete(created_project2.name, delete_dependent_resources=True)
                assert poller
                assert isinstance(poller, LROPoller)
                poller.wait()  # Need to wait for projects to be cleaned before deleting parent hub.

            if created_hub is not None:
                poller = client.workspaces.begin_delete(created_hub.name, delete_dependent_resources=True)
                assert poller
                assert isinstance(poller, LROPoller)
