# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Run the shared async observer through the synchronous client's own pipeline."""

from __future__ import annotations

import asyncio  # pylint: disable=do-not-import-asyncio
import logging
import threading
from collections.abc import AsyncIterator
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, cast

_logger = logging.getLogger(__name__)
_EOF = object()
_SHUTDOWN_TIMEOUT = 45


class _Response:
    """Expose a synchronous HTTP response through the observer's async interface."""

    def __init__(self, response: Any, transport: _Transport) -> None:
        self.response = response
        self.transport = transport

    def __getattr__(self, name: str) -> Any:
        return getattr(self.response, name)

    async def read(self) -> bytes:
        """Read the response body without blocking the observer loop.

        :return: Buffered response bytes.
        :rtype: bytes
        """
        return await asyncio.to_thread(self.response.read)

    async def iter_bytes(self) -> AsyncIterator[bytes]:
        """Yield stream chunks using the dedicated blocking-reader executor.

        :return: The response's incremental byte chunks.
        :rtype: ~collections.abc.AsyncIterator[bytes]
        """
        iterator = self.response.iter_bytes()
        loop = asyncio.get_running_loop()
        while True:
            chunk = await loop.run_in_executor(self.transport.readers, next, iterator, _EOF)
            if chunk is _EOF:
                return
            yield cast(bytes, chunk)

    async def close(self) -> None:
        """Schedule response closure without blocking the observer loop."""
        # Closing a sync response can wait for its current socket read. Keep
        # that wait off the observer loop; client shutdown drains these workers.
        future = asyncio.get_running_loop().run_in_executor(
            None,
            self.transport.close_response,
            self.response,
        )
        future.add_done_callback(self.transport.closed_response)


class _Transport:
    """Reuse the synchronous client's pipeline from the async sampling state machine."""

    def __init__(self, client: Any) -> None:
        from ._patch import _MAX_CONCURRENT_SAMPLES

        self.client = client
        self._config = client._config
        self._completion_feeds: dict[str, Any] = {}
        self._completion_feed_enabled = client._completion_feed_enabled
        self._session_resource_ids = client._session_resource_ids
        self._observer_closed = False
        # Blocking SSE reads use a separate executor so waiting streams cannot consume
        # the workers needed for submissions and result GETs.
        self.readers = ThreadPoolExecutor(max_workers=_MAX_CONCURRENT_SAMPLES, thread_name_prefix="fts-sync-stream")
        self.responses: dict[int, Any] = {}
        self.lock = threading.Lock()

    async def send_request(self, request: Any, **kwargs: Any) -> Any:
        """Run a blocking request off-loop and adapt streaming responses.

        :param request: Request sent through the owning client's pipeline.
        :type request: ~typing.Any
        :return: The buffered response or an async streaming adapter.
        :rtype: ~typing.Any
        """
        stream = kwargs.get("stream", False)
        kwargs["connection_timeout"] = min(kwargs.get("connection_timeout", 5), 5)
        kwargs.setdefault("read_timeout", 35 if stream else 5)
        # The shared sampling state machine owns retries and error budgets.
        kwargs["retry_total"] = 0

        response = await asyncio.to_thread(self._send_sync, request, **kwargs)
        return _Response(response, self) if stream else response

    def _send_sync(self, request: Any, **kwargs: Any) -> Any:
        """Track streams so cancellation cannot hide a late response.

        :param request: Request sent through the owning client's pipeline.
        :type request: ~typing.Any
        :return: The owning pipeline's response.
        :rtype: ~typing.Any
        """
        response = self.client.send_request(request, **kwargs)
        if kwargs.get("stream", False):
            with self.lock:
                self.responses[id(response)] = response
        return response

    def close_response(self, response: Any) -> None:
        """Close and untrack a streaming response, including when closure fails.

        :param response: Tracked streaming response to close.
        :type response: ~typing.Any
        """
        try:
            response.close()
        finally:
            with self.lock:
                self.responses.pop(id(response), None)

    def close(self) -> None:
        """Stop reader workers and close any remaining tracked responses."""
        self.readers.shutdown(wait=True, cancel_futures=True)
        for response in tuple(self.responses.values()):
            try:
                self.close_response(response)
            except Exception as exc:  # pylint: disable=broad-exception-caught
                _logger.warning(
                    "[completion_feed] synchronous response close failed (%s)",
                    type(exc).__name__,
                )

    @staticmethod
    def closed_response(future: asyncio.Future) -> None:
        if not future.cancelled() and future.exception() is not None:
            _logger.warning("[completion_feed] synchronous response close failed")


class _SyncCompletionObserver:
    """One lazily created loop per sync client, not one observer per caller."""

    def __init__(self, client: Any) -> None:
        self.transport = _Transport(client)
        self.loop = asyncio.new_event_loop()
        self.tasks: set[asyncio.Task] = set()
        self.lock = threading.Lock()
        self.shutdown: Future[None] | None = None
        self.thread = threading.Thread(target=self._run, name="fts-sync-observer", daemon=True)
        self.thread.start()

    def _run(self) -> None:
        """Own and finalize the background event loop on its dedicated thread."""
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self._shutdown_loop()

    def _shutdown_loop(self) -> None:
        """Drain loop workers before releasing the transport and loop."""
        self.loop.run_until_complete(self.loop.shutdown_asyncgens())
        self.loop.run_until_complete(self.loop.shutdown_default_executor())
        self.transport.close()
        self.loop.close()

    async def _sample(self, *args: Any, **kwargs: Any) -> Any:
        """Track sampling tasks so client shutdown can cancel owned work.

        :param args: Positional arguments forwarded to convenience sampling.
        :type args: ~typing.Any
        :return: The completed sampling result.
        :rtype: ~typing.Any
        """
        from .aio._patch import sample

        task = asyncio.current_task()
        assert task is not None
        self.tasks.add(task)
        try:
            # The public entrypoint forwards required keywords in kwargs.
            return await sample(cast(Any, self.transport), *args, **kwargs)  # pylint: disable=E1125
        except asyncio.CancelledError:
            if self.transport._observer_closed:  # pylint: disable=protected-access
                raise RuntimeError("Fine-tuning session client is closed") from None
            raise
        finally:
            self.tasks.discard(task)

    def sample(self, *args: Any, **kwargs: Any) -> Any:
        """Run sampling on the observer loop until its result is available.

        :param args: Positional arguments forwarded to convenience sampling.
        :type args: ~typing.Any
        :return: The completed sampling result.
        :rtype: ~typing.Any
        """
        with self.lock:
            if self.shutdown is not None:
                raise RuntimeError("Fine-tuning session client is closed")
            future = asyncio.run_coroutine_threadsafe(self._sample(*args, **kwargs), self.loop)
        try:
            return future.result()
        except BaseException:
            future.cancel()
            raise

    async def _close(self) -> None:
        """Cancel owned sampling tasks before closing their completion feeds."""
        self.transport._observer_closed = True  # pylint: disable=protected-access
        tasks = tuple(self.tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        feeds = self.transport._completion_feeds  # pylint: disable=protected-access
        await asyncio.gather(*(feed.close() for feed in feeds.values()))

    def close(self) -> None:
        """Join shared shutdown and stop the observer thread; safe to call again."""
        with self.lock:
            if self.shutdown is None:
                self.shutdown = asyncio.run_coroutine_threadsafe(self._close(), self.loop)
        self.shutdown.result(timeout=_SHUTDOWN_TIMEOUT)
        if not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(timeout=_SHUTDOWN_TIMEOUT)
        if self.thread.is_alive():
            raise RuntimeError("Completion observer is still shutting down")
