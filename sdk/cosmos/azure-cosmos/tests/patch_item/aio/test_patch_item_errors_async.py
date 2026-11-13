# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``patch_item`` failure behavior on the Rust backend."""

import os
import uuid

import pytest
import pytest_asyncio

from azure.core import MatchConditions
from azure.cosmos import PartitionKey
from azure.cosmos.aio import CosmosClient
from azure.cosmos.exceptions import (
    CosmosAccessConditionFailedError,
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
)
from common._rust_checks import run_on_rust_async

_SEED = {"pk": "customerA", "n": 1, "label": "before", "nested": {"inner": 1}}


@pytest_asyncio.fixture
async def container():
    """Yield an async Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = await client.create_database("patch_errors_aio_" + uuid.uuid4().hex)
        try:
            yield client, await database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            await client.delete_database(database.id)


async def _seed(orders):
    return await orders.create_item(dict(_SEED, id=uuid.uuid4().hex))


@pytest.mark.asyncio
async def test_patch_missing_id_raises_not_found_async_rust(container):
    """Async patch of an id that was never created raises CosmosResourceNotFoundError with status 404."""
    client, orders = container
    with pytest.raises(CosmosResourceNotFoundError) as caught:
        await run_on_rust_async(client, lambda: orders.patch_item(
            item="missing-" + uuid.uuid4().hex, partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 1}],
        ))
    assert caught.value.status_code == 404


@pytest.mark.asyncio
async def test_patch_with_stale_etag_raises_precondition_failed_async_rust(container):
    """Async patch with an outdated etag and IfNotModified fails with 412 instead of overwriting a newer write."""
    client, orders = container
    created = await _seed(orders)
    await orders.patch_item(
        item=created["id"], partition_key="customerA",
        patch_operations=[{"op": "set", "path": "/label", "value": "moved on"}],
    )

    with pytest.raises(CosmosAccessConditionFailedError) as caught:
        await run_on_rust_async(client, lambda: orders.patch_item(
            item=created["id"], partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 999}],
            etag=created["_etag"], match_condition=MatchConditions.IfNotModified,
        ))
    assert caught.value.status_code == 412
    assert (await orders.read_item(created["id"], partition_key="customerA"))["n"] == 1


@pytest.mark.asyncio
async def test_patch_incr_on_path_with_missing_parent_raises_bad_request_async_rust(container):
    """An async incr on a path whose parent does not exist fails with CosmosHttpResponseError status 400."""
    client, orders = container
    created = await _seed(orders)

    with pytest.raises(CosmosHttpResponseError) as caught:
        await run_on_rust_async(client, lambda: orders.patch_item(
            item=created["id"], partition_key="customerA",
            patch_operations=[{"op": "incr", "path": "/definitely/not/here", "value": 1}],
        ))
    assert caught.value.status_code == 400
