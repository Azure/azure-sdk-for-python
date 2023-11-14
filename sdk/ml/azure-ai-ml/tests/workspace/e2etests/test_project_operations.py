# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.entities._workspace.workspace import Workspace

from azure.core.exceptions import ResourceNotFoundError

# Projects (AKA Lean workspaces) have some peculiarities that merit extra e2e testing.
# Unlike other workspaces (both normal and hubs), they can be created without going through
# An arm template. This occurs when the user does not have ARM template deployment permissions,
# but DOES still have permission to deploy a lean workspace a child to a specific workspace hub.
# This occurs when the user has the developer role to a hub, but more restrictive access to the 
# Resource group at large.

# Running note: This test relies on a workspace hub with modified permissions to run properly.
# Since permissions can't be modified by the SDK, there's no way to configure the setup for this
# test without external preperation.
# To that end, here's what needs to be setup.
# A workspace hub (aka AI Resource) with the name "project-e2e-test-container" needs
# to be created in your default resource group.
# That hub then needs to have your access right set to developer.

@pytest.mark.e2etest
@pytest.mark.core_sdk_test
@pytest.mark.usefixtures(
    "recorded_test", "mock_workspace_arm_template_deployment_name", "mock_workspace_dependent_resource_name_generator"
)
class TestWorkspace(AzureRecordedTestCase):
    def test_project_creation_without_template(self, ai_developer_client: MLClient, randstr: Callable[[], str], location: str) -> None:
        proj_name = f"e2etest_{randstr('proj_name')}"

        local_project = Workspace(
            name = proj_name,
            description="e2e test artifact. Delete me if seen for more than a minute.",
            resource_group=ai_developer_client.resource_group_name,
            workspace_hub=ai_developer_client.workspace_name
            )

        res = ai_developer_client.workspaces.begin_create(workspace=local_project)
        created_project = res.result()
        assert created_project.name == local_project.name
        # Returned value should contain full ID of parent hub.
        assert local_project.workspace_hub in created_project.workspace_hub
        assert created_project.location == local_project.location
        assert created_project.storage_account is not None
        assert created_project.key_vault is not None
        assert created_project.application_insights is not None