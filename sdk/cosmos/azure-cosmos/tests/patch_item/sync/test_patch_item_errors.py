# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``patch_item`` failure behavior on the Rust backend."""

import os
import uuid

import pytest

from azure.core import MatchConditions
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import (
    CosmosAccessConditionFailedError,
    CosmosHttpResponseError,
    CosmosResourceNotFoundError,
)
from common._rust_checks import run_on_rust

_SEED = {"pk": "customerA", "n": 1, "label": "before", "nested": {"inner": 1}}


@pytest.fixture
def container():
    """Yield a Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("patch_errors_" + uuid.uuid4().hex)
        try:
            yield client, database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            client.delete_database(database.id)


def _seed(orders):
    item_id = uuid.uuid4().hex
    return orders.create_item(dict(_SEED, id=item_id))


def test_patch_missing_id_raises_not_found_rust(container):
    """Patching an id that was never created raises CosmosResourceNotFoundError with status 404."""
    client, orders = container
    with pytest.raises(CosmosResourceNotFoundError) as caught:
        run_on_rust(client, lambda: orders.patch_item(
            item="missing-" + uuid.uuid4().hex, partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 1}],
        ))
    assert caught.value.status_code == 404


def test_patch_with_stale_etag_raises_precondition_failed_rust(container):
    """Patching with an outdated etag and IfNotModified fails with 412 instead of overwriting a newer write."""
    client, orders = container
    created = _seed(orders)
    orders.patch_item(
        item=created["id"], partition_key="customerA",
        patch_operations=[{"op": "set", "path": "/label", "value": "moved on"}],
    )

    with pytest.raises(CosmosAccessConditionFailedError) as caught:
        run_on_rust(client, lambda: orders.patch_item(
            item=created["id"], partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 999}],
            etag=created["_etag"], match_condition=MatchConditions.IfNotModified,
        ))
    assert caught.value.status_code == 412
    assert orders.read_item(created["id"], partition_key="customerA")["n"] == 1


def test_patch_with_non_matching_filter_predicate_raises_precondition_failed_rust(container):
    """A filter_predicate that does not match the document rejects the patch with 412 and leaves it unchanged."""
    client, orders = container
    created = _seed(orders)

    with pytest.raises(CosmosAccessConditionFailedError) as caught:
        run_on_rust(client, lambda: orders.patch_item(
            item=created["id"], partition_key="customerA",
            patch_operations=[{"op": "set", "path": "/n", "value": 2}],
            filter_predicate="FROM c WHERE c.n = 99999",
        ))
    assert caught.value.status_code == 412
    stored = orders.read_item(created["id"], partition_key="customerA")
    assert stored["n"] == 1
    assert stored["_etag"] == created["_etag"]


def test_patch_incr_on_path_with_missing_parent_raises_bad_request_rust(container):
    """An incr on a path whose parent does not exist fails with CosmosHttpResponseError status 400."""
    client, orders = container
    created = _seed(orders)

    with pytest.raises(CosmosHttpResponseError) as caught:
        run_on_rust(client, lambda: orders.patch_item(
            item=created["id"], partition_key="customerA",
            patch_operations=[{"op": "incr", "path": "/definitely/not/here", "value": 1}],
        ))
    assert caught.value.status_code == 400
