# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import pytest
from threading import Lock
from azure.eventhub._buffered_producer._partition_resolver import generate_hash_code, PartitionResolver


class TestPartitionResolver:
    def test_partition_key(self):
        input = {
            "7": -15263,
            "7149583486996073602": 12977,
            "FWfAT": -22341,
            "sOdeEAsyQoEuEFPGerWO": -6503,
            "FAyAIctPeCgmiwLKbJcyswoHglHVjQdvtBowLACDNORsYvOcLddNJYDmhAVkbyLOrHTKLneMNcbgWVlasVywOByANjs": 5226,
            "1XYM6!(7(lF5wq4k4m*e$Nc!1ezLJv*1YK1Y-C^*&B$O)lq^iUkG(TNzXG;Zi#z2Og*Qq0#^*k):vXh$3,C7We7%W0meJ;b3,rQCg^J;^twXgs5E$$hWKxqp": 23950,
            "E(x;RRIaQcJs*P;D&jTPau-4K04oqr:lF6Z):ERpo&;9040qyV@G1_c9mgOs-8_8/10Fwa-7b7-yP!T-!IH&968)FWuI;(^g$2fN;)HJ^^yTn:": -29304,
            "!c*_!I@1^c": 15372,
            "p4*!jioeO/z-!-;w:dh": -3104,
            "$0cb": 26269,
            "-4189260826195535198": 453
        }

        for k, v in input.items():
            assert generate_hash_code(k) == v

    @pytest.mark.parametrize("partition_cnt", [1, 2, 16, 32, 256])
    def test_basic_round_robin(self, partition_cnt):
        partitions = [str(i) for i in range(partition_cnt)]
        pr = PartitionResolver(partitions)
        for i in range(2*partition_cnt):
            expected = str(i % partition_cnt)
            real = pr.get_next_partition_id()
            assert expected == real

    @pytest.mark.parametrize("partition_cnt", [1, 2, 16, 32, 256])
    def test_concurrent_round_robin_fairly(self, partition_cnt):
        partitions = [str(i) for i in range(partition_cnt)]
        pr = PartitionResolver(partitions)
        exc = ThreadPoolExecutor()

        dic = defaultdict(int)
        lock = Lock()

        def gen_pid():
            pid = pr.get_next_partition_id()
            with lock:
                dic[pid] += 1

        for i in range(5*partition_cnt):
            exc.submit(gen_pid)

        exc.shutdown()
        assert len(dic) == partition_cnt
        for i in range(partition_cnt):
            assert dic[str(i)] == 5
