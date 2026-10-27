# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Record container listing and query pages through the shared pager."""

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
from common.test_container_backend_unit import _new_sync_connection, _new_async_connection
from common.test_list_databases_telemetry_unit import DriverUnsupportedQueryError
from azure.core.exceptions import ServiceResponseError
from azure.core.settings import settings
from azure.cosmos import _telemetry as telemetry
from azure.cosmos._backend import binding_adapter as sync_binding
from azure.cosmos._backend.errors import BindingProtocolError, UnsupportedQueryError
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.cosmos.database import DatabaseProxy
from azure.cosmos.aio._database import DatabaseProxy as AsyncDatabaseProxy
from azure.cosmos.aio._backend import binding_adapter as async_binding
from azure.cosmos.exceptions import CosmosClientTimeoutError, CosmosResourceNotFoundError

# pylint: enable=wrong-import-position


@pytest.fixture(name="container_operation", params=["list_containers", "query_containers"])
def container_operation_setup(request):
    return request.param


@pytest.fixture(name="listing", params=["sync", "async"])
def container_listing_setup(request, recording, monkeypatch, container_operation):  # pylint: disable=unused-argument
    asynchronous = request.param == "async"
    connection = _new_async_connection() if asynchronous else _new_sync_connection()
    monkeypatch.setattr(
        connection,
        "_CosmosClientConnection__Get",
        (AsyncMock if asynchronous else Mock)(side_effect=AssertionError("Unexpected legacy transport")),
    )
    module = async_binding if asynchronous else sync_binding
    backend_type = async_binding.AsyncBindingAdapter if asynchronous else sync_binding.BindingAdapter
    backend = backend_type("https://example.documents.azure.com", master_key="unused")
    monkeypatch.setattr(
        backend,
        "_ensure_driver_handle",
        AsyncMock(return_value="driver") if asynchronous else Mock(return_value="driver"),
    )
    monkeypatch.setattr(module, "_DRIVER_TRANSPORT_ERROR", DriverTransportError)
    monkeypatch.setattr(module, "_UNSUPPORTED_QUERY_ERROR", DriverUnsupportedQueryError)
    connection._backend = backend
    seen = []
    database = (AsyncDatabaseProxy if asynchronous else DatabaseProxy)(
        connection,
        "sales",
        _item_context=ItemClientContext(
            backend,
            response_state=connection._response_state,
            telemetry_handlers=(telemetry.CompletionHandler(seen.append),),
        ),
    )
    h = SimpleNamespace(
        database=database,
        backend=backend,
        connection=connection,
        asynchronous=asynchronous,
        seen=seen,
        calls=[],
        states=[],
        error=None,
        error_has_diagnostics=True,
        status=200,
        gate=None,
        pages={None: ([{"id": "orders"}], "next"), "next": ([{"id": "archive"}], None)},
        transform=lambda value: value,
        malformed=False,
        operation=container_operation,
        create_iterable=(
            database.list_containers
            if container_operation == "list_containers"
            else partial(database.query_containers, "SELECT * FROM root r")
        ),
    )

    def start(handle, prepared, include_attempts, timeout_seconds):
        assert handle == "driver"
        h.calls.append((prepared, include_attempts, timeout_seconds))
        h.states.append(telemetry._OPERATION.get())

    def finish(prepared, include_attempts):
        _, payload = contribution_response(5, time.time_ns())
        if h.error:
            if include_attempts and h.error_has_diagnostics:
                h.error._cosmos_attempt_payload = payload
            raise h.error
        rows, continuation = h.pages[prepared.settings.query.continuation]
        headers = {"x-ms-activity-id": str(len(h.calls)), "x-ms-request-charge": "5"}
        if continuation:
            headers["x-ms-continuation"] = continuation
        body = {"DocumentCollections": rows} if h.status == 200 else {"message": "missing"}
        result = h.transform(
            (
                (h.status, 0, headers, b"invalid-json" if h.malformed else json.dumps(body).encode(), None),
                payload,
            )
        )
        return result if include_attempts else result[0]

    def native(handle, prepared, *, include_attempts=False, timeout_seconds=None):
        start(handle, prepared, include_attempts, timeout_seconds)
        return finish(prepared, include_attempts)

    async def native_async(handle, prepared, *, include_attempts=False, timeout_seconds=None):
        start(handle, prepared, include_attempts, timeout_seconds)
        if h.gate:
            h.gate.set()
            await asyncio.Future()
        await asyncio.sleep(0)
        return finish(prepared, include_attempts)

    monkeypatch.setattr(
        module,
        "_rust_module",
        SimpleNamespace(
            **{
                "list_containers_async" if asynchronous else "list_containers": (
                    native_async if asynchronous else native
                ),
                "query_containers_async" if asynchronous else "query_containers": (
                    native_async if asynchronous else native
                ),
            }
        ),
    )

    async def next_async(pages):
        return [row async for row in await pages.__anext__()]

    h.next = lambda pages: asyncio.run(next_async(pages)) if asynchronous else list(next(pages))
    h.next_async = next_async
    return h


def fetch_spans(recording):
    return [
        s
        for s in recording.exporter.get_finished_spans()
        if s.name in ("DatabaseProxy.list_containers.fetch", "DatabaseProxy.query_containers.fetch")
    ]


@pytest.mark.parametrize("mode", ["enabled", "disabled", "handler-only", "sampled-out", "no-handlers"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_container_listing_telemetry_owns_fetch_and_hook(listing, recording, mode, timeout):
    h = listing
    if mode in ("disabled", "handler-only"):
        settings.tracing_enabled = False
    if mode == "sampled-out":
        recording.provider.sampler = ALWAYS_OFF
    collect = mode in ("enabled", "handler-only", "no-handlers")
    h.database._item_context = replace(
        h.database._item_context,
        telemetry_handlers=(
            ()
            if mode == "no-handlers"
            else (telemetry.CompletionHandler(h.seen.append, collect_attempts=mode == "handler-only"),)
        ),
    )
    hooks = []

    class Hook:
        def __bool__(self):
            return False

        def __call__(self, headers, result):
            assert result is iterable
            if mode != "no-handlers":
                assert len(h.seen) == len(hooks)
            hooks.append(dict(headers))
            headers.clear()

    with trace.get_tracer("customer").start_as_current_span("prepare") as producer:
        iterable = h.create_iterable(max_item_count=1, timeout=timeout, response_hook=Hook())
    assert not h.calls and not h.seen and not fetch_spans(recording)
    pages = iterable.by_page()
    parents = []
    for expected in ([{"id": "orders"}], [{"id": "archive"}]):
        with trace.get_tracer("customer").start_as_current_span("consume") as consumer:
            assert h.next(pages) == expected
            parents.append(consumer.get_span_context().span_id)
            assert trace.get_current_span() is consumer
        assert telemetry._OPERATION.get() is None
        assert h.states[-1] is None or h.states[-1].closed
    assert pages.continuation_token is None
    with pytest.raises(StopAsyncIteration if h.asynchronous else StopIteration):
        h.next(pages)
    with trace.get_tracer("customer").start_as_current_span("replay") as consumer:
        assert h.next(iterable.by_page("next")) == [{"id": "archive"}]
        parents.append(consumer.get_span_context().span_id)
    assert len(h.calls) == len(hooks) == 3
    assert all(call[0].op == h.operation and call[0].container_link == "dbs/sales" for call in h.calls)
    assert all(call[1] == collect for call in h.calls)
    assert all((call[2] is None) == (timeout is None) for call in h.calls)
    assert len(h.seen) == (0 if mode == "no-handlers" else 3)
    for completion in h.seen:
        assert completion.operation == h.operation and completion.outcome == "success"
        assert (completion.diagnostics is not None) == collect
    fetch = fetch_spans(recording)
    assert len(fetch) == (3 if mode in ("enabled", "no-handlers") else 0)
    if fetch:
        creation = [s for s in recording.exporter.get_finished_spans() if s.name == f"DatabaseProxy.{h.operation}"]
        assert creation[0].parent.span_id == producer.context.span_id
        assert all(span.name == f"DatabaseProxy.{h.operation}.fetch" for span in fetch)
        assert [s.parent.span_id for s in fetch] == parents
        for span in fetch:
            assert span.attributes["cosmos.poc.request_count"] == 5
            assert len([s for s in attempt_spans(recording) if s.parent.span_id == span.context.span_id]) == 2
    h.connection._CosmosClientConnection__Get.assert_not_called()


@pytest.mark.parametrize("terminal", [False, True])
def test_container_listing_telemetry_empty_pages(listing, recording, monkeypatch, terminal):
    h = listing
    deadlines = []
    original = h.backend.execute_pages

    def execute_pages(*args, **kwargs):
        deadlines.append(kwargs["deadline"])
        return original(*args, **kwargs)

    monkeypatch.setattr(h.backend, "execute_pages", execute_pages)
    h.pages[None] = ([], None if terminal else "next")
    pages = h.create_iterable(timeout=10).by_page()
    if terminal:
        with pytest.raises(StopAsyncIteration if h.asynchronous else StopIteration):
            h.next(pages)
    else:
        assert h.next(pages) == [{"id": "archive"}]
        assert deadlines[1] == deadlines[0]
        budgets = [call[0].settings.timeout_seconds for call in h.calls]
        assert 0 < budgets[1] <= budgets[0] <= 10
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == (1 if terminal else 2)
    assert all(c.outcome == "success" for c in h.seen)
    assert all(s.status.status_code is trace.StatusCode.UNSET for s in fetch_spans(recording))


@pytest.mark.parametrize("failure", ["service", "transport", "timeout", "parse", "hook"])
@pytest.mark.parametrize("timeout", [None, 10])
def test_container_listing_telemetry_preserves_errors(listing, recording, failure, timeout):
    h = listing
    kwargs = {"timeout": timeout}
    error = None
    if failure == "service":
        h.status, expected = 404, CosmosResourceNotFoundError
    elif failure == "transport":
        h.error, expected = DriverTransportError("failed"), ServiceResponseError
    elif failure == "timeout":
        h.error, expected = TimeoutError("timed out"), CosmosClientTimeoutError if timeout else TimeoutError
    elif failure == "parse":
        h.malformed, expected = True, json.JSONDecodeError
    else:
        error, expected = ValueError("hook failed"), ValueError
        kwargs["response_hook"] = Mock(side_effect=error)
    with pytest.raises(expected) as caught:
        h.next(h.create_iterable(**kwargs).by_page())
    if failure == "hook":
        assert caught.value is error
    if failure == "transport" or (failure == "timeout" and timeout):
        assert caught.value.__cause__ is h.error
    if failure == "timeout" and not timeout:
        assert caught.value is h.error
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == "error" and h.seen[0].diagnostics.request_count == 5
    assert fetch_spans(recording)[0].status.status_code is trace.StatusCode.ERROR
    assert telemetry._OPERATION.get() is None


@pytest.mark.parametrize("detail", ["missing", "malformed", "partial", "reporting", "invalid-response"])
def test_container_listing_telemetry_diagnostics_fail_independently(listing, recording, monkeypatch, detail):
    h = listing
    if detail == "missing":
        h.transform = lambda value: (value[0], None)
    elif detail == "malformed":
        h.transform = lambda value: (value[0], {"schema_version": 99})
    elif detail == "partial":
        h.transform = lambda value: (value[0], {**value[1], "complete": False})
    elif detail == "invalid-response":
        h.transform = lambda _: ("invalid",)
    else:
        monkeypatch.setattr(telemetry, "emit_attempts", Mock(side_effect=RuntimeError("recording failed")))
        h.database._item_context = replace(
            h.database._item_context,
            telemetry_handlers=(
                telemetry.CompletionHandler(Mock(side_effect=ValueError("handler failed"))),
                telemetry.CompletionHandler(h.seen.append),
            ),
        )
    pages = h.create_iterable().by_page()
    if detail == "invalid-response":
        with pytest.raises(BindingProtocolError):
            h.next(pages)
    else:
        assert h.next(pages) == [{"id": "orders"}]
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == ("error" if detail == "invalid-response" else "success")
    assert not any(k.startswith("cosmos.poc.") for k in fetch_spans(recording)[0].attributes)
    assert len(attempt_spans(recording)) == (2 if detail == "partial" else 0)


def test_container_listing_telemetry_partial_consumption_and_current_settings(listing, recording):
    h = listing
    h.pages[None] = ([{"id": "orders"}, {"id": "archive"}], "next")
    settings.tracing_enabled = False
    iterable = h.create_iterable()
    settings.tracing_enabled = True
    first = asyncio.run(iterable.__anext__()) if h.asynchronous else next(iterable)
    assert first == {"id": "orders"}
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.states[0].closed and telemetry._OPERATION.get() is None
    second = asyncio.run(iterable.__anext__()) if h.asynchronous else next(iterable)
    assert second == {"id": "archive"} and len(h.calls) == 1
    settings.tracing_enabled = False
    h.next(iterable.by_page("next"))
    assert [call[1] for call in h.calls] == [True, False]
    assert len(fetch_spans(recording)) == 1


@pytest.mark.parametrize("case", ["unsupported", "disabled-option", "no-import"])
def test_container_listing_telemetry_keeps_other_paths(listing, recording, monkeypatch, case):
    h = listing
    if case in ("unsupported", "disabled-option"):
        kwargs = {"unknown_setting": True} if case == "unsupported" else {"tracing_options": {"enabled": False}}
        with pytest.raises(NotImplementedError):
            h.next(h.create_iterable(**kwargs).by_page())
        assert not h.calls and h.seen[0].outcome == "error"
        assert len(fetch_spans(recording)) == int(case == "unsupported")
    else:
        settings.tracing_enabled = False
        h.database._item_context = replace(h.database._item_context, telemetry_handlers=())
        original_import = builtins.__import__

        def guarded_import(name, *args, **kwargs):
            assert not name.startswith("opentelemetry")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", guarded_import)
        assert h.next(h.create_iterable().by_page()) == [{"id": "orders"}]
        assert not h.calls[0][1]


@pytest.mark.parametrize("enabled", [False, True])
def test_container_listing_telemetry_masks_outer_state(listing, recording, enabled):
    h = listing
    h.database._item_context = replace(
        h.database._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(h.seen.append, collect_attempts=True),),
    )
    with telemetry._operation_scope(h.database, "outer", {}, h.operation):
        outer = telemetry._OPERATION.get()
        h.database._item_context = replace(h.database._item_context, telemetry_handlers=())
        settings.tracing_enabled = enabled
        assert h.next(h.create_iterable().by_page()) == [{"id": "orders"}]
        assert telemetry._OPERATION.get() is outer
        assert outer.collector.contributions == 0
        assert h.states[0] is not outer
    assert not h.seen
    assert h.calls[0][1] == enabled
    assert len(fetch_spans(recording)) == int(enabled)


@pytest.mark.parametrize("collect_attempts", [False, True])
def test_container_listing_telemetry_nested_hook_owns_separate_state(listing, recording, collect_attempts):
    h = listing
    if h.asynchronous:
        pytest.skip("Synchronous nested listing in a synchronous hook")
    h.database._item_context = replace(
        h.database._item_context,
        telemetry_handlers=(telemetry.CompletionHandler(h.seen.append, collect_attempts=collect_attempts),),
    )

    def hook(_headers, _result):
        outer = telemetry._OPERATION.get()
        assert h.next(h.create_iterable().by_page("next")) == [{"id": "archive"}]
        assert telemetry._OPERATION.get() is outer
        assert not outer.closed

    pages = h.create_iterable(response_hook=hook).by_page()
    assert h.next(pages) == [{"id": "orders"}]
    assert pages.continuation_token == "next"
    assert h.states[0] is not h.states[1]
    assert len(h.calls) == len(h.seen) == 2
    assert [call[1] for call in h.calls] == [True, collect_attempts]
    assert (h.seen[0].diagnostics is not None) == collect_attempts
    assert h.seen[1].diagnostics.request_count == 5
    assert all(state.closed for state in h.states)
    # Azure Core suppresses nested spans; their diagnostics must not enter the outer fetch.
    assert len(fetch_spans(recording)) == 1
    assert fetch_spans(recording)[0].attributes["cosmos.poc.request_count"] == 5


def test_container_listing_telemetry_cross_thread_consumption(listing, recording):
    h = listing
    if h.asynchronous:
        pytest.skip("Sync thread handoff")
    pages = h.create_iterable().by_page()

    def consume():
        with trace.get_tracer("customer").start_as_current_span("worker") as parent:
            assert h.next(pages) == [{"id": "orders"}]
            return parent.context.span_id

    with ThreadPoolExecutor(max_workers=1) as executor:
        parent = executor.submit(consume).result()
    assert fetch_spans(recording)[0].parent.span_id == parent
    assert h.seen[0].diagnostics.request_count == 5


def test_container_listing_telemetry_cancellation_closes_state(listing, recording):
    h = listing
    if not h.asynchronous:
        pytest.skip("Async cancellation")

    async def run():
        h.gate = asyncio.Event()
        with trace.get_tracer("customer").start_as_current_span("consumer") as parent:
            task = asyncio.create_task(h.next_async(h.create_iterable(timeout=10).by_page()))
            await h.gate.wait()
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
            assert fetch_spans(recording)[0].parent.span_id == parent.context.span_id
        assert len(h.calls) == len(h.seen) == 1
        assert h.seen[0].outcome == "cancelled" and h.seen[0].diagnostics is None
        assert h.states[0].closed and not h.states[0].delegated_tasks
        h.gate = None
        assert await h.next_async(h.create_iterable().by_page()) == [{"id": "orders"}]
        assert h.states[0] is not h.states[1]
        assert telemetry._OPERATION.get() is None

    asyncio.run(run())


@pytest.mark.parametrize("container_operation", ["query_containers"], indirect=True)
@pytest.mark.parametrize("shape", ["parameters", "specification", "projection", "none"])
def test_container_query_telemetry_preserves_inputs_and_rows(listing, recording, shape):
    h = listing
    parameters = [{"name": "@id", "value": {"nested": ["original"]}}]
    sql = "SELECT * FROM root r WHERE r.id=@id"
    query = {"query": sql, "parameters": parameters} if shape == "specification" else sql
    kwargs = {} if shape == "specification" else {"parameters": parameters}
    if shape == "projection":
        query = "SELECT VALUE r.id FROM root r"
        h.pages[None] = (["orders", 17, None, False, {"nested": ["value"]}], None)
    elif shape == "none":
        query, kwargs = None, {}
    original = deepcopy(parameters)
    iterable = h.database.query_containers(query, **kwargs)
    parameters[0]["value"]["nested"][0] = "mutated"
    if isinstance(query, dict):
        query["query"] = "SELECT * FROM another"
    assert not h.calls
    assert h.next(iterable.by_page()) == h.pages[None][0]
    prepared = h.calls[0][0]
    if shape == "none":
        assert prepared.op == "list_containers" and prepared.body_bytes == b""
    else:
        assert prepared.op == "query_containers"
        body = json.loads(prepared.body_bytes)
        assert body["query"] == (query if isinstance(query, str) else sql)
        assert body["parameters"] == original
    assert h.calls[0][1]
    assert h.seen[0].operation == "query_containers" and h.seen[0].diagnostics.request_count == 5
    assert fetch_spans(recording)[0].name == "DatabaseProxy.query_containers.fetch"


@pytest.mark.parametrize("container_operation", ["query_containers"], indirect=True)
@pytest.mark.parametrize("diagnostics", [False, True])
def test_container_query_telemetry_preserves_unsupported_error(listing, recording, diagnostics):
    h = listing
    h.error = DriverUnsupportedQueryError("unsupported query feature")
    h.error_has_diagnostics = diagnostics
    pages = h.create_iterable().by_page()
    with pytest.raises(UnsupportedQueryError) as caught:
        h.next(pages)
    assert str(caught.value) == str(h.error) and caught.value.__cause__ is h.error
    assert len(h.calls) == len(h.seen) == len(fetch_spans(recording)) == 1
    assert h.seen[0].outcome == "error"
    assert (h.seen[0].diagnostics is not None) == diagnostics
    assert len(attempt_spans(recording)) == (2 if diagnostics else 0)
    with pytest.raises(RuntimeError, match="pager failed"):
        h.next(pages)
    assert len(h.calls) == 1


@pytest.mark.parametrize("container_operation", ["query_containers"], indirect=True)
def test_container_query_and_listing_telemetry_remain_independent(listing, recording):
    h = listing
    listed = h.database.list_containers().by_page()
    queried = h.database.query_containers(None).by_page()
    for pages in (queried, listed, queried, listed):
        h.next(pages)
    assert all(call[0].op == "list_containers" for call in h.calls)
    assert [completion.operation for completion in h.seen] == ["query_containers", "list_containers"] * 2
    assert [span.name for span in fetch_spans(recording)] == [
        "DatabaseProxy.query_containers.fetch",
        "DatabaseProxy.list_containers.fetch",
    ] * 2
    assert len({id(state) for state in h.states}) == 4
    assert all(state.closed for state in h.states)
