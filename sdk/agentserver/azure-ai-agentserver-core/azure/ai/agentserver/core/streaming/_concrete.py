# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""SDK-bundled :class:`~._protocol.EventStream` implementations.

This module is SDK-private (underscore-prefixed). External callers
obtain instances exclusively via the ``streams`` registry's three
``use_*`` configurators. This private import path is reserved for
SDK-internal tests (impl-specific assertions like file lock
detection, corruption recovery, per-event TTL eviction observability,
and broadcast no-buffer semantics). Consumer packages MUST NOT use
this private path.
"""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import hashlib
import json
import logging
import os
import re
import time
from collections.abc import AsyncIterator, Callable
from pathlib import Path
from typing import Any, Optional

from ._protocol import (
    EventStreamClosedError,
    EventStreamNotFoundError,
)

logger = logging.getLogger("azure.ai.agentserver.streaming")

# Try POSIX fcntl; fall back to a lock-file scheme on platforms
# without it (Windows). Per streaming.md rule 32.
try:
    import fcntl  # type: ignore[import-not-found]

    _HAS_FCNTL = True
except ImportError:  # pragma: no cover - windows
    fcntl = None  # type: ignore[assignment]
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

         state model (post  /): per-instance
        states are exactly ``ACTIVE`` and ``CLOSED``. The ``GONE`` value
        is retained as an internal flag the registry sets when it
        tombstones the id — operations on a stale instance reference
        after registry tombstone raise :class:`EventStreamNotFoundError`
    . Per-instance: ``construction → ACTIVE``,
        ``close() from ACTIVE → CLOSED``, ``close()`` from ``CLOSED`` /
        tombstoned → no-op (idempotent).

         close-clock TTL tombstone: replay backings
        with ``ttl_seconds`` configured record ``_close_time`` when
        transitioning to ``CLOSED``. From that moment the SEMANTIC
        tombstone deadline is ``close_time + ttl_seconds`` — operations
        after the deadline raise :class:`EventStreamNotFoundError`.
        Replaces the legacy "buffer empty + had emit" rule, which was
        observer-driven and required a ``total_emit_count > 0`` carve-
        out for never-emitted closed streams.
    """

    _STATE_ACTIVE = "ACTIVE"
    _STATE_CLOSED = "CLOSED"
    # Internal-only — set by the registry when it tombstones the id.
    # External callers MUST NOT depend on this; the documented
    # contract is "operation raises EventStreamNotFoundError".
    _STATE_GONE = "GONE"

    def __init__(self) -> None:
        self._state: str = self._STATE_ACTIVE
        self._subscriber_queues: list[asyncio.Queue[Any]] = []
        self._lock = asyncio.Lock()
        #   — wall-clock time the stream transitioned
        # to CLOSED; used by replay backings to compute the close-clock
        # tombstone deadline (close_time + ttl_seconds).
        self._close_time: Optional[float] = None

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
        """Push to every currently-attached subscriber queue.

        :param payload: The payload to push to each subscriber queue.
        :type payload: Any
        """
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

    See ``streaming.md`` §5.1 +. Subscribers see only events
    emitted **after** they attach. Constant memory overhead — only
    the currently-attached subscriber list is retained.

    No ``cursor_fn``, no ``ttl_seconds``, no ``subscribe(after=...)``
    support (silently ignored). No CLOSED → GONE auto-transition
    (nothing evicts).
    """

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        async with self._lock:
            if self._state == self._STATE_GONE:
                raise EventStreamNotFoundError("stream id is tombstoned")
            if self._state == self._STATE_CLOSED:
                raise EventStreamClosedError("stream is CLOSED")
            await self._fanout_emit(payload)
            if close:
                self._state = self._STATE_CLOSED
                self._close_time = time.time()
                await self._fanout_terminate()

    async def close(self) -> None:
        async with self._lock:
            if self._state != self._STATE_ACTIVE:
                return  # idempotent no-op
            self._state = self._STATE_CLOSED
            self._close_time = time.time()
            await self._fanout_terminate()

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        del after  # silently ignored per rule 17 — no buffer to seek
        if self._state == self._STATE_GONE:
            raise EventStreamNotFoundError("stream id is tombstoned")
        return _BroadcastIterator(self, terminated=self._state == self._STATE_CLOSED)

    async def last_cursor(self) -> Optional[int]:
        if self._state == self._STATE_GONE:
            raise EventStreamNotFoundError("stream id is tombstoned")
        return None  # no cursor tracking

    async def _on_delete(self) -> None:
        async with self._lock:
            self._state = self._STATE_GONE
            await self._fanout_terminate()


class _BroadcastIterator:
    """Per-subscriber iterator for :class:`BroadcastEventStream`."""

    def __init__(self, owner: BroadcastEventStream, *, terminated: bool = False) -> None:
        self._owner = owner
        self._queue: Optional[asyncio.Queue[Any]] = None
        self._terminated = terminated

    def __aiter__(self) -> "_BroadcastIterator":
        # Attach at __aiter__ so the subscriber is registered before
        # the first __anext__ returns (rule for "attach" definition,
        #  / streaming.md §4.3). Skip if pre-terminated (stream
        # was already CLOSED at subscribe() time).
        if self._queue is None and not self._terminated:
            q: asyncio.Queue[Any] = asyncio.Queue()
            self._owner._subscriber_queues.append(q)
            self._queue = q
        return self

    async def __anext__(self) -> Any:
        if self._terminated:
            raise StopAsyncIteration
        if self._queue is None:
            self._queue = await self._owner._register_subscriber()
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

    def __del__(self) -> None:  # rule 15 — subscriber cleanup on GC
        if self._queue is not None:
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

    See ``streaming.md`` §5.2 +. Multi-subscriber. Buffers
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

        :keyword now: Override the current time (seconds); defaults to
            ``time.time()`` when not supplied.
        :paramtype now: Optional[float]
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
        """/ C-STR-TTL-2 — close-clock auto-tombstone.

        When the stream is ``CLOSED`` AND ``ttl_seconds`` is configured
        AND ``now >= close_time + ttl_seconds``, transition to GONE.
        Replaces the legacy "CLOSED + buffer empty + had emit" rule.
        Deterministic and time-driven; NOT observer-driven or
        buffer-state-driven.

        Called from operations that observe the transition
        (``subscribe`` / ``emit``). Per spec §46 / C-STR-TTL-2,
        ``last_cursor`` MUST NOT call this — see ``last_cursor``.
        """
        if (
            self._state == self._STATE_CLOSED
            and self._ttl_seconds is not None
            and self._close_time is not None
            and time.time() >= self._close_time + self._ttl_seconds
        ):
            self._state = self._STATE_GONE

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        async with self._lock:
            self._evict_expired()
            self._maybe_auto_transition_to_gone()
            if self._state == self._STATE_GONE:
                raise EventStreamNotFoundError("stream id is tombstoned")
            if self._state == self._STATE_CLOSED:
                raise EventStreamClosedError("stream is CLOSED")
            emit_time = time.time()
            self._buffer.append(_BufferedEvent(payload, emit_time))
            if self._cursor_fn is not None:
                cursor = self._cursor_fn(payload)
                if self._highest_cursor is None or cursor > self._highest_cursor:
                    self._highest_cursor = cursor
            await self._fanout_emit(payload)
            if close:
                self._state = self._STATE_CLOSED
                self._close_time = time.time()
                await self._fanout_terminate()

    async def close(self) -> None:
        async with self._lock:
            if self._state != self._STATE_ACTIVE:
                return  # idempotent
            self._state = self._STATE_CLOSED
            self._close_time = time.time()
            await self._fanout_terminate()

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        # rule 17: silently ignore `after` if no cursor_fn
        if self._cursor_fn is None:
            after = None
        # Trigger eviction + GONE check before deciding whether to raise
        self._evict_expired()
        self._maybe_auto_transition_to_gone()
        if self._state == self._STATE_GONE:
            raise EventStreamNotFoundError("stream id is tombstoned")
        return _ReplayIterator(self, after=after)

    async def last_cursor(self) -> Optional[int]:
        # rule 8: do NOT trigger auto-transition; only evict-and-check
        # whether the state has been changed by some prior call.
        if self._state == self._STATE_GONE:
            raise EventStreamNotFoundError("stream id is tombstoned")
        return self._highest_cursor

    async def _on_delete(self) -> None:
        async with self._lock:
            self._state = self._STATE_GONE
            self._buffer.clear()
            await self._fanout_terminate()


class _ReplayIterator:  # pylint: disable=protected-access
    """Per-subscriber iterator for :class:`ReplayEventStream`.

    Replays history (subject to ``after`` cursor + per-event TTL) on
    first ``__anext__``, then yields live events from a per-
    subscriber queue.
    """

    def __init__(
        self, owner: "ReplayEventStream | FileBackedReplayEventStream", *, after: Optional[int] = None
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
        # Check if owner has transitioned to GONE via registry-delete
        # (immediate cutoff)
        if self._owner._state == self._owner._STATE_GONE:
            self._terminated = True
            if self._queue is not None:
                self._owner._remove_subscriber(self._queue)
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
# FileBackedReplayEventStream — resilient, jsonl, single-writer
# ---------------------------------------------------------------


_TERMINAL_MARKER = "__terminal__"
"""Field name signalling a terminal-record on disk (rule 27)."""

_COMPACTION_INTERVAL = 1000
"""Compact on-disk file after this many evictions (rule 30). Chosen
default; documented in Phase 1 PR per T028."""

#: Spec 037 #4 — a stream id is well-formed for direct use as a filename stem
# when it contains only these characters and no ``.``/``..`` path segment. Any
# other id is deterministically hash-encoded so it cannot escape the storage
# directory or clobber a sibling stream.
_SAFE_STREAM_ID_RE = re.compile(r"^[A-Za-z0-9._-]+$")

#: The reserved shape produced by the hash-encoding branch (``h_`` + 64 lowercase
# hex). A verbatim id of this exact shape is NOT used verbatim — otherwise it
# could alias the hash-encoding of a different, unsafe id — so it is itself
# hash-encoded, keeping the verbatim and hashed namespaces disjoint.
_HASHED_STREAM_ID_RE = re.compile(r"^h_[0-9a-f]{64}$")


def _safe_stream_filename(stream_id: str) -> str:
    """Return a filesystem-safe ``<stem>.jsonl`` filename for a stream id.

    Well-formed ids (``[A-Za-z0-9._-]`` with no ``.``/``..`` path segment, and
    not already shaped like the reserved ``h_<64hex>`` hash stem) are used
    verbatim for readability and cross-language compatibility. Any id containing
    a path separator, a ``.``/``..`` segment, a NUL, any other filesystem-unsafe
    character, OR the reserved ``h_<64hex>`` shape is SHA-256 hash-encoded to an
    ``h_<hex>`` stem so it can never traverse out of the storage directory or
    collide with a sibling stream (the verbatim and hashed namespaces stay
    disjoint). Mirrors the .NET port's filename hardening.

    :param stream_id: The (possibly attacker-/user-controlled) stream id.
    :type stream_id: str
    :return: A safe ``<stem>.jsonl`` filename (no path separators).
    :rtype: str
    """
    segments = stream_id.split("/")
    is_wellformed = (
        _SAFE_STREAM_ID_RE.match(stream_id)
        and not any(seg in (".", "..") for seg in segments)
        and not _HASHED_STREAM_ID_RE.match(stream_id)
    )
    if is_wellformed:
        return f"{stream_id}.jsonl"
    digest = hashlib.sha256(stream_id.encode("utf-8")).hexdigest()
    return f"h_{digest}.jsonl"


class FileBackedReplayEventStream(_BaseEventStream):  # pylint: disable=too-many-instance-attributes
    """File-backed multicast + replay + cursor + per-event TTL.

    See ``streaming.md`` §5.3 +  + rules 26-32. Persists every
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
        if (serializer is None) != (deserializer is None):
            # C-STR-FBR-3 — a custom serializer and deserializer must be supplied
            # both-or-neither; a half-configured pair would silently default the
            # missing side to JSON and corrupt round-trips. Fail fast.
            raise ValueError(
                "FileBackedReplayEventStream: 'serializer' and 'deserializer' must be "
                "supplied both-or-neither (C-STR-FBR-3)"
            )
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
        if fcntl is not None:
            try:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                self._file.close()
                logger.warning(
                    "FileBackedReplayEventStream: lock contention on %s (another process holds it)", self._path
                )
                raise RuntimeError(
                    f"FileBackedReplayEventStream: another process holds the " f"lock on {self._path}"
                ) from exc
        else:
            # Windows fallback: best-effort lock-file approach.
            lock_path = self._path.with_suffix(self._path.suffix + ".lock")
            try:
                self._lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                self._lock_path = lock_path
            except FileExistsError as exc:
                self._file.close()
                logger.warning("FileBackedReplayEventStream: lock-file contention on %s", self._path)
                raise RuntimeError(
                    f"FileBackedReplayEventStream: another process holds the " f"lock-file on {self._path}"
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

    def _serialize_terminal(self) -> bytes:
        # Spec 037 #2 — the terminal record carries no ``emit_time`` (it was
        # never honored on rehydrate; close-time is best-effort). Matches the
        # C-STR-FBR-5 shape ``{"__terminal__": true}`` and the .NET port.
        return (json.dumps({_TERMINAL_MARKER: True}) + "\n").encode("utf-8")

    def _deserialize_record(self, line: bytes) -> dict:
        record = json.loads(line.decode("utf-8"))
        if self._deserializer is not None and "payload" in record:
            record["payload"] = self._deserializer(
                record["payload"].encode("utf-8")
                if isinstance(record["payload"], str)
                else json.dumps(record["payload"]).encode("utf-8")
            )
        return record

    def _rehydrate(self) -> None:  # pylint: disable=too-many-statements
        self._file.seek(0)
        data = self._file.read()
        if not data:
            return
        lines = data.split(b"\n")
        # Trailing partial: silent discard (rule 29).
        if lines and lines[-1] != b"":
            # Last line lacks \n — partial. Drop it.
            lines = lines[:-1]
            logger.warning(
                "FileBackedReplayEventStream: dropping partial trailing record in %s "
                "(likely a crash mid-write); replay resumes from the last complete record",
                self._path,
            )
            # Truncate the file to remove the partial trailing.
            self._file.seek(0, os.SEEK_END)
            self._file.truncate(self._file.tell() - len(data) + sum(len(l) + 1 for l in lines))
        else:
            lines = [l for l in lines if l]
        had_terminal = False
        records: list[dict] = []
        last_idx = len(lines) - 1
        for idx, line in enumerate(lines):
            try:
                rec = self._deserialize_record(line)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                # Mid-file malformed — RuntimeError at construction (rule 29).
                self._cleanup_locks()
                logger.error("FileBackedReplayEventStream: malformed record at line %d of %s", idx, self._path)
                raise RuntimeError(
                    f"FileBackedReplayEventStream: malformed record at " f"line {idx} of {self._path}"
                ) from exc
            if rec.get(_TERMINAL_MARKER):
                # C-STR-FBR-6 — only a terminal sentinel that is the FINAL record
                # closes the stream. A non-final terminal sentinel (e.g. an
                # earlier lifetime closed, then more events were appended, or a
                # duplicate marker) is IGNORED; loading continues.
                if idx == last_idx:
                    had_terminal = True
                else:
                    logger.debug(
                        "FileBackedReplayEventStream: ignoring non-final terminal marker "
                        "at line %d of %s (C-STR-FBR-6)",
                        idx,
                        self._path,
                    )
                continue
            if "emit_time" not in rec:
                self._cleanup_locks()
                logger.error(
                    "FileBackedReplayEventStream: record at line %d of %s missing 'emit_time' field", idx, self._path
                )
                raise RuntimeError(
                    f"FileBackedReplayEventStream: record at line {idx} of " f"{self._path} missing 'emit_time' field"
                )
            records.append(rec)
        # Load into buffer, applying per-event TTL.
        for rec in records:
            entry = _BufferedEvent(rec["payload"], rec["emit_time"])
            self._buffer.append(entry)
            if self._cursor_fn is not None:
                cursor = self._cursor_fn(entry.payload)
                if self._highest_cursor is None or cursor > self._highest_cursor:
                    self._highest_cursor = cursor
        # Apply TTL eviction now (records may have expired since being written).
        self._evict_expired()
        if had_terminal:
            self._state = self._STATE_CLOSED
            # Spec 037 #2 — close-time is best-effort: the terminal record
            # carries no durable timestamp, so anchor the close-clock at the last
            # real event's emit_time (else ``now``). A process restart therefore
            # cannot meaningfully extend the tombstone deadline.
            if records:
                self._close_time = records[-1]["emit_time"]
            else:
                self._close_time = time.time()
            self._maybe_auto_transition_to_gone()
        # Position file at end for subsequent appends.
        self._file.seek(0, os.SEEK_END)
        logger.debug(
            "FileBackedReplayEventStream: rehydrated %d event(s) from %s (terminal=%s, buffered=%d)",
            len(records),
            self._path,
            had_terminal,
            len(self._buffer),
        )

    def _cleanup_locks(self) -> None:
        try:
            if fcntl is not None:
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
                    tmp.write(self._serialize_terminal())
            # Atomic replace (POSIX guarantees atomicity on same fs).
            os.replace(tmp_path, self._path)
            # ``os.replace`` swapped ``self._path`` to a brand-new inode; our
            # ``self._file`` handle still points at the old (now-unlinked)
            # inode, so every subsequent ``emit``/``close`` write would land in
            # the orphaned file and be lost on the next process lifetime (and
            # the single-writer ``flock`` would be held on the dead inode).
            # Reopen against the live path and re-acquire the lock. Open + lock
            # the new handle BEFORE closing the old one so the single-writer
            # guarantee is never released across the swap.
            old_file = self._file
            new_file = open(self._path, "a+b")  # pylint: disable=consider-using-with
            if fcntl is not None:
                fcntl.flock(new_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            new_file.seek(0, os.SEEK_END)
            self._file = new_file
            try:
                old_file.close()
            except Exception:  # pylint: disable=broad-except
                pass
        except Exception:  # pylint: disable=broad-except
            try:
                tmp_path.unlink(missing_ok=True)
            except Exception:  # pylint: disable=broad-except
                pass

    def _maybe_auto_transition_to_gone(self) -> None:
        """— close-clock auto-tombstone.

        Same rule as ReplayEventStream: CLOSED + ttl_seconds
        configured + ``now >= close_time + ttl_seconds`` → GONE.
        Replaces the legacy "CLOSED + buffer empty + had emit" rule.
        """
        if (
            self._state == self._STATE_CLOSED
            and self._ttl_seconds is not None
            and self._close_time is not None
            and time.time() >= self._close_time + self._ttl_seconds
        ):
            self._state = self._STATE_GONE

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        async with self._lock:
            self._evict_expired()
            self._maybe_auto_transition_to_gone()
            if self._state == self._STATE_GONE:
                raise EventStreamNotFoundError("stream id is tombstoned")
            if self._state == self._STATE_CLOSED:
                raise EventStreamClosedError("stream is CLOSED")
            emit_time = time.time()
            # Persist BEFORE fan-out (rule 26). For atomic emit+close
            # (rule 14), write both records in one fsync.
            record_bytes = self._serialize(payload, emit_time)
            if close:
                record_bytes += self._serialize_terminal()
            self._file.write(record_bytes)
            self._file.flush()
            os.fsync(self._file.fileno())
            # Now update in-memory state + fan out
            self._buffer.append(_BufferedEvent(payload, emit_time))
            if self._cursor_fn is not None:
                cursor = self._cursor_fn(payload)
                if self._highest_cursor is None or cursor > self._highest_cursor:
                    self._highest_cursor = cursor
            await self._fanout_emit(payload)
            if close:
                self._state = self._STATE_CLOSED
                self._close_time = time.time()
                await self._fanout_terminate()

    async def close(self) -> None:
        async with self._lock:
            if self._state != self._STATE_ACTIVE:
                return
            self._file.write(self._serialize_terminal())
            self._file.flush()
            os.fsync(self._file.fileno())
            self._state = self._STATE_CLOSED
            self._close_time = time.time()
            await self._fanout_terminate()

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        if self._cursor_fn is None:
            after = None
        self._evict_expired()
        self._maybe_auto_transition_to_gone()
        if self._state == self._STATE_GONE:
            raise EventStreamNotFoundError("stream id is tombstoned")
        return _ReplayIterator(self, after=after)  # same iterator shape works

    async def last_cursor(self) -> Optional[int]:
        if self._state == self._STATE_GONE:
            raise EventStreamNotFoundError("stream id is tombstoned")
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
