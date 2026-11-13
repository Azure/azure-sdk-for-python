# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Observe original throughput-bucket inputs at the compiled feed boundary."""

import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey, _rust
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from config.settings import TestSettings
from read_items.test_fault_recovery import (
    legacy_fault_database,
)  # pylint: disable=unused-import


@pytest.mark.cosmosEmulator
@pytest.mark.cosmosAADLong
@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_read_all_throughput_bucket_on_every_fetch_rust(
    legacy_fault_database, monkeypatch, asynchronous
):
    # Source: tests/test_headers.py::TestHeaders.test_container_read_all_items_throughput_bucket
    # Source: tests/test_headers_async.py::TestHeadersAsync.test_container_read_all_items_throughput_bucket_async
    owned = legacy_fault_database.create_container(
        "read-all-bucket-" + uuid.uuid4().hex, partition_key=PartitionKey(path="/pk")
    )
    client = None
    try:
        expected = set()
        for _ in range(10):
            item_id = str(uuid.uuid4())
            expected.add(item_id)
            owned.create_item({"id": item_id, "pk": "mypk"})
        client = (AsyncCosmosClient if asynchronous else CosmosClient)(
            TestSettings.host,
            TestSettings.masterKey,
            _backend="rust",
            throughput_bucket=2,
        )
        if asynchronous:
            await client.__aenter__()
        container = client.get_database_client(
            legacy_fault_database.id
        ).get_container_client(owned.id)
        name = (
            "fetch_page_with_cursor_async" if asynchronous else "fetch_page_with_cursor"
        )
        original = getattr(_rust, name)
        calls = []

        def observed(handle, prepared, *args, **kwargs):
            if prepared.op == "read_all_items":
                calls.append(prepared)
                assert prepared.settings.throughput_bucket == 3
            return original(handle, prepared, *args, **kwargs)

        monkeypatch.setattr(_rust, name, observed)
        pages = container.read_all_items(throughput_bucket=3, max_item_count=3)
        assert not calls
        rows = [row async for row in pages] if asynchronous else list(pages)
        assert len(rows) == 10 and {row["id"] for row in rows} == expected
        assert len(calls) > 1
    finally:
        if client is not None:
            if asynchronous:
                await client.close()
            else:
                client.close()
        legacy_fault_database.delete_container(owned.id)
