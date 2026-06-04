# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SDK-bundled :class:`~._protocol.EventStream` implementations.

This module is SDK-private (underscore-prefixed). External callers
obtain instances exclusively via the ``streams`` registry's three
``use_*`` configurators (see ``streaming.md`` §7.1 + rule 38). The
classes here are reachable only via this private import path:

    from azure.ai.agentserver.core.streaming._concrete import (
        BroadcastEventStream,
        ReplayEventStream,
        FileBackedReplayEventStream,
    )

This path is for internal SDK tests (impl-specific assertions: file
lock detection, corruption recovery, per-event TTL eviction
observability, broadcast no-buffer semantics) only. Consumer
packages (responses, invocations) MUST NOT use it — enforced by
SC-006b / SC-010 grep gates.

See ``streaming.md`` §5 for the per-class authoritative contract.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import json
import os
import time
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any, Optional

from ._protocol import (
    EventStream,
    EventStreamClosedError,
    EventStreamGoneError,
)

# Try POSIX fcntl; fall back to a lock-file scheme on platforms
# without it (Windows). Per streaming.md rule 32.
try:
    import fcntl  # type: ignore[import-not-found]

    _HAS_FCNTL = True
except ImportError:  # pragma: no cover - windows
    _HAS_FCNTL = False


# ---------------------------------------------------------------
# Internal sentinels + state markers
# ---------------------------------------------------------------

_GONE_SENTINEL: object = object()
"""Pushed to subscriber queues to signal end-of-stream.

Either close (drain remaining items then terminate cleanly) or
registry-driven delete (immediate cutoff — raise StopAsyncIteration
on next __anext__). The subscriber loop distinguishes by checking
self._state when it sees the sentinel.
"""


# ---------------------------------------------------------------
# Common base — state model + per-subscriber-queue fan-out
# ---------------------------------------------------------------


class _BaseEventStream:
    """Shared state machine + subscriber fan-out for bundled impls.

    Concrete subclasses override ``emit`` / ``close`` / ``subscribe``
    / ``last_cursor`` and the private ``_on_delete`` cleanup hook.

    State transitions (streaming.md rules 1-3):

    - construction → ``ACTIVE``
    - ``close()`` from ``ACTIVE`` → ``CLOSED``; from ``CLOSED`` /
      ``GONE`` → no-op
    - registry ``delete(id)`` → invokes ``_on_delete()`` →
      ``GONE`` (immediate cutoff)
    - ``CLOSED`` → ``GONE`` auto-transition: when impl's per-event
      TTL evicts the last replayable event AND ``total_emit_count >
      0`` AND ``last_cursor()`` is NOT the operation that observed
      the eviction (rule 25 + rule 8 exemption).
    """

    _STATE_ACTIVE = "ACTIVE"
    _STATE_CLOSED = "CLOSED"
    _STATE_GONE = "GONE"

    def __init__(self) -> None:
        self._state: str = self._STATE_ACTIVE
        self._total_emit_count: int = 0
        self._subscriber_queues: list[asyncio.Queue[Any]] = []
        self._lock = asyncio.Lock()

    async def _register_subscriber(self) -> asyncio.Queue[Any]:
        q: asyncio.Queue[Any] = asyncio.Queue()
        self._subscriber_queues.append(q)
        return q

    def _remove_subscriber(self, q: asyncio.Queue[Any]) -> None:
        # Best-effort removal; safe to call even if the queue is
        # already absent (rule 15 — one event-loop-tick cleanup).
        try:
            self._subscriber_queues.remove(q)
        except ValueError:
            pass

    async def _fanout_emit(self, payload: Any) -> None:
        """Push to every currently-attached subscriber queue."""
        for q in list(self._subscriber_queues):
            await q.put(payload)

    async def _fanout_terminate(self) -> None:
        """Push end-of-stream sentinel to every subscriber."""
        for q in list(self._subscriber_queues):
            await q.put(_GONE_SENTINEL)


# ---------------------------------------------------------------
# BroadcastEventStream — live-only, no buffer
# ---------------------------------------------------------------


class BroadcastEventStream(_BaseEventStream):
    """Multicast + no buffer + live-only.

    See ``streaming.md`` §5.1 + FR-008. Subscribers see only events
    emitted **after** they attach. Constant memory overhead — only
    the currently-attached subscriber list is retained.

    No ``cursor_fn``, no ``ttl_seconds``, no ``subscribe(after=...)``
    support (silently ignored). No CLOSED → GONE auto-transition
    (nothing evicts).
    """

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        async with self._lock:
            if self._state == self._STATE_GONE:
                raise EventStreamGoneError("stream is GONE")
            if self._state == self._STATE_CLOSED:
                raise EventStreamClosedError("stream is CLOSED")
            self._total_emit_count += 1
            await self._fanout_emit(payload)
            if close:
                self._state = self._STATE_CLOSED
                await self._fanout_terminate()

    async def close(self) -> None:
        async with self._lock:
            if self._state != self._STATE_ACTIVE:
                return  # idempotent no-op
            self._state = self._STATE_CLOSED
            await self._fanout_terminate()

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        del after  # silently ignored per rule 17 — no buffer to seek
        if self._state == self._STATE_GONE:
            raise EventStreamGoneError("stream is GONE")
        return _BroadcastIterator(self)

    async def last_cursor(self) -> Optional[int]:
        if self._state == self._STATE_GONE:
            raise EventStreamGoneError("stream is GONE")
        return None  # no cursor tracking

    async def _on_delete(self) -> None:
        async with self._lock:
            self._state = self._STATE_GONE
            await self._fanout_terminate()


class _BroadcastIterator:
    """Per-subscriber iterator for :class:`BroadcastEventStream`."""

    def __init__(self, owner: BroadcastEventStream) -> None:
        self._owner = owner
        self._queue: Optional[asyncio.Queue[Any]] = None
        self._terminated = False

    def __aiter__(self) -> "_BroadcastIterator":
        # Attach at __aiter__ so the subscriber is registered before
        # the first __anext__ returns (rule for "attach" definition,
        # FR-003 / streaming.md §4.3).
        if self._queue is None and not self._terminated:
            self._queue = asyncio.get_event_loop().create_task(
                self._owner._register_subscriber()
            )
        return self

    async def __anext__(self) -> Any:
        if self._terminated:
            raise StopAsyncIteration
        if self._queue is None:
            self._queue = await self._owner._register_subscriber()
        elif asyncio.isfuture(self._queue) or asyncio.iscoroutine(self._queue):
            self._queue = await self._queue  # type: ignore[misc]
        try:
            item = await self._queue.get()
            if item is _GONE_SENTINEL:
                self._terminated = True
                self._owner._remove_subscriber(self._queue)
                raise StopAsyncIteration
            return item
        except (asyncio.CancelledError, GeneratorExit):
            if self._queue is not None and not asyncio.isfuture(self._queue):
                self._owner._remove_subscriber(self._queue)
            raise

    def __del__(self) -> None:  # rule 15 — subscriber cleanup on GC
        if self._queue is not None and not asyncio.isfuture(self._queue):
            try:
                self._owner._remove_subscriber(self._queue)
            except Exception:  # pylint: disable=broad-except
                pass


# ---------------------------------------------------------------
# Replay buffer entry — used by ReplayEventStream and
# FileBackedReplayEventStream
# ---------------------------------------------------------------


class _BufferedEvent:
    """A buffered payload + its ``emit_time`` for TTL eviction."""

    __slots__ = ("payload", "emit_time")

    def __init__(self, payload: Any, emit_time: float) -> None:
        self.payload = payload
        self.emit_time = emit_time


# ---------------------------------------------------------------
# ReplayEventStream — in-memory replay buffer + per-event TTL
# ---------------------------------------------------------------


class ReplayEventStream(_BaseEventStream):
    """In-memory replay + optional cursor + optional per-event TTL.

    See ``streaming.md`` §5.2 + FR-009. Multi-subscriber. Buffers
    every emit in memory subject to per-event TTL eviction. Supports
    ``subscribe(after=...)`` iff ``cursor_fn`` is supplied.
    """

    def __init__(
        self,
        *,
        cursor_fn: Optional[Callable[[Any], int]] = None,
        ttl_seconds: Optional[float] = None,
    ) -> None:
        super().__init__()
        self._cursor_fn = cursor_fn
        self._ttl_seconds = ttl_seconds
        self._buffer: list[_BufferedEvent] = []
        self._highest_cursor: Optional[int] = None

    def _evict_expired(self, *, now: Optional[float] = None) -> None:
        """Drop expired entries from the head of the buffer.

        Per-event TTL semantics: each event expires at
        ``emit_time + ttl_seconds`` independently of close/open
        state (rules 22-24). In-flight per-subscriber queue items
        are NOT recalled (rule 24).
        """
        if self._ttl_seconds is None:
            return
        if now is None:
            now = time.time()
        cutoff = now - self._ttl_seconds
        i = 0
        while i < len(self._buffer) and self._buffer[i].emit_time < cutoff:
            i += 1
        if i > 0:
            del self._buffer[:i]

    def _maybe_auto_transition_to_gone(self) -> None:
        """Rule 25: CLOSED + last event evicted + had ≥1 emit → GONE.

        Called from operations that observe the transition
        (``subscribe`` / ``emit``). Per rule 8 + rule 25 exemption,
        ``last_cursor`` MUST NOT call this — see ``last_cursor``.
        """
        if (
            self._state == self._STATE_CLOSED
            and not self._buffer
            and self._total_emit_count > 0
        ):
            self._state = self._STATE_GONE

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        async with self._lock:
            self._evict_expired()
            self._maybe_auto_transition_to_gone()
            if self._state == self._STATE_GONE:
                raise EventStreamGoneError("stream is GONE")
            if self._state == self._STATE_CLOSED:
                raise EventStreamClosedError("stream is CLOSED")
            emit_time = time.time()
            self._buffer.append(_BufferedEvent(payload, emit_time))
            self._total_emit_count += 1
            if self._cursor_fn is not None:
                cursor = self._cursor_fn(payload)
                if self._highest_cursor is None or cursor > self._highest_cursor:
                    self._highest_cursor = cursor
            await self._fanout_emit(payload)
            if close:
                self._state = self._STATE_CLOSED
                await self._fanout_terminate()

    async def close(self) -> None:
        async with self._lock:
            if self._state != self._STATE_ACTIVE:
                return  # idempotent
            self._state = self._STATE_CLOSED
            await self._fanout_terminate()

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        # rule 17: silently ignore `after` if no cursor_fn
        if self._cursor_fn is None:
            after = None
        # Trigger eviction + GONE check before deciding whether to raise
        self._evict_expired()
        self._maybe_auto_transition_to_gone()
        if self._state == self._STATE_GONE:
            raise EventStreamGoneError("stream is GONE")
        return _ReplayIterator(self, after=after)

    async def last_cursor(self) -> Optional[int]:
        # rule 8: do NOT trigger auto-transition; only evict-and-check
        # whether the state has been changed by some prior call.
        if self._state == self._STATE_GONE:
            raise EventStreamGoneError("stream is GONE")
        return self._highest_cursor

    async def _on_delete(self) -> None:
        async with self._lock:
            self._state = self._STATE_GONE
            self._buffer.clear()
            await self._fanout_terminate()


class _ReplayIterator:
    """Per-subscriber iterator for :class:`ReplayEventStream`.

    Replays history (subject to ``after`` cursor + per-event TTL) on
    first ``__anext__``, then yields live events from a per-
    subscriber queue.
    """

    def __init__(
        self, owner: ReplayEventStream, *, after: Optional[int] = None
    ) -> None:
        self._owner = owner
        self._after = after
        self._queue: Optional[asyncio.Queue[Any]] = None
        self._history_buffer: list[Any] = []
        self._history_index = 0
        self._attached = False
        self._terminated = False

    def _attach(self) -> None:
        # Snapshot history + register live subscriber atomically
        # under the owner's lock context (we approximate by reading
        # the buffer before adding the queue — subsequent emits land
        # in our queue, NOT into our history snapshot, so we don't
        # duplicate).
        owner = self._owner
        owner._evict_expired()
        if owner._cursor_fn is not None and self._after is not None:
            for entry in owner._buffer:
                if owner._cursor_fn(entry.payload) > self._after:
                    self._history_buffer.append(entry.payload)
        else:
            self._history_buffer = [e.payload for e in owner._buffer]
        self._queue = asyncio.Queue()
        owner._subscriber_queues.append(self._queue)
        self._attached = True

    def __aiter__(self) -> "_ReplayIterator":
        if not self._attached and not self._terminated:
            self._attach()
        return self

    async def __anext__(self) -> Any:
        if not self._attached and not self._terminated:
            self._attach()
        if self._terminated:
            raise StopAsyncIteration
        # Drain history first
        if self._history_index < len(self._history_buffer):
            item = self._history_buffer[self._history_index]
            self._history_index += 1
            return item
        # If stream was already CLOSED at attach time and queue is
        # empty, terminate cleanly
        if (
            self._owner._state in (self._owner._STATE_CLOSED, self._owner._STATE_GONE)
            and self._queue is not None
            and self._queue.empty()
        ):
            self._terminated = True
            self._owner._remove_subscriber(self._queue)
            raise StopAsyncIteration
        # Live phase
        assert self._queue is not None
        try:
            item = await self._queue.get()
            if item is _GONE_SENTINEL:
                self._terminated = True
                self._owner._remove_subscriber(self._queue)
                raise StopAsyncIteration
            return item
        except (asyncio.CancelledError, GeneratorExit):
            if self._queue is not None:
                self._owner._remove_subscriber(self._queue)
            raise

    def __del__(self) -> None:
        if self._queue is not None:
            try:
                self._owner._remove_subscriber(self._queue)
            except Exception:  # pylint: disable=broad-except
                pass


# ---------------------------------------------------------------
# FileBackedReplayEventStream — durable, jsonl, single-writer
# ---------------------------------------------------------------


_TERMINAL_MARKER = "__terminal__"
"""Field name signalling a terminal-record on disk (rule 27)."""

_COMPACTION_INTERVAL = 1000
"""Compact on-disk file after this many evictions (rule 30). Chosen
default; documented in Phase 1 PR per T028."""


class FileBackedReplayEventStream(_BaseEventStream):
    """File-backed multicast + replay + cursor + per-event TTL.

    See ``streaming.md`` §5.3 + FR-010 + rules 26-32. Persists every
    emit to ``path`` before fan-out (persist-before-publish).
    Rehydrates from disk on construction. Single-writer-per-path
    enforced via ``fcntl.flock``.
    """

    def __init__(
        self,
        *,
        path: Path,
        cursor_fn: Optional[Callable[[Any], int]] = None,
        ttl_seconds: Optional[float] = None,
        serializer: Optional[Callable[[Any], bytes]] = None,
        deserializer: Optional[Callable[[bytes], Any]] = None,
    ) -> None:
        super().__init__()
        self._path = Path(path)
        self._cursor_fn = cursor_fn
        self._ttl_seconds = ttl_seconds
        self._serializer = serializer
        self._deserializer = deserializer
        self._buffer: list[_BufferedEvent] = []
        self._highest_cursor: Optional[int] = None
        self._evictions_since_compaction = 0

        # Acquire single-writer lock + open file for append (rule 32).
        self._path.parent.mkdir(parents=True, exist_ok=True)
        # Open in append+read mode; fcntl.flock on POSIX, lock-file fallback elsewhere.
        self._file = open(self._path, "a+b")  # pylint: disable=consider-using-with
        if _HAS_FCNTL:
            try:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                self._file.close()
                raise RuntimeError(
                    f"FileBackedReplayEventStream: another process holds the "
                    f"lock on {self._path}"
                ) from exc
        else:
            # Windows fallback: best-effort lock-file approach.
            lock_path = self._path.with_suffix(self._path.suffix + ".lock")
            try:
                self._lock_fd = os.open(
                    lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR
                )
                self._lock_path = lock_path
            except FileExistsError as exc:
                self._file.close()
                raise RuntimeError(
                    f"FileBackedReplayEventStream: another process holds the "
                    f"lock-file on {self._path}"
                ) from exc

        # Rehydrate from disk if file already had content (rule 28).
        self._rehydrate()

    def _serialize(self, payload: Any, emit_time: float) -> bytes:
        if self._serializer is not None:
            inner = self._serializer(payload)
            wrapper = {"emit_time": emit_time, "payload": inner.decode("utf-8") if isinstance(inner, bytes) else inner}
        else:
            wrapper = {"emit_time": emit_time, "payload": payload}
        return (json.dumps(wrapper) + "\n").encode("utf-8")

    def _serialize_terminal(self, emit_time: float) -> bytes:
        return (json.dumps({"emit_time": emit_time, _TERMINAL_MARKER: True}) + "\n").encode("utf-8")

    def _deserialize_record(self, line: bytes) -> dict:
        record = json.loads(line.decode("utf-8"))
        if self._deserializer is not None and "payload" in record:
            record["payload"] = self._deserializer(
                record["payload"].encode("utf-8") if isinstance(record["payload"], str)
                else json.dumps(record["payload"]).encode("utf-8")
            )
        return record

    def _rehydrate(self) -> None:
        self._file.seek(0)
        data = self._file.read()
        if not data:
            return
        lines = data.split(b"\n")
        # Trailing partial: silent discard (rule 29).
        if lines and lines[-1] != b"":
            # Last line lacks \n — partial. Drop it.
            lines = lines[:-1]
            # Truncate the file to remove the partial trailing.
            self._file.seek(0, os.SEEK_END)
            self._file.truncate(self._file.tell() - len(data) + sum(len(l) + 1 for l in lines))
        else:
            lines = [l for l in lines if l]
        had_terminal = False
        terminal_seen_at: Optional[int] = None
        records: list[dict] = []
        for idx, line in enumerate(lines):
            try:
                rec = self._deserialize_record(line)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                # Mid-file malformed — RuntimeError at construction (rule 29).
                self._cleanup_locks()
                raise RuntimeError(
                    f"FileBackedReplayEventStream: malformed record at "
                    f"line {idx} of {self._path}"
                ) from exc
            if "emit_time" not in rec:
                self._cleanup_locks()
                raise RuntimeError(
                    f"FileBackedReplayEventStream: record at line {idx} of "
                    f"{self._path} missing 'emit_time' field"
                )
            if rec.get(_TERMINAL_MARKER):
                if had_terminal:
                    # Multiple terminals or terminal-not-at-EOF — malformed.
                    self._cleanup_locks()
                    raise RuntimeError(
                        f"FileBackedReplayEventStream: terminal marker not "
                        f"at end-of-file in {self._path}"
                    )
                had_terminal = True
                terminal_seen_at = idx
                continue
            if had_terminal:
                # Records after terminal marker — malformed.
                self._cleanup_locks()
                raise RuntimeError(
                    f"FileBackedReplayEventStream: record at line {idx} of "
                    f"{self._path} follows terminal marker"
                )
            records.append(rec)
        # Load into buffer, applying per-event TTL.
        for rec in records:
            entry = _BufferedEvent(rec["payload"], rec["emit_time"])
            self._buffer.append(entry)
            self._total_emit_count += 1
            if self._cursor_fn is not None:
                cursor = self._cursor_fn(entry.payload)
                if self._highest_cursor is None or cursor > self._highest_cursor:
                    self._highest_cursor = cursor
        # Apply TTL eviction now (records may have expired since being written).
        self._evict_expired()
        if had_terminal:
            self._state = self._STATE_CLOSED
            # GONE-on-construction (rule 28): if terminal + buffer empty after
            # eviction + had ≥1 emit, the rehydrated stream is in GONE.
            if not self._buffer and self._total_emit_count > 0:
                self._state = self._STATE_GONE
        # Position file at end for subsequent appends.
        self._file.seek(0, os.SEEK_END)

    def _cleanup_locks(self) -> None:
        try:
            if _HAS_FCNTL:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
            else:
                os.close(self._lock_fd)
                self._lock_path.unlink(missing_ok=True)
        except Exception:  # pylint: disable=broad-except
            pass
        try:
            self._file.close()
        except Exception:  # pylint: disable=broad-except
            pass

    def _evict_expired(self) -> None:
        if self._ttl_seconds is None:
            return
        now = time.time()
        cutoff = now - self._ttl_seconds
        i = 0
        while i < len(self._buffer) and self._buffer[i].emit_time < cutoff:
            i += 1
        if i > 0:
            del self._buffer[:i]
            self._evictions_since_compaction += i
            if self._evictions_since_compaction >= _COMPACTION_INTERVAL:
                self._compact_on_disk()
                self._evictions_since_compaction = 0

    def _compact_on_disk(self) -> None:
        """Rewrite the on-disk file to contain only surviving records.

        Lazy compaction (rule 30) — keeps the file bounded across
        repeated process restarts.
        """
        tmp_path = self._path.with_suffix(self._path.suffix + ".compact")
        try:
            with open(tmp_path, "wb") as tmp:
                for entry in self._buffer:
                    tmp.write(self._serialize(entry.payload, entry.emit_time))
                if self._state == self._STATE_CLOSED:
                    tmp.write(self._serialize_terminal(time.time()))
            # Atomic replace (POSIX guarantees atomicity on same fs).
            os.replace(tmp_path, self._path)
        except Exception:  # pylint: disable=broad-except
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:  # pylint: disable=broad-except
                pass

    def _maybe_auto_transition_to_gone(self) -> None:
        if (
            self._state == self._STATE_CLOSED
            and not self._buffer
            and self._total_emit_count > 0
        ):
            self._state = self._STATE_GONE

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        async with self._lock:
            self._evict_expired()
            self._maybe_auto_transition_to_gone()
            if self._state == self._STATE_GONE:
                raise EventStreamGoneError("stream is GONE")
            if self._state == self._STATE_CLOSED:
                raise EventStreamClosedError("stream is CLOSED")
            emit_time = time.time()
            # Persist BEFORE fan-out (rule 26). For atomic emit+close
            # (rule 14), write both records in one fsync.
            record_bytes = self._serialize(payload, emit_time)
            if close:
                record_bytes += self._serialize_terminal(emit_time)
            self._file.write(record_bytes)
            self._file.flush()
            os.fsync(self._file.fileno())
            # Now update in-memory state + fan out
            self._buffer.append(_BufferedEvent(payload, emit_time))
            self._total_emit_count += 1
            if self._cursor_fn is not None:
                cursor = self._cursor_fn(payload)
                if self._highest_cursor is None or cursor > self._highest_cursor:
                    self._highest_cursor = cursor
            await self._fanout_emit(payload)
            if close:
                self._state = self._STATE_CLOSED
                await self._fanout_terminate()

    async def close(self) -> None:
        async with self._lock:
            if self._state != self._STATE_ACTIVE:
                return
            self._file.write(self._serialize_terminal(time.time()))
            self._file.flush()
            os.fsync(self._file.fileno())
            self._state = self._STATE_CLOSED
            await self._fanout_terminate()

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        if self._cursor_fn is None:
            after = None
        self._evict_expired()
        self._maybe_auto_transition_to_gone()
        if self._state == self._STATE_GONE:
            raise EventStreamGoneError("stream is GONE")
        return _ReplayIterator(self, after=after)  # same iterator shape works

    async def last_cursor(self) -> Optional[int]:
        if self._state == self._STATE_GONE:
            raise EventStreamGoneError("stream is GONE")
        return self._highest_cursor

    async def _on_delete(self) -> None:
        async with self._lock:
            self._state = self._STATE_GONE
            self._buffer.clear()
            await self._fanout_terminate()
            self._cleanup_locks()
            try:
                self._path.unlink(missing_ok=True)
            except Exception:  # pylint: disable=broad-except
                pass


__all__ = [
    "BroadcastEventStream",
    "ReplayEventStream",
    "FileBackedReplayEventStream",
]
