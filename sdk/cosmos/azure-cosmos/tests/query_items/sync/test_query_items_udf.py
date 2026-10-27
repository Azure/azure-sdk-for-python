# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Invoke an already-deployed UDF through the selected query backend."""

import os

import pytest

from azure.cosmos import CosmosClient
from common._parity_helpers import run_target_operation, skip_unless_emulator, skip_unless_rust_binding
from query_items._udf_fixture import deployed_review_band


@pytest.mark.cosmosEmulator
@skip_unless_emulator()
@skip_unless_rust_binding()
class TestQueryDeployedUdf:
    @pytest.mark.parametrize("scope", ["partition", "cross-partition"])
    def test_query_items_invokes_deployed_udf_rust(self, scope):
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        with deployed_review_band() as database_id:
            with CosmosClient(
                os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend,
            ) as client:
                assert client.client_connection._backend.name == backend
                container = client.get_database_client(database_id).get_container_client("orders")
                options = (
                    {"partition_key": "customer-42"} if scope == "partition"
                    else {"enable_cross_partition_query": True}
                )
                projected = run_target_operation(
                    client,
                    lambda: list(container.query_items(
                        query="SELECT c.id, udf.reviewBand(c.total) AS reviewBand FROM c",
                        **options,
                    )),
                )
                expected = [
                    {"id": "order-42", "reviewBand": "standard"},
                    {"id": "order-43", "reviewBand": "manual"},
                ]
                if scope == "cross-partition":
                    expected.append({"id": "order-44", "reviewBand": "manual"})
                assert sorted(projected, key=lambda row: row["id"]) == expected
                print(f"UDF projection ({scope}): {projected}")

                filtered = run_target_operation(
                    client,
                    lambda: list(container.query_items(
                        query="SELECT c.id FROM c WHERE c.type = 'order' AND udf.reviewBand(c.total) = @band",
                        parameters=[{"name": "@band", "value": "manual"}],
                        **options,
                    )),
                )
                expected_ids = [{"id": "order-43"}]
                if scope == "cross-partition":
                    expected_ids.append({"id": "order-44"})
                assert sorted(filtered, key=lambda row: row["id"]) == expected_ids
                print(f"UDF filter ({scope}): {filtered}")
