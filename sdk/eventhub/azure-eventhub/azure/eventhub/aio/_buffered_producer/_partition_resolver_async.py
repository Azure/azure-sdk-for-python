# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
jenkins-hash lookup3 algorithm implementation
"""

from asyncio import Lock
from ..._buffered_producer._partition_resolver import (
    generate_hash_code,
)  # pylint: disable=protected-access


class PartitionResolver:
    def __init__(self, partitions):
        self._idx = -1
        self._partitions = partitions
        self._partitions_cnt = len(self._partitions)
        self._lock = Lock()

    async def get_next_partition_id(self):
        """
        round-robin partition assignment
        """
        async with self._lock:
            self._idx += 1
            self._idx %= self._partitions_cnt
            return self._partitions[self._idx]

    async def get_partition_id_by_partition_key(self, partition_key):
        hash_code = generate_hash_code(partition_key)
        return self._partitions[abs(hash_code % self._partitions_cnt)]
