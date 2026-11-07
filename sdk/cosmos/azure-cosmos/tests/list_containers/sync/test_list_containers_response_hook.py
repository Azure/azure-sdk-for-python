# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``list_containers`` per-page response hook behavior on the Rust backend."""
from __future__ import annotations

import os
import uuid

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust

CONTAINER_COUNT = 3


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def populated_database_id():
    client = _rust_client()
    name = "rust_list_containers_hook_" + uuid.uuid4().hex[:8]
    try:
        database = client.create_database(id=name)
        for index in range(CONTAINER_COUNT):
            database.create_container(id="c{}".format(index), partition_key=PartitionKey(path="/pk", kind="Hash"))
        yield name
    finally:
        try:
            client.delete_database(name)
        except exceptions.CosmosResourceNotFoundError:
            pass
        finally:
            client.close()


def test_response_hook_runs_lazily_once_per_page_with_isolated_headers_rust(populated_database_id):
    """The hook is not called until iteration, then once per page with that page's headers and the pager.

    Each page carries its own activity id, a positive request charge and the
    SDK diagnostics header. Changes the hook makes to its headers do not leak
    into ``last_response_headers``. A falsy hook object is still called.
    """
    client = _rust_client()
    try:
        database = client.get_database_client(populated_database_id)
        snapshots = []

        class Hook:
            def __bool__(self):
                return False

            def __call__(self, headers, results_iterator):
                assert results_iterator is pager
                assert headers["x-ms-activity-id"]
                assert float(headers["x-ms-request-charge"]) > 0
                assert headers["x-ms-cosmos-sdk-diagnostics"]
                headers["x-hook-mutation"] = "isolated"
                snapshots.append(headers)

        pager = database.list_containers(
            max_item_count=1, timeout=10,
            initial_headers={"x-company-trace": "list-containers"}, response_hook=Hook(),
        )
        assert snapshots == []

        def target():
            rows = []
            for page in pager.by_page():
                rows.extend(page)
                assert "x-hook-mutation" not in client.client_connection.last_response_headers
            return rows

        rows = run_on_rust(client, target)
    finally:
        client.close()
    assert len(snapshots) == CONTAINER_COUNT
    assert len({headers["x-ms-activity-id"] for headers in snapshots}) == CONTAINER_COUNT
    assert sorted(row["id"] for row in rows) == ["c0", "c1", "c2"]
