# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Async invocation of an already-deployed UDF through query_items."""

import os

import pytest

from azure.cosmos.aio import CosmosClient
from common._parity_helpers import run_target_operation_async, skip_unless_emulator, skip_unless_rust_binding
from query_items._udf_fixture import deployed_review_band


@pytest.mark.cosmosEmulator
@pytest.mark.asyncio
@skip_unless_emulator()
@skip_unless_rust_binding()
class TestQueryDeployedUdfAsync:
    @pytest.mark.parametrize("scope", ["partition", "cross-partition"])
    async def test_query_items_invokes_deployed_udf_async_rust(self, scope):
        backend = os.environ.get("COSMOS_BACKEND", "rust")
        with deployed_review_band() as database_id:
            async with CosmosClient(
                os.environ["ACCOUNT_HOST"], os.environ["ACCOUNT_KEY"], _backend=backend,
            ) as client:
                assert client.client_connection._backend.name == backend
                container = client.get_database_client(database_id).get_container_client("orders")
                options = (
                    {"partition_key": "customer-42"} if scope == "partition"
                    else {"enable_cross_partition_query": True}
                )

                async def project():
                    results = container.query_items(
                        query="SELECT c.id, udf.reviewBand(c.total) AS reviewBand FROM c",
                        **options,
                    )
                    return [row async for row in results]

                projected = await run_target_operation_async(client, project)
                expected = [
                    {"id": "order-42", "reviewBand": "standard"},
                    {"id": "order-43", "reviewBand": "manual"},
                ]
                if scope == "cross-partition":
                    expected.append({"id": "order-44", "reviewBand": "manual"})
                assert sorted(projected, key=lambda row: row["id"]) == expected
                print(f"UDF projection ({scope}): {projected}")

                async def filter_orders():
                    results = container.query_items(
                        query="SELECT c.id FROM c WHERE c.type = 'order' AND udf.reviewBand(c.total) = @band",
                        parameters=[{"name": "@band", "value": "manual"}],
                        **options,
                    )
                    return [row async for row in results]

                filtered = await run_target_operation_async(client, filter_orders)
                expected_ids = [{"id": "order-43"}]
                if scope == "cross-partition":
                    expected_ids.append({"id": "order-44"})
                assert sorted(filtered, key=lambda row: row["id"]) == expected_ids
                print(f"UDF filter ({scope}): {filtered}")
