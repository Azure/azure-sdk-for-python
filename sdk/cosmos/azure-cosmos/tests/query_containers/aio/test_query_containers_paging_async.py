# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live async ``query_containers`` paging and continuation behavior on the Rust backend."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient as SyncCosmosClient, exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust_async

pytestmark = [pytest.mark.asyncio]

CONTAINER_COUNT = 3


@pytest.fixture(scope="module")
def database_with_containers():
    client = SyncCosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")
    name = "rust_query_containers_a_paging_" + uuid.uuid4().hex[:8]
    container_ids = []
    try:
        database = client.create_database(id=name)
        for index in range(CONTAINER_COUNT):
            container_id = "c{}".format(index)
            database.create_container(id=container_id, partition_key=PartitionKey(path="/pk", kind="Hash"))
            container_ids.append(container_id)
        yield name, container_ids
    finally:
        try:
            client.delete_database(name)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


async def test_one_container_per_page_resumes_from_continuation_token_async_rust(database_with_containers):
    """A parameterized query pages one container at a time and resumes from a token with no overlap or loss."""
    database_id, container_ids = database_with_containers
    async with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.get_database_client(database_id)
        query = "SELECT * FROM c WHERE c.id != @excluded"
        options = {"parameters": [{"name": "@excluded", "value": "not_here"}], "max_item_count": 1}

        async def target():
            pages = database.query_containers(query, **options).by_page()
            first = [item async for item in await pages.__anext__()]
            token = pages.continuation_token
            remaining_pages = [[item async for item in page] async for page in pages]
            replay = [
                item
                async for page in database.query_containers(query, **options).by_page(continuation_token=token)
                async for item in page
            ]
            return first, token, remaining_pages, replay

        first, token, remaining_pages, replay = await run_on_rust_async(client, target)
    assert len(first) == 1 and token
    assert len(remaining_pages) == CONTAINER_COUNT - 1
    assert all(len(page) == 1 for page in remaining_pages)
    assert replay == [item for page in remaining_pages for item in page]
    assert not {item["id"] for item in first}.intersection(item["id"] for item in replay)
    assert sorted(item["id"] for item in first + replay) == sorted(container_ids)
