# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import logging, os
from typing import Dict, Callable, Any
from azure.cosmos import CosmosClient, PartitionKey, exceptions

endpoint = os.environ["ACCOUNT_URI"]
key = os.environ["ACCOUNT_KEY"]
# Sample usage of using logging filters for diagnostics filtering
# You can filter based on request and response related attributes that are added to the log record
class CosmosStatusCodeFilter(logging.Filter):
    def filter(self, record):
        ret = (hasattr(record, 'status_code') and record.status_code > 400
               and not (record.status_code in [404, 409, 412] and getattr(record, 'sub_status_code', None) in [0, None])
               and hasattr(record, 'duration') and record.duration > 1000)
        return ret
# Initialize the logger
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('diagnostics1.output')
logger.addHandler(file_handler)
# When using the logging filter, you can set the filter directly on the logger
logger.addFilter(CosmosStatusCodeFilter())
# Initialize the Cosmos client with diagnostics enabled, no need to pass a diagnostics handler
client = CosmosClient(endpoint, key, logger=logger, enable_diagnostics_logging=True)
# Create a database and container
database_name = 'SD'
database = client.create_database_if_not_exists(id=database_name)
container_name = 'SampleContainer'
partition_key = PartitionKey(path=['/State', '/City'])
container = database.create_container_if_not_exists(id=container_name, partition_key=partition_key,
                                                    offer_throughput=400)
items = [
    {'id': '1', 'State': 'California', 'City': 'Los Angeles', 'city_level': 1},
    {'id': '2', 'State': 'Texas', 'City': 'Houston', 'city_level': 2},
    {'id': '3', 'State': 'New York', 'City': 'New York City', 'city_level': 3}
]
# Attempt to read nonexistent items to cause a 404 error
for item in items:
    try:
        container.read_item(item=str(item['id']), partition_key=[str(item['State']), str(item['City'])])
    except exceptions.CosmosHttpResponseError:
        pass

# When using the async client it can also be possible to use the logging filter with a queue logger handler
import asyncio
import queue
from queue import Queue
import logging.handlers
from azure.cosmos.aio import CosmosClient as CosmosAsyncClient
async def log_cosmos_operations():
    # Initialize the logger
    logger = logging.getLogger('azure.cosmos')
    logger.setLevel(logging.INFO)
    # Create a queue
    log_queue: Queue = queue.Queue(-1)
    # Set up the QueueHandler
    queue_handler = logging.handlers.QueueHandler(log_queue)
    # Set up the QueueListener with a FileHandler
    file_handler = logging.FileHandler('diagnostics2.output')
    file_handler.setLevel(logging.INFO)
    queue_listener = logging.handlers.QueueListener(log_queue, file_handler)
    # Configure the root logger
    logging.basicConfig(level=logging.INFO, handlers=[queue_handler])
    # Add the filter to the logger
    logger.addFilter(CosmosStatusCodeFilter())
    # Start the QueueListener
    queue_listener.start()
    # Initialize the Cosmos client with diagnostics enabled, no need to pass a diagnostics handler
    async with CosmosAsyncClient(endpoint, key, logger=logger, enable_diagnostics_logging=True) as client:
        # Create a database and container
        database_name = 'SD'
        database = await client.create_database_if_not_exists(id=database_name)
        container_name = 'SampleContainer'
        partition_key = PartitionKey(path=['/State', '/City'])
        container = await database.create_container_if_not_exists(id=container_name, partition_key=partition_key,
                                                                  offer_throughput=400)
        # Attempt to read nonexistent items to cause a 404 error
        for item in items:
            try:
                await container.read_item(item=str(item['id']), partition_key=[str(item['State']), str(item['City'])])
            except exceptions.CosmosHttpResponseError:
                pass
        # Stop the QueueListener
        queue_listener.stop()

# Run the async method
asyncio.run(log_cosmos_operations())


