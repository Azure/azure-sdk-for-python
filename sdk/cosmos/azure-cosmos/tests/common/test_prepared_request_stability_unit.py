# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Request data stays fixed between preparation and sync/async dispatch."""

import asyncio
import json
from copy import deepcopy
from dataclasses import FrozenInstanceError, replace
from types import MappingProxyType

import pytest

from azure.cosmos._backend.contracts import (
    PreparedClientConfig,
    PreparedFaultInjectionRule,
    PreparedQuery,
    PreparedRequest,
)
from azure.cosmos._backend.partition_key_input import BindingPartitionKey
from azure.cosmos._backend.request_settings import RequestSettings
from azure.cosmos._backend.binding import build_binding_request_from_page as sync_page
from azure.cosmos.aio._backend.binding import build_binding_request_from_page as async_page


def point(**kwargs):
    return PreparedRequest(
        op="read_item",
        container_link="dbs/bank/colls/accounts",
        body_bytes=kwargs.pop("body_bytes", b""),
        partition_key=BindingPartitionKey("components", ("customer-1",)),
        item_id="account-1",
        **kwargs,
    )


@pytest.mark.parametrize("factory", [point, lambda **kw: PreparedQuery(
    op="query_items", container_link="dbs/bank/colls/accounts", query="SELECT * FROM c", **kw
)])
@pytest.mark.parametrize("readonly_view", [False, True])
def test_headers_are_owned_and_readonly(factory, readonly_view):
    original = {"x-customer": "original"}
    prepared = factory(headers=MappingProxyType(original) if readonly_view else original)
    original["x-customer"] = "changed"
    original["x-new"] = "later"
    assert dict(prepared.headers) == {"x-customer": "original"}
    with pytest.raises(TypeError):
        prepared.headers["x-customer"] = "changed"
    assert deepcopy(prepared.headers) == prepared.headers


@pytest.mark.parametrize("adapter", [sync_page, async_page])
def test_nested_query_parameters_keep_json_shape_and_previous_pages(adapter):
    parameters = [{"name": "@values", "value": {"values": [1, {"flag": True}, None]}}]
    page = PreparedQuery(
        op="query_items", container_link="dbs/bank/colls/accounts",
        query="SELECT VALUE @values", parameters=parameters,
        headers={"x-custom": "original"}, continuation="first",
    )
    expected = {"query": "SELECT VALUE @values", "parameters": deepcopy(parameters)}
    parameters[0]["value"]["values"][1]["flag"] = False
    parameters.append({"name": "@other", "value": []})
    with pytest.raises(TypeError):
        page.parameters[0]["value"]["values"][1]["flag"] = False
    with pytest.raises(TypeError):
        page.parameters[0]["value"]["values"][0] = 2
    next_page = replace(page, continuation="second")
    first, second = adapter(page), adapter(next_page)
    assert json.loads(first.body_bytes) == expected
    assert second.body_bytes == first.body_bytes
    assert first.settings.query.continuation == "first"
    assert second.settings.query.continuation == "second"
    assert next_page.parameters is page.parameters
    assert next_page.headers is page.headers


@pytest.mark.parametrize("adapter", [sync_page, async_page])
def test_change_feed_snapshot_and_cursor_ownership(adapter):
    settings = {"mode": "LatestVersion", "feed_range": ["", "FF"]}
    cursor = object()
    page = PreparedQuery(
        op="query_items_change_feed", container_link="dbs/bank/colls/accounts",
        change_feed=settings, cursor=cursor,
    )
    settings["feed_range"][1] = "EE"
    with pytest.raises(TypeError):
        page.change_feed["feed_range"][0] = "AA"
    assert json.loads(adapter(page).body_bytes) == {
        "mode": "LatestVersion", "feed_range": ["", "FF"]
    }
    assert replace(page, continuation="next").cursor is cursor


def test_retained_query_reuses_exact_bytes():
    body = b'{"query":"SELECT @p","parameters":[{"name":"@p","value":[1,2]}]}'
    page = PreparedQuery(
        op="query_items", container_link="dbs/bank/colls/accounts",
        query="SELECT @p", parameters=({"name": "@p", "value": [1, 2]},),
        query_body=body,
    )
    assert sync_page(page).body_bytes is body
    assert async_page(replace(page, continuation="next")).body_bytes is body


def test_nested_readonly_view_is_snapshotted_not_trusted():
    nested = {"values": [1, 2]}
    page = PreparedQuery(
        op="query_items", container_link="", query="SELECT @p",
        parameters=({"name": "@p", "value": MappingProxyType(nested)},),
    )
    nested["values"].append(3)
    assert json.loads(sync_page(page).body_bytes)["parameters"][0]["value"] == {
        "values": [1, 2]
    }


@pytest.mark.parametrize("kind", ["mapping", "list"])
def test_cyclic_query_data_is_rejected_but_shared_children_are_allowed(kind):
    value = {} if kind == "mapping" else []
    if kind == "mapping":
        value["self"] = value
    else:
        value.append(value)
    with pytest.raises(ValueError, match="Circular reference"):
        PreparedQuery(op="query_items", container_link="", parameters=(value,))
    child = {"value": [1]}
    page = PreparedQuery(
        op="query_items", container_link="", query="SELECT @p",
        parameters=({"name": "@p", "value": [child, child]},),
    )
    assert json.loads(sync_page(page).body_bytes)["parameters"][0]["value"] == [
        {"value": [1]}, {"value": [1]}
    ]


def test_unsupported_nested_values_are_not_silently_stringified():
    with pytest.raises(TypeError, match="Unsupported prepared JSON"):
        PreparedQuery(
            op="query_items", container_link="",
            parameters=({"name": "@p", "value": object()},),
        )


@pytest.mark.parametrize("factory", [point, lambda **kw: PreparedQuery(
    op="query_items", container_link="dbs/bank/colls/accounts", **kw
)])
def test_settings_are_typed_and_reused_without_revalidation(factory):
    settings = RequestSettings(excluded_locations=("West US",))
    prepared = factory(settings=settings)
    assert prepared.settings is settings
    with pytest.raises(FrozenInstanceError):
        settings.priority = "High"
    with pytest.raises(TypeError, match="RequestSettings"):
        factory(settings={"priority": "High"})


@pytest.mark.parametrize("body", [bytearray(b"{}"), memoryview(b"{}"), {}])
def test_point_body_must_already_be_immutable_bytes(body):
    with pytest.raises(TypeError, match="bytes"):
        point(body_bytes=body)


@pytest.mark.parametrize("headers", [{"x": []}, {1: "value"}, []])
def test_headers_reject_mutable_or_nonstring_values(headers):
    with pytest.raises(TypeError, match="headers"):
        point(headers=headers)


def test_client_config_snapshots_sequences_and_rejects_mutable_rule_fields():
    preferred, excluded = ["West US"], ["East US"]
    rule = PreparedFaultInjectionRule("test", "Read", 429)
    rules = [rule]
    config = PreparedClientConfig(
        preferred_locations=preferred, excluded_locations=excluded,
        fault_injection_rules=rules,
    )
    preferred.append("North Europe")
    excluded.clear()
    rules.clear()
    assert config.preferred_locations == ("West US",)
    assert config.excluded_locations == ("East US",)
    assert config.fault_injection_rules == (rule,)
    with pytest.raises(TypeError):
        PreparedFaultInjectionRule([], "Read", 429)
    with pytest.raises(TypeError):
        PreparedClientConfig(preferred_locations=[[]])


def test_mutating_source_while_async_dispatch_waits_does_not_change_request():
    async def run():
        headers = {"x-customer": "original"}
        prepared = point(headers=headers)
        ready, release = asyncio.Event(), asyncio.Event()

        async def dispatch():
            ready.set()
            await release.wait()
            return dict(prepared.headers)

        task = asyncio.create_task(dispatch())
        await ready.wait()
        headers["x-customer"] = "changed"
        release.set()
        assert await task == {"x-customer": "original"}

    asyncio.run(run())


def test_real_native_reader_accepts_snapshot_before_driver_lookup():
    from azure.cosmos import _rust

    with pytest.raises(RuntimeError, match="no driver registered"):
        _rust.read_item("unregistered-stability-test", point(headers={"x-test": "True"}))


@pytest.mark.parametrize("async_mode", [False, True])
def test_retained_native_reader_copies_body_without_python_iteration(async_mode):
    from azure.cosmos import _rust

    class Body(bytes):
        def __iter__(self):
            raise AssertionError("body must be copied directly")

    cursor = _rust._ItemFeedCursor()
    page = PreparedQuery(
        op="query_items", container_link="dbs/bank/colls/accounts",
        query_body=Body(b'{"query":"SELECT * FROM c"}'), cursor=cursor,
    )
    dispatch = (
        _rust.fetch_page_with_cursor_async if async_mode
        else _rust.fetch_page_with_cursor
    )
    with pytest.raises(RuntimeError, match="no driver registered"):
        dispatch("unregistered-stability-test", sync_page(page), cursor)


@pytest.fixture
def benchmark(monkeypatch):
    import importlib
    from pathlib import Path

    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "workloads"))
    return importlib.import_module("benchmark_request_boundary")


def test_benchmark_times_requested_invocations_in_microseconds(benchmark, monkeypatch):
    ticks = iter([1000, 11000])
    monkeypatch.setattr(benchmark.time, "perf_counter_ns", lambda: next(ticks))
    calls = []
    assert benchmark.sample(lambda: calls.append(1), 5) == 2
    assert len(calls) == 5


def test_benchmark_records_every_phase_and_repeated_samples(benchmark, monkeypatch, tmp_path):
    output = tmp_path / "result.json"
    executable = tmp_path / "native-test.exe"
    executable.write_bytes(b"unit-test executable")
    monkeypatch.setenv("COSMOS_BOUNDARY_BENCHMARK_OUTPUT", str(output))
    for name in ("ITERATIONS", "ROUNDS", "WARMUP"):
        monkeypatch.setenv(f"COSMOS_BOUNDARY_BENCHMARK_{name}", "2")
    monkeypatch.setattr(benchmark.subprocess, "check_output", lambda *a, **kw: "test\n")
    calls = []

    def extract(prepared):
        assert type(prepared.body_bytes) is bytes
        calls.append(prepared.op)

    benchmark.run(extract, extract, extract, str(executable))
    result = json.loads(output.read_text())
    assert len(result["results"]) == len(benchmark.cases()) * 3
    assert all(len(value["samples"]) == 2 for value in result["results"].values())
    assert result["iterations"] == result["rounds"] == result["warmup"] == 2
    assert result["source_hashes"]
    assert len(result["native_executable_sha256"]) == 64
    assert set(calls) == {"read_item", "create_item", "query_items"}
    # Per case: one initial check, two native phases in warmup and both rounds.
    assert len(calls) == len(benchmark.cases()) * (1 + 2 * 2 + 2 * 2 * 2)


def test_benchmark_rejects_empty_samples(benchmark, monkeypatch, tmp_path):
    monkeypatch.setenv("COSMOS_BOUNDARY_BENCHMARK_OUTPUT", str(tmp_path / "result.json"))
    monkeypatch.setenv("COSMOS_BOUNDARY_BENCHMARK_ITERATIONS", "0")
    with pytest.raises(ValueError, match="positive"):
        benchmark.run(None, None, None, "unused")
