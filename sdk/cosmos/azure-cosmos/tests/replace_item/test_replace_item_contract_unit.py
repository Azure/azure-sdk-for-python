# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline replacement checks through the public sync and async clients."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pytest

from azure.cosmos import _operation_deadline
from azure.cosmos.container import ContainerProxy
from azure.cosmos.aio._container import ContainerProxy as AsyncContainerProxy
from azure.cosmos._backend import rust_backend as sync_rust
from azure.cosmos.aio._backend import rust_backend as async_rust
from azure.cosmos._helpers import _item_prep
from azure.cosmos._helpers._item_context import ItemClientContext
from azure.core import MatchConditions
from azure.cosmos.exceptions import (
    CosmosAccessConditionFailedError, CosmosClientTimeoutError, CosmosResourceNotFoundError,
)


@pytest.fixture(params=[False, True], ids=["sync", "async"])
def replacement(request, monkeypatch):
    asynchronous = request.param
    clock = SimpleNamespace(now=100.0)
    clock.monotonic = lambda: clock.now
    monkeypatch.setattr(_item_prep, "time", clock)
    monkeypatch.setattr(_operation_deadline, "time", clock)
    context = SimpleNamespace(
        clock=clock, initialization_delay=0, native_error=None, status=200,
        body=b'{"id":"order-42","tenant":"northwind"}',
        headers={"etag": '"new"', "x-ms-request-charge": "5.25"},
    )

    def initialize():
        clock.now += context.initialization_delay
        return "replacement-test"

    def replace(_handle, prepared, *, timeout_seconds=None):
        context.prepared = prepared
        context.remaining = timeout_seconds
        if context.native_error:
            raise context.native_error
        return context.status, 0, context.headers, context.body, None

    wrap = AsyncMock if asynchronous else MagicMock
    native_call = wrap(side_effect=replace)
    binding = SimpleNamespace(replace_item=native_call, replace_item_async=native_call)
    module = async_rust if asynchronous else sync_rust
    monkeypatch.setattr(module, "_rust_module", binding)
    backend_type = async_rust.AsyncRustBackend if asynchronous else sync_rust.RustBackend
    backend = backend_type("https://replacement.invalid", master_key="ZmFrZQ==")
    initialize_call = wrap(side_effect=initialize)
    monkeypatch.setattr(backend, "_ensure_driver_handle", initialize_call)
    connection = MagicMock()
    connection._backend = backend
    proxy = (AsyncContainerProxy if asynchronous else ContainerProxy)(
        connection, "dbs/sales", "orders", _item_context=ItemClientContext(backend)
    )

    def call(body=None, *, item="order-42", **kwargs):
        result = proxy.replace_item(
            item,
            body if body is not None else {"id": "order-42", "tenant": "northwind"},
            **kwargs,
        )
        return asyncio.run(result) if asynchronous else result

    context.call = call
    context.native_call = native_call
    context.initialize_call = initialize_call
    yield context
    if asynchronous:
        asyncio.run(backend.close())
    else:
        backend.close()


@pytest.mark.parametrize("source", ["keyword", "request_options", "feed_options"])
def test_replace_passes_only_remaining_timeout(replacement, source):
    replacement.initialization_delay = 2
    kwargs = {"timeout": 5} if source == "keyword" else {source: {"timeout": 5}}
    replacement.call(**kwargs)
    assert replacement.remaining == 3
    assert kwargs == ({"timeout": 5} if source == "keyword" else {source: {"timeout": 5}})


def test_expired_initialization_does_not_send_replacement(replacement):
    replacement.initialization_delay = 6
    with pytest.raises(CosmosClientTimeoutError):
        replacement.call(timeout=5)
    replacement.native_call.assert_not_called()


def test_native_timeout_uses_public_timeout_exception_without_success_hook(replacement):
    replacement.native_error = TimeoutError("metadata exhausted the budget")
    hook = MagicMock()
    with pytest.raises(CosmosClientTimeoutError):
        replacement.call(timeout=5, response_hook=hook)
    hook.assert_not_called()


@pytest.mark.parametrize("item_id", ["bad/id", "bad\\id", "bad#id", "bad?id", "trailing ", 42])
def test_invalid_body_id_is_rejected_before_driver_acquisition(replacement, item_id):
    with pytest.raises((TypeError, ValueError)):
        replacement.call(body={"id": item_id, "tenant": "northwind"})
    replacement.initialize_call.assert_not_called()
    replacement.native_call.assert_not_called()


def test_valid_body_id_is_not_used_to_retarget_replacement(replacement):
    replacement.call(body={"id": "different-order", "tenant": "northwind"})
    assert replacement.prepared.item_id == "order-42"
    assert b'"id":"different-order"' in replacement.prepared.body_bytes


def test_dictionary_target_preserves_self_link_not_just_customer_id(replacement):
    item = {
        "id": "order-42",
        "_self": "dbs/AQAAAA==/colls/AQAAAIABAAA=/docs/AQAAAIABAAABAAAAAAAAAA==/",
    }
    replacement.call(item=item)
    assert replacement.prepared.item_self_link == item["_self"]
    assert replacement.prepared.item_id == item["id"]


def test_dictionary_target_without_self_link_is_still_rejected(replacement):
    with pytest.raises(KeyError, match="_self"):
        replacement.call(item={"id": "order-42"})
    replacement.native_call.assert_not_called()


@pytest.mark.parametrize("self_link", [None, 42])
def test_invalid_self_link_never_falls_back_to_customer_id(replacement, self_link):
    with pytest.raises(TypeError, match="_self"):
        replacement.call(item={"id": "order-42", "_self": self_link})
    replacement.initialize_call.assert_not_called()


@pytest.mark.parametrize("entry_point", ["replace_item", "replace_item_async"])
def test_native_replacement_rejects_invalid_address_before_driver_lookup(replacement, entry_point):
    binding = pytest.importorskip("azure.cosmos._rust")
    replacement.call(item={"id": "order-42", "_self": "not-an-item-address"})
    with pytest.raises(ValueError, match="target _self must identify"):
        getattr(binding, entry_point)(
            "unregistered-test-handle", replacement.prepared, timeout_seconds=0.5
        )


@pytest.mark.parametrize(
    ("status", "exception"),
    [(404, CosmosResourceNotFoundError), (412, CosmosAccessConditionFailedError)],
)
def test_service_failure_preserves_message_headers_and_skips_success_hook(replacement, status, exception):
    replacement.status = status
    replacement.body = b'{"code":"ServiceFailure","message":"Original service explanation"}'
    hook = MagicMock()
    with pytest.raises(exception) as raised:
        replacement.call(response_hook=hook)
    assert raised.value.status_code == status
    assert "Original service explanation" in str(raised.value)
    assert raised.value.headers["x-ms-request-charge"] == "5.25"
    hook.assert_not_called()
    assert replacement.native_call.call_count == 1


def test_no_response_retains_headers_and_invokes_hook_once(replacement):
    replacement.body = b""
    hook = MagicMock()
    result = replacement.call(no_response=True, response_hook=hook)
    assert result == {}
    assert result.get_response_headers()["etag"] == '"new"'
    assert replacement.prepared.settings.no_response is True
    hook.assert_called_once()
    assert hook.call_args.args[1] == {}


def test_conditional_replacement_keeps_customer_etag(replacement):
    replacement.call(etag='"previous"', match_condition=MatchConditions.IfNotModified)
    assert replacement.prepared.settings.item.if_match == '"previous"'


def test_hook_failure_does_not_replay_replacement(replacement):
    failure = ValueError("customer hook failed")
    hook = MagicMock(side_effect=failure)
    with pytest.raises(ValueError) as raised:
        replacement.call(response_hook=hook)
    assert raised.value is failure
    assert replacement.native_call.call_count == 1
