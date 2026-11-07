# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async conditional (etag + match_condition) ``delete_item`` behavior on the Rust backend."""

import os
import uuid
import warnings

import pytest
import pytest_asyncio

from azure.core import MatchConditions
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import CosmosAccessConditionFailedError, CosmosResourceNotFoundError
from common._rust_checks import assert_rust_client, run_on_rust_async
from config.diagnostics import _binding_operation_count


@pytest_asyncio.fixture
async def container():
    """Yield an async Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = await client.create_database("delete_conditions_aio_" + uuid.uuid4().hex)
        try:
            yield client, await database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            await client.delete_database(database.id)


@pytest.mark.asyncio
async def test_delete_with_stale_etag_if_not_modified_raises_precondition_failed_async_rust(container):
    """Async delete with an outdated etag and IfNotModified fails with 412 and keeps the item.

    The item is changed after its etag is captured, so the service rejects the optimistic-concurrency
    delete and the SDK raises the typed precondition error.
    """
    client, orders = container
    item_id = uuid.uuid4().hex
    stale_etag = (await orders.create_item({"id": item_id, "pk": "a"}))["_etag"]
    await orders.upsert_item({"id": item_id, "pk": "a", "bumped": True})

    with pytest.raises(CosmosAccessConditionFailedError) as caught:
        await run_on_rust_async(client, lambda: orders.delete_item(
            item_id, partition_key="a", etag=stale_etag, match_condition=MatchConditions.IfNotModified,
        ))
    assert caught.value.status_code == 412
    assert (await orders.read_item(item_id, partition_key="a"))["bumped"] is True


@pytest.mark.asyncio
async def test_delete_with_current_etag_if_not_modified_succeeds_without_warning_async_rust(container):
    """Async delete with the current etag and IfNotModified removes the item and emits no DeprecationWarning.

    On delete, etag and match_condition are the meaningful concurrency primitive, not deprecated inputs.
    """
    client, orders = container
    item_id = uuid.uuid4().hex
    current_etag = (await orders.create_item({"id": item_id, "pk": "a"}))["_etag"]

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        result = await run_on_rust_async(client, lambda: orders.delete_item(
            item_id, partition_key="a", etag=current_etag, match_condition=MatchConditions.IfNotModified,
        ))

    assert result is None
    offending = [
        str(w.message) for w in recorded
        if issubclass(w.category, DeprecationWarning)
        and ("etag" in str(w.message) or "match_condition" in str(w.message))
    ]
    assert not offending, offending
    with pytest.raises(CosmosResourceNotFoundError):
        await orders.read_item(item_id, partition_key="a")


@pytest.mark.asyncio
async def test_delete_with_etag_but_no_match_condition_raises_value_error_before_io_async_rust(container):
    """Async delete with etag but no match_condition raises ValueError locally and leaves the item.

    The SDK refuses to guess the caller's intent, so no request reaches the Rust binding.
    """
    client, orders = container
    assert_rust_client(client)
    item_id = uuid.uuid4().hex
    await orders.create_item({"id": item_id, "pk": "a"})

    before = _binding_operation_count()
    with pytest.raises(ValueError):
        await orders.delete_item(item_id, partition_key="a", etag="x")
    assert _binding_operation_count() == before, "the request must be rejected before any I/O"
    assert (await orders.read_item(item_id, partition_key="a"))["id"] == item_id
