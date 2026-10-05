# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import io
import json
import unittest
from collections import deque
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

import test_pk_range_child_update_live_async as child_tests
from azure.cosmos.exceptions import CosmosHttpResponseError
from azure.cosmos.http_constants import HttpHeaders


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

    async def test_query_observer_preserves_response_and_bounds_redacted_history(self):
        response = (
            {"Documents": [{"id": "item-000"}]},
            {HttpHeaders.Continuation: "response-token", HttpHeaders.ActivityId: "activity"},
        )
        original_post = AsyncMock(return_value=response)
        requests = deque(maxlen=50)
        observe_post = child_tests._observe_query_post(original_post, requests)
        headers = {
            HttpHeaders.IsQuery: "true",
            HttpHeaders.PartitionKeyRangeID: "0",
            HttpHeaders.Continuation: "request-token",
        }
        body = {"query": "SELECT * FROM c"}
        result = await observe_post("/dbs/db/colls/c/docs", None, body, headers, timeout=30)
        self.assertIs(result, response)
        original_post.assert_awaited_once_with("/dbs/db/colls/c/docs", None, body, headers, timeout=30)
        self.assertEqual(requests[0]["ids"], ["item-000"])
        self.assertEqual(requests[0]["range_id"], "0")
        self.assertEqual(requests[0]["request_continuation_hash"], child_tests._continuation_hash("request-token"))
        self.assertEqual(requests[0]["response_continuation_hash"], child_tests._continuation_hash("response-token"))
        self.assertNotIn("request-token", json.dumps(list(requests)))
        self.assertNotIn("response-token", json.dumps(list(requests)))
        for _ in range(54):
            await observe_post("/dbs/db/colls/c/docs", None, body, headers)
        self.assertEqual(len(requests), 50)
        self.assertEqual(requests[0]["request"], 6)
        self.assertEqual(requests[-1]["request"], 55)

    async def test_query_observer_preserves_split_error_and_cancellation(self):
        error = CosmosHttpResponseError(
            message="split",
            response=SimpleNamespace(
                status_code=410,
                reason="Gone",
                headers={HttpHeaders.SubStatus: "1002", HttpHeaders.ActivityId: "split-activity"},
            ),
        )
        for failure in (error, asyncio.CancelledError()):
            requests = deque(maxlen=50)
            original_post = AsyncMock(side_effect=failure)
            observe_post = child_tests._observe_query_post(original_post, requests)
            with self.assertRaises(type(failure)) as caught:
                await observe_post(
                    "/dbs/db/colls/c/docs", None, {}, {HttpHeaders.IsQuery: "true"}
                )
            self.assertIs(caught.exception, failure)
            self.assertEqual(requests[0]["outcome"], "error")
            self.assertEqual(requests[0]["error_type"], type(failure).__name__)
            self.assertIn("elapsed_seconds", requests[0])
            if failure is error:
                self.assertEqual(requests[0]["status_code"], 410)
                self.assertEqual(requests[0]["sub_status"], 1002)
                self.assertEqual(requests[0]["activity_id"], "split-activity")
        self.assertEqual(child_tests._error_fields(error)["sub_status"], 1002)

    async def test_scan_mismatch_keeps_assertion_and_records_page_ids(self):
        case = self._case()
        case.expected_ids = ["item-000", "item-001"]
        response = (
            {"Documents": [{"id": "item-000"}, {"id": "item-000"}, {"id": "item-001"}]},
            {},
        )
        original_post = AsyncMock(return_value=response)
        connection = SimpleNamespace(_CosmosClientConnection__Post=original_post)
        case.client = SimpleNamespace(client_connection=connection)

        async def query_items(**kwargs):
            result, _ = await connection._CosmosClientConnection__Post(
                "/dbs/db/colls/c/docs", None, {}, {HttpHeaders.IsQuery: "true"}
            )
            for item in result["Documents"]:
                yield item

        case.container = SimpleNamespace(query_items=query_items)
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(AssertionError):
            await case._scan()
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(records[0]["event"], "scan_mismatch")
        self.assertEqual(records[0]["duplicate_ids"], {"item-000": 2})
        self.assertEqual(records[0]["requests"][0]["ids"], ["item-000", "item-000", "item-001"])
        self.assertEqual(case.scans, 0)
        self.assertIs(connection._CosmosClientConnection__Post, original_post)
