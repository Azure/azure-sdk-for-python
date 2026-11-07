# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# Rust behavior test
"""Live ``query_containers`` per-page response hook behavior on the Rust backend."""
from __future__ import annotations

import os
import uuid
from unittest.mock import patch

import pytest

from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from common._rust_checks import run_on_rust

CONTAINER_COUNT = 3


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_with_containers():
    client = _rust_client()
    name = "rust_query_containers_hook_" + uuid.uuid4().hex[:8]
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


@pytest.mark.parametrize("timeout", [None, 10])
def test_response_hook_runs_once_per_fetched_page_rust(database_with_containers, timeout):
    """With or without a timeout, the hook runs lazily and exactly once per page the driver fetches.

    Each call gets that page's headers (distinct activity id, positive charge,
    SDK diagnostics header) and the pager. Changes the hook makes to its
    headers do not leak into ``last_response_headers``. A falsy hook object is
    still called.
    """
    database_id, container_ids = database_with_containers
    client = _rust_client()
    try:
        database = client.get_database_client(database_id)
        snapshots = []

        class Hook:
            def __bool__(self):
                return False

            def __call__(self, headers, results_iterator):
                assert results_iterator is pager
                assert headers["x-ms-activity-id"]
                assert float(headers["x-ms-request-charge"]) > 0
                assert headers["x-ms-cosmos-sdk-diagnostics"]
                snapshots.append(headers)
                headers["x-local"] = "mutation"

        pager = database.query_containers(
            "SELECT * FROM c", max_item_count=1, timeout=timeout,
            initial_headers={"x-company-trace": "query-containers"}, response_hook=Hook(),
        )
        assert snapshots == []
        adapter = client._adapter
        with patch.object(adapter, "execute_pages", wraps=adapter.execute_pages) as fetch:
            rows = run_on_rust(client, lambda: list(pager))
        assert "x-local" not in client.client_connection.last_response_headers
    finally:
        client.close()
    assert len(snapshots) == fetch.call_count >= CONTAINER_COUNT
    assert len({headers["x-ms-activity-id"] for headers in snapshots}) == len(snapshots)
    assert sorted(row["id"] for row in rows) == sorted(container_ids)
