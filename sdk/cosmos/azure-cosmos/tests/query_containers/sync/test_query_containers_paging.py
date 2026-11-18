# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``query_containers`` paging and continuation behavior on the Rust backend."""
from __future__ import annotations

import os
import uuid
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import assert_live_page_headers, run_on_rust

CONTAINER_COUNT = 3


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


def _ids(containers):
    return sorted(container["id"] for container in containers)


@pytest.fixture(scope="module")
def database_with_containers():
    client = _rust_client()
    name = "rust_query_containers_paging_" + uuid.uuid4().hex[:8]
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


def test_one_container_per_page_resumes_from_continuation_token_rust(database_with_containers):
    """A parameterized query pages one container at a time and resumes from a token with no overlap or loss."""
    database_id, container_ids = database_with_containers
    client = _rust_client()
    try:
        database = client.get_database_client(database_id)
        query = "SELECT * FROM c WHERE c.id != @excluded"
        options = {"parameters": [{"name": "@excluded", "value": "not_here"}], "max_item_count": 1}
        snapshots = []

        def target():
            adapter = client._adapter
            with patch.object(adapter, "execute_pages", wraps=adapter.execute_pages) as fetch:
                pages = database.query_containers(
                    query, response_hook=lambda headers, _results: snapshots.append(dict(headers)), **options
                ).by_page()
                first = list(next(pages))
                token = pages.continuation_token
                remaining_pages = [list(page) for page in pages]
            assert len(snapshots) == fetch.call_count >= CONTAINER_COUNT
            assert_live_page_headers(snapshots)
            replay = [
                item
                for page in database.query_containers(query, **options).by_page(continuation_token=token)
                for item in page
            ]
            return first, token, remaining_pages, replay

        first, token, remaining_pages, replay = run_on_rust(client, target)
    finally:
        client.close()
    assert len(first) == 1 and token
    assert len(remaining_pages) == CONTAINER_COUNT - 1
    assert all(len(page) == 1 for page in remaining_pages)
    assert replay == [item for page in remaining_pages for item in page]
    assert not set(_ids(first)).intersection(_ids(replay))
    assert _ids(first + replay) == sorted(container_ids)
