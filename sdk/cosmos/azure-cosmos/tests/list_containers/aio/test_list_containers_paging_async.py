# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``list_containers`` paging behavior on the Rust backend."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient, exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import assert_live_page_headers, run_on_rust_async

pytestmark = [pytest.mark.asyncio]

CONTAINER_COUNT = 3
EXPECTED_IDS = ["c0", "c1", "c2"]


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


def _owned_database(prefix, container_count):
    client = SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
    name = prefix + uuid.uuid4().hex[:8]
    try:
        database = client.create_database(id=name)
        for index in range(container_count):
            database.create_container(id="c{}".format(index), partition_key=PartitionKey(path="/pk", kind="Hash"))
        yield name
    finally:
        try:
            client.delete_database(name)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


@pytest.fixture(scope="module")
def empty_database_id():
    yield from _owned_database("rust_list_containers_a_empty_", 0)


@pytest.fixture(scope="module")
def populated_database_id():
    yield from _owned_database("rust_list_containers_a_", CONTAINER_COUNT)


async def test_empty_database_lists_no_containers_async_rust(empty_database_id):
    """Listing the containers of a database that has none returns an empty list instead of raising."""
    async with _rust_client() as client:
        database = client.get_database_client(empty_database_id)

        async def target():
            return sorted([container["id"] async for container in database.list_containers()])

        assert await run_on_rust_async(client, target) == []


async def test_one_container_per_page_returns_every_container_async_rust(populated_database_id):
    """With ``max_item_count=1`` each page holds one container and the pages together hold all of them."""
    async with _rust_client() as client:
        database = client.get_database_client(populated_database_id)
        snapshots = []

        async def target():
            return [
                [item async for item in page]
                async for page in database.list_containers(
                    max_item_count=1,
                    timeout=10,
                    initial_headers={"x-company-trace": "list-containers"},
                    response_hook=lambda headers, _results: snapshots.append(dict(headers)),
                ).by_page()
            ]

        pages = await run_on_rust_async(client, target)
    assert_live_page_headers(snapshots)
    assert len(snapshots) == len(pages)
    assert len(pages) == CONTAINER_COUNT
    assert all(len(page) == 1 for page in pages)
    assert sorted(item["id"] for page in pages for item in page) == EXPECTED_IDS


async def test_resume_from_continuation_token_returns_remaining_containers_async_rust(populated_database_id):
    """Resuming from the token after the first page returns exactly the containers not yet seen."""
    async with _rust_client() as client:
        database = client.get_database_client(populated_database_id)

        async def target():
            pages = database.list_containers(max_item_count=1).by_page()
            first = [item async for item in await pages.__anext__()]
            token = pages.continuation_token
            rest = [item async for page in pages async for item in page]
            replay = [
                item
                async for page in database.list_containers(max_item_count=1).by_page(continuation_token=token)
                async for item in page
            ]
            return first, token, rest, replay

        first, token, rest, replay = await run_on_rust_async(client, target)
    assert len(first) == 1 and token
    assert replay == rest
    assert not {item["id"] for item in first}.intersection(item["id"] for item in rest)
    assert sorted(item["id"] for item in first + replay) == EXPECTED_IDS
