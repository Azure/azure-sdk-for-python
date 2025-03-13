import logging, os
from typing import Dict, Callable, Any
from azure.cosmos import CosmosClient, PartitionKey, cosmos_diagnostics_handler, exceptions
from torch.multiprocessing.queue import Queue

# Initialize the logger
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('diagnostics1.output')
logger.addHandler(file_handler)
diagnostics_handler = cosmos_diagnostics_handler.CosmosDiagnosticsHandler()
diagnostics_handler["duration"] = lambda x: x > 20

# Initialize the Cosmos client with diagnostics handler
endpoint = os.environ["ACCOUNT_URI"]
key = os.environ["ACCOUNT_KEY"]
client = CosmosClient(endpoint, key,logger=logger, diagnostics_handler=diagnostics_handler, enable_diagnostics_logging=True)

# Create a database and container
database_name = 'SD'
database = client.create_database_if_not_exists(id=database_name)
container_name = 'SampleContainer'
partition_key = PartitionKey(path=['/State', '/City'])
container = database.create_container_if_not_exists(id=container_name, partition_key=partition_key, offer_throughput=400)

# Add 3 items to the container
items = [
    {'id': '1', 'State': 'California', 'City': 'Los Angeles', 'city_level': 1},
    {'id': '2', 'State': 'Texas', 'City': 'Houston', 'city_level': 2},
    {'id': '3', 'State': 'New York', 'City': 'New York City', 'city_level': 3}
]
for item in items:
    container.create_item(body=item)

# Delete the items
for item in items:
    container.delete_item(item=str(item['id']), partition_key=[str(item['State']), str(item['City'])])


# Custom should_log method
def should_log(self, **kwargs):
    duration = kwargs.get('duration')
    return duration and duration > 100

# Initialize the logger
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('diagnostics2.output')
logger.addHandler(file_handler)

# Initialize the Cosmos client with custom diagnostics handler
client = CosmosClient(endpoint, key,logger=logger, diagnostics_handler=should_log, enable_diagnostics_logging=True)

# Create a database and container
database_name = 'SD'
database = client.create_database_if_not_exists(id=database_name)
container_name = 'SampleContainer'
partition_key = PartitionKey(path=['/State', '/City'])
container = database.create_container_if_not_exists(id=container_name, partition_key=partition_key, offer_throughput=400)

# Add 3 items to the container
items = [
    {'id': '1', 'State': 'California', 'City': 'Los Angeles', 'city_level': 1},
    {'id': '2', 'State': 'Texas', 'City': 'Houston', 'city_level': 2},
    {'id': '3', 'State': 'New York', 'City': 'New York City', 'city_level': 3}
]
for item in items:
    container.create_item(body=item)

# Delete the items
for item in items:
    container.delete_item(item=str(item['id']), partition_key=[str(item['State']), str(item['City'])])


# Diagnostics handler dictionary
diagnostics_handler_dict: Dict[str, Callable[[Any], Any]] = {
    'duration': lambda duration: duration > 2000,
    'status code': (lambda x: (
                    isinstance(x, (list, tuple)) and x[0] >= 400) if isinstance(x, (list, tuple)) else x >= 400),
    'verb': lambda verb: verb in ['POST', 'DELETE'],
    'resource type': lambda resource_type: resource_type == 'item'
}

# Initialize the logger
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('diagnostics3.output')
logger.addHandler(file_handler)

# Initialize the Cosmos client with diagnostics handler dictionary
client = CosmosClient(endpoint, key,logger=logger, diagnostics_handler=diagnostics_handler_dict, enable_diagnostics_logging=True)

# Create a database and container
database_name = 'SD'
database = client.create_database_if_not_exists(id=database_name)
container_name = 'SampleContainer'
partition_key = PartitionKey(path=['/State', '/City'])
container = database.create_container_if_not_exists(id=container_name, partition_key=partition_key, offer_throughput=400)

# Add 3 items to the container
items = [
    {'id': '1', 'State': 'California', 'City': 'Los Angeles', 'city_level': 1},
    {'id': '2', 'State': 'Texas', 'City': 'Houston', 'city_level': 2},
    {'id': '3', 'State': 'New York', 'City': 'New York City', 'city_level': 3}
]
for item in items:
    container.create_item(body=item)

# Delete the items
for item in items:
    container.delete_item(item=str(item['id']), partition_key=[str(item['State']), str(item['City'])])

# Sample usage of using logging filters for diagnostics filtering
# The same filter parameters that are found in the cosmos_diagnostics_handler can be used in the logging filter
class CosmosStatusCodeFilter(logging.Filter):
    def filter(self, record):
        return hasattr(record, 'status_code') and record.status_code >= 400
# Initialize the logger
logger = logging.getLogger('azure.cosmos')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler('diagnostics4.output')
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
container = database.create_container_if_not_exists(id=container_name, partition_key=partition_key, offer_throughput=400)
# Attempt to read nonexistent items to cause a 404 error
for item in items:
    try:
        container.read_item(item=str(item['id']), partition_key=[str(item['State']), str(item['City'])])
    except exceptions.CosmosHttpResponseError:
        pass

# When using the async client it can also be possible to use the logging filter with a queue logger handler
import asyncio
import queue
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
    file_handler = logging.FileHandler('diagnostics5.output')
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
        container = await database.create_container_if_not_exists(id=container_name, partition_key=partition_key, offer_throughput=400)
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


