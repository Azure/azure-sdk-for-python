# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Offline lifecycle and ownership checks; no live service or leak verdict."""

import asyncio
import importlib
from pathlib import Path

import pytest


@pytest.fixture
def harness(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "workloads"))
    return importlib.import_module("memory_cycle_harness")


def configuration(harness, **changes):
    values = dict(
        namespace="a" * 32, partition_key="/customerId", pool_size=4, cycles=3,
        concurrency=2, idle_seconds=0.001, sample_seconds=0.1,
        max_seconds=5, max_rss_bytes=16 * 1024**3, operation_timeout=1,
    )
    return harness.CycleConfig(**{**values, **changes})


class Container:
    def __init__(self, path="/customerId", fail_create=False, stall=False):
        self.path = path
        self.rows = {"unrelated": {"id": "unrelated", "customerId": "old-js-data"}}
        self.fail_create = fail_create
        self.stall = stall
        self.created = []
        self.deleted = []
        self.active = 0
        self.peak = 0
        self.max_owned = 0

    async def read(self):
        return {"partitionKey": {"paths": [self.path]}}

    def query_items(self, _, parameters, **kwargs):
        prefix = parameters[0]["value"]

        async def rows():
            for item in list(self.rows.values()):
                if item["id"].startswith(prefix):
                    yield dict(item)
        return rows()

    async def create_item(self, item, response_hook):
        self.active += 1
        self.peak = max(self.peak, self.active)
        try:
            await asyncio.sleep(0)
            self.rows[item["id"]] = {**item, "_etag": "etag"}
            self.created.append(item["id"])
            self.max_owned = max(self.max_owned, len(self.rows) - 1)
            if self.fail_create:
                raise RuntimeError("ambiguous create failure")
            if self.stall:
                await asyncio.sleep(10)
            response_hook({"x-ms-request-charge": "5"}, item)
        finally:
            self.active -= 1

    async def delete_item(self, item, partition_key, response_hook=None, **kwargs):
        assert self.rows[item][self.path[1:]] == partition_key
        if response_hook is None:
            assert kwargs["etag"] == self.rows[item]["_etag"]
            assert "match_condition" in kwargs
        del self.rows[item]
        self.deleted.append(item)
        if response_hook:
            response_hook({"x-ms-request-charge": "7"}, None)


class Client:
    def __init__(self, container):
        self.container = container
        self.entries = 0
        self.exits = 0

    async def __aenter__(self):
        self.entries += 1
        return self

    async def __aexit__(self, *_):
        self.exits += 1

    def get_database_client(self, _):
        return self

    def get_container_client(self, _):
        return self.container


@pytest.mark.parametrize("partition", ["/id", "/customerId"])
def test_cycles_bound_items_and_keep_one_client(harness, partition):
    config = configuration(harness, partition_key=partition)
    container = Container(partition)
    client = Client(container)
    rows = []
    asyncio.run(harness.run_memory_cycles(client, "db", "container", config, rows.append))
    assert client.entries == client.exits == 1
    assert container.max_owned == config.pool_size
    assert len(set(container.created)) == config.pool_size
    assert len(container.created) == len(container.deleted) == config.pool_size * config.cycles
    assert container.peak == config.concurrency
    assert list(container.rows) == ["unrelated"]
    ends = [row for row in rows if row["record_type"] == "phase_end"]
    assert [(row["phase"], row["completed"], row["request_charge"]) for row in ends] == [
        ("create", 4, 20), ("delete", 4, 28), ("idle", 0, 0)
    ] * 3
    assert rows[-1]["memory_verdict"] == "not_evaluated"
    assert len({row["pid"] for row in rows}) == 1


@pytest.mark.parametrize("mode", ["wrong_partition", "occupied"])
def test_preflight_refuses_without_writes(harness, mode):
    config = configuration(harness)
    container = Container("/id" if mode == "wrong_partition" else "/customerId")
    if mode == "occupied":
        container.rows[config.item(0)["id"]] = config.item(0)
    client = Client(container)
    with pytest.raises(ValueError):
        asyncio.run(harness.run_memory_cycles(client, "db", "container", config, lambda _: None))
    assert not container.created and not container.deleted
    assert client.entries == client.exits == 1


@pytest.mark.parametrize("mode", ["failure", "timeout", "cancellation", "sink_failure"])
def test_failed_cycles_drain_cleanup_and_do_not_claim_success(harness, mode):
    config = configuration(harness, operation_timeout=0.02 if mode == "timeout" else 1)
    container = Container(fail_create=mode == "failure", stall=mode in ("timeout", "cancellation"))
    client = Client(container)
    rows = []

    def emit(row):
        if mode == "sink_failure" and row["record_type"] == "phase_end":
            raise OSError("disk full")
        rows.append(row)

    async def scenario():
        task = asyncio.create_task(
            harness.run_memory_cycles(client, "db", "container", config, emit)
        )
        if mode == "cancellation":
            while not container.created:
                await asyncio.sleep(0)
            task.cancel()
        expected = {
            "failure": RuntimeError, "timeout": TimeoutError,
            "cancellation": asyncio.CancelledError, "sink_failure": OSError,
        }[mode]
        with pytest.raises(expected):
            await task

    asyncio.run(scenario())
    assert container.active == 0
    assert list(container.rows) == ["unrelated"]
    assert client.entries == client.exits == 1
    assert not any(row["record_type"] == "completion" for row in rows)


def test_cleanup_rejects_changed_owned_body_before_deleting(harness):
    config = configuration(harness)
    container = Container(fail_create=True)
    client = Client(container)
    original = container.create_item

    async def corrupt(item, response_hook):
        try:
            await original(item, response_hook)
        finally:
            container.rows[item["id"]]["quantity"] = 99

    container.create_item = corrupt
    with pytest.raises(RuntimeError, match="cleanup also failed"):
        asyncio.run(harness.run_memory_cycles(client, "db", "container", config, lambda _: None))
    assert not container.deleted


def test_client_close_failure_does_not_publish_completion(harness):
    class BrokenCloseClient(Client):
        async def __aexit__(self, *_):
            self.exits += 1
            raise RuntimeError("close failed")

    client = BrokenCloseClient(Container())
    rows = []
    with pytest.raises(RuntimeError, match="close failed"):
        asyncio.run(harness.run_memory_cycles(
            client, "db", "container", configuration(harness), rows.append,
        ))
    assert list(client.container.rows) == ["unrelated"]
    assert not any(row["record_type"] == "completion" for row in rows)


@pytest.mark.parametrize("mode", ["elapsed_budget", "sampler_failure", "missing_charge"])
def test_budget_or_observation_failure_stops_and_cleans(harness, mode, monkeypatch):
    config = configuration(
        harness, max_seconds=0.15 if mode == "elapsed_budget" else 5,
    )
    container = Container(stall=mode != "missing_charge")
    client = Client(container)
    rows = []
    if mode == "missing_charge":
        original = container.create_item

        async def without_charge(item, response_hook):
            return await original(item, lambda *_: None)
        container.create_item = without_charge
    if mode == "sampler_failure":
        original_process = harness.psutil.Process
        process = original_process()

        class FailingSampler:
            pid = process.pid
            cpu_times = process.cpu_times
            num_threads = process.num_threads

            def memory_info(self):
                if container.active:
                    raise OSError("sampling failed")
                return process.memory_info()

        monkeypatch.setattr(harness.psutil, "Process", FailingSampler)
    with pytest.raises((RuntimeError, TimeoutError, OSError)):
        asyncio.run(harness.run_memory_cycles(client, "db", "container", config, rows.append))
    assert container.active == 0
    assert list(container.rows) == ["unrelated"]
    assert client.entries == client.exits == 1
    assert not any(row["record_type"] == "completion" for row in rows)


@pytest.mark.parametrize("changes", [
    {"pool_size": 0}, {"concurrency": 5}, {"partition_key": "/other"},
    {"namespace": "old"}, {"idle_seconds": float("nan")}, {"max_seconds": 0.001},
])
def test_configuration_rejects_unsafe_bounds(harness, changes):
    with pytest.raises(ValueError):
        configuration(harness, **changes)
