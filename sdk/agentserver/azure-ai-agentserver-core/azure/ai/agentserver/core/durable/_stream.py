# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Pluggable stream handler protocol and default implementation.

Provides :class:`StreamHandler` — a structural protocol that controls
how stream items are transported between the task function (producer
via ``ctx.stream()``) and consumers (via ``async for chunk in run``).

The default :class:`QueueStreamHandler` wraps :class:`asyncio.Queue`
and preserves the existing in-memory, single-consumer behavior.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class StreamHandler(Protocol):
    """Protocol for pluggable stream transports.

    Implementations control how stream items move between the task
    function (producer) and any number of consumers. The framework
    calls :meth:`put` from ``ctx.stream()``, consumers call
    :meth:`get` via ``async for chunk in run``, and the framework
    calls :meth:`close` when the task finishes.

    All three methods are required.
    """

    async def put(self, item: Any) -> None:
        """Accept a stream item from the task function.

        :param item: The value to stream.
        :type item: Any
        """
        ...

    async def get(self) -> Any:
        """Return the next stream item, blocking until one is available.

        :return: The next streamed item.
        :rtype: Any
        :raises StopAsyncIteration: When the stream has been closed.
        """
        ...

    async def close(self) -> None:
        """Signal end-of-stream.

        After this call, :meth:`get` must raise
        :class:`StopAsyncIteration`. Called by the framework when the
        task finishes — both on success and on failure.
        """
        ...


class QueueStreamHandler:
    """Default stream handler wrapping :class:`asyncio.Queue`.

    Single-consumer, in-memory, unbounded. Preserves the exact
    behavior of the previous raw-queue implementation.

    .. versionadded:: 2.1.0
    """

    _SENTINEL: object = object()
    """Internal sentinel placed in the queue by :meth:`close`."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[Any] = asyncio.Queue()

    async def put(self, item: Any) -> None:
        """Enqueue a stream item.

        :param item: The value to stream.
        :type item: Any
        """
        await self._queue.put(item)

    async def get(self) -> Any:
        """Dequeue the next stream item.

        Blocks until an item is available. Raises
        :class:`StopAsyncIteration` when the stream has been closed.

        :return: The next streamed item.
        :rtype: Any
        :raises StopAsyncIteration: When the stream has been closed.
        """
        item = await self._queue.get()
        if item is self._SENTINEL:
            raise StopAsyncIteration
        return item

    async def close(self) -> None:
        """Signal end-of-stream by placing the sentinel in the queue.

        Subsequent :meth:`get` calls will raise
        :class:`StopAsyncIteration`.
        """
        await self._queue.put(self._SENTINEL)


#: Type alias for a factory that creates a :class:`StreamHandler` from a
#: ``task_id``.  Used on the decorator to ensure crash-recovery and resume
#: paths construct the correct handler instead of defaulting to
#: :class:`QueueStreamHandler`.
StreamHandlerFactory = Callable[[str], StreamHandler]
