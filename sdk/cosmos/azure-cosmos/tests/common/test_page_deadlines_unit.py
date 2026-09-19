# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Shared page arguments, results and errors preserve sync/async behavior."""
import asyncio
import time
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos._backend import binding as sync_rust
from azure.cosmos.aio._backend import binding as async_rust
from azure.cosmos._backend.contracts import PreparedQuery
from azure.cosmos._backend.operations import STATELESS_QUERY_TO_BINDING_METHOD, CURSOR_QUERY_TO_BINDING_METHOD
from azure.cosmos._backend.binding import build_binding_request_from_page
from azure.cosmos.exceptions import CosmosClientTimeoutError


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("budget", ["none", "future", "expired"])
@pytest.mark.parametrize("uses_cursor,op,method", [
    (cursor, op, method)
    for cursor, methods in ((False, STATELESS_QUERY_TO_BINDING_METHOD), (True, CURSOR_QUERY_TO_BINDING_METHOD))
    for op, method in methods.items()
])
def test_every_page_dispatch_preserves_cursor_and_deadline_arguments(
    monkeypatch, async_mode, budget, uses_cursor, op, method
):
    module = async_rust if async_mode else sync_rust
    cls = module.AsyncRustBinding if async_mode else module.RustBinding
    backend = object.__new__(cls)
    acquire = AsyncMock(return_value="handle") if async_mode else MagicMock(return_value="handle")
    monkeypatch.setattr(backend, "_ensure_driver_handle", acquire)
    response = (206, 7, {"x-ms-continuation": "next", "x-custom": "value"}, b"{}", {"elapsed": 2})
    dispatch = (AsyncMock if async_mode else MagicMock)(return_value=response)
    monkeypatch.setattr(module, "_rust_module", SimpleNamespace(
        **{method + ("_async" if async_mode else ""): dispatch}
    ))
    prepared = PreparedQuery(
        op=op, container_link="dbs/d/colls/c", query="SELECT * FROM c", change_feed={},
        cursor=SimpleNamespace(has_more=False, continuation_supported=True) if uses_cursor else None,
    )
    deadline = None if budget == "none" else time.monotonic() + (-1 if budget == "expired" else 10)

    async def collect():
        return [page async for page in backend.execute_pages(prepared, deadline=deadline)]

    def run():
        return asyncio.run(collect()) if async_mode else list(backend.execute_pages(prepared, deadline=deadline))

    if budget == "expired":
        with pytest.raises(CosmosClientTimeoutError):
            run()
        dispatch.assert_not_called()
    else:
        pages = run()
        assert len(pages) == 1
        page = pages[0]
        assert (page.status_code, page.sub_status, page.body, page.diagnostics) == (
            206, 7, b"{}", {"elapsed": 2}
        )
        assert page.continuation == "next"
        assert page.headers["x-custom"] == "value"
        assert page.has_more is (False if uses_cursor and op == "query_items" else None)
        assert page.continuation_supported is True
        args, kwargs = dispatch.call_args
        assert args[0] == "handle"
        assert args[1].op == op
        assert len(args) == (3 if uses_cursor else 2)
        if uses_cursor:
            assert args[2] is prepared.cursor
        if deadline is not None:
            assert 0 < kwargs["timeout_seconds"] <= 10
        else:
            assert kwargs == ({"timeout_seconds": None} if uses_cursor else {})


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("has_deadline", [False, True])
@pytest.mark.parametrize("error_kind", ["timeout", "unsupported", "transport", "cancelled"])
def test_page_error_translation_preserves_cause_and_cancellation(
    monkeypatch, async_mode, has_deadline, error_kind
):
    from azure.core.exceptions import ServiceResponseError
    from azure.cosmos._backend.errors import UnsupportedQueryError

    class NativeUnsupportedQueryError(Exception):
        pass

    class TransportError(Exception):
        pass

    error = {
        "timeout": TimeoutError,
        "unsupported": NativeUnsupportedQueryError,
        "transport": TransportError,
        "cancelled": asyncio.CancelledError,
    }[error_kind]("page dispatch failed")
    module = async_rust if async_mode else sync_rust
    backend = object.__new__(module.AsyncRustBinding if async_mode else module.RustBinding)
    mock = AsyncMock if async_mode else MagicMock
    monkeypatch.setattr(backend, "_ensure_driver_handle", mock(return_value="handle"))
    dispatch = mock(side_effect=error)
    method = "list_databases_async" if async_mode else "list_databases"
    monkeypatch.setattr(module, "_rust_module", SimpleNamespace(**{method: dispatch}))
    monkeypatch.setattr(module, "_UNSUPPORTED_QUERY_ERROR", NativeUnsupportedQueryError)
    monkeypatch.setattr(module, "_DRIVER_TRANSPORT_ERROR", TransportError)
    prepared = PreparedQuery(op="list_databases", container_link="")
    deadline = time.monotonic() + 10 if has_deadline else None
    expected = {
        "timeout": CosmosClientTimeoutError if has_deadline else TimeoutError,
        "unsupported": UnsupportedQueryError,
        "transport": ServiceResponseError,
        "cancelled": asyncio.CancelledError,
    }[error_kind]

    async def collect():
        return [page async for page in backend.execute_pages(prepared, deadline=deadline)]

    with pytest.raises(expected) as caught:
        if async_mode:
            asyncio.run(collect())
        else:
            list(backend.execute_pages(prepared, deadline=deadline))
    if error_kind == "cancelled" or (error_kind == "timeout" and not has_deadline):
        assert caught.value is error
    else:
        assert caught.value.__cause__ is error
    assert dispatch.call_count == 1


def test_async_page_cancellation_reaches_pending_native_await(monkeypatch):
    backend = object.__new__(async_rust.AsyncRustBinding)
    monkeypatch.setattr(backend, "_ensure_driver_handle", AsyncMock(return_value="handle"))

    async def run():
        entered, stopped = asyncio.Event(), asyncio.Event()

        async def dispatch(*args, **kwargs):
            entered.set()
            try:
                await asyncio.Future()
            finally:
                stopped.set()

        monkeypatch.setattr(async_rust, "_rust_module", SimpleNamespace(list_databases_async=dispatch))
        pages = backend.execute_pages(PreparedQuery(op="list_databases", container_link=""))
        pending = asyncio.create_task(pages.__anext__())
        try:
            await asyncio.wait_for(entered.wait(), timeout=1)
            pending.cancel()
            with pytest.raises(asyncio.CancelledError):
                await pending
            assert stopped.is_set()
        finally:
            pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)
            await pages.aclose()

    asyncio.run(run())


@pytest.mark.parametrize("async_mode", [False, True])
@pytest.mark.parametrize("op,method", list(STATELESS_QUERY_TO_BINDING_METHOD.items()))
def test_native_page_entry_validates_timeout_before_driver_lookup(op, method, async_mode):
    from azure.cosmos import _rust

    link = "" if "databases" in op else "dbs/d" if "containers" in op else "dbs/d/colls/c"
    prepared = build_binding_request_from_page(
        PreparedQuery(op=op, container_link=link, query="SELECT * FROM c")
    )
    call = getattr(_rust, method + ("_async" if async_mode else ""))
    with pytest.raises(ValueError, match="timeout_seconds"):
        call("unregistered-driver", prepared, timeout_seconds=0)
