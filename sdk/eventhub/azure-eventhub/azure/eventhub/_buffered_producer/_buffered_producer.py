# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import queue
import logging
from threading import Lock, Condition, Semaphore
from concurrent.futures import ThreadPoolExecutor, Future
from functools import partial
from weakref import WeakSet

from typing import Optional, Any, Callable, List

from .._producer import EventHubProducer
from .._common import EventData, EventDataBatch
from ..exceptions import OperationTimeoutError

_LOGGER = logging.getLogger(__name__)


class BufferedProducer:
    def __init__(
            self,
            producer: EventHubProducer,
            partition_id: str,
            on_success: Callable[[List[EventData], Optional[str]], None],
            on_error: Callable[[List[EventData], Exception, Optional[str]], None],
            *,
            executor: Optional[ThreadPoolExecutor] = None,
            max_workers: Optional[int] = None,
            max_wait_time: float = 1,
            max_concurrent_sends: int = 1,
            max_buffer_length: int = 1500,
            **kwargs: Any
    ):
        self._buffered_queue = queue.Queue()
        self._cur_buffered_len = 0
        self._executor: ThreadPoolExecutor = executor or ThreadPoolExecutor(max_workers=max_workers)
        self._producer: EventHubProducer = producer
        self._lock = Lock()
        self._not_empty = Condition(self._lock)
        self._not_full = Condition(self._lock)
        self._max_buffer_len = max_buffer_length
        self._max_concurrent_sends = max_concurrent_sends
        self._max_concurrent_sends_semaphore = Semaphore(self._max_concurrent_sends)
        self._max_wait_time = max_wait_time
        self._on_success = self.enhanced_callback_decorator(on_success)
        self._on_error = self.enhanced_callback_decorator(on_error)
        self._last_send_time = None
        self._running = False
        self._cur_batch: Optional[EventDataBatch] = None
        self._send_futures = WeakSet()
        self._check_max_wait_time_future = None
        self.partition_id = partition_id

    def start(self):
        with self._lock:
            if self._max_wait_time:
                self._last_send_time = time.time()
                self._check_max_wait_time_future = self._executor.submit(self.check_max_wait_time_worker)

    def stop(self, flush=True, timeout=None):
        self._running = False
        if self._check_max_wait_time_future:
            try:
                self._check_max_wait_time_future.result()
        if flush:
            self.flush(timeout=timeout)
        else:
            if self._cur_buffered_len:
                logging.warning("no flush, there are still events in the batch which will got lost")

    def put_events(self, events, timeout=None):
        with self._not_full:
            try:
                new_events_len = len(events)
            except TypeError:
                new_events_len = 1
            timeout_time = time.time() + timeout if timeout else None
            while self._max_buffer_len - self._cur_buffered_len < new_events_len:
                if not self._not_full.wait((timeout_time - time.time()) if timeout_time else None):
                    raise OperationTimeoutError("Failed to enqueue buffer")
            try:
                self._cur_batch.add(events)
            except AttributeError:
                self._buffered_queue.put(events)
                self._cur_batch = EventDataBatch()
                self._buffered_queue.put(self._cur_batch)
            except ValueError:
                self._cur_batch = EventDataBatch()
                self._buffered_queue.put(self._cur_batch)
                self._cur_batch.add(events)
            self._max_buffer_len += new_events_len
            self._not_empty.notify()

    def enhanced_callback_decorator(self, callback):
        def wrapper_callback(*args, **kwargs):
            try:
                callback(*args, **kwargs)
            except Exception as exc:
                _LOGGER.warning("callback exception", callback.__name__, exc, self.partition_id)
        return wrapper_callback

    def sent_callback(self, events, future: Future):
        try:
            future.result()
            self._on_success(events, self.partition_id)
        except Exception as exc:
            self._on_error(events, exc, self.partition_id)
        finally:
            self._cur_buffered_len -= len(events)
            self._max_concurrent_sends_semaphore.release()

    def flush(self, timeout=None):
        _LOGGER.debug("buffered producer for partition: {} starts flushing.".format(self.partition_id))
        with self._not_empty:
            timeout_time = time.time() + timeout if timeout else None
            while not self._buffered_queue.empty():
                remaining_time = timeout_time - time.time() if timeout_time else None
                if ((remaining_time and remaining_time > 0) or remaining_time is None) and\
                        self._max_concurrent_sends_semaphore.acquire(timeout=remaining_time):
                    batch = self._buffered_queue.get()
                    try:
                        _LOGGER.debug("buffered producer for partition: {} is sending.".format(self.partition_id))
                        self._producer.send(
                            batch,
                            timeout=timeout_time - time.time() if timeout_time else None
                        )
                        _LOGGER.debug(
                            "buffered producer for partition: {} sending succeeded.".format(
                                self.partition_id
                            )
                        )
                        self._on_success(batch._internal_events, self.partition_id)
                    except Exception as exc:
                        _LOGGER.debug(
                            "buffered producer for partition: {} sending failed due to exception: {!r} ".format(
                                self.partition_id, exc
                            )
                        )
                        self._on_error(batch._internal_events, exc, self.partition_id)
                else:
                    _LOGGER.info(
                        "buffered producer for partition: {} fails to flush due to time out.".format(
                            self.partition_id
                        )
                    )
                    raise OperationTimeoutError("Failed to flush {!r}".format(self.partition_id))
        _LOGGER.debug("buffered producer for partition: {} finishes flushing.".format(self.partition_id))

    def check_max_wait_time_worker(self):
        while self._running:
            with self._not_empty:
                self._not_empty.wait()
                now_time = time.time()
                if now_time - self._last_send_time > self._max_wait_time:
                    try:
                        self.flush()
                        # TODO: what if flush takes forever, shall I give take the max_wait_time as the default timeout?
                        self._last_send_time = now_time
                    except OperationTimeoutError:
                        _LOGGER.error("Flush times out")

    @property
    def buffered_event_count(self):
        return self._cur_buffered_len
