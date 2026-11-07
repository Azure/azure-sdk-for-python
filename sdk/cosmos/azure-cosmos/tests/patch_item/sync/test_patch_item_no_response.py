# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``patch_item(no_response=True)`` behavior on the Rust backend."""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._rust_checks import run_on_rust


@pytest.fixture
def container():
    """Yield a Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("patch_no_response_" + uuid.uuid4().hex)
        try:
            yield client, database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            client.delete_database(database.id)


def test_patch_with_no_response_returns_empty_dict_and_applies_patch_rust(container):
    """patch_item(no_response=True) returns an empty dict while the patch is still applied on the service."""
    client, orders = container
    item_id = uuid.uuid4().hex
    orders.create_item({"id": item_id, "pk": "customerA", "n": 1, "label": "before"})

    result = run_on_rust(client, lambda: orders.patch_item(
        item=item_id, partition_key="customerA",
        patch_operations=[{"op": "set", "path": "/n", "value": 2}],
        no_response=True,
    ))

    assert dict(result) == {}
    stored = orders.read_item(item_id, partition_key="customerA")
    assert stored["n"] == 2
    assert stored["label"] == "before"
