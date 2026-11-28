# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Check Rust consistency names through both public clients on a configured account.

Set ACCOUNT_HOST and ACCOUNT_KEY to run. These tests check acceptance and read
results, not cross-region freshness or the account's replication guarantees.
"""

import base64
from email.utils import formatdate
import hashlib
import hmac
import json
import os
from urllib.parse import quote
from urllib.request import Request, urlopen
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.aio import CosmosClient as AsyncCosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from common._rust_checks import run_on_rust, run_on_rust_async
from common.throughput_fixtures import owned_database

pytestmark = pytest.mark.cosmosEmulator


LEVELS = ["Eventual", "ConsistentPrefix", "Session", "BoundedStaleness", "Strong"]
SOURCES = ["client", "request_options", "feed_options", "initial_headers"]


def _account_supports_strong_reads(endpoint, key):
    """Read account configuration independently of the SDK under test."""
    date = formatdate(usegmt=True)
    payload = f"get\n\n\n{date.lower()}\n\n".encode("utf-8")
    signature = base64.b64encode(hmac.new(base64.b64decode(key), payload, hashlib.sha256).digest()).decode()
    request = Request(endpoint, headers={
        "authorization": quote(f"type=master&ver=1.0&sig={signature}", safe=""),
        "x-ms-date": date, "x-ms-version": "2018-12-31",
    })
    with urlopen(request, timeout=30) as response:
        account = json.load(response)
    return (
        account["userConsistencyPolicy"]["defaultConsistencyLevel"] == "Strong"
        and not account["enableMultipleWriteLocations"]
    )


@pytest.fixture(scope="module")
def consistency_order():
    endpoint, key = os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"]
    strong_account = _account_supports_strong_reads(endpoint, key)
    with CosmosClient(endpoint, key, _backend="rust") as setup:
        with owned_database(setup, "consistency-review-" + uuid.uuid4().hex) as database:
            container = database.create_container(id="orders", partition_key=PartitionKey(path="/pk"))
            expected = {"id": "order-42", "pk": "customer-17", "value": 1}
            container.create_item(dict(expected))
            yield endpoint, key, database.id, expected, strong_account


def _read_options(source, level):
    if source == "client":
        return {}
    name = "x-ms-consistency-level" if source == "initial_headers" else "consistencyLevel"
    return {source: {name: level}}


@pytest.mark.parametrize("level", LEVELS)
@pytest.mark.parametrize("source", SOURCES)
def test_rust_read_consistency_rust(consistency_order, source, level):
    endpoint, key, database_id, expected, strong_account = consistency_order
    default = level if source == "client" else "Session"
    with CosmosClient(endpoint, key, _backend="rust", consistency_level=default) as client:
        container = client.get_database_client(database_id).get_container_client("orders")

        def read(options):
            return run_on_rust(
                client,
                lambda: container.read_item(expected["id"], partition_key=expected["pk"], **options),
            )

        if level == "Strong" and not strong_account:
            with pytest.raises(
                CosmosHttpResponseError,
                match="only valid against accounts whose default consistency level is Strong",
            ) as caught:
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
async def test_rust_read_consistency_async_rust(consistency_order, source, level):
    endpoint, key, database_id, expected, strong_account = consistency_order
    default = level if source == "client" else "Session"
    async with AsyncCosmosClient(endpoint, key, _backend="rust", consistency_level=default) as client:
        container = client.get_database_client(database_id).get_container_client("orders")

        async def read(options):
            return await run_on_rust_async(
                client,
                lambda: container.read_item(expected["id"], partition_key=expected["pk"], **options),
            )

        if level == "Strong" and not strong_account:
            with pytest.raises(
                CosmosHttpResponseError,
                match="only valid against accounts whose default consistency level is Strong",
            ) as caught:
                await read(_read_options(source, level))
            assert caught.value.status_code == 400
        else:
            actual = await read(_read_options(source, level))
            assert {field: actual[field] for field in expected} == expected
        if source != "client":
            actual = await read({})
            assert {field: actual[field] for field in expected} == expected
