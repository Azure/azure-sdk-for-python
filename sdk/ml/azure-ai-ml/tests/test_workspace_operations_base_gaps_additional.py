from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.entities import Hub, Project, Workspace


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsBaseGetBranches(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_get_returns_hub_and_project_types(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Verify get() returns correct types for existing workspaces.
        # Hub/Project creation & deletion exceeds pytest-timeout (>120s),
        # so we only test get() on the pre-existing workspace.
        ws = client.workspaces.get(client.workspace_name)
        assert ws is not None
        assert isinstance(ws, (Workspace, Hub, Project))
        assert ws.name == client.workspace_name
