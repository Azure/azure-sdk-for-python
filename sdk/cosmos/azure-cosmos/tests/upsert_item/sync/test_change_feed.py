# The MIT License (MIT)
# Copyright (c) Microsoft Corporation. All rights reserved.
"""Rust-path copy of the sync change-feed start-time test, which seeds items with upsert_item.

The class fixture owns a unique database and provides the original key-auth (control-plane)
and data-plane database proxies, both Rust-backed. The test body is unchanged.
"""
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from time import sleep

import pytest
from _pytest.outcomes import fail

import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from config.clients import create_data_client, create_setup_client
from config.settings import TestSettings, unique_database_id


@pytest.fixture(scope="class")
def setup():
    # Build two clients: a key-auth client for create/delete container (control plane)
    # and a data-plane client (AAD or key) for the change feed reads.
    database_id = unique_database_id("upsert-change-feed")
    # Closed decision: Rust owns endpoint discovery and multi-write routing
    # (docs/V5/api-review/RUST_PARITY_PUSHBACKS.md#client-init-routing). Rust-backed clients reject the
    # original's multiple_write_locations argument (even False), so it is omitted.
    key_client = create_setup_client(_backend="rust")
    data_client = create_data_client(_backend="rust")
    try:
        key_db = key_client.create_database(database_id)
        try:
            yield {
                "key_db": key_db,
                "data_db": data_client.get_database_client(database_id),
                "is_emulator": TestSettings.is_emulator
            }
        finally:
            key_client.delete_database(database_id)
    finally:
        data_client.close()
        key_client.close()

def round_time():
    # Round now down to whole seconds: change feed start_time is second-granular, so
    # sub-second values would make the start_time checks flaky.
    utc_now = datetime.now(timezone.utc)
    return utc_now - timedelta(microseconds=utc_now.microsecond)

@pytest.mark.cosmosCircuitBreaker
@pytest.mark.cosmosQuery
@pytest.mark.cosmosAADCircuitBreaker
@pytest.mark.unittest
@pytest.mark.usefixtures("setup")
class TestChangeFeed:
    """Rust-path copy of tests/test_change_feed.py::TestChangeFeed."""

    def test_query_change_feed_with_start_time_rust(self, setup):
        # Source: tests/test_change_feed.py::TestChangeFeed.test_query_change_feed_with_start_time
        # start_time must select only changes at or after that instant; a future time
        # returns nothing; a non-UTC time is normalized to UTC. Without it, timezone or
        # start-position bugs would slip through.
        created_collection_ref = setup["key_db"].create_container_if_not_exists(
            "query_change_feed_start_time_test",
            PartitionKey(path="/pk"))
        created_collection = setup["data_db"].get_container_client(created_collection_ref.id)
        batchSize = 50

        def create_random_items(container, batch_size):
            created_ids = set()
            for _ in range(batch_size):
                # Generate a Random partition key
                partition_key = 'pk' + str(uuid.uuid4())

                # Generate a random item
                item = {
                    'id': 'item' + str(uuid.uuid4()),
                    'pk': partition_key,
                    'content': 'This is some random content',
                }

                try:
                    # Create the item in the container
                    container.upsert_item(item)
                    created_ids.add(item['id'])
                except exceptions.CosmosHttpResponseError as e:
                    fail(str(e))
            return created_ids

        # Create first batch of random items
        first_batch_ids = create_random_items(created_collection, batchSize)

        # wait for 1 second and record the time, then wait another second
        sleep(1)
        start_time = round_time()
        # Use an equivalent instant in a non-UTC timezone to validate SDK timezone normalization.
        not_utc_time = start_time.astimezone(timezone(timedelta(hours=5, minutes=30)))
        sleep(1)

        # now create another batch of items
        second_batch_ids = create_random_items(created_collection, batchSize)

        # now query change feed based on start time
        change_feed_iter = list(created_collection.query_items_change_feed(start_time=start_time))
        change_feed_ids = {item['id'] for item in change_feed_iter}

        # start_time is second-granular; boundary writes from the first batch can be included.
        assert second_batch_ids.issubset(change_feed_ids)
        assert change_feed_ids.issubset(first_batch_ids.union(second_batch_ids))

        # negative test: pass in a valid time in the future
        future_time = start_time + timedelta(hours=1)
        change_feed_iter = list(created_collection.query_items_change_feed(start_time=future_time))
        # A future time should return 0
        assert len(change_feed_iter) == 0

        # test a date that is not utc, will be converted to utc by sdk
        change_feed_iter = list(created_collection.query_items_change_feed(start_time=not_utc_time))
        change_feed_non_utc_ids = {item['id'] for item in change_feed_iter}
        assert change_feed_non_utc_ids == change_feed_ids

        setup["key_db"].delete_container(created_collection.id)


if __name__ == "__main__":
    unittest.main()
