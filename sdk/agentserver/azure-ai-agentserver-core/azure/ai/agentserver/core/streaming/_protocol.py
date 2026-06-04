# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""``EventStream`` Protocol and exception hierarchy.

This module defines the data-flow surface only — lifecycle
(create / lookup / destroy) is the registry's responsibility
(``_registry.py``). See ``docs/streaming-guide.md`` for the developer
guide covering the registry API, backings, per-turn id convention,
and exception/wire mapping.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any, Optional, Protocol, runtime_checkable


class EventStreamError(Exception):
    """Base class for all ``EventStream``-raised exceptions.

    Lets callers ``except EventStreamError`` to catch any of the
    subclasses uniformly.
    """


class EventStreamClosedError(EventStreamError):
    """Raised when ``emit()`` is called on an already-closed stream.

    The stream still exists; the caller cannot add more events. This
    is a server-side bug (the producer kept emitting after closing)
    and should be wire-mapped to 5xx, not 4xx.
    """


class EventStreamGoneError(EventStreamError):
    """Raised when any operation is attempted on a destroyed stream.

    A stream becomes "gone" when it is destroyed via
    ``streams.delete(id)``, or — for the replay backings configured
    with a TTL — when the stream is closed and its replayable history
    has been fully evicted.

    Wire-mapped to HTTP 410 Gone (the resource existed but is now
    destroyed). Distinct from :class:`EventStreamNotFoundError`.
    """


class EventStreamNotFoundError(EventStreamError):
    """Raised when ``streams.get(id)`` is called for an id that was
    never registered (i.e. no ``get_or_create(id)`` for this id has
    ever been called).

    Distinct from :class:`EventStreamGoneError`: NotFound means the
    id was never registered; Gone means it was registered and the
    stream is now destroyed. The registry retains tombstones for
    destroyed ids so this distinction holds across the destroy
    boundary.

    Wire-mapped to HTTP 404 Not Found.
    """


@runtime_checkable
class EventStream(Protocol):
    """A multi-cast event stream.

    Four data-flow methods: :meth:`emit`, :meth:`close`,
    :meth:`subscribe`, :meth:`last_cursor`. Lifecycle (create /
    lookup / destroy) is the registry's job (``streams``); the
    Protocol intentionally does NOT include a destructive method.

    See ``docs/streaming-guide.md`` for the developer guide.
    """

    async def emit(self, payload: Any, *, close: bool = False) -> None:
        """Emit a payload to all currently-attached subscribers.

        :param payload: Opaque value. The framework never inspects,
            validates, or rewrites it.
        :param close: If ``True``, the emit and the close-of-stream
            are observably atomic: every subscriber attached before
            this call returns sees BOTH the payload AND the
            end-of-stream signal; subscribers attached after see
            neither.

        :raises EventStreamClosedError: If the stream has already
            been closed.
        :raises EventStreamGoneError: If the stream has been
            destroyed.
        """
        ...

    async def close(self) -> None:
        """Transition the stream from active to closed. Idempotent.

        On an already-closed or destroyed stream, this is a no-op
        (never raises). Subscribers attached at close time drain any
        remaining queued items, then their iterators terminate
        cleanly with ``StopAsyncIteration``.
        """
        ...

    def subscribe(self, *, after: Optional[int] = None) -> AsyncIterator[Any]:
        """Return an async iterator over emitted payloads.

        NOT a coroutine: call without ``await`` and immediately use
        with ``async for`` / ``aiter()`` / ``anext()``.

        :param after: If supplied and the active backing supports
            cursored replay, yield only payloads whose cursor value
            is strictly greater than ``after``. Backings without
            cursor support silently ignore non-``None`` values.

        :raises EventStreamGoneError: Raised synchronously at the
            call site (before the iterator is returned) if the
            stream has been destroyed.
        """
        ...

    async def last_cursor(self) -> Optional[int]:
        """Return the highest cursor seen so far, or ``None``.

        Semantics:

        - While the stream is active: the highest cursor value
          persisted so far, or ``None`` if zero emits OR the active
          backing has no cursor support.
        - After the stream is closed: the last cursor the backing
          ever saw, even if those events have since been evicted by
          per-event TTL. ``last_cursor()`` is a read-only watermark
          query and does not itself fire the close → destroy
          auto-transition. This is load-bearing for the file-backed
          replay rehydration path (handler reads ``last_cursor()``
          on entry to pick the next cursor).
        - After the stream is destroyed (auto-transition has fired):
          raises :class:`EventStreamGoneError`.

        ``last_cursor()`` is the **emitter's** recovery primitive.
        It is NOT a workflow-recovery primitive — workflow
        watermarks (what work is done) belong in ``ctx.metadata``,
        batched per side-effecting operation. See
        ``docs/streaming-guide.md`` for the metadata-vs-cursor
        antipattern note.
        """
        ...


__all__ = [
    "EventStream",
    "EventStreamError",
    "EventStreamClosedError",
    "EventStreamGoneError",
    "EventStreamNotFoundError",
]
