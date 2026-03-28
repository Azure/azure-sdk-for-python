from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsBaseGaps(AzureRecordedTestCase):
    @pytest.mark.e2etest
    @pytest.mark.skipif(
        condition=not is_live(),
        reason="Live-only integration validation for workspace operations base gaps",
    )
    def test_placeholder_list_workspaces_does_not_error(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # This placeholder integration test ensures the test scaffolding runs in a live environment.
        # It does not attempt to mock or construct internal operation objects.
        workspaces = list(client.workspaces.list())
        # Assert we get a concrete list object (could be empty in the subscription)
        assert isinstance(workspaces, list)
