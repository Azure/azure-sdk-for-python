# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import asyncio
from collections import defaultdict
import pytest
from azure.eventhub.aio._buffered_producer._partition_resolver_async import PartitionResolver


class TestPartitionResolver:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("partition_cnt", [1, 2, 16, 32, 256])
    async def test_basic_round_robin(self, partition_cnt):
        partitions = [str(i) for i in range(partition_cnt)]
        pr = PartitionResolver(partitions)
        for i in range(2*partition_cnt):
            expected = str(i % partition_cnt)
            real = await pr.get_next_partition_id()
            assert expected == real

    @pytest.mark.asyncio
    @pytest.mark.parametrize("partition_cnt", [1, 2, 16, 32, 256])
    async def test_concurrent_round_robin_fairly(self, partition_cnt):
        partitions = [str(i) for i in range(partition_cnt)]
        pr = PartitionResolver(partitions)
        dic = defaultdict(int)
        lock = asyncio.Lock()

        async def gen_pid():
            pid = await pr.get_next_partition_id()
            async with lock:
                dic[pid] += 1

        futures = [asyncio.ensure_future(gen_pid()) for _ in range(5*partition_cnt)]

        for future in futures:
            await future

        assert len(dic) == partition_cnt
        for i in range(partition_cnt):
            assert dic[str(i)] == 5
