# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

"""
Async unit tests to verify that GlobalEndpointManager.refresh_endpoint_list
clears self.refresh_task after a failed/cancelled health-check task,
preventing sticky exceptions on subsequent refresh calls.
"""

import asyncio
from unittest.mock import MagicMock

import pytest

from azure.cosmos.aio._global_endpoint_manager_async import _GlobalEndpointManager


def _make_mock_client():
    """Create a minimal mock client for _GlobalEndpointManager."""
    client = MagicMock()
    client.url_connection = "https://fake-account.documents.azure.com:443/"
    client.connection_policy = MagicMock()
    client.connection_policy.PreferredLocations = []
    client.connection_policy.EnableEndpointDiscovery = False
    client.connection_policy.UseMultipleWriteLocations = False
    return client


@pytest.mark.asyncio
async def test_refresh_task_cleared_after_exception():
    """refresh_task should be None after the awaited task raised an exception."""
    client = _make_mock_client()
    manager = _GlobalEndpointManager(client)

    # Create a completed-with-exception task
    async def _failing_coro():
        raise RuntimeError("transient failure")

    task = asyncio.ensure_future(_failing_coro())
    await asyncio.sleep(0)  # let the task complete
    assert task.done()

    manager.refresh_task = task
    # Ensure no actual refresh logic runs
    manager.last_refresh_time = float("inf")
    manager.refresh_needed = False

    # First call should observe the failure and clear the task
    await manager.refresh_endpoint_list(None)
    assert manager.refresh_task is None

    # Second call should not raise or re-log the stale exception
    await manager.refresh_endpoint_list(None)
    assert manager.refresh_task is None


@pytest.mark.asyncio
async def test_refresh_task_cleared_after_cancellation():
    """refresh_task should be None after the awaited task was cancelled."""
    client = _make_mock_client()
    manager = _GlobalEndpointManager(client)

    # Create a cancelled task
    async def _hanging_coro():
        await asyncio.sleep(3600)

    task = asyncio.ensure_future(_hanging_coro())
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    assert task.done()

    manager.refresh_task = task
    manager.last_refresh_time = float("inf")
    manager.refresh_needed = False

    await manager.refresh_endpoint_list(None)
    assert manager.refresh_task is None


@pytest.mark.asyncio
async def test_refresh_task_cleared_after_success():
    """refresh_task should also be None after a successful task (existing behavior)."""
    client = _make_mock_client()
    manager = _GlobalEndpointManager(client)

    async def _success_coro():
        return "ok"

    task = asyncio.ensure_future(_success_coro())
    await asyncio.sleep(0)
    assert task.done()

    manager.refresh_task = task
    manager.last_refresh_time = float("inf")
    manager.refresh_needed = False

    await manager.refresh_endpoint_list(None)
    assert manager.refresh_task is None
