# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Seekable replay subject for in-process SSE event broadcasting."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
from typing import Any, AsyncIterator


class _ResponseEventSubject:
    """In-process hot observable with replay buffer for SSE event broadcasting.

    Equivalent to .NET's ``SeekableReplaySubject`` / ``ConcurrentReplayAsyncSubject``.
    Multiple concurrent subscribers can join at any time and receive:

    - All buffered events emitted since creation (or from a cursor).
    - Subsequent live events as they are published in real time.
    - A completion signal when the stream ends.

    This enables live SSE replay behaviour for
    ``GET /responses/{id}?stream=true`` while a background+stream response is
    still in flight, matching the .NET ``SseReplayResult`` / ``IResponsesStreamProvider``
    contract.
    """

    _DONE: object = object()  # sentinel that signals stream completion

    def __init__(self) -> None:
        """Initialise the subject with an empty event buffer and no subscribers."""
        self._events: list[dict[str, Any]] = []
        self._subscribers: list[asyncio.Queue[Any]] = []
        self._done: bool = False
        self._lock: asyncio.Lock = asyncio.Lock()

    async def publish(self, event: dict[str, Any]) -> None:
        """Push a new event to all current subscribers and append it to the replay buffer.

        :param event: The normalised event dict (``{"type": str, "payload": dict}``).
        :type event: dict[str, Any]
        """
        async with self._lock:
            self._events.append(event)
            for q in self._subscribers:
                q.put_nowait(event)

    async def complete(self) -> None:
        """Signal stream completion to all current and future subscribers.

        After calling this, new :meth:`subscribe` calls will still deliver the full
        buffered event history and then exit immediately.
        """
        async with self._lock:
            self._done = True
            for q in self._subscribers:
                q.put_nowait(self._DONE)

    async def subscribe(self, cursor: int = -1) -> AsyncIterator[dict[str, Any]]:
        """Subscribe to events, yielding buffered history then live events.

        :param cursor: Sequence-number cursor.  Only events whose
            ``payload["sequence_number"]`` is strictly greater than *cursor* are
            yielded.  Pass ``-1`` (default) to receive all events.
        :type cursor: int
        :returns: An async iterator of normalised event dicts.
        :rtype: AsyncIterator[dict[str, Any]]
        """
        q: asyncio.Queue[Any] = asyncio.Queue()
        async with self._lock:
            # Replay all buffered events that are after the cursor
            for event in self._events:
                if event["payload"]["sequence_number"] > cursor:
                    q.put_nowait(event)
            if self._done:
                # Stream already completed — put sentinel so iterator exits after replay
                q.put_nowait(self._DONE)
            else:
                # Register for live events
                self._subscribers.append(q)

        try:
            while True:
                item = await q.get()
                if item is self._DONE:
                    return
                yield item
        finally:
            # Clean up subscription on client disconnect or normal completion
            async with self._lock:
                try:
                    self._subscribers.remove(q)
                except ValueError:
                    pass  # already removed (e.g. complete() ran concurrently)
