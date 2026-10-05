# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.

import io
import json
import os
import subprocess
import sys
import textwrap
import time
import unittest
import uuid
from contextlib import redirect_stdout
from pathlib import Path
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
        def first_failure():
            raise ValueError("secret-token-first")

        def second_failure():
            raise RuntimeError("secret-token-second")

        output = io.StringIO()
        failures = []
        with redirect_stdout(output):
            with split_stage("read_items_after", failures) as diagnostics:
                diagnostics.update(expected_count=5, actual_count=4, session_token="secret-token")
                first_failure()
            with split_stage("change_feed_after", failures) as diagnostics:
                diagnostics.update(expected_count=3, actual_count="secret-token")
                second_failure()
            with self.assertRaisesRegex(
                AssertionError, "read_items_after.*change_feed_after"
            ) as caught:
                assert_no_stage_failures(failures)
        records = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(
            [r["outcome"] for r in records], ["started", "failed", "started", "failed"]
        )
        self.assertNotIn("secret-token", output.getvalue())
        self.assertNotIn("secret-token", json.dumps(failures))
        self.assertNotIn("secret-token", str(caught.exception))
        self.assertIsNone(caught.exception.__cause__)
        self.assertTrue(caught.exception.__suppress_context__)
        self.assertEqual(failures[0]["context"], {"expected_count": 5, "actual_count": 4})
        self.assertEqual(failures[1]["context"], {"expected_count": 3})
        for failure, function in zip(failures, ("first_failure", "second_failure")):
            self.assertEqual(failure["locations"][-1]["file"], Path(__file__).name)
            self.assertEqual(failure["locations"][-1]["function"], function)
            self.assertGreater(failure["locations"][-1]["line"], 0)
            self.assertIn(function, str(caught.exception))

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


@pytest.mark.cosmosEmulator
@pytest.mark.parametrize("showlocals", [False, True])
def test_aggregate_pytest_output_is_sanitized(tmp_path: Path, showlocals: bool):
    source = textwrap.dedent(
        """\
        import os
        from _split_test_utils import assert_no_stage_failures, split_stage

        def first_stage_failure():
            raise ValueError(os.environ["SPLIT_FIRST_SENTINEL"])

        def second_stage_failure():
            raise RuntimeError(os.environ["SPLIT_SECOND_SENTINEL"])

        def test_two_failed_stages():
            failures = []
            with split_stage("read_items_after", failures) as diagnostics:
                diagnostics.update(expected_count=5, actual_count=4)
                first_stage_failure()
            with split_stage("change_feed_after", failures) as diagnostics:
                diagnostics.update(expected_count=3, actual_count=2)
                second_stage_failure()
            assert_no_stage_failures(failures)
        """
    )
    test_file = tmp_path / "test_aggregate_failure.py"
    test_file.write_text(source, encoding="utf-8")
    first_marker = str(uuid.uuid4())
    second_marker = str(uuid.uuid4())
    environment = os.environ.copy()
    environment.update(
        SPLIT_FIRST_SENTINEL=first_marker,
        SPLIT_SECOND_SENTINEL=second_marker,
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1",
    )
    environment.pop("PYTEST_ADDOPTS", None)
    tests = Path(__file__).resolve().parent
    environment["PYTHONPATH"] = os.pathsep.join(
        (str(tests.parent), str(tests), environment.get("PYTHONPATH", ""))
    )
    command = [
        sys.executable, "-m", "pytest", "--noconftest", "--color=no", "--tb=long", "-q", str(test_file)
    ]
    if showlocals:
        command.append("--showlocals")
    result = subprocess.run(
        command,
        cwd=tmp_path,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=30,
        check=False,
    )
    assert result.returncode == 1, result.stdout
    assert first_marker not in result.stdout
    assert second_marker not in result.stdout
    assert "read_items_after (ValueError)" in result.stdout
    assert "change_feed_after (RuntimeError)" in result.stdout
    assert '"expected_count": 5' in result.stdout
    assert '"actual_count": 4' in result.stdout
    for error_type, function in (
        ("ValueError", "first_stage_failure"),
        ("RuntimeError", "second_stage_failure"),
    ):
        line = next(
            number for number, text in enumerate(source.splitlines(), 1) if f"raise {error_type}" in text
        )
        assert f"{test_file.name}:{line} ({function})" in result.stdout
