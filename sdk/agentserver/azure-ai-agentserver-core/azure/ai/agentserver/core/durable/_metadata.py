# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Mutable progress metadata for durable tasks.

Provides a dict-like interface with typed mutation methods and
debounced persistence to the task storage backend.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import collections.abc
import logging
from collections.abc import Iterator
from typing import Any

logger = logging.getLogger("azure.ai.agentserver.durable")

# Sentinel to distinguish "not set" from None
_NOT_SET = object()


class TaskMetadata:
    """Mutable progress dict persisted to the task record's payload.

    Changes are batched and flushed on a configurable interval, or
    immediately on explicit :meth:`flush`, suspension, or completion.

    :param initial: Initial metadata values (from a recovered task).
    :type initial: dict[str, Any] | None
    :param flush_callback: Async callable that persists dirty metadata.
    :type flush_callback: Callable[[dict[str, Any]], Awaitable[None]] | None
    :param flush_interval: Seconds between automatic flushes (0 = disabled).
    :type flush_interval: float
    """

    def __init__(
        self,
        initial: dict[str, Any] | None = None,
        *,
        flush_callback: Any = None,
        flush_interval: float = 5.0,
    ) -> None:
        self._data: dict[str, Any] = dict(initial) if initial else {}
        self._dirty = False
        self._flush_callback = flush_callback
        self._flush_interval = flush_interval
        self._flush_task: asyncio.Task[None] | None = None
        self._lock = asyncio.Lock()

    def set(self, key: str, value: Any) -> None:
        """Set a key-value pair.

        :param key: Metadata key (must be a string).
        :type key: str
        :param value: Any JSON-serializable value.
        :type value: Any
        :raises TypeError: If key is not a string.
        """
        if not isinstance(key, str):
            raise TypeError(f"Metadata key must be a string, got {type(key).__name__}")
        self._data[key] = value
        self._mark_dirty()

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value by key.

        :param key: Metadata key.
        :type key: str
        :param default: Default value if key is absent.
        :type default: Any
        :return: The value, or *default*.
        :rtype: Any
        """
        return self._data.get(key, default)

    def increment(self, key: str, delta: int = 1) -> None:
        """Atomically increment a numeric value.

        :param key: Metadata key.
        :type key: str
        :param delta: Amount to add (default 1).
        :type delta: int
        :raises TypeError: If the existing value is not numeric.
        """
        if not isinstance(delta, (int, float)):
            raise TypeError(f"Delta must be numeric, got {type(delta).__name__}")
        current = self._data.get(key, 0)
        if not isinstance(current, (int, float)):
            raise TypeError(
                f"Cannot increment non-numeric value at key {key!r}: "
                f"{type(current).__name__}"
            )
        self._data[key] = current + delta
        self._mark_dirty()

    def append(self, key: str, value: Any) -> None:
        """Append a value to a list.

        Creates the list if the key is absent.

        :param key: Metadata key.
        :type key: str
        :param value: Value to append.
        :type value: Any
        :raises TypeError: If the existing value is not a list.
        """
        current = self._data.get(key, _NOT_SET)
        if current is _NOT_SET:
            self._data[key] = [value]
        elif isinstance(current, list):
            current.append(value)
        else:
            raise TypeError(
                f"Cannot append to non-list value at key {key!r}: "
                f"{type(current).__name__}"
            )
        self._mark_dirty()

    def to_dict(self) -> dict[str, Any]:
        """Return a snapshot of all metadata.

        :return: A shallow copy of the metadata dict.
        :rtype: dict[str, Any]
        """
        return dict(self._data)

    # -- Dict protocol (MutableMapping) ------------------------------------

    def __setitem__(self, key: str, value: Any) -> None:
        if not isinstance(key, str):
            raise TypeError(f"Metadata key must be a string, got {type(key).__name__}")
        self._data[key] = value
        self._mark_dirty()

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __delitem__(self, key: str) -> None:
        del self._data[key]
        self._mark_dirty()

    def __contains__(self, key: object) -> bool:
        return key in self._data

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def keys(self) -> collections.abc.KeysView[str]:
        """Return a view of metadata keys.

        :return: A view of the metadata keys.
        :rtype: ~collections.abc.KeysView[str]
        """
        return self._data.keys()

    def values(self) -> collections.abc.ValuesView[Any]:
        """Return a view of metadata values.

        :return: A view of the metadata values.
        :rtype: ~collections.abc.ValuesView[Any]
        """
        return self._data.values()

    def items(self) -> collections.abc.ItemsView[str, Any]:
        """Return a view of metadata key-value pairs.

        :return: A view of the metadata key-value pairs.
        :rtype: ~collections.abc.ItemsView[str, Any]
        """
        return self._data.items()

    async def flush(self) -> None:
        """Force-flush pending metadata changes to the store.

        No-op if there are no pending changes or no flush callback.
        """
        async with self._lock:
            await self._do_flush()

    def start_auto_flush(self) -> None:
        """Start the background auto-flush loop.

        Called by the framework when the task starts executing. Should
        not be called by user code.
        """
        if (
            self._flush_interval > 0
            and self._flush_callback is not None
            and self._flush_task is None
        ):
            self._flush_task = asyncio.get_event_loop().create_task(
                self._auto_flush_loop()
            )

    async def stop_auto_flush(self) -> None:
        """Stop the auto-flush loop and perform a final flush."""
        if self._flush_task is not None:
            self._flush_task.cancel()
            try:
                await self._flush_task
            except asyncio.CancelledError:
                pass
            self._flush_task = None
        # Final flush
        async with self._lock:
            await self._do_flush()

    def _mark_dirty(self) -> None:
        self._dirty = True

    async def _do_flush(self) -> None:
        if not self._dirty or self._flush_callback is None:
            return
        try:
            await self._flush_callback(dict(self._data))
            self._dirty = False
        except Exception:  # pylint: disable=broad-exception-caught
            logger.warning("Failed to flush metadata", exc_info=True)

    async def _auto_flush_loop(self) -> None:
        """Periodically flush dirty metadata."""
        while True:
            await asyncio.sleep(self._flush_interval)
            async with self._lock:
                await self._do_flush()


# Register as a virtual subclass so isinstance checks work
# without inheriting (preserves custom increment/append/flush).
collections.abc.MutableMapping.register(TaskMetadata)
