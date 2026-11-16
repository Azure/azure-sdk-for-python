# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check client defaults at the Python-to-binding boundary, not on the wire."""

import asyncio
import importlib
from unittest.mock import AsyncMock, Mock

import pytest
from azure.core.utils import CaseInsensitiveDict

from common.test_connection_policy_unit import client_module  # pylint: disable=unused-import


@pytest.mark.parametrize("from_connection_string", [False, True])
def test_client_headers_and_call_hooks_reach_binding_without_inheriting_constructor_hook(
    client_module, monkeypatch, from_connection_string,
):
    defaults = {"X-Alpha-App": "orders", "x-alpha-run": "normal"}
    constructor_hook = Mock()
    kwargs = {"_backend": "rust", "headers": defaults, "response_hook": constructor_hook}
    if from_connection_string:
        client = client_module.CosmosClient.from_connection_string(
            "AccountEndpoint=https://headers.invalid;AccountKey=ZmFrZQ==;", **kwargs
        )
    else:
        client = client_module.CosmosClient("https://headers.invalid", "ZmFrZQ==", **kwargs)
    asynchronous = ".aio." in client_module.__name__
    binding = importlib.import_module(type(client._adapter).__module__)._rust_module
    sent = []
    response_headers = {"x-ms-request-charge": "2.5", "x-ms-activity-id": "read-activity"}

    def read(_handle, prepared, **_kwargs):
        sent.append(CaseInsensitiveDict(prepared.headers))
        return 200, 0, response_headers.copy(), b'{"id":"order-42","customerId":"customer-17"}', None

    async def async_read(*args, **kwargs):
        return read(*args, **kwargs)

    monkeypatch.setattr(binding, "read_item_async" if asynchronous else "read_item",
                        async_read if asynchronous else read)
    monkeypatch.setattr(
        client._adapter, "_ensure_driver_handle",
        AsyncMock(return_value="mock-handle") if asynchronous else Mock(return_value="mock-handle"),
    )
    defaults["X-Alpha-App"] = "changed-after-construction"
    call_headers = {"X-ALPHA-RUN": "comparison", "x-call-only": "once"}
    call_hook = Mock()
    container = client.get_database_client("sales").get_container_client("orders")

    async def run_async():
        try:
            first = await container.read_item(
                "order-42", partition_key="customer-17",
                initial_headers=call_headers, response_hook=call_hook,
            )
            second = await container.read_item("order-42", partition_key="customer-17")
            return first, second
        finally:
            await client.close()

    if asynchronous:
        first, second = asyncio.run(run_async())
    else:
        try:
            first = container.read_item(
                "order-42", partition_key="customer-17",
                initial_headers=call_headers, response_hook=call_hook,
            )
            second = container.read_item("order-42", partition_key="customer-17")
        finally:
            client.close()

    assert first["id"] == second["id"] == "order-42"
    assert len(sent) == 2
    assert sent[0]["x-alpha-app"] == sent[1]["x-alpha-app"] == "orders"
    assert sent[0]["x-alpha-run"] == "comparison"
    assert sent[0]["x-call-only"] == "once"
    assert sent[1]["x-alpha-run"] == "normal"
    assert "x-call-only" not in sent[1]
    assert call_headers == {"X-ALPHA-RUN": "comparison", "x-call-only": "once"}
    constructor_hook.assert_not_called()
    call_hook.assert_called_once()
    hook_headers, hook_body = call_hook.call_args.args
    assert hook_headers["x-ms-request-charge"] == first.get_response_headers()["x-ms-request-charge"]
    assert hook_headers["x-ms-activity-id"] == first.get_response_headers()["x-ms-activity-id"]
    assert hook_body == first
