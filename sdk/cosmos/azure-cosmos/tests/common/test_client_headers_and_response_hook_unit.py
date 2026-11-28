# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Tests for request headers and response hooks set on the client and on each call.

Terms used in this file:

- compiled module: ``azure.cosmos._rust``, the compiled part of the SDK that
  sends requests.
- adapter: the object the client uses to call the compiled module.
- handle: the adapter's link to a connection in the compiled module, opened on
  the first request.

The compiled module's read function is replaced with a fake, so the tests check
the headers the SDK hands to the compiled module, not what reaches the network.
"""

import asyncio
import importlib
from unittest.mock import AsyncMock, Mock

import pytest
from azure.core.utils import CaseInsensitiveDict

from common.test_connection_policy_unit import client_module  # pylint: disable=unused-import


@pytest.mark.parametrize("from_connection_string", [False, True])
def test_read_item_uses_client_headers_call_headers_and_call_response_hook(
    client_module, monkeypatch, from_connection_string,
):
    """Headers given to the client are used for every request, as they were when
    the client was created; changing the dict afterwards has no effect.

    Headers given to one call are added for that call only, and replace a client
    header with the same name, whatever its letter case. A header value that is
    not a string, such as 5, is turned into text. The caller's dict is not
    changed.

    A ``response_hook`` given to the call is called once, with the response
    headers and the item. A ``response_hook`` given to the client is not called
    for item reads. This is checked for a client created from a URL and key, and
    from a connection string.
    """
    client_headers = {"X-Alpha-App": "orders", "x-alpha-run": "normal"}
    constructor_hook = Mock()
    client_options = {"_backend": "rust", "headers": client_headers, "response_hook": constructor_hook}
    if from_connection_string:
        client = client_module.CosmosClient.from_connection_string(
            "AccountEndpoint=https://headers.invalid;AccountKey=ZmFrZQ==;", **client_options
        )
    else:
        client = client_module.CosmosClient("https://headers.invalid", "ZmFrZQ==", **client_options)
    asynchronous = ".aio." in client_module.__name__
    compiled_module = importlib.import_module(type(client._adapter).__module__)._rust_module
    # The headers the compiled module received, one entry per request.
    headers_received = []
    response_headers = {"x-ms-request-charge": "2.5", "x-ms-activity-id": "read-activity"}

    def fake_read_item(_handle, request, **_kwargs):
        headers_received.append(CaseInsensitiveDict(request.headers))
        return 200, 0, response_headers.copy(), b'{"id":"order-42","customerId":"customer-17"}', None

    async def fake_read_item_async(*args, **kwargs):
        return fake_read_item(*args, **kwargs)

    monkeypatch.setattr(compiled_module, "read_item_async" if asynchronous else "read_item",
                        fake_read_item_async if asynchronous else fake_read_item)
    # Return a fake handle instead of opening a real one.
    monkeypatch.setattr(
        client._adapter, "_ensure_driver_handle",
        AsyncMock(return_value="fake-handle") if asynchronous else Mock(return_value="fake-handle"),
    )
    # Changing the dict after the client is created must not change the headers used.
    client_headers["X-Alpha-App"] = "changed-after-construction"
    call_headers = {"X-ALPHA-RUN": "comparison", "x-call-only": "once", "x-call-number": 5}
    call_hook = Mock()
    container = client.get_database_client("sales").get_container_client("orders")

    async def run_async():
        try:
            first_read = await container.read_item(
                "order-42", partition_key="customer-17",
                initial_headers=call_headers, response_hook=call_hook,
            )
            second_read = await container.read_item("order-42", partition_key="customer-17")
            return first_read, second_read
        finally:
            await client.close()

    if asynchronous:
        first_read, second_read = asyncio.run(run_async())
    else:
        try:
            first_read = container.read_item(
                "order-42", partition_key="customer-17",
                initial_headers=call_headers, response_hook=call_hook,
            )
            second_read = container.read_item("order-42", partition_key="customer-17")
        finally:
            client.close()

    assert first_read["id"] == second_read["id"] == "order-42"
    assert len(headers_received) == 2
    assert headers_received[0]["x-alpha-app"] == headers_received[1]["x-alpha-app"] == "orders"
    assert headers_received[0]["x-alpha-run"] == "comparison"
    assert headers_received[0]["x-call-only"] == "once"
    assert headers_received[0]["x-call-number"] == "5"
    assert headers_received[1]["x-alpha-run"] == "normal"
    assert "x-call-only" not in headers_received[1]
    assert call_headers == {"X-ALPHA-RUN": "comparison", "x-call-only": "once", "x-call-number": 5}
    constructor_hook.assert_not_called()
    call_hook.assert_called_once()
    hook_headers, hook_body = call_hook.call_args.args
    assert hook_headers["x-ms-request-charge"] == first_read.get_response_headers()["x-ms-request-charge"]
    assert hook_headers["x-ms-activity-id"] == first_read.get_response_headers()["x-ms-activity-id"]
    assert hook_body == first_read


@pytest.mark.parametrize("name", [5, None, b"x-customer"])
@pytest.mark.parametrize("source", ["initial_headers", "request_options", "feed_options"])
def test_non_string_header_name_raises_before_opening_a_handle(
    client_module, monkeypatch, name, source,
):
    """A header name that is not a string (5, None or bytes) raises TypeError
    before the SDK opens a handle.

    This is checked when the header is passed as ``initial_headers``, and as
    ``initialHeaders`` inside the ``request_options`` or ``feed_options``
    keyword. The caller's dict is not changed.
    """
    client = client_module.CosmosClient("https://headers.invalid", "ZmFrZQ==", _backend="rust")
    assert client._adapter.name == "rust"
    asynchronous = ".aio." in client_module.__name__
    # Fails the test if the SDK tries to open a handle.
    open_handle = (AsyncMock if asynchronous else Mock)(side_effect=AssertionError("a handle was opened"))
    monkeypatch.setattr(client._adapter, "_ensure_driver_handle", open_handle)
    container = client.get_database_client("sales").get_container_client("orders")
    headers = {name: "value"}
    call_options = {source: headers if source == "initial_headers" else {"initialHeaders": headers}}

    async def run_async():
        try:
            with pytest.raises(TypeError, match="Request header names must be strings"):
                await container.read_item("order-42", partition_key="customer-17", **call_options)
        finally:
            await client.close()

    if asynchronous:
        asyncio.run(run_async())
    else:
        try:
            with pytest.raises(TypeError, match="Request header names must be strings"):
                container.read_item("order-42", partition_key="customer-17", **call_options)
        finally:
            client.close()
    open_handle.assert_not_called()
    assert headers == {name: "value"}
