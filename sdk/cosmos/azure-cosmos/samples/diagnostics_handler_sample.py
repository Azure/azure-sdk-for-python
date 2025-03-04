import logging, os
from typing import Dict, Callable, Any
from azure.cosmos import CosmosClient, PartitionKey, cosmos_diagnostics_handler

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

