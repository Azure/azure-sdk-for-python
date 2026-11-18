# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``delete_item`` not-found behavior on the Rust backend."""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust


@pytest.fixture
def database():
    """Yield a Rust client and an owned database that is deleted afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        owned = client.create_database("delete_errors_" + uuid.uuid4().hex)
        try:
            yield client, owned
        finally:
            client.delete_database(owned.id)


def test_delete_missing_id_raises_not_found_rust(database):
    """Deleting an id that was never created raises CosmosResourceNotFoundError with status 404."""
    client, owned = database
    orders = owned.create_container("orders", partition_key=PartitionKey(path="/pk"))

    with pytest.raises(CosmosResourceNotFoundError) as caught:
        run_on_rust(client, lambda: orders.delete_item("does-not-exist-" + uuid.uuid4().hex, partition_key="a"))
    assert caught.value.status_code == 404


@pytest.mark.parametrize("self_link_only", [False, True], ids=["item_dict", "self_link_only"])
def test_delete_through_stale_item_address_leaves_recreated_container_item_rust(database, self_link_only):
    """A stale item dict or bare _self from a deleted container cannot delete the recreated container's item.

    The container is deleted and recreated with the same name and an item with the same id. Deleting
    through the old item's address raises 404 and the new item survives unchanged.
    """
    client, owned = database
    name = "orders_" + uuid.uuid4().hex[:8]
    original = owned.create_container(name, partition_key=PartitionKey(path="/pk"))
    old = original.create_item({"id": "same-id", "pk": "a", "generation": "old"})
    owned.delete_container(name)
    replacement = owned.create_container(name, partition_key=PartitionKey(path="/pk"))
    new = replacement.create_item({"id": "same-id", "pk": "a", "generation": "new"})
    assert old["_self"] != new["_self"]
    target = {"_self": old["_self"]} if self_link_only else old

    with pytest.raises(CosmosResourceNotFoundError) as caught:
        run_on_rust(client, lambda: replacement.delete_item(target, partition_key="a"))
    assert caught.value.status_code == 404

    surviving = replacement.read_item("same-id", partition_key="a")
    assert surviving["_self"] == new["_self"]
    assert surviving["generation"] == "new"
