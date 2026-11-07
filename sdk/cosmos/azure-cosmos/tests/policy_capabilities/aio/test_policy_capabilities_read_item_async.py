# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Live client-policy capabilities of a Rust-backed async ``read_item``."""

import importlib
import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient
from common._rust_checks import run_on_rust_async

HEADER = "x-alpha-bank-operation-id"


@pytest.fixture(scope="module")
def saved_order():
    """Own a database holding one order that every test reads; the database is deleted afterwards."""
    with SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("policy_caps_aio_" + uuid.uuid4().hex)
        try:
            container = database.create_container("orders", partition_key=PartitionKey(path="/customerId"))
            order = container.create_item({"id": "order-42", "customerId": "customer-17", "status": "paid"})
            yield database.id, dict(order)
        finally:
            client.delete_database(database.id)


def _capture_prepared_headers(client, monkeypatch):
    binding = importlib.import_module(type(client._adapter).__module__)._rust_module
    original = binding.read_item_async
    captured = []

    async def execute(driver_handle, prepared, **kwargs):
        captured.append(dict(prepared.headers))
        return await original(driver_handle, prepared, **kwargs)

    monkeypatch.setattr(binding, "read_item_async", execute)
    return captured


@pytest.mark.asyncio
@pytest.mark.parametrize("scope", ["client_default", "per_call"])
async def test_read_sends_custom_application_header_on_request_async_rust(saved_order, scope, monkeypatch):
    """A custom header set as a client default or per call is sent on the async item read request.

    The read goes through the Rust binding without falling back and returns the stored order.
    """
    database_id, expected = saved_order
    client_kwargs = {"headers": {HEADER: "read-order-42"}} if scope == "client_default" else {}
    call_kwargs = {"initial_headers": {HEADER: "read-order-42"}} if scope == "per_call" else {}
    async with CosmosClient(
        os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust", **client_kwargs,
    ) as client:
        container = client.get_database_client(database_id).get_container_client("orders")
        captured = _capture_prepared_headers(client, monkeypatch)
        result = await run_on_rust_async(client, lambda: container.read_item(
            "order-42", partition_key="customer-17", **call_kwargs,
        ))

    assert dict(result) == expected
    assert captured, "The item read did not prepare a request"
    assert all(headers.get(HEADER) == "read-order-42" for headers in captured), captured


def test_async_client_with_network_span_namer_is_rejected_at_construction_async_rust():
    """Constructing an async client with network_span_namer raises TypeError because Rust cannot honor it."""
    with pytest.raises(TypeError, match="network_span_namer is not supported by Rust-backed APIs"):
        CosmosClient(
            os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust",
            network_span_namer=lambda request: "alpha-bank-http",
            tracing_attributes={"alpha_bank.operation": "read-order-42"},
        )
