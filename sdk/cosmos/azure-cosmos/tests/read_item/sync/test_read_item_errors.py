# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``read_item`` not-found behavior on the Rust backend."""

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError
from common._rust_checks import run_on_rust


@pytest.fixture
def container():
    """Yield a Rust client and a ``/pk`` container in an owned database deleted afterwards."""
    with CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust") as client:
        database = client.create_database("read_errors_" + uuid.uuid4().hex)
        try:
            yield client, database.create_container("orders", partition_key=PartitionKey(path="/pk"))
        finally:
            client.delete_database(database.id)


def test_read_existing_id_with_wrong_partition_key_raises_not_found_rust(container):
    """Reading an existing id with the wrong partition key raises CosmosResourceNotFoundError with status 404."""
    client, orders = container
    item_id = uuid.uuid4().hex
    orders.create_item({"id": item_id, "pk": "a", "value": 1})

    with pytest.raises(CosmosResourceNotFoundError) as caught:
        run_on_rust(client, lambda: orders.read_item(item_id, partition_key="b"))
    assert caught.value.status_code == 404
