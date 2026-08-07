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
    """Interleave SSE keep-alive comments while the source is idle.

    :param source: The source SSE stream.
    :type source: ~collections.abc.AsyncIterator
    :param interval_seconds: Seconds of inactivity between keep-alive comments,
        or zero/``None`` to disable them.
    :type interval_seconds: float or None
    :return: The source chunks with keep-alive comments inserted during idle periods.
    :rtype: ~collections.abc.AsyncIterator
    """
    if not interval_seconds:
        async for item in source:
            yield item
        return

    requests: asyncio.Queue[asyncio.Future[Any]] = asyncio.Queue(maxsize=1)
    sentinel = object()

    async def _pump() -> None:
        try:
            while True:
                result = await requests.get()
                try:
                    item = await anext(source)
                except StopAsyncIteration:
                    result.set_result(sentinel)
                    return
                except Exception as exc:  # pylint: disable=broad-exception-caught
                    result.set_exception(exc)
                    return
                result.set_result(item)
        finally:
            close = getattr(source, "aclose", None)
            if close is not None:
                await close()

    pump_task = asyncio.create_task(_pump())
    next_result: asyncio.Future[Any] | None = None
    try:
        while True:
            if next_result is None:
                next_result = asyncio.get_running_loop().create_future()
                requests.put_nowait(next_result)
            try:
                item = await asyncio.wait_for(
                    asyncio.shield(next_result),
                    timeout=interval_seconds,
                )
            except asyncio.TimeoutError:
                yield _KEEP_ALIVE_COMMENT
                continue
            next_result = None
            if item is sentinel:
                break
            yield item
    finally:
        if next_result is not None:
            next_result.cancel()
        pump_task.cancel()
        await asyncio.gather(pump_task, return_exceptions=True)
