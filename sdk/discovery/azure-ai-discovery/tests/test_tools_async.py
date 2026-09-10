# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Async tests for Tools operations.

Mirrors test_tools.py against the async ``WorkspaceClient`` from
``azure.ai.discovery.aio``.
"""

from devtools_testutils.aio import recorded_by_proxy_async
from azure.core.exceptions import HttpResponseError
from .testcase import DiscoveryWorkspaceTestCase
from .constants import TOOL_ID, NODE_POOL_ID, WORKSPACE_ENDPOINT, PROJECT_NAME


class TestToolsOperationsAsync(DiscoveryWorkspaceTestCase):
    """Async tests for ToolsOperations."""

    # ---- helpers ---------------------------------------------------------

    async def _begin_run(self, client, *, command='echo "hello world"'):
        """Start a tool run and return the poller."""
        return await client.tools.begin_run(
            project_name=PROJECT_NAME,
            tool_id=TOOL_ID,
            node_pool_ids=[NODE_POOL_ID],
            command=command,
        )

    @staticmethod
    def _operation_id_from_poller(poller):
        if hasattr(poller, "operation_id") and poller.operation_id:
            return poller.operation_id
        initial_response = poller._polling_method._initial_response
        op_location = initial_response.http_response.headers.get("operation-location", "")
        operation_id = op_location.split("/operations/")[-1].split("?")[0]
        assert operation_id, "Could not extract operation_id from poller"
        return operation_id

    # ---- tests -----------------------------------------------------------

    @recorded_by_proxy_async
    async def test_begin_run(self):
        client = self.create_async_workspace_client(endpoint=WORKSPACE_ENDPOINT)
        async with client:
            poller = await self._begin_run(client)
            result = await poller.result()
            assert result is not None

    @recorded_by_proxy_async
    async def test_get_run_status(self):
        client = self.create_async_workspace_client(endpoint=WORKSPACE_ENDPOINT)
        async with client:
            poller = await self._begin_run(client, command='echo "status test (async)"')
            await poller.result()
            operation_id = self._operation_id_from_poller(poller)

            status = await client.tools.get_run_status(
                project_name=PROJECT_NAME,
                operation_id=operation_id,
            )
            assert status is not None
            assert status["status"] is not None
            assert "result" in status

    @recorded_by_proxy_async
    async def test_get_run_status_with_log_count(self):
        client = self.create_async_workspace_client(endpoint=WORKSPACE_ENDPOINT)
        async with client:
            poller = await self._begin_run(client, command='echo "log count test (async)"')
            await poller.result()
            operation_id = self._operation_id_from_poller(poller)

            status = await client.tools.get_run_status(
                project_name=PROJECT_NAME,
                operation_id=operation_id,
                log_count=10,
            )
            assert status is not None
            assert status["status"] is not None
            assert "result" in status

    @recorded_by_proxy_async
    async def test_begin_cancel_run_lro(self):
        """Was sync ``tools.cancel_run`` in beta; LRO ``begin_cancel_run_lro`` in GA.

        Uses ``wait`` rather than ``result`` so the poller does not raise when
        the terminal status is ``Canceled`` (the success case for a cancel).
        """
        client = self.create_async_workspace_client(endpoint=WORKSPACE_ENDPOINT)
        async with client:
            poller = await self._begin_run(client, command='echo "cancel test (async)" && sleep 300')
            operation_id = self._operation_id_from_poller(poller)

            cancel_poller = await client.tools.begin_cancel_run_lro(
                project_name=PROJECT_NAME,
                operation_id=operation_id,
            )
            # Cancel LROs report terminal status ``Canceled`` which azure-core
            # treats as ``OperationFailed``. Catch the exception and verify the
            # terminal status reflects a successful cancellation.
            try:
                await cancel_poller.wait()
                terminal_status = cancel_poller.status()
            except HttpResponseError:
                terminal_status = cancel_poller.status()
            # NOTE: unlike the sync ``LROPoller`` (whose ``done()`` tracks the
            # polling thread finishing), ``AsyncLROPoller.done()`` only flips to
            # True when ``wait()`` returns normally. A terminal ``Canceled``
            # status makes ``wait()`` raise, so ``done()`` stays False here even
            # though the operation is terminal. Assert on the terminal status
            # instead, which reliably reflects that the cancel completed.
            assert terminal_status in (
                "Canceled",
                "Succeeded",
            ), f"Expected terminal Canceled or Succeeded, got {terminal_status!r}"

    @recorded_by_proxy_async
    async def test_get_operations(self):
        client = self.create_async_workspace_client()
        async with client:
            operations = await client.tools.get_operations(
                project_name=PROJECT_NAME,
            )
            assert operations is not None
            assert "value" in operations
            assert isinstance(operations["value"], list)

    @recorded_by_proxy_async
    async def test_get_compute_usage(self):
        client = self.create_async_workspace_client()
        async with client:
            usage = await client.tools.get_compute_usage(
                project_name=PROJECT_NAME,
            )
            assert usage is not None
