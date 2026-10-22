# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep each database service page's diagnostics inside its consumption span."""

import asyncio
import builtins
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from functools import partial
import json
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

pytest.importorskip("opentelemetry.sdk.trace")
# pylint: disable=wrong-import-position
from opentelemetry import trace
from opentelemetry.sdk.trace.sampling import ALWAYS_OFF
from common.test_rust_telemetry_unit import (  # pylint: disable=unused-import
    DriverTransportError,
    attempt_spans,
    contribution_response,
    recording_setup,
)
from query_items.test_query_backend_routing_unit import listing_client  # pylint: disable=unused-import
from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.cosmos import _telemetry as telemetry
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos._backend.errors import BindingProtocolError, UnsupportedQueryError
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosResourceNotFoundError

# pylint: enable=wrong-import-position


class DriverUnsupportedQueryError(RuntimeError):
    pass


@pytest.fixture(name="listing_telemetry", params=["list_databases", "query_databases"])
def listing_telemetry_setup(
    listing_client, recording, monkeypatch, request
):  # pylint: disable=redefined-outer-name,unused-argument
    client, connection, _, asynchronous = listing_client
    module = async_binding if asynchronous else sync_binding
    backend_type = async_binding.AsyncBindingAdapter if asynchronous else sync_binding.BindingAdapter
    backend = backend_type("https://example.documents.azure.com", master_key="unused")
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        AsyncMock(return_value="test-driver") if asynchronous else Mock(return_value="test-driver"),
    )
    monkeypatch.setattr(module, "_DRIVER_TRANSPORT_ERROR", DriverTransportError)
    monkeypatch.setattr(module, "_UNSUPPORTED_QUERY_ERROR", DriverUnsupportedQueryError)
    client._adapter = connection._backend = backend
    seen = []
    client._item_context = ItemClientContext(
        backend,
        response_state=connection._response_state,
        telemetry_handlers=(telemetry.CompletionHandler(seen.append),),
    )
    harness = SimpleNamespace(
        client=client,
        backend=backend,
        asynchronous=asynchronous,
        seen=seen,
        calls=[],
        states=[],
        payloads=[],
        error=None,
        error_has_diagnostics=True,
        gate=None,
        status=200,
        pages=[([{"id": "sales"}], "next"), ([{"id": "archive"}], None)],
        transform=lambda value: value,
        malformed_body=False,
        empty_start=False,
        operation=request.param,
        create_iterable=(
            client.list_databases
            if request.param == "list_databases"
            else partial(client.query_databases, "SELECT * FROM root r")
        ),
    )

    def start(handle, prepared, include_attempts, timeout_seconds):
        assert handle == "test-driver"
        harness.calls.append((prepared, include_attempts, timeout_seconds))
        harness.states.append(telemetry._OPERATION.get())

    def finish(prepared, include_attempts):
        _, payload = contribution_response(5, time.time_ns())
        harness.payloads.append(payload)
        if harness.error:
            if include_attempts and harness.error_has_diagnostics:
                harness.error._cosmos_attempt_payload = payload
            raise harness.error
        token = prepared.settings.query.continuation
        if harness.empty_start and token is None:
            rows, continuation = [], "empty"
        else:
            rows, continuation = harness.pages[int(token == "next")]
        body = {"Databases": rows} if harness.status == 200 else {"message": "missing"}
        response = (
            harness.status,
            0,
            {"x-ms-continuation": continuation, "x-ms-activity-id": str(len(harness.calls))},
            b"invalid-json" if harness.malformed_body else json.dumps(body).encode(),
            None,
        )
        result = harness.transform((response, payload))
        return result if include_attempts else result[0]

    def native(handle, prepared, *, include_attempts=False, timeout_seconds=None):
        start(handle, prepared, include_attempts, timeout_seconds)
        return finish(prepared, include_attempts)

    async def native_async(handle, prepared, *, include_attempts=False, timeout_seconds=None):
        start(handle, prepared, include_attempts, timeout_seconds)
        if harness.gate is not None:
            harness.gate.set()
            await asyncio.Future()
        await asyncio.sleep(0)
        return finish(prepared, include_attempts)

    monkeypatch.setattr(
        module,
        "_rust_module",
        SimpleNamespace(
            **{
                "list_databases_async" if asynchronous else "list_databases": native_async if asynchronous else native,
                "query_databases_async" if asynchronous else "query_databases": (
                    native_async if asynchronous else native
                ),
            }
        ),
    )

    async def next_async(pages):
        return [row async for row in await pages.__anext__()]

    harness.next = lambda pages: asyncio.run(next_async(pages)) if asynchronous else list(next(pages))
    harness.next_async = next_async
    return harness


def fetch_spans(recording):
    return [
        s
        for s in recording.exporter.get_finished_spans()
        if s.name in ("CosmosClient.list_databases.fetch", "CosmosClient.query_databases.fetch")
    ]


@pytest.mark.parametrize("mode", ["enabled", "disabled", "handler-only", "sampled-out", "no-handlers"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_listing_page_telemetry_parent_boundary_and_replay(listing_telemetry, recording, mode, timeout):
    h = listing_telemetry
    if mode in ("disabled", "handler-only"):
        settings.tracing_enabled = False
    if mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    collect = mode in ("enabled", "handler-only", "no-handlers")
    h.client._item_context = replace(
        h.client._item_context,
        telemetry_handlers=(
            ()
            if mode == "no-handlers"
            else (telemetry.CompletionHandler(h.seen.append, collect_attempts=mode == "handler-only"),)
        ),
    )
    hooks = []

    def hook(headers):
        assert telemetry._OPERATION.get() is not None or mode == "no-handlers"
        if mode != "no-handlers":
            assert len(h.seen) == len(hooks)
        hooks.append(headers)
        headers.clear()

    with trace.get_tracer("customer").start_as_current_span("prepare") as producer:
        iterable = h.create_iterable(response_hook=hook, timeout=timeout)
        pages = iterable.by_page()
    assert not h.calls and not h.seen and not fetch_spans(recording)
    parents = []
    for expected in ([{"id": "sales"}], [{"id": "archive"}]):
        with trace.get_tracer("customer").start_as_current_span("consume") as consumer:
            assert h.next(pages) == expected
            parents.append(consumer.get_span_context().span_id)
            assert trace.get_current_span() is consumer
        assert telemetry._OPERATION.get() is None
        assert h.states[-1] is None or h.states[-1].closed
    assert pages.continuation_token is None
    with pytest.raises(StopAsyncIteration if h.asynchronous else StopIteration):
        h.next(pages)
    with trace.get_tracer("customer").start_as_current_span("resume") as consumer:
        assert h.next(iterable.by_page("next")) == [{"id": "archive"}]
        parents.append(consumer.get_span_context().span_id)
    assert len(h.calls) == len(hooks) == 3
    assert [call[1] for call in h.calls] == [collect] * 3
    assert all((call[2] is None) == (timeout is None) for call in h.calls)
    assert len(h.seen) == (0 if mode == "no-handlers" else 3)
    for completion in h.seen:
        assert completion.operation == h.operation and completion.outcome == "success"
        assert (completion.diagnostics is not None) == collect
        if collect:
            assert completion.diagnostics.request_count == 5
    fetch = fetch_spans(recording)
    assert len(fetch) == (3 if mode in ("enabled", "no-handlers") else 0)
    if fetch:
        creation = [s for s in recording.exporter.get_finished_spans() if s.name == f"CosmosClient.{h.operation}"]
        assert all(s.name == f"CosmosClient.{h.operation}.fetch" for s in fetch)
        assert creation[0].parent.span_id == producer.context.span_id
        assert [s.parent.span_id for s in fetch] == parents
        assert all(s.attributes["cosmos.poc.request_count"] == 5 for s in fetch)
        assert all(s.status.status_code is trace.StatusCode.UNSET for s in fetch)
        for span in fetch:
            assert len([s for s in attempt_spans(recording) if s.parent.span_id == span.context.span_id]) == 2


@pytest.mark.parametrize("terminal", [False, True])
def test_listing_page_telemetry_empty_pages_are_successes(listing_telemetry, recording, terminal):
    h = listing_telemetry
    h.empty_start = not terminal
    if terminal:
        h.pages = [([], None)]
    pages = h.create_iterable(timeout=10).by_page()
    if terminal:
        with pytest.raises(StopAsyncIteration if h.asynchronous else StopIteration):
            h.next(pages)
    else:
        assert h.next(pages) == [{"id": "sales"}]
        assert h.calls[1][2] <= h.calls[0][2]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == (1 if terminal else 2)
    assert all(c.outcome == "success" for c in h.seen)
    assert all(s.status.status_code is trace.StatusCode.UNSET for s in fetch_spans(recording))


@pytest.mark.parametrize("failure", ["service", "transport", "timeout", "parse", "hook", "hook-stop", "nonprogress"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_listing_page_telemetry_preserves_failure_and_diagnostics(listing_telemetry, recording, failure, timeout):
    h = listing_telemetry
    kwargs = {"timeout": timeout}
    error = None
    if failure == "service":
        h.status, expected = 404, CosmosResourceNotFoundError
    elif failure == "transport":
        h.error, expected = DriverTransportError("transport failed"), ServiceResponseError
    elif failure == "timeout":
        h.error, expected = TimeoutError("binding timeout"), CosmosClientTimeoutError if timeout else TimeoutError
    elif failure == "parse":
        h.malformed_body, expected = True, json.JSONDecodeError
    elif failure in ("hook", "hook-stop"):
        error = ValueError("hook failed") if failure == "hook" else StopIteration("hook ended")
        kwargs["response_hook"] = Mock(side_effect=error)
        expected = ValueError if failure == "hook" else RuntimeError
    else:
        h.pages = [([], "next"), ([], "next")]
        expected = BindingProtocolError
    pages = h.create_iterable(**kwargs).by_page()
    with pytest.raises(expected) as caught:
        h.next(pages)
    if failure == "hook":
        assert caught.value is error
    if failure == "hook-stop":
        assert caught.value.__cause__ is error
    if failure == "transport" or (failure == "timeout" and timeout):
        assert caught.value.__cause__ is h.error
    if failure == "timeout" and not timeout:
        assert caught.value is h.error
    count = 2 if failure == "nonprogress" else 1
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == count
    assert h.seen[-1].outcome == "error" and h.seen[-1].diagnostics.request_count == 5
    assert fetch_spans(recording)[-1].status.status_code is trace.StatusCode.ERROR
    assert pages.continuation_token is None
    with pytest.raises(RuntimeError, match="pager failed"):
        h.next(pages)
    assert len(h.calls) == count
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("detail", ["missing", "malformed", "partial", "reporting", "envelope"])
def test_listing_page_telemetry_optional_detail_never_repeats_fetch(listing_telemetry, recording, monkeypatch, detail):
    h = listing_telemetry
    if detail == "missing":
        h.transform = lambda value: (value[0], None)
    elif detail == "malformed":
        h.transform = lambda value: (value[0], {"schema_version": 99})
    elif detail == "partial":
        h.transform = lambda value: (value[0], {**value[1], "complete": False})
    elif detail == "envelope":
        h.transform = lambda value: value[0]
    else:
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("report failed")))
        h.client._item_context = replace(
            h.client._item_context,
            telemetry_handlers=(
                telemetry.CompletionHandler(Mock(side_effect=ValueError("handler failed"))),
                telemetry.CompletionHandler(h.seen.append),
            ),
        )
    assert h.next(h.create_iterable().by_page()) == [{"id": "sales"}]
    assert len(h.calls) == len(h.seen) == 1
    assert h.seen[0].outcome == "success"
    span = fetch_spans(recording)[0]
    assert not any(key.startswith("cosmos.poc.") for key in span.attributes)
    assert len(attempt_spans(recording)) == (2 if detail == "partial" else 0)


def test_listing_page_telemetry_is_selected_at_consumption(listing_telemetry, recording):
    h = listing_telemetry
    settings.tracing_enabled = False
    pages = h.create_iterable().by_page()
    settings.tracing_enabled = True
    h.next(pages)
    settings.tracing_enabled = False
    h.next(pages)
    assert [call[1] for call in h.calls] == [True, False]
    assert len(fetch_spans(recording)) == 1


@pytest.mark.parametrize("enabled", [False, True])
def test_listing_page_telemetry_masks_outer_state_and_restores_it(listing_telemetry, recording, enabled):
    h = listing_telemetry
    h.client._item_context = replace(
        h.client._item_context, telemetry_handlers=(telemetry.CompletionHandler(h.seen.append, collect_attempts=True),)
    )
    with telemetry._operation_scope(h.client, "outer", {}, h.operation):
        outer = telemetry._OPERATION.get()
        assert outer is not None
        h.client._item_context = replace(h.client._item_context, telemetry_handlers=())
        settings.tracing_enabled = enabled
        assert h.next(h.create_iterable().by_page()) == [{"id": "sales"}]
        assert telemetry._OPERATION.get() is outer
        assert outer.collector.contributions == 0
        assert h.states[0] is not outer
    assert not h.seen
    assert h.calls[0][1] == enabled
    assert len(fetch_spans(recording)) == int(enabled)


def test_listing_page_telemetry_rejects_invalid_response_without_retry(listing_telemetry, recording):
    h = listing_telemetry
    h.transform = lambda _value: ("invalid-response",)
    with pytest.raises(BindingProtocolError, match="attempt envelope"):
        h.next(h.create_iterable().by_page())
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == "error" and h.seen[0].diagnostics is None


def test_listing_page_telemetry_partial_consumption_closes_before_app_work(listing_telemetry, recording):
    h = listing_telemetry
    h.pages = [([{"id": "sales"}, {"id": "archive"}], None)]
    iterable = h.create_iterable()
    first = asyncio.run(iterable.__anext__()) if h.asynchronous else next(iterable)
    assert first == {"id": "sales"}
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.states[0].closed and telemetry._OPERATION.get() is None
    second = asyncio.run(iterable.__anext__()) if h.asynchronous else next(iterable)
    assert second == {"id": "archive"}
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1


@pytest.mark.parametrize("kind", ["construction", "unsupported", "explicit-disable", "no-import"])
def test_listing_page_telemetry_leaves_other_paths_unchanged(listing_telemetry, recording, monkeypatch, kind):
    h = listing_telemetry
    if kind == "construction":
        with pytest.raises(ValueError):
            h.create_iterable(max_item_count=0)
        assert not h.calls and not h.seen and not fetch_spans(recording)
        return
    if kind in ("unsupported", "explicit-disable"):
        kwargs = {"unknown_setting": True} if kind == "unsupported" else {"tracing_options": {"enabled": False}}
        pages = h.create_iterable(**kwargs).by_page()
        with pytest.raises(NotImplementedError):
            h.next(pages)
        assert not h.calls and len(h.seen) == 1 and h.seen[0].outcome == "error"
        assert len(fetch_spans(recording)) == int(kind == "unsupported")
        return
    settings.tracing_enabled = False
    h.client._item_context = replace(h.client._item_context, telemetry_handlers=())
    original_import = builtins.__import__

    def import_without_telemetry(name, *args, **kwargs):
        assert not name.startswith("opentelemetry")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", import_without_telemetry)
    assert h.next(h.create_iterable().by_page()) == [{"id": "sales"}]
    assert not h.calls[0][1]


def test_listing_page_telemetry_can_cross_threads(listing_telemetry, recording):
    h = listing_telemetry
    if h.asynchronous:
        pytest.skip("Sync thread handoff")
    pages = h.create_iterable().by_page()

    def consume():
        with trace.get_tracer("customer").start_as_current_span("worker") as parent:
            assert h.next(pages) == [{"id": "sales"}]
            return parent.context.span_id

    with ThreadPoolExecutor(max_workers=1) as executor:
        parent = executor.submit(consume).result()
    assert fetch_spans(recording)[0].parent.span_id == parent
    assert h.seen[0].diagnostics.request_count == 5
    assert telemetry._OPERATION.get() is None


def test_listing_page_telemetry_cancellation_and_concurrent_fetch(listing_telemetry, recording):
    h = listing_telemetry
    if not h.asynchronous:
        pytest.skip("Async cancellation")

    async def run():
        h.gate = asyncio.Event()
        pages = h.create_iterable(timeout=10).by_page()
        with trace.get_tracer("customer").start_as_current_span("consumer") as parent:
            task = asyncio.create_task(h.next_async(pages))
            await h.gate.wait()
            with pytest.raises(RuntimeError, match="Concurrent"):
                await h.next_async(pages)
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert fetch_spans(recording)[0].parent.span_id == parent.context.span_id
        assert len(h.calls) == len(h.seen) == 1
        assert h.seen[0].outcome == "cancelled" and h.seen[0].diagnostics is None
        assert h.states[0].closed and not h.states[0].delegated_tasks
        with pytest.raises(RuntimeError, match="pager failed"):
            await h.next_async(pages)
        h.gate = None
        assert await h.next_async(h.create_iterable().by_page()) == [{"id": "sales"}]
        assert len(h.calls) == len(h.seen) == 2
        assert h.states[0] is not h.states[1]
        assert telemetry._OPERATION.get() is None

    asyncio.run(run())


@pytest.mark.parametrize("listing_telemetry", ["query_databases"], indirect=True)
@pytest.mark.parametrize("shape", ["parameters", "specification", "projection", "none"])
def test_database_query_telemetry_preserves_inputs_and_rows(listing_telemetry, recording, shape):
    h = listing_telemetry
    parameters = [{"name": "@id", "value": {"nested": ["original"]}}]
    sql = "SELECT * FROM root r WHERE r.id = @id"
    query = {"query": sql, "parameters": parameters} if shape == "specification" else sql
    if shape == "projection":
        query = "SELECT VALUE r.id FROM root r"
        h.pages = [(["sales", 17, None, False, {"nested": ["value"]}], None)]
    elif shape == "none":
        query = None
    original = deepcopy(parameters)
    kwargs = {} if shape == "specification" else {"parameters": parameters}
    iterable = h.client.query_databases(query, **kwargs)
    parameters[0]["value"]["nested"][0] = "mutated"
    if isinstance(query, dict):
        query["query"] = "SELECT * FROM another"
    assert not h.calls
    rows = h.next(iterable.by_page())
    assert rows == h.pages[0][0]
    prepared = h.calls[0][0]
    if shape == "none":
        assert prepared.op == "list_databases" and prepared.body_bytes == b""
    else:
        assert prepared.op == "query_databases"
        body = json.loads(prepared.body_bytes)
        assert body["query"] == (query if isinstance(query, str) else sql)
        assert body["parameters"] == original
    assert h.calls[0][1]
    assert h.seen[0].operation == "query_databases"
    assert h.seen[0].diagnostics.request_count == 5
    assert fetch_spans(recording)[0].name == "CosmosClient.query_databases.fetch"


@pytest.mark.parametrize("listing_telemetry", ["query_databases"], indirect=True)
@pytest.mark.parametrize("diagnostics", [False, True])
def test_database_query_telemetry_preserves_unsupported_error(listing_telemetry, recording, diagnostics):
    h = listing_telemetry
    h.error = DriverUnsupportedQueryError("unsupported query feature")
    h.error_has_diagnostics = diagnostics
    pages = h.create_iterable().by_page()
    with pytest.raises(UnsupportedQueryError) as caught:
        h.next(pages)
    assert str(caught.value) == str(h.error) and caught.value.__cause__ is h.error
    assert len(h.calls) == len(h.seen) == 1
    assert h.seen[0].outcome == "error"
    assert (h.seen[0].diagnostics is not None) == diagnostics
    assert len(attempt_spans(recording)) == (2 if diagnostics else 0)
    assert fetch_spans(recording)[0].status.status_code is trace.StatusCode.ERROR
    with pytest.raises(RuntimeError, match="pager failed"):
        h.next(pages)
    assert len(h.calls) == 1


@pytest.mark.parametrize("listing_telemetry", ["query_databases"], indirect=True)
def test_database_query_and_listing_own_independent_page_records(listing_telemetry, recording):
    h = listing_telemetry
    listing = h.client.list_databases().by_page()
    query = h.client.query_databases("SELECT * FROM root r").by_page()
    for pages in (query, listing, query, listing):
        h.next(pages)
    assert [c.operation for c in h.seen] == ["query_databases", "list_databases"] * 2
    assert [s.name for s in fetch_spans(recording)] == [
        "CosmosClient.query_databases.fetch",
        "CosmosClient.list_databases.fetch",
    ] * 2
    assert len({id(state) for state in h.states}) == 4
    assert all(state.closed for state in h.states)
    assert all(c.diagnostics.request_count == 5 for c in h.seen)
