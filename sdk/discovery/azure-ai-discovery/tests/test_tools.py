# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Tests for Tools operations.

Covers all 5 methods on WorkspaceClient.tools:
  - begin_run (LRO)
  - get_run_status
  - cancel_run
  - get_operations
  - get_compute_usage
"""
import os

from devtools_testutils import recorded_by_proxy
from .testcase import DiscoveryWorkspaceTestCase
from .constants import TOOL_ID, NODE_POOL_ID, WORKSPACE_ENDPOINT, PROJECT_NAME


class TestToolsOperations(DiscoveryWorkspaceTestCase):
    """Tests for ToolsOperations."""

    # ---- helpers ---------------------------------------------------------

    def _begin_run(self, client, *, command='echo "hello world"'):
        """Start a tool run and return the poller."""
        return client.tools.begin_run(
            project_name=PROJECT_NAME,
            tool_id=TOOL_ID,
            node_pool_ids=[NODE_POOL_ID],
            command=command,
        )

    @staticmethod
    def _operation_id_from_poller(poller):
        """Extract the server-assigned operation_id from an LRO poller.

        Reads the operation-location header from the initial response, since
        the SDK does not expose the id directly on the poller object.
        """
        if hasattr(poller, "operation_id") and poller.operation_id:
            return poller.operation_id
        initial_response = poller._polling_method._initial_response
        op_location = initial_response.http_response.headers.get("operation-location", "")
        operation_id = op_location.split("/operations/")[-1].split("?")[0]
        assert operation_id, "Could not extract operation_id from poller"
        return operation_id

    # ---- tests -----------------------------------------------------------

    @recorded_by_proxy
    def test_begin_run(self):
        """Test starting a tool run (LRO).

        Requires a valid tool_id and node_pool_ids configured in the workspace.
        Tool runs consume compute resources.
        """
        client = self.create_workspace_client(endpoint=WORKSPACE_ENDPOINT)
        poller = self._begin_run(client)
        result = poller.result()
        assert result is not None

    @recorded_by_proxy
    def test_get_run_status(self):
        """Test getting the status of a tool run.

        Starts a fresh run to obtain a real operation_id, waits for it to
        complete, then queries its status.
        """
        client = self.create_workspace_client(endpoint=WORKSPACE_ENDPOINT)
        poller = self._begin_run(client, command='echo "status test"')
        poller.result()  # wait for completion so status is final
        operation_id = self._operation_id_from_poller(poller)

        status = client.tools.get_run_status(
            project_name=PROJECT_NAME,
            operation_id=operation_id,
        )
        assert status is not None
        assert status["status"] is not None
        assert "result" in status

    @recorded_by_proxy
    def test_get_run_status_with_log_count(self):
        """Test getting run status with the log_count parameter."""
        client = self.create_workspace_client(endpoint=WORKSPACE_ENDPOINT)
        poller = self._begin_run(client, command='echo "log count test"')
        poller.result()
        operation_id = self._operation_id_from_poller(poller)

        status = client.tools.get_run_status(
            project_name=PROJECT_NAME,
            operation_id=operation_id,
            log_count=10,
        )
        assert status is not None
        assert status["status"] is not None
        assert "result" in status

    @recorded_by_proxy
    def test_cancel_run(self):
        """Test cancelling a tool run by starting one and immediately cancelling it."""
        client = self.create_workspace_client(endpoint=WORKSPACE_ENDPOINT)

        # Start a long-running command so we have time to cancel it
        poller = self._begin_run(client, command='echo "cancel test" && sleep 300')
        operation_id = self._operation_id_from_poller(poller)

        client.tools.cancel_run(
            project_name=PROJECT_NAME,
            operation_id=operation_id,
        )

    @recorded_by_proxy
    def test_get_operations(self):
        """Test listing tool operations in a project."""
        client = self.create_workspace_client()
        operations = client.tools.get_operations(
            project_name=PROJECT_NAME,
        )
        assert operations is not None
        assert "value" in operations
        assert isinstance(operations["value"], list)

    @recorded_by_proxy
    def test_get_compute_usage(self):
        """Test getting compute usage for a project."""
        client = self.create_workspace_client()
        usage = client.tools.get_compute_usage(
            project_name=PROJECT_NAME,
        )
        assert usage is not None