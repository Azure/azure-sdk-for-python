# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live conditional (etag + match_condition) ``read_item`` behavior on the Rust backend."""

import os
import uuid

import pytest

from azure.core import MatchConditions
from azure.cosmos import CosmosClient, PartitionKey
from common._rust_checks import run_on_rust


@pytest.fixture
def container():
    """Yield a Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("read_conditional_" + uuid.uuid4().hex)
        try:
            yield client, database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            client.delete_database(database.id)


def test_read_with_unchanged_etag_if_modified_returns_empty_not_modified_result_rust(container):
    """Reading with the current etag and IfModified returns an empty CosmosDict (304) carrying the etag.

    This is the cache-validation idiom: the item is unchanged, so the call succeeds with no body and
    the response headers expose the still-current etag.
    """
    client, orders = container
    item_id = uuid.uuid4().hex
    current_etag = orders.create_item({"id": item_id, "pk": "a", "value": 1})["_etag"]

    result = run_on_rust(client, lambda: orders.read_item(
        item_id, partition_key="a", etag=current_etag, match_condition=MatchConditions.IfModified,
    ))

    assert len(result) == 0, dict(result)
    headers = result.get_response_headers()
    assert headers.get("etag") == current_etag, sorted(headers)


def test_read_with_matching_etag_if_not_modified_returns_full_body_rust(container):
    """Reading with the current etag and IfNotModified returns the item (200) with its full body."""
    client, orders = container
    item_id = uuid.uuid4().hex
    created = orders.create_item({"id": item_id, "pk": "a", "value": 1})

    result = run_on_rust(client, lambda: orders.read_item(
        item_id, partition_key="a", etag=created["_etag"], match_condition=MatchConditions.IfNotModified,
    ))

    assert dict(result) == dict(created)
    assert result.get_response_headers().get("etag") == created["_etag"]
