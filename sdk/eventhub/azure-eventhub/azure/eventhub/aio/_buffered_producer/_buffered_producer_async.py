# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import asyncio
import logging
import queue
import time
from asyncio import Lock
from typing import Optional, Callable, Awaitable, TYPE_CHECKING

from .._producer_async import EventHubProducer
from ..._common import EventDataBatch
from ...exceptions import OperationTimeoutError

if TYPE_CHECKING:
    from ..._producer_client import SendEventTypes

_LOGGER = logging.getLogger(__name__)


class BufferedProducer:
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        producer: EventHubProducer,
        partition_id: str,
        on_success: Callable[["SendEventTypes", Optional[str]], Awaitable[None]],
        on_error: Callable[
            ["SendEventTypes", Optional[str], Exception], Awaitable[None]
        ],
        max_message_size_on_link: int,
        *,
        max_wait_time: float = 1,
        max_buffer_length: int
    ):
        self._buffered_queue: queue.Queue = queue.Queue()
        self._max_buffer_len = max_buffer_length
        self._cur_buffered_len = 0
        self._producer: EventHubProducer = producer
        self._lock = Lock()
        self._max_wait_time = max_wait_time
        self._on_success = self.failsafe_callback(on_success)
        self._on_error = self.failsafe_callback(on_error)
        self._last_send_time = None
        self._running = False
        self._cur_batch: Optional[EventDataBatch] = None
        self._max_message_size_on_link = max_message_size_on_link
        self._check_max_wait_time_future = None
        self.partition_id = partition_id

    async def start(self):
        async with self._lock:
            self._cur_batch = EventDataBatch(self._max_message_size_on_link)
            self._running = True
            if self._max_wait_time:
                self._last_send_time = time.time()
                self._check_max_wait_time_future = asyncio.ensure_future(
                    self.check_max_wait_time_worker()
                )

    async def stop(self, flush=True, timeout_time=None, raise_error=False):
        self._running = False
        if flush:
            async with self._lock:
                await self._flush(timeout_time=timeout_time, raise_error=raise_error)
        else:
            if self._cur_buffered_len:
                _LOGGER.warning(
                    "Shutting down Partition %r."
                    " There are still %r events in the buffer which will be lost",
                    self.partition_id,
                    self._cur_buffered_len,
                )
        if self._check_max_wait_time_future:
            try:
                await self._check_max_wait_time_future
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "Partition %r stopped with error %r", self.partition_id, exc
                )
        await self._producer.close()

    async def put_events(self, events, timeout_time=None):
        # Put single event or EventDataBatch into the queue.
        # This method would raise OperationTimeout if the queue does not have enough space for the input and
        # flush cannot finish in timeout.
        async with self._lock:
            try:
                new_events_len = len(events)
            except TypeError:
                new_events_len = 1

            if self._max_buffer_len - self._cur_buffered_len < new_events_len:
                _LOGGER.info(
                    "The buffer for partition %r is full. Attempting to flush before adding %r events.",
                    self.partition_id,
                    new_events_len,
                )
                # flush the buffer
                await self._flush(timeout_time=timeout_time)

            if timeout_time and time.time() > timeout_time:
                print("Failed to enqueue events into buffer due to timeout.")
                raise OperationTimeoutError(
                    "Failed to enqueue events into buffer due to timeout."
                )

            try:
                # add single event into current batch
                self._cur_batch.add(events)
            except AttributeError:  # if the input events is a EventDataBatch, put the whole into the buffer
                # if there are events in cur_batch, enqueue cur_batch to the buffer
                if self._cur_batch:
                    self._buffered_queue.put(self._cur_batch)
                self._buffered_queue.put(events)
                # create a new batch for incoming events
                self._cur_batch = EventDataBatch(self._max_message_size_on_link)
            except ValueError:
                # add single event exceeds the cur batch size, create new batch
                self._buffered_queue.put(self._cur_batch)
                self._cur_batch = EventDataBatch(self._max_message_size_on_link)
                self._cur_batch.add(events)
            self._cur_buffered_len += new_events_len

    def failsafe_callback(self, callback):
        async def wrapper_callback(*args, **kwargs):
            try:
                await callback(*args, **kwargs)
            except Exception as exc:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "On partition %r, callback %r encountered exception %r",
                    callback.__name__,
                    exc,
                    self.partition_id,
                )

        return wrapper_callback

    async def flush(self, timeout_time=None, raise_error=True):
        async with self._lock:
            await self._flush(timeout_time, raise_error)

    async def _flush(self, timeout_time=None, raise_error=True):
        # pylint: disable=protected-access
        # try flushing all the buffered batch within given time
        _LOGGER.info("Partition: %r started flushing.", self.partition_id)
        if self._cur_batch:  # if there is batch, enqueue it to the buffer first
            self._buffered_queue.put(self._cur_batch)
            self._cur_batch = EventDataBatch(self._max_message_size_on_link)
        while self._buffered_queue.qsize() > 0:
            remaining_time = timeout_time - time.time() if timeout_time else None
            if (remaining_time and remaining_time > 0) or remaining_time is None:
                try:
                    batch = self._buffered_queue.get(block=False)
                except queue.Empty:
                    #reset curr_buffered
                    self._cur_buffered_len = 0
                    break
                self._buffered_queue.task_done()
                try:
                    _LOGGER.info("Partition %r is sending.", self.partition_id)
                    await self._producer.send(
                        batch,
                        timeout=timeout_time - time.time() if timeout_time else None,
                    )
                    _LOGGER.info(
                        "Partition %r sending %r events succeeded.",
                        self.partition_id,
                        len(batch),
                    )
                    await self._on_success(batch._internal_events, self.partition_id)
                except Exception as exc:  # pylint: disable=broad-except
                    _LOGGER.info(
                        "Partition %r sending %r events failed due to exception: %r",
                        self.partition_id,
                        len(batch),
                        exc,
                    )
                    await self._on_error(batch._internal_events, self.partition_id, exc)
                finally:
                    self._cur_buffered_len -= len(batch)
            # If flush could not get the semaphore, we log and raise error if wanted
            else:
                _LOGGER.info(
                    "Partition %r fails to flush due to timeout.", self.partition_id
                )
                if raise_error:
                    raise OperationTimeoutError(
                        "Failed to flush {!r} within {}".format(
                            self.partition_id, timeout_time
                        )
                    )
                break
        # after finishing flushing, reset cur batch and put it into the buffer
        self._last_send_time = time.time()
        self._cur_batch = EventDataBatch(self._max_message_size_on_link)
        _LOGGER.info("Partition %r finished flushing.", self.partition_id)

    async def check_max_wait_time_worker(self):
        while self._running:
            if self._cur_buffered_len > 0:
                now_time = time.time()
                _LOGGER.info(
                    "Partition %r worker is checking max_wait_time.", self.partition_id
                )
                # flush the partition if its beyond the waiting time or the buffer is at max capacity
                if (now_time - self._last_send_time > self._max_wait_time) or (
                    self._cur_buffered_len >= self._max_buffer_len
                ):
                    # in the worker, not raising error for flush, users can not handle this
                    async with self._lock:
                        await self._flush(raise_error=False)
            await asyncio.sleep(min(self._max_wait_time, 5))

    @property
    def buffered_event_count(self):
        return self._cur_buffered_len
