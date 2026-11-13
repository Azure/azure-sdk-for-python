# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Coordinate client-owned sampling observation; notifications never contain results."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import codecs
import json
import logging
import random
import re
import time
from collections import deque
from collections.abc import AsyncIterator, Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from azure.core.rest import HttpRequest

from .._operation_compat import _retry_delay

_logger = logging.getLogger(__name__)
_LIMIT = 400
_MAX_FRAME_BYTES = 65536
_STOP_TIMEOUT = 5
_MAX_CONCURRENT_FETCHES = 256
_STREAM_WAIT_SECONDS = 30
_STREAM_TIMEOUT_SECONDS = 45
_RECONNECT_INITIAL_DELAY = 1.0
_RECONNECT_MAX_DELAY = 30.0
_COMPLETION_FEED_PATH = "/fine_tuning_sessions/{resource_session_id}/retrieve_futures"


def _reconnect_delay(exc: Exception, backoff: float) -> float:
    """Honor server retry hints without shortening the jittered local delay.

    :param exc: The failed observation attempt.
    :type exc: Exception
    :param backoff: Current reconnect backoff in seconds.
    :type backoff: float
    :return: Reconnect delay including jitter and bounded server hints.
    :rtype: float
    """
    delay = backoff * random.uniform(0.8, 1.2)
    response = getattr(exc, "response", None)
    if response is not None:
        delay = max(delay, _retry_delay(response, {}, 0))
    return delay


def _cursor(value: str) -> tuple[int, int]:
    if not re.fullmatch(r"[0-9]+-[0-9]+", value):
        raise ValueError("Invalid completion cursor")
    parts = tuple(int(part) for part in value.split("-"))
    if any(part > 2**64 - 1 for part in parts):
        raise ValueError("Completion cursor exceeds uint64")
    return parts  # type: ignore[return-value]


def _decode_frame(event: str, cursor: str, data: list[str]) -> tuple[str, str, str] | None:
    if event == "end":
        return "", "", "end"
    if event != "completion":
        return None
    _cursor(cursor)
    payload = json.loads("\n".join(data))
    if (
        not isinstance(payload, dict)
        or not isinstance(payload.get("request_id"), str)
        or not payload["request_id"]
        or len(payload["request_id"]) > 1024
        or payload.get("status") not in ("completed", "failed")
    ):
        raise ValueError("Invalid completion event")
    return cursor, payload["request_id"], payload["status"]


async def _frames(response: Any) -> AsyncIterator[tuple[str, str, str]]:
    """Decode complete frames and discard an incomplete trailing frame.

    :param response: Streaming observation response.
    :type response: ~typing.Any
    :return: Decoded completion and end frames.
    :rtype: ~collections.abc.AsyncIterator[tuple[str, str, str]]
    """
    decoder = codecs.getincrementaldecoder("utf-8")()
    pending = ""
    event = cursor = ""
    data: list[str] = []
    size = 0
    async for chunk in response.iter_bytes():
        pending += decoder.decode(chunk)
        while "\n" in pending:
            line, pending = pending.split("\n", 1)
            line = line.removesuffix("\r")
            size += len(line.encode("utf-8"))
            if size > _MAX_FRAME_BYTES:
                raise ValueError("Completion frame too large")
            if line:
                key, _, value = line.partition(":")
                value = value.removeprefix(" ")
                if key == "event":
                    event = value
                elif key == "id":
                    cursor = value
                elif key == "data":
                    data.append(value)
                continue
            frame = _decode_frame(event, cursor, data)
            event = cursor = ""
            data, size = [], 0
            if frame is not None:
                yield frame
        if len(pending.encode("utf-8")) > _MAX_FRAME_BYTES:
            raise ValueError("Completion line too large")


@dataclass
class _Request:
    future: asyncio.Future
    retrieve: Callable[[], Awaitable[Any]]
    due: float
    task: asyncio.Task | None = None
    notified: bool = False


@dataclass
class _AckPosition:
    cursor: str
    request_id: str
    handled: bool
    submission_generation: int


class _CompletionFeed:  # pylint: disable=too-many-instance-attributes
    """One logical consumer, bounded by the client's full-lifecycle sample permits."""

    def __init__(self, client: Any, resource_session_id: str, headers: dict, params: dict) -> None:
        self.client, self.headers, self.params = (
            client,
            headers,
            params,
        )
        self.path = _COMPLETION_FEED_PATH.format(resource_session_id=resource_session_id)
        # read_cursor tracks accepted notifications; processed_cursor tracks the
        # contiguous prefix safe to ACK. Neither means the result has been fetched.
        self.read_cursor = self.processed_cursor = "0-0"
        self.requests: dict[str, _Request] = {}
        self.completed_samples = 0
        self.failed_samples = 0
        self.pending_samples = 0
        # Track submissions whose POST has not yet supplied a request ID.
        self.registrations: set[int] = set()
        self.submission_generation = 0
        self.closed = False
        self.changed = asyncio.Event()
        self.lifecycle = asyncio.Event()
        self.runner: asyncio.Task | None = None
        self.closing: asyncio.Task | None = None
        self.submissions: set[asyncio.Future] = set()
        self.positions: deque[_AckPosition] = deque()
        self.recent: deque[str] = deque(maxlen=_LIMIT)
        self.fetch_slots = asyncio.Semaphore(_MAX_CONCURRENT_FETCHES)

    @property
    def active(self) -> bool:
        return bool(self.requests or self.registering or self.submissions)

    @property
    def registering(self) -> int:
        return len(self.registrations)

    def begin(self) -> int:
        if self.closed:
            raise RuntimeError("Fine-tuning session client is closed")
        # Register before POST: a completion can arrive before its response.
        self.submission_generation += 1
        self.registrations.add(self.submission_generation)
        self._notify()
        if self.runner is None:
            self.runner = asyncio.create_task(self._run(), name="fts-completion-feed")
        return self.submission_generation

    def end(self, registration: int) -> None:
        self.registrations.remove(registration)
        oldest = min(self.registrations, default=self.submission_generation + 1)
        for position in self.positions:
            # Later submissions cannot own an event received before they began.
            if position.submission_generation < oldest:
                position.handled = True
        self._advance()
        self._notify()

    def _notify(self) -> None:
        self.changed.set()
        self.lifecycle.set()

    async def call(self, operation: Callable[[], Awaitable[Any]]) -> Any:
        if self.closed:
            raise RuntimeError("Fine-tuning session client is closed")
        task = asyncio.ensure_future(operation())
        self.submissions.add(task)
        try:
            return await task
        except asyncio.CancelledError:
            if self.closed:
                raise RuntimeError("Fine-tuning session client is closed") from None
            raise
        finally:
            self.submissions.discard(task)
            self._notify()

    def _advance(self) -> None:
        while self.positions and self.positions[0].handled:
            self.processed_cursor = self.positions.popleft().cursor

    def _fetch(self, request_id: str) -> None:
        request = self.requests[request_id]
        if request.task is None and not request.future.done():
            request.task = asyncio.create_task(self._retrieve(request), name="fts-completion-result")

    async def _retrieve(self, request: _Request) -> None:
        try:
            async with self.fetch_slots:
                result = await request.retrieve()
            if result is not None:
                if not request.future.done():
                    request.future.set_result(result)
            else:
                request.due = time.monotonic() + 300
        except Exception as exc:  # pylint: disable=broad-exception-caught
            if not request.future.done():
                request.future.set_exception(exc)
        finally:
            request.task = None
            self._notify()

    async def wait(self, request_id: str, retrieve: Callable[[], Awaitable[Any]], registration: int) -> Any:
        if self.closed:
            self.end(registration)
            raise RuntimeError("Fine-tuning session client is closed")
        request = _Request(asyncio.get_running_loop().create_future(), retrieve, time.monotonic() + 600)
        self.requests[request_id] = request
        for position in self.positions:
            if position.request_id == request_id:
                request.notified = True
                self._fetch(request_id)
                position.handled = True
        self._advance()
        self.end(registration)
        self._notify()
        try:
            return await request.future
        finally:
            self.requests.pop(request_id, None)
            self.recent.append(request_id)
            if request.task is not None:
                request.task.cancel()
                await asyncio.gather(request.task, return_exceptions=True)
            self._notify()

    async def _accept(self, cursor: str, request_id: str) -> None:
        if _cursor(cursor) <= _cursor(self.read_cursor):
            return
        while len(self.positions) >= _LIMIT:
            self.lifecycle.clear()
            await self.lifecycle.wait()
        handled = True
        if request_id in self.requests:
            request = self.requests[request_id]
            if not request.notified:
                request.notified = True
                self._fetch(request_id)
        elif self.registering and request_id not in self.recent:
            handled = False
        # Snapshot which submissions could own this event to bound its ACK wait.
        self.positions.append(_AckPosition(cursor, request_id, handled, self.submission_generation))
        self.read_cursor = cursor
        self._advance()

    async def _consume_events(self, response: Any) -> bool:
        if "text/event-stream" not in response.headers.get("content-type", ""):
            raise ValueError("Completion response is not an event stream")
        async for cursor, request_id, status in _frames(response):
            if status == "end":
                return True
            _logger.info(
                "[completion_feed] notification_received request_id=%s status=%s",
                request_id,
                status,
            )
            await self._accept(cursor, request_id)
        raise ConnectionError("Completion stream ended before its end marker")

    async def _round(self, wait: int) -> bool:
        from ._patch import (
            _ProxyJwtRetryState,  # Avoid the patched-client import cycle.
        )

        jwt = _ProxyJwtRetryState()
        while True:
            response = None
            try:
                request = HttpRequest(
                    "POST",
                    "{endpoint}" + self.path,
                    headers=self.headers,
                    params=self.params,
                    json={
                        "read_cursor": self.read_cursor,
                        "processed_cursor": self.processed_cursor,
                        "wait_seconds": wait,
                    },
                )
                response = await self.client.send_request(request, stream=True)
                if response.status_code >= 400:
                    await response.read()
                delay = jwt.update_and_get_delay(response, method="POST", path=self.path)
                if delay is not None:
                    await asyncio.sleep(delay)
                    continue
                response.raise_for_status()
                if wait == 0:
                    if response.status_code != 204:
                        raise ValueError("Completion ACK did not return 204")
                    return True
                return await self._consume_events(response)
            finally:
                try:
                    if response is not None:
                        await response.close()
                finally:
                    if wait:
                        _logger.info(
                            "[completion_feed] Sampling progress: %d completed, "
                            "%d failed since last update; %d pending",
                            self.completed_samples,
                            self.failed_samples,
                            self.pending_samples,
                        )
                        self.completed_samples = self.failed_samples = 0

    async def _watch(self, stopping: asyncio.Event) -> None:
        backoff = _RECONNECT_INITIAL_DELAY
        while not stopping.is_set() and self.active:
            try:
                await asyncio.wait_for(self._round(_STREAM_WAIT_SECONDS), _STREAM_TIMEOUT_SECONDS)
                backoff = _RECONNECT_INITIAL_DELAY
            except Exception as exc:  # pylint: disable=broad-exception-caught
                if stopping.is_set() or not self.active:
                    return
                delay = _reconnect_delay(exc, backoff)
                _logger.warning(
                    "[completion_feed] stream failed (%s); reconnecting in %.1fs",
                    type(exc).__name__,
                    delay,
                )
                await asyncio.sleep(delay)
                backoff = min(backoff * 2, _RECONNECT_MAX_DELAY)

    async def _schedule(self, stopping: asyncio.Event) -> None:
        # Notifications are hints, not the result store. Sparse GETs recover requests
        # whose notification was missed without restoring continuous polling.
        while not stopping.is_set():
            self.changed.clear()
            now = time.monotonic()
            due = []
            for request_id, request in self.requests.items():
                if request.task is None and not request.future.done():
                    if request.due <= now:
                        self._fetch(request_id)
                    else:
                        due.append(request.due)
            timeout = max(0, min(due) - now) if due else None
            try:
                await asyncio.wait_for(self.changed.wait(), timeout)
            except asyncio.TimeoutError:
                pass

    async def _ack(self) -> None:
        try:
            await asyncio.wait_for(self._round(0), 5)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            _logger.warning("[completion_feed] final ACK failed (%s)", type(exc).__name__)

    async def _run(self) -> None:
        stopping = asyncio.Event()
        watcher = asyncio.create_task(self._watch(stopping), name="fts-completion-watcher")
        scheduler = asyncio.create_task(self._schedule(stopping), name="fts-completion-scheduler")
        watcher.add_done_callback(lambda _: self._notify())
        try:
            while True:
                self.lifecycle.clear()
                # When idle, let the open stream reach its end marker so work that
                # arrives inside the window reuses it; only close() cuts it short.
                if self.closed or watcher.done():
                    break
                await self.lifecycle.wait()
        finally:
            # Python 3.10/3.11 wait_for can swallow cancellation after a wakeup.
            stopping.set()
            self._notify()
            watcher.cancel()
            scheduler.cancel()
            try:
                await asyncio.wait_for(
                    asyncio.gather(watcher, scheduler, return_exceptions=True),
                    _STOP_TIMEOUT,
                )
            except asyncio.TimeoutError:
                _logger.warning("[completion_feed] worker shutdown exceeded deadline")
            await self._ack()
            self.runner = None
            # New sampling work may arrive during final ACK; restart observation rather
            # than leaving that work without a watcher.
            if self.active and not self.closed:
                self.runner = asyncio.create_task(self._run(), name="fts-completion-feed")

    async def close(self) -> None:
        self.closed = True
        if self.closing is None:
            self.closing = asyncio.create_task(self._close(), name="fts-completion-shutdown")
        await asyncio.shield(self.closing)

    async def _close(self) -> None:
        tasks = []
        for task in self.submissions:
            task.cancel()
            tasks.append(task)
        for request in self.requests.values():
            if not request.future.done():
                request.future.set_exception(RuntimeError("Fine-tuning session client is closed"))
            if request.task is not None:
                request.task.cancel()
                tasks.append(request.task)
        if self.runner is not None:
            self._notify()
            tasks.append(self.runner)
        await asyncio.gather(*tasks, return_exceptions=True)
        self.runner = None
