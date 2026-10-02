# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace

import pytest

import test_pk_range_child_update_live_async as child_tests


@pytest.mark.cosmosEmulator
class TestChildRangeDiagnostics(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    def _case():
        case = child_tests.TestPkRangeChildUpdateLiveAsync(
            "test_existing_child_revision_does_not_full_reload"
        )
        case.routing_map = SimpleNamespace(
            _rangeById={"0": object()},
            get_ordered_partition_key_ranges=lambda: [
                SimpleNamespace(id="0", parents=[], status="online")
            ],
        )
        case.scans = 0
        return case

    async def test_failure_preserves_original_error_and_records_phase(self):
        case = self._case()

        async def replace_throughput(throughput):
            raise ValueError("replace failed")

        case.key_container = SimpleNamespace(replace_throughput=replace_throughput)
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaisesRegex(
            ValueError, "replace failed"
        ):
            await case._split_to(20000)
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(
            [r["event"] for r in records],
            ["scale_start", "split_failed", "split_incomplete"],
        )
        self.assertEqual(records[-1]["phase"], "replace_throughput")

    async def test_timeout_records_incomplete_phase(self):
        case = self._case()

        async def replace_throughput(throughput):
            await asyncio.sleep(1)

        case.key_container = SimpleNamespace(replace_throughput=replace_throughput)
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(asyncio.TimeoutError):
            await asyncio.wait_for(case._split_to(20000), timeout=0.01)
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(records[-1]["event"], "split_incomplete")
        self.assertEqual(records[-1]["phase"], "replace_throughput")
