# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
# Rust behavior test
"""Queries on Rust evaluate a UDF that is already deployed on the container."""

import os

import pytest

from azure.cosmos import CosmosClient
from common._rust_checks import run_on_rust
from query_items._udf_fixture import deployed_review_band

pytestmark = [pytest.mark.cosmosEmulator]


def _rust_client():
    return CosmosClient(os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend="rust")


@pytest.fixture(scope="module")
def database_id():
    """Orders in a throwaway database whose container has the reviewBand UDF deployed."""
    # Rust exposes no ScriptsProxy, so the shared fixture deploys the UDF over the legacy transport.
    with deployed_review_band() as name:
        yield name


@pytest.mark.parametrize("scope", ["partition", "cross-partition"])
def test_query_items_evaluates_deployed_udf_in_projection_and_filter_rust(database_id, scope):
    """The UDF is evaluated in a SELECT projection and in a parameterized WHERE filter."""
    options = (
        {"partition_key": "customer-42"} if scope == "partition"
        else {"enable_cross_partition_query": True}
    )
    with _rust_client() as client:
        container = client.get_database_client(database_id).get_container_client("orders")
        projected = run_on_rust(client, lambda: list(container.query_items(
            query="SELECT c.id, udf.reviewBand(c.total) AS reviewBand FROM c",
            **options,
        )))
        filtered = run_on_rust(client, lambda: list(container.query_items(
            query="SELECT c.id FROM c WHERE c.type = 'order' AND udf.reviewBand(c.total) = @band",
            parameters=[{"name": "@band", "value": "manual"}],
            **options,
        )))

    expected = [
        {"id": "order-42", "reviewBand": "standard"},
        {"id": "order-43", "reviewBand": "manual"},
    ]
    expected_ids = [{"id": "order-43"}]
    if scope == "cross-partition":
        expected.append({"id": "order-44", "reviewBand": "manual"})
        expected_ids.append({"id": "order-44"})
    assert sorted(projected, key=lambda row: row["id"]) == expected
    assert sorted(filtered, key=lambda row: row["id"]) == expected_ids
