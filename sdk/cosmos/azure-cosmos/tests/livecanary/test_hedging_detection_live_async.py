# Async live multi-region smoke test for hedging detection (AC13).
#
# Same env-var contract as the sync version. Skipped by default.

import os
import uuid

import pytest

from azure.cosmos import RequestedRegionReason, exceptions
from azure.cosmos.aio import CosmosClient
from azure.cosmos import PartitionKey

ENDPOINT = os.environ.get("COSMOS_MULTI_REGION_ENDPOINT")
KEY = os.environ.get("COSMOS_MULTI_REGION_KEY")
DB_NAME = os.environ.get("COSMOS_MULTI_REGION_DATABASE", "hedging-livecanary")
CONTAINER_NAME = os.environ.get("COSMOS_MULTI_REGION_CONTAINER", "items")

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.skipif(
        not (ENDPOINT and KEY),
        reason=(
            "Live multi-region canary requires COSMOS_MULTI_REGION_ENDPOINT and "
            "COSMOS_MULTI_REGION_KEY env vars."
        ),
    ),
]


async def test_live_hedged_read_records_hedging_async():
    async with CosmosClient(ENDPOINT, credential=KEY) as client:
        db = await client.create_database_if_not_exists(id=DB_NAME)
        c = await db.create_container_if_not_exists(
            id=CONTAINER_NAME, partition_key=PartitionKey(path="/pk")
        )
        item_id = f"hd-{uuid.uuid4()}"
        await c.upsert_item({"id": item_id, "pk": item_id, "value": 1})
        strategy = {"threshold_ms": 1, "threshold_steps_ms": 1}
        response = await c.read_item(
            item=item_id, partition_key=item_id, availability_strategy=strategy
        )
        regions = response.get_requested_regions()
        assert len(regions) >= 1
        if response.is_hedging_started():
            assert RequestedRegionReason.HEDGING in {r.reason for r in regions}


async def test_live_all_regions_fail_records_dispatch_on_error_async():
    async with CosmosClient(ENDPOINT, credential=KEY) as client:
        db = await client.create_database_if_not_exists(id=DB_NAME)
        c = await db.create_container_if_not_exists(
            id=CONTAINER_NAME, partition_key=PartitionKey(path="/pk")
        )
        missing_id = f"does-not-exist-{uuid.uuid4()}"
        strategy = {"threshold_ms": 1, "threshold_steps_ms": 1}
        with pytest.raises(exceptions.CosmosResourceNotFoundError) as ei:
            await c.read_item(
                item=missing_id, partition_key=missing_id,
                availability_strategy=strategy,
            )
        exc = ei.value
        regions = exc.get_requested_regions()
        assert isinstance(regions, tuple)
        assert len(regions) >= 1
