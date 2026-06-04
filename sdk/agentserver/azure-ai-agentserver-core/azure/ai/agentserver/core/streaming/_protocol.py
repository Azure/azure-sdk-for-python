# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""``EventStream`` Protocol and exception hierarchy.

See ``sdk/agentserver/specs/streaming.md`` §4 for the authoritative
contract. This module defines the data-flow surface only — lifecycle
(create / lookup / destroy) is the registry's responsibility
(``_registry.py``).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Optional, Protocol, runtime_checkable


class EventStreamError(Exception):
    """Base class for all ``EventStream``-raised exceptions.

    Lets callers ``except EventStreamError`` to catch any of the
    subclasses uniformly. See ``streaming.md`` §4.2 + rule 21.
    """


class EventStreamClosedError(EventStreamError):
    """Raised when ``emit()`` is called on a ``CLOSED`` stream.

    The stream still exists; the caller cannot add more events. This
    is a server-side bug (the producer kept emitting after closing)
    and should be wire-mapped to 5xx, not 4xx. See ``streaming.md``
    §4.2 + rule 4.
    """


class EventStreamGoneError(EventStreamError):
    """Raised when any operation is attempted on a ``GONE`` stream.

    ``GONE`` is reached via ``streams.delete(id)`` or via the
    auto-transition specified in ``streaming.md`` rule 25 (CLOSED →
    GONE when the last replayable event evicts on a stream that had
    ≥1 emit).

    Wire-mapped to HTTP 410 Gone (the resource existed but is
    destroyed). See ``streaming.md`` §4.2 + rules 5-7.
    """


class EventStreamNotFoundError(EventStreamError):
    """Raised when ``streams.get(id)`` is called for an id that was
    never registered (i.e. no ``get_or_create(id)`` for this id has
    ever been called).

    Distinct from :class:`EventStreamGoneError`: NotFound means the
    id was never registered; Gone means it was registered and the
    stream is now destroyed. The registry MUST retain tombstones for
    destroyed ids so this distinction holds across the destroy
    boundary (``streaming.md`` rule 36a).

    Wire-mapped to HTTP 404 Not Found. See ``streaming.md`` §4.2 +
    rule 36.
    """


@runtime_checkable
class EventStream(Protocol):
    """A multi-cast event stream.

    Four data-flow methods. Lifecycle (create / lookup / destroy) is
    the registry's job (``streams`` in ``_registry.py``); the
    Protocol intentionally does NOT include a destructive method.

    See ``streaming.md`` §4.3 for the authoritative signature and §13
    for the conformance rules every implementation MUST satisfy.

    States: ``ACTIVE`` / ``CLOSED`` / ``GONE`` (``streaming.md``
    §4.1, rules 1-3). Operations check the current state and raise
    the specific exception per rules 4-7.
    """

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        """Emit a payload to all currently-attached subscribers.

        :param payload: Opaque value. The framework never inspects,
            validates, or rewrites it.
        :param close: If ``True``, the emit and the close-of-stream
            are observably atomic (``streaming.md`` rule 14): every
            subscriber attached before this call returns sees BOTH
            the payload AND the end-of-stream signal; subscribers
            attached after see neither.

        :raises EventStreamClosedError: If the stream is ``CLOSED``.
        :raises EventStreamGoneError: If the stream is ``GONE``.
        """
        ...

    async def close(self) -> None:
        """Transition ``ACTIVE`` → ``CLOSED``. Idempotent.

        On ``CLOSED`` or ``GONE``, this is a no-op (never raises) per
        ``streaming.md`` rule 9. Subscribers attached at close time
        drain any remaining queued items, then their iterators
        terminate cleanly with ``StopAsyncIteration`` (rule 13).
        """
        ...

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        """Return an async iterator over emitted payloads.

        NOT a coroutine (``streaming.md`` rule 16): call without
        ``await`` and immediately use with ``async for`` /
        ``aiter()`` / ``anext()``.

        :param after: If supplied and the impl has a ``cursor_fn``,
            yield only payloads whose ``cursor_fn(payload) > after``.
            Impls without a ``cursor_fn`` (and :class:`BroadcastEventStream`
            always) silently ignore non-``None`` values per rule 17.

        :raises EventStreamGoneError: Raised synchronously at the
            call site (before the iterator is returned) if the
            stream is ``GONE``.
        """
        ...

    async def last_cursor(self) -> Optional[int]:
        """Return the highest cursor seen so far, or ``None``.

        Semantics per ``streaming.md`` rule 8:

        - On ``ACTIVE``: highest ``cursor_fn(payload)`` value
          persisted so far, or ``None`` if zero emits OR impl has no
          ``cursor_fn`` (e.g. :class:`BroadcastEventStream`).
        - On ``CLOSED``: the last cursor the impl ever saw, even if
          those events have since been evicted by per-event TTL.
          **Special case (rule 25 exemption)**: ``last_cursor()``
          MUST NOT itself trigger the ``CLOSED`` → ``GONE``
          auto-transition. It is a read-only watermark query and
          survives the eviction window. The transition fires only
          on the next ``subscribe()`` or ``emit()``. The recovery
          path in :class:`FileBackedReplayEventStream` rehydration
          (handler reads ``last_cursor()`` on entry to pick the next
          cursor) depends on this exemption.
        - On ``GONE`` (after the transition has fired): raises
          :class:`EventStreamGoneError` per rule 7.

        ``last_cursor()`` is the **emitter's** recovery primitive.
        It is NOT a workflow-recovery primitive — workflow
        watermarks (what work is done) belong in ``ctx.metadata``,
        batched per side-effecting operation (``streaming.md`` §8.1
        metadata-vs-cursor split antipattern note).
        """
        ...


__all__ = [
    "EventStream",
    "EventStreamError",
    "EventStreamClosedError",
    "EventStreamGoneError",
    "EventStreamNotFoundError",
]
