# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Unit tests for reporting a CancelledError that leaked from a create handler as a handler error (S-024)."""

from __future__ import annotations

import asyncio
import sys
from typing import Any

import pytest

from azure.ai.agentserver.responses.hosting._routing import _HandlerCancelledError, _surface_leaked_cancellation

requires_task_cancelling = pytest.mark.skipif(
    sys.version_info < (3, 11),
    reason="Task.cancelling() is needed to tell a leaked CancelledError from a cancellation",
)


async def _leaking_events() -> Any:
    yield {"type": "response.created"}
    # What an anyio cancel scope exited from another task leaves behind.
    raise asyncio.CancelledError("Cancelled via cancel scope")


@requires_task_cancelling
async def test_leaked_cancellation_is_reported_as_handler_error() -> None:
    iterator = _surface_leaked_cancellation(_leaking_events(), asyncio.Event())

    assert await iterator.__anext__() == {"type": "response.created"}
    with pytest.raises(_HandlerCancelledError) as raised:
        await iterator.__anext__()
    assert isinstance(raised.value.__cause__, asyncio.CancelledError)


async def test_requested_cancellation_propagates() -> None:
    signal = asyncio.Event()
    signal.set()
    iterator = _surface_leaked_cancellation(_leaking_events(), signal)

    await iterator.__anext__()
    with pytest.raises(asyncio.CancelledError):
        await iterator.__anext__()


async def test_task_cancellation_propagates() -> None:
    started = asyncio.Event()

    async def events() -> Any:
        started.set()
        await asyncio.Event().wait()
        yield {"type": "response.created"}

    async def consume() -> None:
        async for _ in _surface_leaked_cancellation(events(), asyncio.Event()):
            pass

    task = asyncio.create_task(consume())
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


async def test_closing_closes_the_handler_iterator() -> None:
    closed: list[bool] = []

    async def events() -> Any:
        try:
            yield {"type": "response.created"}
            yield {"type": "response.in_progress"}
        finally:
            closed.append(True)

    iterator = _surface_leaked_cancellation(events(), asyncio.Event())
    await iterator.__anext__()
    await iterator.aclose()
    assert closed == [True]
