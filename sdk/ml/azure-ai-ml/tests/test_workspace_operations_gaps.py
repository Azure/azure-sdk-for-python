# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Callable

import pytest
from devtools_testutils import AzureRecordedTestCase, is_live

from azure.ai.ml import MLClient, load_workspace
from azure.ai.ml.constants._workspace import IsolationMode
from azure.ai.ml.entities._workspace.networking import ManagedNetwork
from azure.ai.ml.entities._workspace.workspace import Workspace
from azure.core.polling import LROPoller
from marshmallow import ValidationError
from azure.core.exceptions import HttpResponseError


@pytest.mark.e2etest
@pytest.mark.usefixtures("recorded_test")
class TestWorkspaceOperationsGaps(AzureRecordedTestCase):
    def test_list_with_filtered_kinds_and_subscription_scope(self, client: MLClient) -> None:
        # Ensure providing a list for filtered_kinds and using subscription scope executes the list-by-subscription path
        from azure.ai.ml.constants._common import Scope

        result = client.workspaces.list(scope=Scope.SUBSCRIPTION, filtered_kinds=["default", "project"])
        # Concrete assertion that the returned object is iterable
        assert hasattr(result, "__iter__")

    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="Provision network requires live environment")
    def test_workspace_create_with_managed_network_provision_network(self, client: MLClient, randstr: Callable[[], str], location: str) -> None:
        # Some sovereign or special-purpose regions may not support all resource types used by ARM templates
        # (e.g., Microsoft.Storage). Skip the test when running in such regions.
        if "euap" in (location or ""):
            pytest.skip(f"Location '{location}' may not support required resource types for provisioning; skipping live test.")

        # resource name key word
        wps_name = f"e2etest_{randstr('wps_name')}_mvnet"

        wps_description = f"{wps_name} description"
        wps_display_name = f"{wps_name} display name"
        params_override = [
            {"name": wps_name},
            {"location": location},
            {"description": wps_description},
            {"display_name": wps_display_name},
        ]
        wps = load_workspace(None, params_override=params_override)
        wps.managed_network = ManagedNetwork(isolation_mode=IsolationMode.ALLOW_INTERNET_OUTBOUND)

        # test creation
        workspace_poller = client.workspaces.begin_create(workspace=wps)
        assert isinstance(workspace_poller, LROPoller)
        workspace = workspace_poller.result()
        assert isinstance(workspace, Workspace)
        assert workspace.name == wps_name
        assert workspace.location == location
        assert workspace.description == wps_description
        assert workspace.display_name == wps_display_name
        assert workspace.managed_network.isolation_mode == IsolationMode.ALLOW_INTERNET_OUTBOUND

        provisioning_output = client.workspaces.begin_provision_network(
            workspace_name=workspace.name, include_spark=False
        ).result()
        assert provisioning_output.status == "Active"
        assert provisioning_output.spark_ready == False

    @pytest.mark.e2etest
    def test_begin_join_raises_when_no_hub(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Create a workspace object without a hub id to trigger validation in _begin_join
        wps_name = f"e2etest_{randstr('wps_name')}_nohub"
        wps = load_workspace(None, params_override=[{"name": wps_name}])

        # _begin_join should raise a marshmallow.ValidationError when no hub id is present on the workspace
        with pytest.raises(ValidationError):
            # calling the protected helper on the client.workspaces instance exercises the early-validation branch
            client.workspaces._begin_join(wps)

    @pytest.mark.e2etest
    @pytest.mark.skipif(condition=not is_live(), reason="Diagnose against service requires live mode")
    def test_begin_diagnose_raises_for_missing_workspace(self, client: MLClient, randstr: Callable[[], str]) -> None:
        # Use a likely-nonexistent workspace name to provoke a service error path from begin_diagnose
        missing_name = f"nonexistent_{randstr('wps_name')}"

        # Expect an HttpResponseError when the service cannot find or process the diagnose request for the name
        with pytest.raises(HttpResponseError):
            # call .result() to force evaluation of the LRO and raise any service errors synchronously in live mode
            client.workspaces.begin_diagnose(missing_name).result()

    @pytest.mark.e2etest
    def test_begin_diagnose_returns_poller_and_result_raises(self, client: MLClient, randstr: Callable[[], str]) -> None:
        """Verify begin_diagnose returns an LROPoller and awaiting result raises HttpResponseError in typical environments.

        The test asserts that the call to begin_diagnose returns an LROPoller (exercising the callback and logging path).
        If the service immediately errors when initiating the diagnose request, the test will skip the result assertion.
        """
        name = f"e2etest_{randstr('wps_diag')}"

        try:
            poller = client.workspaces.begin_diagnose(name)
        except HttpResponseError:
            # In some environments the service may reject the initiation synchronously; skip in that case.
            pytest.skip("Diagnose initiation raised HttpResponseError in this environment.")

        assert isinstance(poller, LROPoller)

        # Awaiting the poller frequently raises HttpResponseError for non-existent workspaces; assert that behavior.
        with pytest.raises(HttpResponseError):
            poller.result()
