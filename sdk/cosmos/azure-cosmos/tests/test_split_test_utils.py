# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import io
import json
import time
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from azure.cosmos.http_constants import HttpHeaders

from _split_test_utils import (
    assert_no_stage_failures,
    create_item,
    snapshot_split_routing_map,
    split_stage,
    wait_for_split_ranges,
    wait_for_split_ranges_async,
)


PARENT = {"id": "0", "parents": []}
CHILDREN = [{"id": "1", "parents": ["0"]}, {"id": "2", "parents": ["0"]}]


def _container(read_ranges):
    connection = SimpleNamespace(_ReadPartitionKeyRanges=read_ranges)
    return SimpleNamespace(
        client_connection=connection, container_link="test-container"
    )


@pytest.mark.cosmosEmulator
class TestSplitTestUtils(unittest.TestCase):
    def test_creates_regular_and_hpk_items(self):
        for hpk, fields in (
            (False, {"pk": "A7"}),
            (True, {"state": "CA", "city": "LA7", "zipcode": "90001"}),
        ):
            with self.subTest(hpk=hpk), patch(
                "_split_test_utils.uuid.uuid4", return_value="fixed-id"
            ) as generate_id, patch(
                "_split_test_utils.random.randint", return_value=7
            ) as random_number:
                self.assertEqual(
                    create_item(hpk), {"id": "itemfixed-id", "name": "sample", **fields}
                )
                generate_id.assert_called_once_with()
                random_number.assert_called_once_with(1, 10)

    def test_restores_only_this_containers_name_and_rid_entries(self):
        link = "dbs/test/colls/split"
        parent_map = object()
        children_map = object()
        cache = {"container-rid": parent_map, "unrelated-rid": object()}
        container = SimpleNamespace(
            container_link=link,
            client_connection=SimpleNamespace(
                _routing_map_provider=SimpleNamespace(
                    _collection_routing_map_by_item=cache
                )
            ),
        )
        restore = snapshot_split_routing_map(container, "container-rid")
        for _ in range(2):
            cache["container-rid"] = children_map
            cache[link] = children_map
            unrelated_map = object()
            cache["unrelated-rid"] = unrelated_map
            restore()
            self.assertIs(cache["container-rid"], parent_map)
            self.assertNotIn(link, cache)
            self.assertIs(cache["unrelated-rid"], unrelated_map)

    def test_snapshot_requires_a_warmed_routing_map(self):
        container = SimpleNamespace(
            container_link="dbs/test/colls/split",
            client_connection=SimpleNamespace(
                _routing_map_provider=SimpleNamespace(
                    _collection_routing_map_by_item={}
                )
            ),
        )
        with self.assertRaisesRegex(AssertionError, "warm"):
            snapshot_split_routing_map(container, "container-rid")

    def test_waits_for_both_children(self):
        snapshots = iter(([PARENT], [CHILDREN[0]], CHILDREN))
        container = _container(lambda link: iter(next(snapshots)))
        with redirect_stdout(io.StringIO()):
            wait_for_split_ranges(container, "0", time.monotonic() + 1, poll_interval=0)

    def test_offer_completion_without_children_skips(self):
        container = _container(lambda link: iter([PARENT]))
        with redirect_stdout(io.StringIO()), self.assertRaisesRegex(
            unittest.SkipTest, "last ranges"
        ):
            wait_for_split_ranges(container, "0", time.monotonic() - 1)

    def test_collects_independent_failures_without_exposing_error_messages(self):
        output = io.StringIO()
        failures = []
        with redirect_stdout(output):
            with split_stage("read_items_after", failures):
                raise ValueError("secret-token")
            with split_stage("change_feed_after", failures):
                raise RuntimeError("secret-token")
            with self.assertRaisesRegex(
                AssertionError, "read_items_after.*change_feed_after"
            ):
                assert_no_stage_failures(failures)
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(
            [r["outcome"] for r in records], ["started", "failed", "started", "failed"]
        )
        self.assertNotIn("secret-token", output.getvalue())

    def test_precondition_failure_propagates(self):
        with redirect_stdout(io.StringIO()), self.assertRaisesRegex(
            ValueError, "precondition"
        ):
            with split_stage("change_feed_before"):
                raise ValueError("precondition")

    def test_service_error_reports_request_ids_without_message(self):
        class ServiceError(RuntimeError):
            status_code = 429
            sub_status = 1002
            headers = {HttpHeaders.ActivityId: "request-id"}

        output = io.StringIO()
        failures = []
        with redirect_stdout(output):
            with split_stage("read_items_after", failures):
                raise ServiceError("secret-token")
        record = json.loads(output.getvalue().splitlines()[-1])
        self.assertEqual(record["status_code"], 429)
        self.assertEqual(record["sub_status"], 1002)
        self.assertEqual(record["activity_id"], "request-id")
        self.assertNotIn("secret-token", output.getvalue())
        self.assertEqual(len(failures), 1)

    def test_skip_propagates_without_recording_a_failure(self):
        failures = []
        with redirect_stdout(io.StringIO()), self.assertRaises(unittest.SkipTest):
            with split_stage("split_and_convergence", failures):
                raise unittest.SkipTest("not ready")
        self.assertEqual(failures, [])


@pytest.mark.cosmosEmulator
class TestSplitTestUtilsAsync(unittest.IsolatedAsyncioTestCase):
    async def test_waits_for_both_children_async(self):
        snapshots = iter(([PARENT], [CHILDREN[0]], CHILDREN))

        async def read_ranges(link):
            for item in next(snapshots):
                yield item

        with redirect_stdout(io.StringIO()):
            await wait_for_split_ranges_async(
                _container(read_ranges), "0", time.monotonic() + 1, poll_interval=0
            )

    async def test_times_out_without_physical_split_async(self):
        async def read_ranges(link):
            yield PARENT

        with redirect_stdout(io.StringIO()), self.assertRaises(unittest.SkipTest):
            await wait_for_split_ranges_async(
                _container(read_ranges), "0", time.monotonic() - 1
            )
