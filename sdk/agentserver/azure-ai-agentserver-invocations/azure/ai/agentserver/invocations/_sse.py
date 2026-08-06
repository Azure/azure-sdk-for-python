# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Internal server-sent events helpers for the invocations protocol."""

import asyncio  # pylint: disable=do-not-import-asyncio
from collections.abc import AsyncIterator
from typing import Any

_KEEP_ALIVE_COMMENT = ": keep-alive\n\n"


async def _with_keep_alive(
    source: AsyncIterator[Any],
    interval_seconds: float | None,
) -> AsyncIterator[Any]:
    """Interleave SSE keep-alive comments while the source is idle."""
    if not interval_seconds:
        async for item in source:
            yield item
        return

    queue: asyncio.Queue[Any] = asyncio.Queue()
    sentinel = object()
    pump_error: BaseException | None = None

    async def _pump() -> None:
        nonlocal pump_error
        try:
            async for item in source:
                queue.put_nowait(item)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            pump_error = exc
        finally:
            queue.put_nowait(sentinel)

    pump_task = asyncio.create_task(_pump())
    get_task: asyncio.Task[Any] | None = None
    try:
        while True:
            if get_task is None:
                get_task = asyncio.create_task(queue.get())
            try:
                item = await asyncio.wait_for(
                    asyncio.shield(get_task),
                    timeout=interval_seconds,
                )
            except asyncio.TimeoutError:
                yield _KEEP_ALIVE_COMMENT
                continue
            get_task = None
            if item is sentinel:
                break
            yield item
        if pump_error is not None:
            raise pump_error
    finally:
        pending = [task for task in (pump_task, get_task) if task is not None]
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
