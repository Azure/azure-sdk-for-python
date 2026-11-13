# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Retained None options; the removed max_concurrency option is not replayed."""

import uuid

import pytest

from azure.cosmos import PartitionKey
from config.clients import create_data_client, create_data_client_async
from read_items.test_fault_recovery import (
    legacy_fault_database,
)  # pylint: disable=unused-import


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@pytest.mark.parametrize("asynchronous", [False, True], ids=["sync", "async"])
async def test_container_read_items_none_options_rust(
    legacy_fault_database, asynchronous
):
    # Source: tests/test_none_options.py::TestNoneOptions.test_container_read_items_none_options
    # Source: tests/test_none_options_async.py::TestNoneOptionsAsync.test_container_read_items_none_options_async
    owned = legacy_fault_database.create_container(
        "none-options-" + uuid.uuid4().hex, partition_key=PartitionKey(path="/pk")
    )
    try:
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        owned.create_item(item)
        options = dict(
            consistency_level=None,
            session_token=None,
            initial_headers=None,
            excluded_locations=None,
            priority=None,
            throughput_bucket=None,
        )
        if asynchronous:
            async with create_data_client_async(_backend="rust") as client:
                container = client.get_database_client(
                    legacy_fault_database.id
                ).get_container_client(owned.id)
                results = await container.read_items(
                    [(item["id"], item["pk"])], **options
                )
        else:
            with create_data_client(_backend="rust") as client:
                container = client.get_database_client(
                    legacy_fault_database.id
                ).get_container_client(owned.id)
                results = container.read_items([(item["id"], item["pk"])], **options)
        assert any(r["id"] == item["id"] for r in results)
    finally:
        legacy_fault_database.delete_container(owned.id)
