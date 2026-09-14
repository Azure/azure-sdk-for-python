# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
""":data:`streams` registry — process-level lifecycle owner.

Six methods:

- Three async lifecycle: :meth:`_StreamsRegistry.get`,
  :meth:`_StreamsRegistry.get_or_create`,
  :meth:`_StreamsRegistry.delete`.
- Three sync configurators: :meth:`_StreamsRegistry.use_in_memory_live`,
  :meth:`_StreamsRegistry.use_in_memory_replay`,
  :meth:`_StreamsRegistry.use_file_backed_replay`.

The registry is the lifecycle owner for the three SDK-bundled
backings. Third-party :class:`EventStream` impls do NOT plug into
this registry — they ship their own peer registry.

: ``get(id)`` raises
:class:`EventStreamNotFoundError` for ANY id that is not currently
a live stream — never registered, explicitly :meth:`delete`d, or
close-clock TTL elapsed. The registry retains tombstones for
deleted / auto-tombstoned ids primarily to support re-create-after-
delete semantics (a subsequent :meth:`get_or_create` clears the
tombstone and constructs a fresh stream), NOT to differentiate
the error type — there is only ONE error type for "id is missing".
All paths wire-map to HTTP 404.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any, Optional, Union

from ._concrete import (
    BroadcastEventStream,
    FileBackedReplayEventStream,
    ReplayEventStream,
    _safe_stream_filename,
)
from ._protocol import (
    EventStream,
    EventStreamNotFoundError,
)

logger = logging.getLogger("azure.ai.agentserver.streaming")


# Sentinel for tombstoned slots (rule 36a)
_TOMBSTONE: object = object()

#: Spec 037 #6 — default per-event TTL for file-backed replay streams when the
# caller does not specify one (10 minutes). Bounds on-disk growth; mirrors the
# .NET port's default. JSON serialization is the default already (a ``None``
# serializer/deserializer round-trips via JSON in the stream itself).
_DEFAULT_STREAM_TTL_SECONDS = 600.0


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
        # use_in_memory_live per rule 37a (also).
        self._factory: Callable[[str], EventStream] = lambda _id: BroadcastEventStream()

    # ----- Configurators (sync) -----

    def use_in_memory_live(self) -> None:
        """Configure the registry to construct in-memory **live** streams
        (multicast, no replay buffer). Subscribers see events emitted
        after they subscribe — late subscribers miss earlier events.
        Suitable when consumers attach before the producer starts.
        """
        self._factory = lambda _id: BroadcastEventStream()

    def use_in_memory_replay(
        self,
        *,
        cursor_fn: Optional[Callable[[Any], int]] = None,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        """Configure the registry to construct in-memory **replay** streams.

        Each stream retains its event history (subject to ``ttl_seconds``
        per-event TTL eviction once the stream is closed). Late
        subscribers see the full retained history. Pass ``cursor_fn``
        to enable cursored re-subscription via ``subscribe(after=...)``.

        :keyword cursor_fn: Optional cursor extractor enabling
            ``subscribe(after=...)`` re-subscription.
        :paramtype cursor_fn: Optional[Callable[[Any], int]]
        :keyword ttl_seconds: Optional per-event TTL eviction window.
        :paramtype ttl_seconds: Optional[float]
        """
        self._factory = lambda _id: ReplayEventStream(cursor_fn=cursor_fn, ttl_seconds=ttl_seconds)

    def use_file_backed_replay(
        self,
        *,
        storage_dir: Optional[Path] = None,
        cursor_fn: Optional[Callable[[Any], int]] = None,
        ttl_seconds: Optional[float] = None,
        serializer: Optional[Callable[[Any], bytes]] = None,
        deserializer: Optional[Callable[[bytes], Any]] = None,
    ) -> None:
        """Configure the registry to construct **file-backed replay** streams.

        Each stream persists its event log to ``storage_dir / "<file>.jsonl"``
        (the id is sanitized to a filesystem-safe name) and rehydrates on
        construction if the file already exists (crash-recovery friendly). Same
        replay + TTL + cursor semantics as :meth:`use_in_memory_replay`.

        Ergonomic defaults (Spec 037 #6) — the common case is a single call
        supplying only ``cursor_fn``:

        - ``storage_dir`` defaults to ``resolve_state_subdir("streams")`` (a
          ``streams`` directory under the shared agent-server state root,
          alongside ``tasks``).
        - ``ttl_seconds`` defaults to ``600`` (10 minutes).
        - ``serializer`` / ``deserializer`` default to JSON.

        :keyword storage_dir: Directory the per-stream event logs are written to.
            Defaults to ``resolve_state_subdir("streams")``.
        :paramtype storage_dir: Optional[~pathlib.Path]
        :keyword cursor_fn: Optional cursor extractor enabling
            ``subscribe(after=...)`` re-subscription.
        :paramtype cursor_fn: Optional[Callable[[Any], int]]
        :keyword ttl_seconds: Optional per-event TTL eviction window. Defaults to
            600 seconds (10 minutes).
        :paramtype ttl_seconds: Optional[float]
        :keyword serializer: Optional payload-to-bytes serializer. Defaults to JSON.
        :paramtype serializer: Optional[Callable[[Any], bytes]]
        :keyword deserializer: Optional bytes-to-payload deserializer. Defaults to JSON.
        :paramtype deserializer: Optional[Callable[[bytes], Any]]
        """
        if (serializer is None) != (deserializer is None):
            # C-STR-FBR-3 — fail fast at config time on a half-configured pair.
            raise ValueError(
                "use_file_backed_replay: 'serializer' and 'deserializer' must be "
                "supplied both-or-neither (C-STR-FBR-3)"
            )
        if storage_dir is None:
            from .._config import resolve_state_subdir  # pylint: disable=import-outside-toplevel

            storage_dir = resolve_state_subdir("streams")
        if ttl_seconds is None:
            ttl_seconds = _DEFAULT_STREAM_TTL_SECONDS
        storage_dir = Path(storage_dir)
        storage_dir.mkdir(parents=True, exist_ok=True)
        self._factory = lambda _id: FileBackedReplayEventStream(
            path=storage_dir / _safe_stream_filename(_id),
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

          — every "id is not currently a live
        stream" condition raises :class:`EventStreamNotFoundError`:

        - Unregistered id (never seen).
        - Explicitly :meth:`delete`d id (tombstoned).
        - Closed stream whose close-clock TTL deadline has elapsed
          (auto-tombstoned).

        :param id: The stream id to look up.
        :type id: str
        :return: The live stream instance for ``id``.
        :rtype: EventStream
        """
        slot = self._slots.get(id, None)
        if slot is None:
            raise EventStreamNotFoundError(id)
        if slot is _TOMBSTONE:
            raise EventStreamNotFoundError(id)
        #   — opportunistic close-clock check.
        # If the stream's internal _maybe_auto_transition_to_gone
        # would fire, install the registry tombstone now and raise
        # NotFound. This makes the registry-level auto-tombstone
        # observable even without an explicit emit/subscribe on the
        # instance.
        if await self._tombstone_if_close_clock_elapsed(id, slot):
            raise EventStreamNotFoundError(id)
        return slot  # type: ignore[return-value]

    async def _tombstone_if_close_clock_elapsed(self, id: str, slot: Any) -> bool:
        """If the stream's close-clock TTL elapsed, run its
        ``_on_delete`` cleanup hook and install the registry
        tombstone. Returns True iff the tombstone was installed.

          /  — file-backed cleanup happens
        BEFORE the registry tombstone install per C-STR-FBR-4.

        :param id: The stream id to check.
        :type id: str
        :param slot: The registry slot (stream instance) for ``id``.
        :type slot: Any
        :return: True iff the tombstone was installed.
        :rtype: bool
        """
        maybe_check = getattr(slot, "_maybe_auto_transition_to_gone", None)
        if maybe_check is None:
            return False
        # Trigger the check; the instance may flip its state to GONE.
        try:
            async with getattr(slot, "_lock", asyncio.Lock()):
                maybe_check()
        except Exception:  # pylint: disable=broad-except
            return False
        # Read the state attribute non-strictly.
        if getattr(slot, "_state", None) != "GONE":
            return False
        # State has transitioned — perform cleanup + install tombstone.
        on_delete = getattr(slot, "_on_delete", None)
        if on_delete is not None:
            try:
                await on_delete()
            except Exception:  # pylint: disable=broad-except
                logger.warning(
                    "EventStream %s: _on_delete cleanup hook failed during auto-tombstone", id, exc_info=True
                )
        self._slots[id] = _TOMBSTONE
        logger.debug("EventStream %s auto-tombstoned (close-clock TTL elapsed)", id)
        return True

    async def get_or_create(self, id: str) -> EventStream:
        """Return cached instance for ``id``, or create a new one.

        Atomic across concurrent callers: a per-id lock prevents
        split-brain construction when two coroutines race to create
        the same id. A previously-destroyed id is cleared on
        re-creation.

        :param id: The stream id to return or create.
        :type id: str
        :return: The cached or newly-created stream instance.
        :rtype: EventStream
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
            logger.debug("EventStream %s created (%s)", id, type(instance).__name__)
            return instance

    async def delete(self, id: str) -> None:
        """Destroy the stream registered for ``id``.

        Idempotent — calling on an unregistered or already-destroyed
        id is a no-op (but still ensures the tombstone is in place so
        subsequent ``get(id)`` raises ``EventStreamNotFoundError``).

        Cleans up backing resources (e.g. file handles for the
        file-backed replay backing) before installing the tombstone
        / C-STR-FBR-4.

        :param id: The stream id to destroy.
        :type id: str
        """
        slot = self._slots.get(id, None)
        if slot is None:
            # Never registered — install tombstone for symmetry
            # (the next get(id) raises ``EventStreamNotFoundError``).
            # This matches rule 36a's "delete is symmetric with rm -f
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
        logger.debug("EventStream %s deleted", id)


# Module-level singleton — THE public registry.
streams = _StreamsRegistry()


__all__ = ["streams"]
