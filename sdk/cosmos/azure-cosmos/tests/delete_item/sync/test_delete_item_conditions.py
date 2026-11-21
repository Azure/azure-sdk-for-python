# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live conditional (etag + match_condition) ``delete_item`` behavior on the Rust backend."""

import os
import uuid
import warnings

import pytest

from azure.core import MatchConditions
from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosAccessConditionFailedError, CosmosResourceNotFoundError
from common._rust_checks import run_on_rust


@pytest.fixture
def container():
    """Yield a Rust-backed ``/pk`` container in an owned database that is deleted afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("delete_conditions_" + uuid.uuid4().hex)
        try:
            yield client, database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            client.delete_database(database.id)


def test_delete_with_stale_etag_if_not_modified_raises_precondition_failed_rust(container):
    """Deleting with an outdated etag and IfNotModified fails with 412 and keeps the item.

    The item is changed after its etag is captured, so the service rejects the optimistic-concurrency
    delete and the SDK raises the typed precondition error.
    """
    client, orders = container
    item_id = uuid.uuid4().hex
    stale_etag = orders.create_item({"id": item_id, "pk": "a"})["_etag"]
    orders.upsert_item({"id": item_id, "pk": "a", "bumped": True})

    with pytest.raises(CosmosAccessConditionFailedError) as caught:
        run_on_rust(client, lambda: orders.delete_item(
            item_id, partition_key="a", etag=stale_etag, match_condition=MatchConditions.IfNotModified,
        ))
    assert caught.value.status_code == 412
    assert orders.read_item(item_id, partition_key="a")["bumped"] is True


def test_delete_with_current_etag_if_not_modified_succeeds_without_warning_rust(container):
    """Deleting with the current etag and IfNotModified removes the item and emits no DeprecationWarning.

    On delete, etag and match_condition are the meaningful concurrency primitive, not deprecated inputs.
    """
    client, orders = container
    item_id = uuid.uuid4().hex
    current_etag = orders.create_item({"id": item_id, "pk": "a"})["_etag"]

    with warnings.catch_warnings(record=True) as recorded:
        warnings.simplefilter("always")
        result = run_on_rust(client, lambda: orders.delete_item(
            item_id, partition_key="a", etag=current_etag, match_condition=MatchConditions.IfNotModified,
        ))

    assert result is None
    offending = [
        str(w.message) for w in recorded
        if issubclass(w.category, DeprecationWarning)
        and ("etag" in str(w.message) or "match_condition" in str(w.message))
    ]
    assert not offending, offending
    with pytest.raises(CosmosResourceNotFoundError):
        orders.read_item(item_id, partition_key="a")
