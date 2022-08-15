# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from __future__ import annotations
import asyncio
import logging
from typing import Dict, List, Callable, Optional, Awaitable, TYPE_CHECKING
from asyncio import Lock

from ._partition_resolver_async import PartitionResolver
from ...aio._producer_async import EventHubProducer
from ._buffered_producer_async import BufferedProducer
from ...exceptions import EventDataSendError, ConnectError, EventHubError

if TYPE_CHECKING:
    from .._transport._base_async import AmqpTransportAsync
    from ..._producer_client import SendEventTypes

_LOGGER = logging.getLogger(__name__)


class BufferedProducerDispatcher:
    # pylint: disable=too-many-instance-attributes
    def __init__(
        self,
        partitions: List[str],
        on_success: Callable[["SendEventTypes", Optional[str]], Awaitable[None]],
        on_error: Callable[
            ["SendEventTypes", Optional[str], Exception], Awaitable[None]
        ],
        create_producer: Callable[..., EventHubProducer],
        eventhub_name: str,
        max_message_size_on_link: int,
        *,
        max_buffer_length: int = 1500,
        max_wait_time: float = 1
    ):
        self._buffered_producers: Dict[str, BufferedProducer] = {}
        self._partition_ids: List[str] = partitions
        self._lock = Lock()
        self._on_success = on_success
        self._on_error = on_error
        self._create_producer = create_producer
        self._eventhub_name = eventhub_name
        self._max_message_size_on_link = max_message_size_on_link
        self._partition_resolver = PartitionResolver(self._partition_ids)
        self._max_wait_time = max_wait_time
        self._max_buffer_length = max_buffer_length

    async def _get_partition_id(self, partition_id, partition_key):
        if partition_id:
            if partition_id not in self._partition_ids:
                raise ConnectError(
                    "Invalid partition {} for the event hub {}".format(
                        partition_id, self._eventhub_name
                    )
                )
            return partition_id
        if isinstance(partition_key, str):
            return await self._partition_resolver.get_partition_id_by_partition_key(
                partition_key
            )
        return await self._partition_resolver.get_next_partition_id()

    async def enqueue_events(
        self, events, *, partition_id=None, partition_key=None, timeout_time=None
    ):
        pid = await self._get_partition_id(partition_id, partition_key)
        async with self._lock:
            try:
                await self._buffered_producers[pid].put_events(events, timeout_time)
            except KeyError:
                buffered_producer = BufferedProducer(
                    self._create_producer(partition_id=pid),
                    pid,
                    self._on_success,
                    self._on_error,
                    self._max_message_size_on_link,
                    max_wait_time=self._max_wait_time,
                    max_buffer_length=self._max_buffer_length,
                )
                await buffered_producer.start()
                self._buffered_producers[pid] = buffered_producer
                await buffered_producer.put_events(events, timeout_time)

    async def flush(self, timeout_time=None):
        # flush all the buffered producer, the method will block until finishes or times out
        async with self._lock:
            futures = []
            for pid, producer in self._buffered_producers.items():
                # call each producer's flush method
                futures.append(
                    (
                        pid,
                        asyncio.ensure_future(
                            producer.flush(timeout_time=timeout_time)
                        ),
                    )
                )

            # gather results
            exc_results = {}
            for pid, future in futures:
                try:
                    await future
                except Exception as exc:  # pylint: disable=broad-except
                    exc_results[pid] = exc

            if not exc_results:
                _LOGGER.info("Flushing all partitions succeeded")
                return

            _LOGGER.warning(
                "Flushing all partitions partially failed with result %r.", exc_results
            )
            raise EventDataSendError(
                message="Flushing all partitions partially failed, failed partitions are {!r}"
                " Exception details are {!r}".format(exc_results.keys(), exc_results)
            )

    async def close(self, *, flush=True, timeout_time=None, raise_error=False):

        async with self._lock:

            futures = []
            # stop all buffered producers
            for pid, producer in self._buffered_producers.items():
                futures.append(
                    (
                        pid,
                        asyncio.ensure_future(
                            producer.stop(
                                flush=flush,
                                timeout_time=timeout_time,
                                raise_error=raise_error,
                            )
                        ),
                    )
                )

            exc_results = {}
            # gather results
            for pid, future in futures:
                try:
                    await future
                except Exception as exc:  # pylint: disable=broad-except
                    exc_results[pid] = exc

            if exc_results:
                _LOGGER.warning(
                    "Stopping all partitions failed with result %r.", exc_results
                )
                if raise_error:
                    raise EventHubError(
                        message="Stopping all partitions partially failed, failed partitions are {!r}"
                        " Exception details are {!r}".format(
                            exc_results.keys(), exc_results
                        )
                    )

    def get_buffered_event_count(self, pid):
        try:
            return self._buffered_producers[pid].buffered_event_count
        except KeyError:
            return 0

    @property
    def total_buffered_event_count(self):
        return sum(
            [self.get_buffered_event_count(pid) for pid in self._buffered_producers]
        )
