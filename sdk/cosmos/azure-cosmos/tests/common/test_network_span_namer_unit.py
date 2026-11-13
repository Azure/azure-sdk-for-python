# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Reject unsupported request callbacks before Rust work, without probing them."""

import asyncio
import inspect
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from azure.cosmos._backend.capabilities import prepare_operation_kwargs, reject_rust_arguments
from common.test_connection_policy_unit import client_module, construct_client  # pylint: disable=unused-import

ERROR = "network_span_namer is not supported by Rust-backed APIs"


@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("selection", ["keyword", "environment"])
@pytest.mark.parametrize("supplied_none", [False, True])
@pytest.mark.parametrize("tracing_enabled", [False, True])
def test_constructor_rejects_namer_before_backend_creation(
    client_module, monkeypatch, from_connection_string, selection, supplied_none, tracing_enabled
):
    callback = Mock(side_effect=AssertionError("Callback must not be probed"))
    backend_factory = Mock(side_effect=AssertionError("Backend must not be constructed"))
    connection = Mock(side_effect=AssertionError("Legacy connection must not be constructed"))
    asynchronous = ".aio." in client_module.__name__
    monkeypatch.setattr(client_module, "make_async_backend" if asynchronous else "make_backend", backend_factory)
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    monkeypatch.setenv("COSMOS_BACKEND", "rust" if selection == "environment" else "core-python")
    kwargs = {
        "network_span_namer": None if supplied_none else callback,
        "tracing_options": {"enabled": tracing_enabled},
    }
    if selection == "keyword":
        kwargs["_backend"] = "rust"
    with pytest.raises(TypeError, match=ERROR):
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://naming.invalid;AccountKey=ZmFrZQ==;", **kwargs
            )
        else:
            client_module.CosmosClient("https://naming.invalid", "ZmFrZQ==", **kwargs)
    callback.assert_not_called()
    backend_factory.assert_not_called()
    connection.assert_not_called()


@pytest.fixture
def native(client_module, monkeypatch):
    client = client_module.CosmosClient("https://naming.invalid", "ZmFrZQ==", _backend="rust")
    asynchronous = ".aio." in client_module.__name__
    acquire = (AsyncMock if asynchronous else Mock)(side_effect=AssertionError("Unexpected driver acquisition"))
    execute = (AsyncMock if asynchronous else Mock)(side_effect=AssertionError("Unexpected execution"))
    execute_pages = Mock(side_effect=AssertionError("Unexpected paging"))
    monkeypatch.setattr(client._adapter, "_ensure_driver_handle", acquire)
    monkeypatch.setattr(client._adapter, "execute", execute)
    monkeypatch.setattr(client._adapter, "execute_pages", execute_pages)
    database = client.get_database_client("sales")
    container = database.get_container_client("orders")
    try:
        yield SimpleNamespace(
            client=client,
            database=database,
            container=container,
            acquire=acquire,
            execute=execute,
            execute_pages=execute_pages,
        )
    finally:
        result = client.close()
        if asynchronous:
            asyncio.run(result)


@pytest.mark.parametrize("location", ["keyword", "request_options", "feed_options"])
@pytest.mark.parametrize(
    "target,args",
    [
        ("container.read_item", ("order-42",)),
        ("container.create_item", ({"id": "order-42", "customerId": "customer-17"},)),
        ("database.read", ()),
        ("client.create_database", ("sales",)),
        ("client.create_database_if_not_exists", ("sales",)),
        ("container.read_all_items", ()),
        ("container.query_items", ("SELECT * FROM c",)),
        ("container.query_items_change_feed", ()),
        ("client.list_databases", ()),
        ("client.query_databases", ("SELECT * FROM c",)),
        ("database.list_containers", ()),
        ("database.query_containers", ("SELECT * FROM c",)),
    ],
)
def test_public_operations_reject_namer_before_work(native, location, target, args):
    callback = Mock(side_effect=AssertionError("Callback must not be probed"))
    options = {"network_span_namer": callback}
    kwargs = options if location == "keyword" else {location: options}
    kwargs = dict(kwargs, tracing_options={"enabled": False})
    if target == "container.read_item":
        kwargs["partition_key"] = "customer-17"
    owner, operation = target.split(".")
    call = getattr(getattr(native, owner), operation)
    with pytest.raises(TypeError, match=ERROR):
        result = call(*args, **kwargs)
        if inspect.isawaitable(result):
            asyncio.run(result)
    callback.assert_not_called()
    native.acquire.assert_not_called()
    native.execute.assert_not_called()
    native.execute_pages.assert_not_called()
    assert options["network_span_namer"] is callback


@pytest.mark.parametrize("from_connection_string", [False, True])
def test_core_python_constructor_retains_callback(construct_client, client_module, from_connection_string):
    callback = Mock(return_value="orders-get")
    construct_client(
        _backend="core-python",
        network_span_namer=callback,
        from_connection_string=from_connection_string,
    )
    assert client_module.CosmosClientConnection.call_args.kwargs["network_span_namer"] is callback
    callback.assert_not_called()


def test_core_python_operation_preserves_callback_and_rust_omission_is_supported():
    callback = Mock(return_value="orders-get")
    kwargs = {"network_span_namer": callback}
    legacy = SimpleNamespace(_item_context=SimpleNamespace(adapter=SimpleNamespace(name="core-python")))
    prepare_operation_kwargs(legacy, kwargs)
    assert kwargs == {"network_span_namer": callback}
    callback.assert_not_called()
    reject_rust_arguments({})
    reject_rust_arguments({"tracing_attributes": {"bank.component": "orders"}, "tracing_options": {"enabled": True}})


@pytest.mark.parametrize("value", [None, False, "orders-get"])
@pytest.mark.parametrize("location", ["keyword", "request_options", "feed_options"])
def test_rejection_depends_on_keyword_presence_not_value(value, location):
    options = {"network_span_namer": value}
    kwargs = options if location == "keyword" else {location: options}
    with pytest.raises(TypeError, match=ERROR):
        reject_rust_arguments(kwargs)
