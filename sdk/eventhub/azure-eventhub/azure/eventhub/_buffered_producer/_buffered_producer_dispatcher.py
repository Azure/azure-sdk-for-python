# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, List

from ._partition_resolver import PartitionResolver
from ._buffered_producer import BufferedProducer
from ..exceptions import EventDataSendError, ConnectError


class BufferedProducerDispatcher:
    def __init__(
            self,
            partitions,
            on_success,
            on_error,
            create_producer,
            eventhub_name,
            *,
            executor: Optional[ThreadPoolExecutor] = None,
            max_worker: Optional[int] = None,
            **kwargs
    ):
        self._buffered_producers: Dict[dict, BufferedProducer] = {}
        self._partition_ids: List[str] = partitions
        self._lock = Lock()
        self._on_success = on_success
        self._on_error = on_error
        self._create_producer = create_producer
        self._eventhub_name = eventhub_name
        self._partition_resolver = PartitionResolver(self._partition_ids)
        self._executor = executor or ThreadPoolExecutor(max_worker)

    def _get_partition_id(self, partition_id, partition_key):
        if partition_id:
            if partition_id not in self._partition_ids:
                raise ConnectError(
                    "Invalid partition {} for the event hub {}".format(
                        partition_id, self._eventhub_name
                    )
                )
            return partition_id
        if partition_key is None:
            return self._partition_resolver.get_partition_id_by_partition_key(partition_key)
        return self._partition_resolver.next_partition_id

    def enqueue_events(self, events, *, partition_id=None, partition_key=None, timeout=None):
        pid = self._get_partition_id(partition_id, partition_key)
        with self._lock:
            try:
                self._buffered_producers[pid].put_events(events, timeout)
            except KeyError:
                buffered_producer = BufferedProducer(
                    self._create_producer(pid),
                    pid,
                    self._on_success,
                    self._on_error,
                    executor=self._executor
                )
                buffered_producer.start()
                self._buffered_producers[pid] = buffered_producer
                buffered_producer.put_events(events, timeout)

    def flush(self, timeout=None):
        with self._lock:
            futures = []
            for producer in self._buffered_producers.values():
                futures.append(self._executor.submit(producer.flush(timeout=timeout)))

            success_results = {}
            exc_results = {}
            for future in futures:
                try:
                    future.result()
                    success_results[producer.partition_id] = 0
                except Exception as exc:
                    exc_results[producer.partition_id] = exc

            if not exc_results:
                return

            # TODO: better error
            raise EventDataSendError(
                message="Flush partially failed",
                details=exc_results
            )

    def close(self, flush=True, timeout=None):
        pass

    def get_buffered_event_count(self, pid):
        try:
            return self._buffered_producers[pid].buffered_event_count
        except KeyError:
            return 0
