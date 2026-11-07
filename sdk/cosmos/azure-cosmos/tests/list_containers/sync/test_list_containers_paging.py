# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``list_containers`` paging behavior on the Rust backend."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust

CONTAINER_COUNT = 3
EXPECTED_IDS = ["c0", "c1", "c2"]


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


def _ids(containers):
    return sorted(container["id"] for container in containers)


def _owned_database(prefix, container_count):
    client = _rust_client()
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
    yield from _owned_database("rust_list_containers_empty_", 0)


@pytest.fixture(scope="module")
def populated_database_id():
    yield from _owned_database("rust_list_containers_", CONTAINER_COUNT)


@pytest.fixture
def client():
    rust_client = _rust_client()
    try:
        yield rust_client
    finally:
        rust_client.close()


def test_empty_database_lists_no_containers_rust(client, empty_database_id):
    """Listing the containers of a database that has none returns an empty list instead of raising."""
    database = client.get_database_client(empty_database_id)
    assert run_on_rust(client, lambda: _ids(database.list_containers())) == []


def test_one_container_per_page_returns_every_container_rust(client, populated_database_id):
    """With ``max_item_count=1`` each page holds exactly one container and the pages together hold all of them."""
    database = client.get_database_client(populated_database_id)

    def target():
        return [list(page) for page in database.list_containers(max_item_count=1).by_page()]

    pages = run_on_rust(client, target)
    assert len(pages) == CONTAINER_COUNT
    assert all(len(page) == 1 for page in pages)
    assert _ids([item for page in pages for item in page]) == EXPECTED_IDS


def test_resume_from_continuation_token_returns_remaining_containers_rust(client, populated_database_id):
    """Resuming from the token after the first page returns exactly the containers not yet seen."""
    database = client.get_database_client(populated_database_id)

    def target():
        pages = database.list_containers(max_item_count=1).by_page()
        first = list(next(pages))
        token = pages.continuation_token
        rest = [item for page in pages for item in page]
        replay = [
            item
            for page in database.list_containers(max_item_count=1).by_page(continuation_token=token)
            for item in page
        ]
        return first, token, rest, replay

    first, token, rest, replay = run_on_rust(client, target)
    assert len(first) == 1 and token
    assert replay == rest
    assert not set(_ids(first)).intersection(_ids(rest))
    assert _ids(first + replay) == EXPECTED_IDS
