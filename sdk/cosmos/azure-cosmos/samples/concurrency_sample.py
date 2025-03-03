# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
# These examples are ingested by the documentation system, and are
# displayed in the SDK reference documentation. When editing these
# example snippets, take into consideration how this might affect
# the readability and usability of the reference documentation.

import os
from azure.cosmos import PartitionKey, ThroughputProperties
from azure.cosmos.aio import CosmosClient
import asyncio
import time

# Specify information to connect to the client.
CLEAR_DATABASE = True
CONN_STR = os.environ['CONN_STR']
# Specify information for Database and container.
DB_ID = "Cosmos_Concurrency_DB"
CONT_ID = "Cosmos_Concurrency_Cont"
# specify partition key for the container
pk = PartitionKey(path="/id")

# Batch the creation of items for better optimization on performance.
# Note: Error handling should be in the method being batched. As you will get
# an error for each failed Cosmos DB Operation.
# Note: While the Word `Batch` here is used to describe the subsets of data being created, it is not referring
# to batch operations such as `Transactional Batching` which is a feature of Cosmos DB.
async def create_all_the_items(prefix, c, i):
    await asyncio.wait(
        [asyncio.create_task(c.create_item({"id": prefix + str(j)})) for j in range(100)]
    )
    print(f"Batch {i} done!")

# The following demonstrates the performance difference between using sequential item creation,
# sequential item creation in batches, and concurrent item creation in batches. This is to show best practice
# in using Cosmos DB for performance.
# It’s important to note that batching a bunch of operations can affect throughput/RUs.
# To avoid using resources, it’s recommended to test things on the emulator of Cosmos DB first.
# The performance improvement shown on the emulator is relative to what you will see on a live account
async def main():
    try:
        async with CosmosClient.from_connection_string(CONN_STR) as client:
            # For emulator: default Throughput needs to be increased
            # throughput_properties = ThroughputProperties(auto_scale_max_throughput=5000)
            # db = await client.create_database_if_not_exists(id=DB_ID, offer_throughput=throughput_properties)
            db = await client.create_database_if_not_exists(id=DB_ID)
            container = await db.create_container_if_not_exists(CONT_ID, partition_key=pk)

            # A: Sequential without batching
            timer = time.time()
            print("Starting Sequential Item Creation.")
            for i in range(20):
                for j in range(100):
                    await container.create_item({"id": f"{i}-sequential-{j}"})
                print(f"{(i + 1) * 100} items created!")
            sequential_item_time = time.time() - timer
            print("Time taken: " + str(sequential_item_time))


            # B: Sequential batches
            # Batching operations can improve performance by dealing with multiple operations at a time.
            timer = time.time()
            print("Starting Sequential Batched Item Creation.")
            for i in range(20):
                await create_all_the_items(f"{i}-sequential-Batch-", container, i)
            sequential_batch_time = time.time() - timer
            print("Time taken: " + str(sequential_batch_time))

            # C: Concurrent batches
            # By using asyncio with batching, we can create multiple batches of items concurrently, which means that
            # while one connection is waiting for IO (like waiting for data to arrive),
            # Python can switch context to another connection and make progress there.
            # This can lead to better utilization of system resources and can give the appearance of parallelism,
            # as multiple connections are making progress seemingly at the same time
            timer = time.time()
            print("Starting Concurrent Batched Item Creation.")
            await asyncio.wait(
                [asyncio.create_task(create_all_the_items(f"{i}-concurrent-Batch", container, i)) for i in range(20)]
            )
            concurrent_batch_time = time.time() - timer
            print("Time taken: " + str(concurrent_batch_time))

            # Calculate performance improvement on time metrics.
            sequential_per = round((sequential_item_time - sequential_batch_time / sequential_item_time) * 100, 2)
            print(f"Sequential Batching is {sequential_per}% faster than Sequential Item Creation")
            concurrent_per = round((sequential_item_time - concurrent_batch_time / sequential_item_time) * 100, 2)
            print(f"Concurrent Batching is {concurrent_per}% faster than Sequential Item Creation")

            item_list = [i async for i in container.read_all_items()]
            print(f"End of the test. Read {len(item_list)} items.")

    finally:
        if CLEAR_DATABASE:
            await clear_database()


async def clear_database():
    async with CosmosClient.from_connection_string(CONN_STR) as client:
        await client.delete_database(DB_ID)
    print(f"Deleted {DB_ID} database.")


if __name__ == "__main__":
    asyncio.run(main())

