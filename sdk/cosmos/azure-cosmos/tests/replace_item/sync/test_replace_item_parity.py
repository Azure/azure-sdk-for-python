# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Cross-backend parity tests for replace_item (sync): run both backends in one
process and diff the result. Skips without an account or the rust binding."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, PartitionKey
from common._parity_helpers import run_on_both_backends, skip_unless_emulator, skip_unless_rust_binding

pytestmark = [skip_unless_emulator(), skip_unless_rust_binding()]


@pytest.fixture
def container_for(request):
    """Provide an isolated container so each test targets only its own items."""
    client = CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"])
    db = client.create_database_if_not_exists("parity_db")
    cname = "rp_" + request.node.name + "_" + uuid.uuid4().hex[:6]
    container = db.create_container(id=cname, partition_key=PartitionKey(path="/pk"))
    yield container
    try:
        db.delete_container(cname)
    except Exception:  # pylint: disable=broad-except
        pass


def test_create_then_replace(container_for):
    """create an item, replace its body — parity on both backends."""
    item_id = uuid.uuid4().hex

    def _do(client):
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        c.upsert_item({"id": item_id, "pk": "a", "n": 1})
        return c.replace_item(item=item_id, body={"id": item_id, "pk": "a", "n": 2})

    cmp = run_on_both_backends(_do, description="replace", request_body={"id": item_id, "pk": "a"})
    cmp.print_report()
    cmp.assert_functional_parity()


def test_replace_missing_raises(container_for):
    """replacing a missing id raises CosmosResourceNotFoundError on both."""
    def _do(client):
        c = client.get_database_client("parity_db").get_container_client(container_for.id)
        return c.replace_item(item="missing-" + uuid.uuid4().hex, body={"id": "x", "pk": "a"})

    cmp = run_on_both_backends(_do, description="replace missing -> 404")
    cmp.print_report()
    cmp.assert_exception_parity()

