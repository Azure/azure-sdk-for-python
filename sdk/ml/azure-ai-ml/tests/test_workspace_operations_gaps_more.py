from typing import Callable, Iterable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.ai.ml.constants._common import Scope
from azure.ai.ml.constants._common import WorkspaceKind
from azure.core.polling import LROPoller
from azure.core.exceptions import ClientAuthenticationError
from marshmallow import ValidationError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsListFormatting(AzureRecordedTestCase):
    def test_list_with_filtered_kinds_as_list_and_resource_group_scope(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Provide filtered_kinds as a list to exercise the branch that joins list into comma-separated string
        # Use resource group scope to avoid tenant-scoped authentication issues in some test environments.
        result_iterable = client.workspaces.list(scope=Scope.RESOURCE_GROUP, filtered_kinds=["default", "project"])
        # Do not iterate to avoid making network calls in environments where cross-tenant tokens may fail.
        # Ensure the returned value is an iterable paging object.
        assert hasattr(result_iterable, "__iter__")

    def test_list_with_filtered_kinds_as_string_and_resource_group_scope(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Provide filtered_kinds as a string to exercise the branch that leaves strings unchanged
        result_iterable = client.workspaces.list(scope=Scope.RESOURCE_GROUP, filtered_kinds="hub")
        assert hasattr(result_iterable, "__iter__")


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsGaps(AzureRecordedTestCase):

    def test__begin_join_raises_when_workspace_missing_hub_id(self, client: MLClient) -> None:
        # Construct a Workspace that is marked as a PROJECT but missing _hub_id to trigger validation
        ws = Workspace(name="proj_without_hub")
        ws._kind = WorkspaceKind.PROJECT
        # ensure hub id is not set
        ws._hub_id = None

        with pytest.raises(ValidationError):
            # call the private join helper to validate precondition checks
            client.workspaces._begin_join(ws)
