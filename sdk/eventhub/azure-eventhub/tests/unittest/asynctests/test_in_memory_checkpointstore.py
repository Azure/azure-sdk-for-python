import time
import pytest
from azure.eventhub.aio._eventprocessor.in_memory_checkpoint_store import InMemoryCheckpointStore


TEST_NAMESPACE = "test_namespace"
TEST_EVENTHUB = "test_eventhub"
TEST_CONSUMER_GROUP = "test_consumer_group"
TEST_OWNER = "test_owner_id"


@pytest.mark.asyncio
async def test_claim_new_ownership():
    ownership = {
        "fully_qualified_namespace": TEST_NAMESPACE,
        "partition_id": "0",
        "eventhub_name": TEST_EVENTHUB,
        "consumer_group": TEST_CONSUMER_GROUP,
        "owner_id": "owner_0"
    }
    checkpoint_store = InMemoryCheckpointStore()
    claimed_ownership = await checkpoint_store.claim_ownership([ownership])
    assert len(claimed_ownership) == 1
    listed_ownership = await checkpoint_store.list_ownership(TEST_NAMESPACE, TEST_EVENTHUB, TEST_CONSUMER_GROUP)

    assert listed_ownership[0] == ownership
    assert ownership["last_modified_time"] is not None
    assert ownership["etag"] is not None


@pytest.mark.asyncio
async def test_claim_existing_ownership():
    ownership = {
        "fully_qualified_namespace": TEST_NAMESPACE,
        "partition_id": "0",
        "eventhub_name": TEST_EVENTHUB,
        "consumer_group": TEST_CONSUMER_GROUP,
        "owner_id": "owner_0",
    }
    checkpoint_store = InMemoryCheckpointStore()
    await checkpoint_store.claim_ownership([ownership])
    listed_ownership = await checkpoint_store.list_ownership(TEST_NAMESPACE, TEST_EVENTHUB, TEST_CONSUMER_GROUP)
    existing_ownership = listed_ownership[0]
    etag_existing = existing_ownership["etag"]
    last_modified_exising = existing_ownership["last_modified_time"]

    time.sleep(0.01)  # so time is changed
    copied_existing_ownership = existing_ownership.copy()
    copied_existing_ownership["owner_id"] = "owner_1"
    await checkpoint_store.claim_ownership([copied_existing_ownership])
    listed_ownership2 = await checkpoint_store.list_ownership(TEST_NAMESPACE, TEST_EVENTHUB, TEST_CONSUMER_GROUP)

    assert len(listed_ownership2) == 1
    assert listed_ownership2[0] == copied_existing_ownership
    assert listed_ownership2[0]["owner_id"] == "owner_1"
    assert listed_ownership2[0]["etag"] != etag_existing
    assert listed_ownership2[0]["last_modified_time"] != last_modified_exising


@pytest.mark.asyncio
async def test_claim_two_ownerships():
    ownership_0 = {
        "fully_qualified_namespace": TEST_NAMESPACE,
        "partition_id": "0",
        "eventhub_name": TEST_EVENTHUB,
        "consumer_group": TEST_CONSUMER_GROUP,
        "owner_id": "owner_0"
    }
    ownership_1 = {
        "fully_qualified_namespace": TEST_NAMESPACE,
        "partition_id": "0",
        "eventhub_name": TEST_EVENTHUB,
        "consumer_group": TEST_CONSUMER_GROUP+"1",
        "owner_id": "owner_1"
    }
    checkpoint_store = InMemoryCheckpointStore()
    claimed_ownership = await checkpoint_store.claim_ownership([ownership_0, ownership_1])
    assert len(claimed_ownership) == 2
    listed_ownership0 = await checkpoint_store.list_ownership(TEST_NAMESPACE, TEST_EVENTHUB, TEST_CONSUMER_GROUP)
    listed_ownership1 = await checkpoint_store.list_ownership(TEST_NAMESPACE, TEST_EVENTHUB, TEST_CONSUMER_GROUP+"1")
    assert listed_ownership0[0]["consumer_group"] == TEST_CONSUMER_GROUP
    assert listed_ownership1[0]["consumer_group"] == TEST_CONSUMER_GROUP+"1"


@pytest.mark.asyncio
async def test_claim_two_partitions():
    ownership_0 = {
        "fully_qualified_namespace": TEST_NAMESPACE,
        "partition_id": "0",
        "eventhub_name": TEST_EVENTHUB,
        "consumer_group": TEST_CONSUMER_GROUP,
        "owner_id": "owner_0"
    }
    ownership_1 = {
        "fully_qualified_namespace": TEST_NAMESPACE,
        "partition_id": "1",
        "eventhub_name": TEST_EVENTHUB,
        "consumer_group": TEST_CONSUMER_GROUP,
        "owner_id": "owner_0"
    }
    checkpoint_store = InMemoryCheckpointStore()
    await checkpoint_store.claim_ownership([ownership_0, ownership_1])
    listed_ownership0 = await checkpoint_store.list_ownership(TEST_NAMESPACE, TEST_EVENTHUB, TEST_CONSUMER_GROUP)
    assert set(x["partition_id"] for x in listed_ownership0) == {"0", "1"}


@pytest.mark.asyncio
async def test_update_checkpoint():
    checkpoint = {
        "fully_qualified_namespace": TEST_NAMESPACE,
        "partition_id": "0",
        "eventhub_name": TEST_EVENTHUB,
        "consumer_group": TEST_CONSUMER_GROUP,
        "offset": "0",
        "sequencenumber": 0
    }
    checkpoint_store = InMemoryCheckpointStore()
    await checkpoint_store.update_checkpoint(checkpoint)
    listed_checkpoint = await checkpoint_store.list_checkpoints(TEST_NAMESPACE, TEST_EVENTHUB, TEST_CONSUMER_GROUP)

    assert listed_checkpoint[0] == checkpoint
    assert listed_checkpoint[0]["offset"] == "0"
    assert listed_checkpoint[0]["sequencenumber"] == 0
