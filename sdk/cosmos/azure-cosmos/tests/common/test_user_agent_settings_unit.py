# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Reject unsupported User-Agent controls without changing the legacy path."""

import asyncio
import inspect
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from azure.cosmos._backend.capabilities import prepare_operation_kwargs, reject_rust_arguments
from common.test_connection_policy_unit import client_module, construct_client  # pylint: disable=unused-import
from common.test_network_span_namer_unit import native  # pylint: disable=unused-import


UNSUPPORTED_SETTINGS = [
    ("user_agent", "alpha-orders"),
    ("user_agent", ""),
    ("user_agent", None),
    ("user_agent_overwrite", True),
    ("user_agent_overwrite", False),
    ("user_agent_overwrite", None),
    ("user_agent_use_env", True),
    ("user_agent_use_env", False),
    ("user_agent_use_env", None),
]


@pytest.mark.parametrize("name,value", UNSUPPORTED_SETTINGS)
@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("selection", ["keyword", "environment"])
def test_constructor_rejects_user_agent_controls_before_backend_creation(
    client_module, monkeypatch, name, value, from_connection_string, selection
):
    backend_factory = Mock(side_effect=AssertionError("Backend must not be constructed"))
    connection = Mock(side_effect=AssertionError("Legacy connection must not be constructed"))
    asynchronous = ".aio." in client_module.__name__
    monkeypatch.setattr(client_module, "make_async_backend" if asynchronous else "make_backend", backend_factory)
    monkeypatch.setattr(client_module, "CosmosClientConnection", connection)
    monkeypatch.delenv("COSMOS_BACKEND", raising=False)
    kwargs = {name: value}
    if selection == "keyword":
        monkeypatch.setenv("COSMOS_BACKEND", "core-python")
        kwargs["_backend"] = "rust"
    elif selection == "environment":
        monkeypatch.setenv("COSMOS_BACKEND", "rust")

    with pytest.raises(TypeError, match=f"{name} is not supported by Rust-backed APIs") as error:
        if from_connection_string:
            client_module.CosmosClient.from_connection_string(
                "AccountEndpoint=https://user-agent.invalid;AccountKey=ZmFrZQ==;", **kwargs
            )
        else:
            client_module.CosmosClient("https://user-agent.invalid", "ZmFrZQ==", **kwargs)
    assert "user_agent_suffix" in str(error.value)
    backend_factory.assert_not_called()
    connection.assert_not_called()
    assert kwargs[name] is value


@pytest.mark.parametrize("name,value", UNSUPPORTED_SETTINGS)
@pytest.mark.parametrize("location", ["keyword", "request_options", "feed_options"])
def test_user_agent_rejection_depends_on_presence_and_preserves_core_python_options(name, value, location):
    options = {name: value}
    kwargs = options if location == "keyword" else {location: options}
    with pytest.raises(TypeError, match=f"{name} is not supported by Rust-backed APIs"):
        reject_rust_arguments(kwargs)

    legacy = SimpleNamespace(_item_context=SimpleNamespace(adapter=SimpleNamespace(name="core-python")))
    prepare_operation_kwargs(legacy, kwargs)
    assert options == {name: value}
    if location != "keyword":
        assert kwargs[location] is options


@pytest.mark.parametrize("name", ["user_agent", "user_agent_overwrite", "user_agent_use_env"])
@pytest.mark.parametrize("operation,args", [("read_item", ("order-42",)), ("read_all_items", ())])
def test_public_operations_reject_user_agent_before_work(native, name, operation, args):
    kwargs = {name: None}
    if operation == "read_item":
        kwargs["partition_key"] = "customer-17"
    with pytest.raises(TypeError, match=f"{name} is not supported by Rust-backed APIs"):
        result = getattr(native.container, operation)(*args, **kwargs)
        if inspect.isawaitable(result):
            asyncio.run(result)
    native.acquire.assert_not_called()
    native.execute.assert_not_called()
    native.execute_pages.assert_not_called()


@pytest.mark.parametrize("name,value", UNSUPPORTED_SETTINGS)
@pytest.mark.parametrize("from_connection_string", [False, True])
@pytest.mark.parametrize("backend", ["core-python", None])
def test_core_python_constructor_retains_user_agent_controls(
    construct_client, client_module, name, value, from_connection_string, backend
):
    construct_client(
        _backend=backend,
        from_connection_string=from_connection_string,
        **{name: value},
    )
    assert client_module.CosmosClientConnection.call_args.kwargs[name] is value


@pytest.mark.parametrize("suffix", [None, "", "alpha-orders"])
@pytest.mark.parametrize("from_connection_string", [False, True])
def test_rust_constructor_preserves_supported_suffix(construct_client, monkeypatch, suffix, from_connection_string):
    monkeypatch.setenv("AZURE_HTTP_USER_AGENT", "alpha-platform")
    client, _ = construct_client(user_agent_suffix=suffix, from_connection_string=from_connection_string)
    config = client._adapter._client_config
    if suffix:
        assert config.user_agent_suffix == suffix
    else:
        assert config is None
    reject_rust_arguments({})
