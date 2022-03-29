# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
from threading import Lock
from typing import Dict

from ._partition_resolver import PartitionResolver
from ._buffered_producer import BufferedProducer


class BufferedProducerDispatcher:
    def __init__(self, partition_cnt, on_success, on_error, create_producer, **kwargs):
        self._buffered_producers: Dict[dict, BufferedProducer] = {}
        self._partition_cnt = partition_cnt
        self._lock = Lock()
        self._on_success = on_success
        self._on_error = on_error
        self._create_producer = create_producer
        self._partition_resolver = PartitionResolver(self._partition_cnt)

    def _get_partition_id(self, partition_id, partition_key, events):
        # TODO: validation
        # TODO: check whether events is a EventDataBatch and contains the pkey/pid information
        if partition_id:
            return partition_id
        if partition_key is None:
            return self._partition_resolver.get_partition_id_by_partition_key(partition_key)
        return self._partition_resolver.next_partition_id

    def enqueue_events(self, events, partition_id, partition_key, timeout=None):
        pid = self._get_partition_id(partition_id, partition_key, events)
        with self._lock:
            try:
                buffered_producer = self._buffered_producers[pid]
            except KeyError:
                buffered_producer = BufferedProducer(self._create_producer(pid), pid, self._on_success, self._on_error)
                self._buffered_producers[pid] = buffered_producer
        buffered_producer.put_events(events, timeout)

    def flush(self, timeout=None):
        pass
