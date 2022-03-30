# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import time
import queue
import logging
from threading import RLock, Condition, Semaphore
from concurrent.futures import ThreadPoolExecutor, Future
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
            max_message_size_on_link,
            executor: ThreadPoolExecutor,
            *,
            max_wait_time: float = 1,
            max_concurrent_sends: int = 1,
            max_buffer_length: int = 10,
            **kwargs: Any
    ):
        self._buffered_queue = queue.Queue()
        self._cur_buffered_len = 0
        self._executor: ThreadPoolExecutor = executor
        self._producer: EventHubProducer = producer
        self._lock = RLock()
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
        self._max_message_size_on_link = max_message_size_on_link
        self._send_futures = WeakSet()
        self._check_max_wait_time_future = None
        self.partition_id = partition_id

    def start(self):
        with self._lock:
            self._cur_batch = EventDataBatch(self._max_message_size_on_link)
            self._buffered_queue.put(self._cur_batch)
            self._running = True
            if self._max_wait_time:
                self._last_send_time = time.time()
                self._check_max_wait_time_future = self._executor.submit(self.check_max_wait_time_worker)

    def stop(self, flush=True, timeout=None):
        self._running = False
        if self._check_max_wait_time_future:
            try:
                self._check_max_wait_time_future.result(timeout)
            except Exception as exc:
                _LOGGER.warning(
                    "Partition {} stopped with error {!r}".format(
                        self.partition_id,
                        exc
                    )
                )
        if flush:
            self.flush(timeout=timeout, raise_error=False)
        else:
            if self._cur_buffered_len:
                _LOGGER.warning(
                    "Shutting down Partition {}."
                    " There are still {} events in the buffer which will got lost".format(
                        self.partition_id,
                        self._cur_buffered_len
                    )
                )
        self._producer.close()

    def put_events(self, events, timeout=None):
        # Put single event or EventDataBatch into the queue.
        # This method would raise OperationTimeout if the queue does not have enough space for the input and
        # flush cannot finish in timeout.
        with self._not_full:
            try:
                new_events_len = len(events)
            except TypeError:
                new_events_len = 1
            timeout_time = time.time() + timeout if timeout else None

            if self._max_buffer_len - self._cur_buffered_len < new_events_len:
                _LOGGER.info(
                    "Partition {} does not have enough room for coming {} events."
                    "Flush first.".format(
                        self.partition_id, new_events_len
                    )
                )
                # flush the buffer
                self.flush(timeout=timeout)

            if timeout_time and time.time() > timeout_time:
                raise OperationTimeoutError("Failed to enqueue events into buffer due to timeout.")

            try:
                # add single event into current batch
                self._cur_batch.add(events)
            except AttributeError:
                # if the input events is a EventDataBatch, put the whole into the buffer
                self._buffered_queue.put(events)
                # create a new batch for incoming events
                self._cur_batch = EventDataBatch(self._max_message_size_on_link)
                # put the new batch into the buffer
                self._buffered_queue.put(self._cur_batch)
            except ValueError:
                # add single event exceeds the cur batch size, create new batch
                self._cur_batch = EventDataBatch(self._max_message_size_on_link)
                self._buffered_queue.put(self._cur_batch)
                self._cur_batch.add(events)
            self._cur_buffered_len += new_events_len
            # notify the max_wait_time worker
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

    def flush(self, timeout=None, raise_error=True):
        # try flushing all the buffered batch within given time
        _LOGGER.info("Partition: {} started flushing.".format(self.partition_id))
        with self._not_empty:
            timeout_time = time.time() + timeout if timeout else None
            while not self._buffered_queue.empty():
                remaining_time = timeout_time - time.time() if timeout_time else None
                # If flush could get the semaphore, perform sending
                if ((remaining_time and remaining_time > 0) or remaining_time is None) and \
                        self._max_concurrent_sends_semaphore.acquire(timeout=remaining_time):
                    batch = self._buffered_queue.get()
                    if not batch:
                        self._max_concurrent_sends_semaphore.release()
                        continue
                    try:
                        _LOGGER.info("Partition {} is sending.".format(self.partition_id))
                        self._producer.send(
                            batch,
                            timeout=timeout_time - time.time() if timeout_time else None
                        )
                        self._on_success(batch._internal_events, self.partition_id)
                        _LOGGER.info(
                            "Partition {} sending {} events succeeded.".format(
                                self.partition_id, len(batch)
                            )
                        )
                    except Exception as exc:
                        self._on_error(batch._internal_events, exc, self.partition_id)
                        _LOGGER.info(
                            "Partition {} sending {} events failed due to exception: {!r} ".format(
                                self.partition_id, len(batch), exc
                            )
                        )
                    finally:
                        self._cur_buffered_len -= len(batch)
                        self._max_concurrent_sends_semaphore.release()
                        self._not_full.notify()
                # If flush could not get the semaphore, we log and raise error if wanted
                else:
                    _LOGGER.info(
                        "Partition {} fails to flush due to timeout.".format(
                            self.partition_id
                        )
                    )
                    if raise_error:
                        raise OperationTimeoutError("Failed to flush {!r}".format(self.partition_id))
        # after finishing flushing, reset cur batch and put it into the buffer
        self._last_send_time = time.time()
        self._cur_batch = EventDataBatch(self._max_message_size_on_link)
        self._buffered_queue.put(self._cur_batch)
        _LOGGER.info("Partition {} finished flushing.".format(self.partition_id))

    def check_max_wait_time_worker(self):
        while self._running:
            with self._not_empty:
                if not self._buffered_queue.qsize():
                    _LOGGER.info("Partition {} worker is awaiting data.".format(self.partition_id))
                    self._not_empty.wait()
                now_time = time.time()
                _LOGGER.info("Partition {} worker is checking max_wait_time.".format(self.partition_id))
                if now_time - self._last_send_time > self._max_wait_time:
                    # in the worker, not raising error for flush, users can not handle this
                    self.flush(raise_error=False)
                    self._last_send_time = now_time
            time.sleep(self._max_wait_time - (now_time - self._last_send_time))

    @property
    def buffered_event_count(self):
        return self._cur_buffered_len
