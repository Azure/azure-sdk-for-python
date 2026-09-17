# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Observable contracts behind wrapper names and native cursor dispatch."""

import asyncio
import inspect
import json
import logging
from dataclasses import fields, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Callable, get_type_hints
from unittest.mock import AsyncMock, MagicMock

import pytest
from azure.core.utils import CaseInsensitiveDict

from azure.cosmos._backend import rust as sync_rust
from azure.cosmos.aio._backend import rust as async_rust
from azure.cosmos._backend.contracts import (
    BackendResponse,
    PreparedQuery,
    PreparedRequest,
)
from azure.cosmos._backend.cosmos_backend import CosmosBackend
from azure.cosmos.aio._backend.cosmos_backend import AsyncCosmosBackend
from azure.cosmos._backend.errors import (
    BackendProtocolError,
    PageNotSupportedByBackendError,
)
from azure.cosmos._backend.partition_key import PartitionKeyInput
from azure.cosmos._backend.request_settings import RequestSettings
from azure.cosmos._backend.operations import (
    CURSOR_QUERY_TO_BINDING_METHOD,
    STATELESS_QUERY_TO_BINDING_METHOD,
    get_page_binding_method,
)
from azure.cosmos._helpers import _item_prep, _response_parse
from azure.cosmos import _operation_deadline
from azure.cosmos._helpers._document import serialize_document
from azure.cosmos._helpers._item_context import ClientLastResponseHeaders
from azure.cosmos._helpers._response_parse import (
    parse_backend_response,
    process_backend_response,
)
from azure.cosmos._helpers.item_helper import (
    normalize_item_arguments,
    validate_rust_item_options,
)
from azure.cosmos.exceptions import (
    CosmosClientTimeoutError,
    CosmosResourceNotFoundError,
)


@pytest.mark.parametrize(
    "method,request_type",
    [
        ("run_operation", PreparedRequest),
        ("run_page_operation", PreparedQuery),
    ],
)
def test_sync_and_async_use_the_same_typed_builder(method, request_type):
    for backend in (CosmosBackend, AsyncCosmosBackend):
        function = getattr(backend, method)
        assert get_type_hints(function)["build_request"] == Callable[[], request_type]
        assert "prepare_request" not in inspect.signature(function).parameters
        assert "process_response" in inspect.signature(function).parameters


def test_point_execution_is_direct_and_deadlines_belong_to_the_invocation():
    for backend in (CosmosBackend, AsyncCosmosBackend):
        assert not hasattr(backend, "run_item_operation")
        hints = get_type_hints(backend.execute)
        assert hints["prepared"] is PreparedRequest
        assert hints["return"] is BackendResponse
        for method in (backend.execute, backend.execute_pages):
            parameter = inspect.signature(method).parameters["deadline"]
            assert parameter.kind is inspect.Parameter.KEYWORD_ONLY
            assert parameter.default is None
    for contract in (PreparedRequest, PreparedQuery):
        assert "deadline" not in {field.name for field in fields(contract)}


def test_retired_helpers_have_no_forwarding_modules():
    directory = Path(_item_prep.__file__).parent
    for name in (
        "_body_wire",
        "_format_ru",
        "_create_item",
        "_read_item",
        "_patch_item",
        "_item_operation",
        "_auto_id",
        "_options",
        "_request_headers",
        "_container_rid",
    ):
        assert not (directory / f"{name}.py").exists()
    for name in ("_legacy_partition_key", "_paths", "_resource_validation"):
        assert (directory / f"{name}.py").exists()


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def executor(request, monkeypatch):
    async_mode = request.param
    module = async_rust if async_mode else sync_rust
    backend_type = module.AsyncRustBackend if async_mode else module.RustBackend
    backend = object.__new__(backend_type)
    state = SimpleNamespace(now=100.0, init_delay=0.0)

    def acquire():
        state.now += state.init_delay
        return "handle"

    mock = AsyncMock if async_mode else MagicMock
    state.binding = mock(return_value=(200, 0, {}, b"{}", None))
    state.handle = mock(side_effect=acquire)
    monkeypatch.setattr(backend, "_ensure_driver_handle", state.handle)
    monkeypatch.setattr(
        _operation_deadline, "time", SimpleNamespace(monotonic=lambda: state.now)
    )
    monkeypatch.setattr(
        module,
        "_rust_module",
        SimpleNamespace(
            read_item=state.binding,
            read_item_async=state.binding,
            create_item=state.binding,
            create_item_async=state.binding,
            fetch_page_with_cursor=state.binding,
            fetch_page_with_cursor_async=state.binding,
            ItemFeedCursor=lambda: SimpleNamespace(),
        ),
    )

    def run(prepared, *, deadline=None):
        async def collect():
            if isinstance(prepared, PreparedQuery):
                return [
                    page
                    async for page in backend.execute_pages(prepared, deadline=deadline)
                ]
            return await backend.execute(prepared, deadline=deadline)

        if async_mode:
            return asyncio.run(collect())
        if isinstance(prepared, PreparedQuery):
            return list(backend.execute_pages(prepared, deadline=deadline))
        return backend.execute(prepared, deadline=deadline)

    state.run = run
    return state


def point_request():
    return PreparedRequest(
        op="read_item",
        container_link="dbs/d/colls/c",
        item_id="item",
        body_bytes=b"",
        partition_key=PartitionKeyInput("components", ("p",)),
    )


@pytest.mark.parametrize("paged", [False, True])
@pytest.mark.parametrize(
    "init_delay,expires", [(0.75, False), (1.0, True), (2.0, True)]
)
def test_executor_converts_the_same_deadline_after_initialization(
    executor, paged, init_delay, expires
):
    prepared = (
        PreparedQuery(
            op="read_all_items",
            container_link="dbs/d/colls/c",
            cursor=SimpleNamespace(has_more=False, continuation_supported=True),
        )
        if paged
        else point_request()
    )
    executor.init_delay = init_delay
    if expires:
        with pytest.raises(CosmosClientTimeoutError):
            executor.run(prepared, deadline=101.0)
        executor.binding.assert_not_called()
    else:
        executor.run(prepared, deadline=101.0)
        assert executor.binding.call_args.kwargs["timeout_seconds"] == 0.25
        assert not hasattr(executor.binding.call_args.args[1], "deadline")
    executor.handle.assert_called_once()


def test_executor_rejects_none_before_acquiring_a_driver(executor):
    with pytest.raises(TypeError, match="PreparedRequest"):
        executor.run(None)
    executor.handle.assert_not_called()
    executor.binding.assert_not_called()


def test_executor_enforces_its_response_postcondition(executor):
    executor.binding.return_value = None
    with pytest.raises(BackendProtocolError, match="no response.*read_item"):
        executor.run(point_request())
    executor.binding.assert_called_once()


@pytest.mark.parametrize("deadline", [None, 101.0])
def test_executor_maps_only_budgeted_native_timeouts(executor, deadline):
    error = TimeoutError("native failure")
    executor.binding.side_effect = error
    with pytest.raises(
        TimeoutError if deadline is None else CosmosClientTimeoutError
    ) as raised:
        executor.run(point_request(), deadline=deadline)
    if deadline is None:
        assert raised.value is error
    else:
        assert raised.value.__cause__ is error


def test_no_response_write_still_returns_a_response_record(executor):
    executor.binding.return_value = (201, 0, {"etag": "written"}, b"", None)
    result = executor.run(
        replace(
            point_request(),
            op="create_item",
            body_bytes=b'{"id":"item","pk":"p"}',
            settings=RequestSettings(no_response=True),
        )
    )
    assert isinstance(result, BackendResponse)
    assert result.body == b""
    assert result.headers["etag"] == "written"


def test_serializer_never_allocates_ids(monkeypatch):
    generate = MagicMock(side_effect=AssertionError("serializer generated an ID"))
    monkeypatch.setattr("azure.cosmos._helpers._document.uuid.uuid4", generate)
    source = {"nested": {"value": 1}}
    result = serialize_document(source, operation="create_item")
    assert result.body_id is None
    assert json.loads(result.body_bytes) == source
    assert "generate_id" not in inspect.signature(serialize_document).parameters
    generate.assert_not_called()


def test_parser_does_not_mutate_owned_headers_or_accept_effects():
    headers = CaseInsensitiveDict({"x-ms-request-charge": 2.5})
    response = BackendResponse(
        200, 0, headers, b'{"nested":{"value":1}}', {"region": "west"}
    )
    parsed = parse_backend_response(response)
    assert headers["x-ms-request-charge"] == 2.5
    assert "x-ms-cosmos-sdk-diagnostics" not in headers
    assert parsed.get_response_headers()["x-ms-request-charge"] == "2.5"
    parsed["nested"]["value"] = 2
    assert response.body == b'{"nested":{"value":1}}'
    assert list(inspect.signature(parse_backend_response).parameters) == ["response"]


@pytest.mark.parametrize(
    "status,body,error",
    [
        (404, b'{"message":"missing"}', CosmosResourceNotFoundError),
        (200, b"not JSON", json.JSONDecodeError),
    ],
)
def test_processor_publishes_headers_before_errors_without_hook(status, body, error):
    response = BackendResponse(status, 0, {"etag": "current"}, body)
    state = ClientLastResponseHeaders()
    hook = MagicMock()
    with pytest.raises(error):
        process_backend_response(response, response_state=state, response_hook=hook)
    assert state.last_response_headers["etag"] == "current"
    hook.assert_not_called()


def test_completion_checks_deadline_even_without_hook_and_has_no_read_alias(
    monkeypatch,
):
    result = parse_backend_response(BackendResponse(200, 0, {}, b"{}"))
    check = MagicMock(side_effect=CosmosClientTimeoutError())
    monkeypatch.setattr(_response_parse, "remaining_timeout", check)
    with pytest.raises(CosmosClientTimeoutError):
        _response_parse.complete_item_response(result, None, 10.0)
    check.assert_called_once_with(10.0)
    assert not hasattr(_item_prep, "finish_read_item")
    assert not hasattr(_item_prep, "complete_item_response")


def test_patch_normalization_owns_mutation_and_validation_does_not():
    source = {
        "container_link": "dbs/d/colls/c",
        "item_id": "item",
        "patch_operations": [{"op": "set", "path": "/value", "value": 1}],
        "request_options": {
            "partitionKey": "p",
            "initialHeaders": {"If-Match": "etag"},
        },
    }
    args, options = normalize_item_arguments("patch_item", source)
    assert source["request_options"]["initialHeaders"] == {"If-Match": "etag"}
    assert options["accessCondition"] == {"type": "IfMatch", "condition": "etag"}
    before = json.dumps(options, sort_keys=True)
    assert validate_rust_item_options(args, options) is None
    assert json.dumps(options, sort_keys=True) == before


ALL_PAGE_OPS = sorted(
    STATELESS_QUERY_TO_BINDING_METHOD.keys() | CURSOR_QUERY_TO_BINDING_METHOD.keys()
)


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("uses_cursor", [False, True])
@pytest.mark.parametrize("op", ALL_PAGE_OPS)
def test_page_dispatch_is_selected_once_by_operation_and_cursor_mode(
    monkeypatch, caplog, async_mode, uses_cursor, op
):
    module = async_rust if async_mode else sync_rust
    backend_type = module.AsyncRustBackend if async_mode else module.RustBackend
    backend = object.__new__(backend_type)
    handle = (
        AsyncMock(return_value="handle")
        if async_mode
        else MagicMock(return_value="handle")
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", handle)
    cursor = SimpleNamespace(has_more=False, continuation_supported=True)
    cursor_factory = MagicMock(return_value=cursor)
    methods = (
        CURSOR_QUERY_TO_BINDING_METHOD
        if uses_cursor
        else STATELESS_QUERY_TO_BINDING_METHOD
    )
    expected = methods.get(op)
    calls = []

    def dispatch(*args, **kwargs):
        calls.append((args, kwargs))
        return 200, 0, {}, b"{}", None

    async def dispatch_async(*args, **kwargs):
        return dispatch(*args, **kwargs)

    exports = {"ItemFeedCursor": cursor_factory}
    if expected is not None:
        exports[expected + ("_async" if async_mode else "")] = (
            dispatch_async if async_mode else dispatch
        )
    monkeypatch.setattr(module, "_rust_module", SimpleNamespace(**exports))
    prepared = PreparedQuery(
        op=op,
        container_link="dbs/d/colls/c",
        query="SELECT * FROM c",
        change_feed={},
        cursor=cursor if uses_cursor else None,
    )

    async def collect():
        return [page async for page in backend.execute_pages(prepared)]

    def run():
        return (
            asyncio.run(collect())
            if async_mode
            else list(backend.execute_pages(prepared))
        )

    caplog.set_level(logging.DEBUG, logger=module.__name__)
    assert get_page_binding_method(op, uses_cursor=uses_cursor) == expected
    if expected is None:
        with pytest.raises(PageNotSupportedByBackendError):
            run()
        handle.assert_not_called()
        cursor_factory.assert_not_called()
        return
    assert len(run()) == 1
    assert len(calls) == 1
    assert f"dispatch={expected}" + ("_async" if async_mode else "") in caplog.text
    if uses_cursor:
        assert calls[0][0][2] is cursor
        assert prepared.cursor is cursor
        assert "timeout_seconds" in calls[0][1]
        assert len(run()) == 1
        cursor_factory.assert_not_called()
    else:
        assert len(calls[0][0]) == 2
        assert calls[0][1] == {}
        cursor_factory.assert_not_called()


def test_installed_native_cursor_exports_have_no_concept_aliases():
    native = pytest.importorskip("azure.cosmos._rust")
    assert hasattr(native, "ItemFeedCursor")
    for name in ("fetch_page_with_cursor", "fetch_page_with_cursor_async"):
        assert "cursor" in inspect.signature(getattr(native, name)).parameters
    for old in (
        "ReadAllItemsCursor",
        "read_all_items_page",
        "read_all_items_page_async",
        "query_items_change_feed",
        "query_items_change_feed_async",
    ):
        assert not hasattr(native, old)


@pytest.mark.parametrize("async_mode", [False, True])
def test_missing_cursor_export_is_a_rebuild_error_not_a_stateless_fallback(
    monkeypatch, async_mode
):
    module = async_rust if async_mode else sync_rust
    backend_type = module.AsyncRustBackend if async_mode else module.RustBackend
    backend = object.__new__(backend_type)
    forbidden = MagicMock(
        side_effect=AssertionError("driver acquisition or stateless dispatch")
    )
    monkeypatch.setattr(backend, "_ensure_driver_handle", forbidden)
    monkeypatch.setattr(
        module,
        "_rust_module",
        SimpleNamespace(query_items=forbidden, query_items_async=forbidden),
    )
    prepared = PreparedQuery(
        op="query_items",
        container_link="dbs/d/colls/c",
        query="SELECT * FROM c",
        cursor=SimpleNamespace(has_more=False, continuation_supported=True),
    )

    async def collect():
        return [page async for page in backend.execute_pages(prepared)]

    with pytest.raises(RuntimeError, match="rebuild"):
        asyncio.run(collect()) if async_mode else list(backend.execute_pages(prepared))
    forbidden.assert_not_called()
