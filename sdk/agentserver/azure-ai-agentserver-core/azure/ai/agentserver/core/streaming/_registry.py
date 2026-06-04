# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""":data:`streams` registry — process-level lifecycle owner.

See ``streaming.md`` §7 for the authoritative contract. Six methods:

- Three async lifecycle: :meth:`_StreamsRegistry.get`,
  :meth:`_StreamsRegistry.get_or_create`,
  :meth:`_StreamsRegistry.delete`.
- Three sync configurators: :meth:`_StreamsRegistry.use_in_memory_live`,
  :meth:`_StreamsRegistry.use_in_memory_replay`,
  :meth:`_StreamsRegistry.use_file_backed_replay`.

The registry is type-strict — it only ever holds instances of the
three SDK-bundled concrete classes from ``_concrete.py``. Third-
party :class:`EventStream` impls do NOT plug into this registry
(FR-013e + streaming.md §8.4); they ship their own peer registry.

Tombstone retention (rule 36a) — when a stream is destroyed (via
:meth:`delete` or via the CLOSED → GONE auto-transition), the
registry retains a tombstone for the id until it is explicitly
re-created via :meth:`get_or_create`. The tombstone is consulted by
:meth:`get` to distinguish "id never registered" (raises
:class:`EventStreamNotFoundError` → 404) from "id was registered,
now destroyed" (raises :class:`EventStreamGoneError` → 410).
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional, Union

from ._concrete import (
    BroadcastEventStream,
    FileBackedReplayEventStream,
    ReplayEventStream,
)
from ._protocol import (
    EventStream,
    EventStreamGoneError,
    EventStreamNotFoundError,
)


# Sentinel for tombstoned slots (rule 36a)
_TOMBSTONE: object = object()


class _StreamsRegistry:
    """Implementation of the module-level :data:`streams` singleton.

    Do not instantiate directly — use the exported ``streams``
    instance. This is the SDK-private implementation type; the
    public surface is the singleton + the six methods on it.
    """

    def __init__(self) -> None:
        # Streams keyed by id; value is either an EventStream
        # instance OR _TOMBSTONE for destroyed ids.
        self._slots: dict[str, Union[EventStream, object]] = {}
        # Per-id locks for get_or_create atomicity (rule 34).
        self._id_locks: dict[str, asyncio.Lock] = {}
        # Global lock guarding _slots + _id_locks structural mutations.
        self._struct_lock = asyncio.Lock()
        # Factory closure — set by use_* configurators. Default:
        # use_in_memory_live() per rule 37a (also FR-013a).
        self._factory: Callable[[str], EventStream] = lambda _id: BroadcastEventStream()

    # ----- Configurators (sync) -----

    def use_in_memory_live(self) -> None:
        """Configure the registry to construct :class:`BroadcastEventStream`
        instances per :meth:`get_or_create`. See streaming.md §7.1 + §7.2.
        """
        self._factory = lambda _id: BroadcastEventStream()

    def use_in_memory_replay(
        self,
        *,
        cursor_fn: Optional[Callable[[Any], int]] = None,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        """Configure the registry to construct :class:`ReplayEventStream`
        instances per :meth:`get_or_create`. See streaming.md §7.1.
        """
        self._factory = lambda _id: ReplayEventStream(
            cursor_fn=cursor_fn, ttl_seconds=ttl_seconds
        )

    def use_file_backed_replay(
        self,
        *,
        storage_dir: Path,
        cursor_fn: Optional[Callable[[Any], int]] = None,
        ttl_seconds: Optional[float] = None,
        serializer: Optional[Callable[[Any], bytes]] = None,
        deserializer: Optional[Callable[[bytes], Any]] = None,
    ) -> None:
        """Configure the registry to construct :class:`FileBackedReplayEventStream`
        instances per :meth:`get_or_create`. Path layout:
        ``storage_dir / f"{id}.jsonl"``. See streaming.md §7.1.
        """
        storage_dir = Path(storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        self._factory = lambda _id: FileBackedReplayEventStream(
            path=storage_dir / f"{_id}.jsonl",
            cursor_fn=cursor_fn,
            ttl_seconds=ttl_seconds,
            serializer=serializer,
            deserializer=deserializer,
        )

    # ----- Lifecycle (async) -----

    async def _get_id_lock(self, id: str) -> asyncio.Lock:
        async with self._struct_lock:
            lock = self._id_locks.get(id)
            if lock is None:
                lock = asyncio.Lock()
                self._id_locks[id] = lock
            return lock

    async def get(self, id: str) -> EventStream:
        """Look up the existing instance for ``id``.

        - Unregistered id → :class:`EventStreamNotFoundError` (rule 36).
        - Tombstoned (destroyed) id → :class:`EventStreamGoneError`
          (rule 36 + rule 36a).
        - Otherwise: returns the cached :class:`EventStream` instance.
        """
        slot = self._slots.get(id, None)
        if slot is None:
            raise EventStreamNotFoundError(id)
        if slot is _TOMBSTONE:
            raise EventStreamGoneError(id)
        return slot  # type: ignore[return-value]

    async def get_or_create(self, id: str) -> EventStream:
        """Return cached instance for ``id``, or create a new one.

        Atomic across concurrent callers (rule 34): per-id lock
        prevents split-brain construction. A tombstoned id is
        cleared on re-creation (rule 36a).
        """
        # Fast path — already present, not tombstoned
        slot = self._slots.get(id, None)
        if slot is not None and slot is not _TOMBSTONE:
            return slot  # type: ignore[return-value]
        # Slow path — acquire per-id lock + create
        lock = await self._get_id_lock(id)
        async with lock:
            slot = self._slots.get(id, None)
            if slot is not None and slot is not _TOMBSTONE:
                return slot  # type: ignore[return-value]
            instance = self._factory(id)
            self._slots[id] = instance
            return instance

    async def delete(self, id: str) -> None:
        """Destroy the stream registered for ``id``.

        Idempotent (rule 35) — calling on an unregistered or
        already-tombstoned id is a no-op (but still ensures the
        tombstone is in place per rule 36a).

        Invokes the impl's private ``_on_delete()`` hook (rule 33)
        BEFORE installing the tombstone.
        """
        slot = self._slots.get(id, None)
        if slot is None:
            # Never registered — install tombstone for symmetry
            # (the next get(id) raises Gone, not NotFound). This
            # matches rule 36a's "delete is symmetric with rm -f
            # but still leaves a marker" semantics.
            self._slots[id] = _TOMBSTONE
            return
        if slot is _TOMBSTONE:
            return  # idempotent
        # Invoke private cleanup hook on the bundled impl
        on_delete = getattr(slot, "_on_delete", None)
        if on_delete is not None:
            await on_delete()
        self._slots[id] = _TOMBSTONE


# Module-level singleton — THE public registry per FR-013.
streams = _StreamsRegistry()


__all__ = ["streams"]
