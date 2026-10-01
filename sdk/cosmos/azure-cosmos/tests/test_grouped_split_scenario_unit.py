# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import asyncio
import io
import json
import unittest
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

import pytest

import test_latest_session_token as sync_tests
import test_latest_session_token_async as async_tests
import test_pk_range_child_update_live_async as child_tests


class _State:
    def __init__(self):
        self.documents = {}
        self.events = []
        self.split = False
        self.scale_calls = 0
        self.deleted = False
        self.read_calls = 0
        self.fail_post_read = False
        self.closed_clients = 0
        self.headers = {"etag": "0"}

    def create_item(self, body):
        self.documents[body["id"]] = body
        self.events.append(body)
        return body

    def read_items(self, items):
        self.read_calls += 1
        if self.fail_post_read and self.read_calls == 2:
            raise ValueError("read unavailable")
        return [self.documents[item_id] for item_id, _ in items]

    def changes(self, start_time=None, continuation=None):
        start = 0 if start_time == "Beginning" else int(continuation)
        for item in self.events[start:]:
            yield item
        self.headers["etag"] = str(len(self.events))

    def scale(self, container, throughput):
        assert throughput == 11000
        self.scale_calls += 1
        self.split = True

    def ranges(self, link):
        if self.split:
            return [{"id": "1", "parents": ["0"]}, {"id": "2", "parents": ["0"]}]
        return [{"id": "0"}]


class _Container:
    id = "grouped-test"

    def __init__(self, state):
        self.state = state
        self.container_link = "dbs/test/colls/grouped-test"
        self.client_connection = SimpleNamespace(last_response_headers=state.headers)

    def create_item(self, body):
        return self.state.create_item(body)

    def read_items(self, items):
        return self.state.read_items(items)

    def query_items_change_feed(self, start_time=None, continuation=None):
        return self.state.changes(start_time, continuation)

    def feed_range_from_partition_key(self, pk):
        return {"pk": pk}

    @staticmethod
    def get_latest_session_token(pairs, target):
        return pairs[-1][1]


class _AsyncContainer(_Container):
    async def create_item(self, body):
        return self.state.create_item(body)

    async def read_items(self, items):
        return self.state.read_items(items)

    def query_items_change_feed(self, start_time=None, continuation=None):
        async def changes():
            for item in self.state.changes(start_time, continuation):
                yield item

        return changes()

    async def feed_range_from_partition_key(self, pk):
        return {"pk": pk}

    @staticmethod
    async def get_latest_session_token(pairs, target):
        return pairs[-1][1]


class _KeyContainer:
    id = "grouped-test"
    container_link = "dbs/test/colls/grouped-test"

    def __init__(self, state):
        self.client_connection = SimpleNamespace(_ReadPartitionKeyRanges=state.ranges)


class _AsyncKeyContainer(_KeyContainer):
    def __init__(self, state):
        async def read_ranges(link):
            for item in state.ranges(link):
                yield item

        self.client_connection = SimpleNamespace(_ReadPartitionKeyRanges=read_ranges)


class _KeyDatabase:
    def __init__(self, state, key_container):
        self.state = state
        self.container = key_container

    def create_container(self, container_id, partition_key, offer_throughput):
        return SimpleNamespace(id="grouped-test")

    def get_container_client(self, container_id):
        return self.container

    def delete_container(self, container_id):
        self.state.deleted = True


class _AsyncKeyDatabase(_KeyDatabase):
    async def create_container(self, container_id, partition_key, offer_throughput):
        return super().create_container(container_id, partition_key, offer_throughput)

    async def delete_container(self, container_id):
        super().delete_container(container_id)


class _Database:
    def __init__(self, container):
        self.container = container

    def get_container_client(self, container_id):
        return self.container


class _AsyncClient:
    def __init__(self, state):
        self.state = state

    async def __aenter__(self):
        return self

    async def close(self):
        self.state.closed_clients += 1


def _parse_token(token):
    return "2", SimpleNamespace(global_lsn=int(token[1:]))


def _write_session_items(container, target, previous, pairs, hpk=False):
    for _ in range(100):
        container.create_item(
            {"pk": "A1", "id": "session_{}".format(len(container.state.events))}
        )
    token = "t{}".format(len(container.state.events))
    pairs.append((target, token))
    return token, previous


def _write_physical_items(container, target, previous, pairs, hpk=False):
    token, _ = _write_session_items(container, target, previous, pairs, hpk)
    return token, {"range": "physical"}, previous


async def _write_session_items_async(container, target, previous, pairs, hpk=False):
    for _ in range(100):
        await container.create_item(
            {"pk": "A1", "id": "session_{}".format(len(container.state.events))}
        )
    token = "t{}".format(len(container.state.events))
    pairs.append((target, token))
    return token, previous


async def _write_physical_items_async(container, target, previous, pairs, hpk=False):
    token, _ = await _write_session_items_async(container, target, previous, pairs, hpk)
    return token, {"range": "physical"}, previous


@pytest.mark.cosmosEmulator
class TestGroupedSplitScenario(unittest.TestCase):
    @staticmethod
    def _stages(output):
        return [
            (record["stage"], record["outcome"])
            for record in (
                json.loads(line)
                for line in output.splitlines()
                if line.startswith('{"event": "split_test_stage"')
            )
            if record["outcome"] != "started"
        ]

    def _run_sync(self, state):
        container = _Container(state)
        key_db = _KeyDatabase(state, _KeyContainer(state))
        case = sync_tests.TestLatestSessionToken(
            "test_change_feed_session_token_and_read_items_after_split"
        )
        case.key_database = key_db
        case.database = _Database(container)
        result = unittest.TestResult()
        output = io.StringIO()
        with patch.object(
            sync_tests.TestLatestSessionToken,
            "create_items_logical_pk",
            new=staticmethod(_write_session_items),
        ), patch.object(
            sync_tests.TestLatestSessionToken,
            "create_items_physical_pk",
            new=staticmethod(_write_physical_items),
        ), patch.object(
            sync_tests.test_config.TestConfig, "trigger_split", side_effect=state.scale
        ), patch.object(
            sync_tests, "parse_session_token", side_effect=_parse_token
        ), redirect_stdout(
            output
        ):
            case.run(result)
        return result, self._stages(output.getvalue())

    def test_sync_uses_one_split_and_checks_three_behaviors(self):
        state = _State()
        result, stages = self._run_sync(state)
        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)
        self.assertEqual(state.scale_calls, 1)
        self.assertTrue(state.deleted)
        self.assertEqual(
            stages[-4:],
            [
                ("read_items_after", "passed"),
                ("change_feed_after", "passed"),
                ("logical_session_token_after", "passed"),
                ("physical_session_token_after", "passed"),
            ],
        )

    def test_sync_reports_all_independent_post_split_failures_and_cleans_up(self):
        state = _State()
        state.fail_post_read = True
        result, stages = self._run_sync(state)
        self.assertEqual(len(result.failures), 1)
        self.assertIn("read_items_after", result.failures[0][1])
        self.assertIn(("change_feed_after", "passed"), stages)
        self.assertIn(("logical_session_token_after", "passed"), stages)
        self.assertIn(("physical_session_token_after", "passed"), stages)
        self.assertTrue(state.deleted)

    def test_async_uses_one_split_and_cleans_up(self):
        state = _State()
        container = _AsyncContainer(state)
        key_db = _AsyncKeyDatabase(state, _AsyncKeyContainer(state))
        key_client, data_client = _AsyncClient(state), _AsyncClient(state)
        case = async_tests.TestLatestSessionTokenAsync(
            "test_change_feed_session_token_and_read_items_after_split_async"
        )
        result = unittest.TestResult()
        output = io.StringIO()

        async def trigger(container, throughput):
            state.scale(container, throughput)

        with patch.object(
            async_tests.test_config.TestConfig,
            "create_test_clients_async",
            return_value=(key_client, key_db, data_client, _Database(container)),
        ), patch.object(
            async_tests.TestLatestSessionTokenAsync,
            "create_items_logical_pk_async",
            new=staticmethod(_write_session_items_async),
        ), patch.object(
            async_tests.TestLatestSessionTokenAsync,
            "create_items_physical_pk_async",
            new=staticmethod(_write_physical_items_async),
        ), patch.object(
            async_tests.test_config.TestConfig,
            "trigger_split_async",
            side_effect=trigger,
        ), patch.object(
            async_tests, "parse_session_token", side_effect=_parse_token
        ), redirect_stdout(
            output
        ):
            case.run(result)

        self.assertTrue(result.wasSuccessful(), result.errors + result.failures)
        self.assertEqual(state.scale_calls, 1)
        self.assertTrue(state.deleted)
        self.assertEqual(state.closed_clients, 2)
        self.assertEqual(
            self._stages(output.getvalue())[-4:],
            [
                ("read_items_after", "passed"),
                ("change_feed_after", "passed"),
                ("logical_session_token_after", "passed"),
                ("physical_session_token_after", "passed"),
            ],
        )


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
