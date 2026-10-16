# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check Rust consistency names through both public clients on a configured account.

Set ACCOUNT_HOST and ACCOUNT_KEY to run. These tests check acceptance and read
results, not cross-region freshness or the account's replication guarantees.
"""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from common._parity_helpers import (
    run_target_operation,
    run_target_operation_async,
    skip_unless_emulator,
    skip_unless_rust_binding,
)


pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]
LEVELS = ["Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong"]
SOURCES = ["client", "request_options", "feed_options", "initial_headers"]


@pytest.fixture(scope="module")
def consistency_order():
    endpoint, key = os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    with CosmosClient(endpoint, key, _backend="core-python") as setup:
        account = setup.get_database_account()
        strong_account = (
            account.ConsistencyPolicy["defaultConsistencyLevel"] == "Strong"
            and not account._EnableMultipleWritableLocations
        )
        database = setup.create_database("consistency-review-" + uuid.uuid4().hex)
        try:
            container = database.create_container(id="orders", partition_key=PartitionKey(path="/pk"))
            expected = {"id": "order-42", "pk": "customer-17", "value": 1}
            container.create_item(dict(expected))
            yield endpoint, key, database.id, expected, strong_account
        finally:
            setup.delete_database(database.id)


def _read_options(source, level):
    if source == "client":
        return {}
    name = "x-ms-consistency-level" if source == "initial_headers" else "consistencyLevel"
    return {source: {name: level}}


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("source", SOURCES)
def test_rust_read_consistency(consistency_order, source, level):
    endpoint, key, database_id, expected, strong_account = consistency_order
    default = level if source == "client" else "Session"
    with CosmosClient(endpoint, key, _backend="rust", consistency_level=default) as client:
        container = client.get_database_client(database_id).get_container_client("orders")

        def read(options):
            return run_target_operation(
                client,
                lambda: container.read_item(expected["id"], partition_key=expected["pk"], **options),
            )

        if level == "Strong" and not strong_account:
            with pytest.raises(CosmosHttpResponseError) as caught:
                read(_read_options(source, level))
            assert caught.value.status_code == 400
        else:
            actual = read(_read_options(source, level))
            assert {field: actual[field] for field in expected} == expected
        if source != "client":
            actual = read({})
            assert {field: actual[field] for field in expected} == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("source", SOURCES)
async def test_rust_read_consistency_async(consistency_order, source, level):
    endpoint, key, database_id, expected, strong_account = consistency_order
    default = level if source == "client" else "Session"
    async with AsyncCosmosClient(endpoint, key, _backend="rust", consistency_level=default) as client:
        container = client.get_database_client(database_id).get_container_client("orders")

        async def read(options):
            return await run_target_operation_async(
                client,
                lambda: container.read_item(expected["id"], partition_key=expected["pk"], **options),
            )

        if level == "Strong" and not strong_account:
            with pytest.raises(CosmosHttpResponseError) as caught:
                await read(_read_options(source, level))
            assert caught.value.status_code == 400
        else:
            actual = await read(_read_options(source, level))
            assert {field: actual[field] for field in expected} == expected
        if source != "client":
            actual = await read({})
            assert {field: actual[field] for field in expected} == expected
