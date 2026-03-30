from typing import Callable

import pytest
from collections.abc import Iterable as _Iterable
from devtools_testutils import AzureRecordedTestCase

from azure.ai.ml import MLClient
from azure.ai.ml.constants._common import Scope
from azure.core.exceptions import HttpResponseError
from azure.ai.ml.entities._workspace.workspace import Workspace
from marshmallow import ValidationError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsEarlyGaps(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_list_with_filtered_kinds_accepts_list_and_string(self, client: MLClient) -> None:
        """Verify list accepts filtered_kinds as list and as comma string and returns an iterable."""
        # filtered_kinds as list
        result_list = client.workspaces.list(filtered_kinds=["default", "hub"])  # type: ignore[arg-type]
        assert isinstance(result_list, _Iterable)

        # filtered_kinds as string
        result_str = client.workspaces.list(filtered_kinds="default,hub")
        assert isinstance(result_str, _Iterable)

        # scope subscription path
        result_sub = client.workspaces.list(scope=Scope.SUBSCRIPTION)
        assert isinstance(result_sub, _Iterable)

    @pytest.mark.e2etest
    def test_get_and_get_keys_raise_for_missing_workspace(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Verify get and get_keys raise HttpResponseError for a non-existent workspace name."""
        name = f"e2etest_{randstr('missing')}_get"

        with pytest.raises(HttpResponseError):
            client.workspaces.get(name)

        with pytest.raises(HttpResponseError):
            client.workspaces.get_keys(name)

    @pytest.mark.e2etest
    def test_begin_sync_keys_and_begin_provision_network_behaviors(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Verify begin_sync_keys and begin_provision_network raise HttpResponseError for non-existent workspace."""
        name = f"e2etest_{randstr('missing')}_ops"

        # begin_sync_keys should raise HttpResponseError for a non-existent workspace
        # (either synchronously during initiation or when polling for result)
        with pytest.raises(HttpResponseError):
            poller = client.workspaces.begin_sync_keys(name)
            poller.result()

        # begin_provision_network should also raise for a non-existent workspace
        with pytest.raises(HttpResponseError):
            prov_poller = client.workspaces.begin_provision_network(workspace_name=name, include_spark=True)
            prov_poller.result()


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsGaps(AzureRecordedTestCase):
    @pytest.mark.e2etest
    def test_begin_diagnose_returns_poller_and_result_raises_for_nonexistent_workspace(
        self, client: MLClient, randstr: Callable[[], str]
    ) -> None:
        """Ensure begin_diagnose returns an LROPoller and that awaiting result surfaces service errors.

        Covers markers around begin_diagnose callback and poller handling.
        """
        # use a likely-nonexistent workspace name to exercise error propagation from the service
        fake_name = f"e2etest_{randstr('wps_name')}_diag"

        # begin_diagnose should raise HttpResponseError for a non-existent workspace
        # (either synchronously during initiation or when polling for result)
        with pytest.raises(HttpResponseError):
            poller = client.workspaces.begin_diagnose(fake_name)
            poller.result()

    @pytest.mark.e2etest
    def test__begin_join_raises_when_workspace_missing_hub_id(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Validate that _begin_join performs local validation and raises ValidationError when _hub_id is missing.

        Covers the _begin_join validation branch that checks for workspace._hub_id and raises.
        """
        name = f"e2etest_{randstr('wps_name')}_nojoint"
        # construct a Workspace entity without _hub_id to trigger validation
        ws = Workspace(name=name)

        with pytest.raises(ValidationError):
            # calling the protected helper on the public client operations surface to trigger validation
            client.workspaces._begin_join(ws)
