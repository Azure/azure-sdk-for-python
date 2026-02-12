# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import json
import uuid

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to work with feed ranges in Azure Cosmos DB.
#
# Feed ranges represent a scope within a container, defined by a range of partition key hash values.
# They enable sub-container-level operations such as parallel query processing, scoped change feed
# consumption, and workload partitioning across multiple workers.
#
# Feed ranges are returned as opaque dict[str, Any] values and should not be manually constructed
# or parsed. Use the provided container methods to create and compare them.
#
# 1. Reading feed ranges from a container
# 2. Getting a feed range for a specific partition key
# 3. Checking if one feed range is a subset of another
# 4. Querying items scoped to a feed range
# 5. Querying items using a feed range derived from a partition key
# 6. Consuming change feed scoped to a feed range
# 7. Parallel change feed processing using feed ranges
# ----------------------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create (and delete) a Database and Container on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

# Partition key values used throughout the sample
PARTITION_KEY_VALUES = ['Seattle', 'Portland', 'Denver', 'Austin', 'Chicago']


def create_sample_items(container):
    """Create sample items across multiple partition keys."""
    print('\nCreating sample items across partition keys: {}'.format(PARTITION_KEY_VALUES))
    items = []
    for city in PARTITION_KEY_VALUES:
        for i in range(3):
            item = {
                'id': 'item-{}-{}'.format(city, str(uuid.uuid4())[:8]),
                'city': city,
                'name': 'Sample Item {} from {}'.format(i + 1, city),
                'value': i * 10
            }
            container.create_item(body=item)
            items.append(item)
    print('Created {} items'.format(len(items)))
    return items


def read_feed_ranges(container):
    """Demonstrates reading all feed ranges from a container.

    Feed ranges represent the partitioning of your container's data. The number of feed ranges
    corresponds to the number of physical partitions backing your container. As your data grows
    and partitions split, the number of feed ranges may increase.
    """
    print('\n--- 1. Reading feed ranges from the container ---\n')

    # read_feed_ranges() returns an iterable of feed range dicts.
    # Each feed range represents a scope within the container.
    feed_ranges = list(container.read_feed_ranges())

    print('Container has {} feed range(s):'.format(len(feed_ranges)))
    for i, feed_range in enumerate(feed_ranges):
        # Feed ranges are opaque dict values. You can serialize them with json.dumps() for
        # storage or logging, but should not parse or construct them manually.
        print('  Feed range {}: {}'.format(i + 1, json.dumps(feed_range)))

    # You can force a refresh of the cached partition key ranges if needed
    # (e.g., after a partition split):
    refreshed_feed_ranges = list(container.read_feed_ranges(force_refresh=True))
    print('\nAfter force refresh: {} feed range(s)'.format(len(refreshed_feed_ranges)))

    return feed_ranges


def feed_range_from_partition_key(container):
    """Demonstrates getting a feed range for a specific partition key value.

    This is useful when you need a feed range representation of a single partition key,
    for example to use with is_feed_range_subset() or to scope a change feed query.
    """
    print('\n--- 2. Getting feed ranges from partition key values ---\n')

    feed_ranges_by_pk = {}
    for city in PARTITION_KEY_VALUES:
        # Convert a partition key value to its corresponding feed range
        feed_range = container.feed_range_from_partition_key(city)
        feed_ranges_by_pk[city] = feed_range
        print('Feed range for partition key "{}": {}'.format(city, json.dumps(feed_range)))

    # You can also get a feed range for a None partition key (JSON null)
    null_feed_range = container.feed_range_from_partition_key(None)
    print('\nFeed range for None partition key: {}'.format(json.dumps(null_feed_range)))

    return feed_ranges_by_pk


def check_feed_range_subset(container, feed_ranges_by_pk):
    """Demonstrates checking if one feed range is a subset of another.

    This is useful for determining which container-level feed range contains a specific
    partition key's feed range, enabling scenarios like routing operations to the correct
    worker in a fan-out architecture.
    """
    print('\n--- 3. Checking feed range subset relationships ---\n')

    # Read all container-level feed ranges (these cover the full container)
    container_feed_ranges = list(container.read_feed_ranges())
    print('Container has {} feed range(s)'.format(len(container_feed_ranges)))

    # For each partition key, find which container feed range contains it
    for city, pk_feed_range in feed_ranges_by_pk.items():
        for i, container_fr in enumerate(container_feed_ranges):
            # is_feed_range_subset checks if 'child' is fully contained within 'parent'
            is_subset = container.is_feed_range_subset(
                parent_feed_range=container_fr,
                child_feed_range=pk_feed_range
            )
            if is_subset:
                print('Partition key "{}" belongs to container feed range {}'.format(city, i + 1))
                break

    # Verify that each container feed range is a subset of itself
    print('\nEach container feed range is a subset of itself:')
    for i, fr in enumerate(container_feed_ranges):
        assert container.is_feed_range_subset(fr, fr), "A feed range should be a subset of itself"
        print('  Feed range {} is a subset of itself: True'.format(i + 1))


def query_items_with_feed_range(container):
    """Demonstrates querying items scoped to individual feed ranges.

    By reading all feed ranges and querying each one separately, you can parallelize
    query execution across multiple workers. Each worker processes a distinct subset
    of the container's data with no overlap.

    Note: feed_range and partition_key are mutually exclusive parameters in query_items().
    """
    print('\n--- 4. Querying items scoped to feed ranges ---\n')

    feed_ranges = list(container.read_feed_ranges())
    all_items = []

    for i, feed_range in enumerate(feed_ranges):
        print('Querying items in feed range {}...'.format(i + 1))

        # Use the feed_range keyword to scope the query to a specific feed range.
        # This replaces the need for enable_cross_partition_query when you want to
        # process data in parallel across feed ranges.
        items = list(container.query_items(
            query="SELECT c.id, c.city, c.name FROM c",
            feed_range=feed_range
        ))

        print('  Found {} items'.format(len(items)))
        for item in items:
            print('    - {} (city: {})'.format(item['id'], item['city']))

        all_items.extend(items)

    print('\nTotal items across all feed ranges: {}'.format(len(all_items)))
    print('(This should equal the total number of items in the container)')


def query_items_with_feed_range_from_pk(container):
    """Demonstrates querying items using a feed range derived from a partition key.

    You can convert a partition key to a feed range and use it with query_items().
    This is functionally equivalent to using the partition_key parameter, but gives
    you a feed range that can also be used with is_feed_range_subset() or stored
    for later use.
    """
    print('\n--- 5. Querying items with a feed range from a partition key ---\n')

    target_city = 'Seattle'

    # Get the feed range for a specific partition key
    feed_range = container.feed_range_from_partition_key(target_city)
    print('Feed range for "{}": {}'.format(target_city, json.dumps(feed_range)))

    # Query using feed_range - returns items from that partition key's scope
    items_via_feed_range = list(container.query_items(
        query="SELECT c.id, c.city FROM c",
        feed_range=feed_range
    ))

    # Compare with query using partition_key directly
    items_via_partition_key = list(container.query_items(
        query="SELECT c.id, c.city FROM c",
        partition_key=target_city
    ))

    print('Items found via feed_range:    {}'.format(len(items_via_feed_range)))
    print('Items found via partition_key:  {}'.format(len(items_via_partition_key)))
    print('Results match: {}'.format(
        sorted([i['id'] for i in items_via_feed_range]) ==
        sorted([i['id'] for i in items_via_partition_key])
    ))

    # Note: Using both feed_range and partition_key together will raise a ValueError
    print('\nNote: feed_range and partition_key are mutually exclusive.')
    try:
        list(container.query_items(
            query="SELECT * FROM c",
            feed_range=feed_range,
            partition_key=target_city
        ))
    except ValueError as e:
        print('Expected error when using both: {}'.format(e))


def change_feed_with_feed_range(container):
    """Demonstrates consuming the change feed scoped to a specific feed range.

    By using feed_range with query_items_change_feed(), you can process changes for a
    subset of your container's data. This is useful when you want to process changes
    for a specific partition or range of partitions without consuming the entire change feed.

    Note: feed_range, partition_key, and partition_key_range_id are mutually exclusive
    parameters in query_items_change_feed().
    """
    print('\n--- 6. Change feed scoped to a feed range ---\n')

    # Get a feed range for a specific partition key
    target_city = 'Portland'
    feed_range = container.feed_range_from_partition_key(target_city)
    print('Consuming change feed for partition key "{}"...'.format(target_city))

    # Read change feed from the beginning, scoped to this feed range
    response = container.query_items_change_feed(
        feed_range=feed_range,
        start_time="Beginning"
    )

    change_count = 0
    for item in response:
        change_count += 1
        if change_count <= 5:  # Print first 5 for brevity
            print('  Changed item: {} (city: {})'.format(item.get('id', 'N/A'), item.get('city', 'N/A')))

    if change_count > 5:
        print('  ... and {} more items'.format(change_count - 5))
    print('Total changes in feed range: {}'.format(change_count))


def parallel_change_feed_processing(container):
    """Demonstrates the pattern for parallel change feed processing using feed ranges.

    This is one of the most powerful use cases for feed ranges: distributing change feed
    processing across multiple workers. Each worker is assigned one or more feed ranges
    and processes changes independently, with no overlap between workers.

    In this sample, we simulate the parallel pattern synchronously. In a real application,
    each feed range would be processed by a separate thread, process, or machine.
    """
    print('\n--- 7. Parallel change feed processing with feed ranges ---\n')

    # Step 1: Read all feed ranges for the container
    feed_ranges = list(container.read_feed_ranges())
    print('Container has {} feed range(s) to distribute across workers'.format(len(feed_ranges)))

    # Step 2: Each "worker" processes changes for its assigned feed range
    total_changes = 0
    for worker_id, feed_range in enumerate(feed_ranges):
        print('\n[Worker {}] Processing change feed for feed range: {}'.format(
            worker_id, json.dumps(feed_range)[:80] + '...'
        ))

        # Each worker reads the change feed for its assigned feed range
        response = container.query_items_change_feed(
            feed_range=feed_range,
            start_time="Beginning"
        )

        worker_changes = 0
        partition_keys_seen = set()
        for item in response:
            worker_changes += 1
            partition_keys_seen.add(item.get('city', 'unknown'))

        print('[Worker {}] Processed {} changes covering partition keys: {}'.format(
            worker_id, worker_changes, partition_keys_seen
        ))
        total_changes += worker_changes

    print('\nTotal changes across all workers: {}'.format(total_changes))
    print('Each item was processed by exactly one worker (no duplicates, no gaps)')


def run_sample():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})

    try:
        # Setup database and container
        try:
            db = client.create_database(id=DATABASE_ID)
        except exceptions.CosmosResourceExistsError:
            db = client.get_database_client(DATABASE_ID)

        try:
            container = db.create_container(
                id=CONTAINER_ID,
                partition_key=PartitionKey(path='/city'),
                offer_throughput=400
            )
            print('Container with id \'{0}\' created'.format(CONTAINER_ID))
        except exceptions.CosmosResourceExistsError:
            container = db.get_container_client(CONTAINER_ID)
            print('Container with id \'{0}\' already exists'.format(CONTAINER_ID))

        # Create sample data
        create_sample_items(container)

        # 1. Read feed ranges from the container
        feed_ranges = read_feed_ranges(container)

        # 2. Get feed ranges from partition key values
        feed_ranges_by_pk = feed_range_from_partition_key(container)

        # 3. Check feed range subset relationships
        check_feed_range_subset(container, feed_ranges_by_pk)

        # 4. Query items scoped to feed ranges
        query_items_with_feed_range(container)

        # 5. Query items using a feed range derived from a partition key
        query_items_with_feed_range_from_pk(container)

        # 6. Read change feed scoped to a feed range
        change_feed_with_feed_range(container)

        # 7. Parallel change feed processing using feed ranges
        parallel_change_feed_processing(container)

        # Cleanup
        try:
            client.delete_database(db)
        except exceptions.CosmosResourceNotFoundError:
            pass

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == '__main__':
    run_sample()
