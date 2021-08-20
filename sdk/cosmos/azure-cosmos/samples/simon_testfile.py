import sys
sys.path.append(r"C:\Users\simonmoreno\Repos\azure-sdk-for-python\sdk\cosmos\azure-cosmos")


from azure.cosmos import container
from azure.core.tracing.decorator import distributed_trace
import asyncio
from azure.cosmos import partition_key, cosmos_client
from azure.cosmos.aio.cosmos_client import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos.database import DatabaseProxy

import config
import heroes

endpoint = ''
key = ''

def creation():

	# <create_cosmos_client>
	client = CosmosClient(endpoint, key)
	# </create_cosmos_client

	# Create a database
	# <create_database_if_not_exists>
	database_name = 'MockHeroesDatabase'
	database = client.create_database_if_not_exists(id=database_name)
	# </create_database_if_not_exists>

	container_name = 'mockHeroesContainer'
	container = database.create_container_if_not_exists(
		id=container_name, 
		partition_key=PartitionKey(path="/lastName"),
		offer_throughput=400
	)

	real_heroes = [heroes.get_superman(), heroes.get_batman(), heroes.get_flash(), heroes.get_spider(), heroes.get_iron()]
	generics = [heroes.get_generic_hero(), heroes.get_generic_hero(), heroes.get_generic_hero()]

	for hero in real_heroes:
		container.create_item(body=hero)

	for generic in generics:
		container.create_item(body=generic)

	for hero in real_heroes:
		response = container.read_item(item=hero['id'], partition_key=hero['lastName'])
		request_charge = container.client_connection.last_response_headers['x-ms-request-charge'] #!
		if hero['id'] == 'Superman': print(container.client_connection.last_response_headers)
		print('Read item with id {0}. Operation consumed {1} request units'.format(response['id'], (request_charge)))

	query = "SELECT * FROM c WHERE c.lastName IN ('Kent', 'Parker')"

	items = list(container.query_items(
		query=query,
		enable_cross_partition_query=True #!
	))

	request_charge = container.client_connection.last_response_headers['x-ms-request-charge'] #!
	print('Query returned {0} items. Operation consumed {1} request units'.format(len(items), request_charge))

def clean_heroes():
	client = CosmosClient(endpoint, key)
	database_name = 'MockHeroesDatabase'
	database = client.get_database_client(database_name)
	container_name = 'mockHeroesContainer'
	container = database.get_container_client(container_name)
	real_heroes = [heroes.get_superman(), heroes.get_batman(), heroes.get_flash(), heroes.get_spider(), heroes.get_iron()]
	for h in real_heroes:
		response = container.delete_item(h['id'], partition_key=h['lastName'])
		print(response)

def destroy():
	client = CosmosClient(endpoint, key)
	database_name = 'MockHeroesDatabase'
	response = client.delete_database(database_name)
	print(f"Database with name {database_name} has been deleted.")
	print(response)

async def createaio():
	client = CosmosClient(endpoint, key)
	database_name = 'MockHeroesDatabase'
	database = client.create_database_if_not_exists(id=database_name)

	container_name = 'mockHeroesContainer'
	container = database.create_container_if_not_exists(
		id=container_name,
		partition_key=PartitionKey(path="/lastName"),
		offer_throughput=400
	)

	real_heroes = [heroes.get_superman(), heroes.get_batman(), heroes.get_flash(), heroes.get_spider(), heroes.get_iron()]
	generics = [heroes.get_generic_hero(), heroes.get_generic_hero(), heroes.get_generic_hero()]

	for hero in real_heroes:
		await container.create_item_aio(body=hero)

	# for generic in generics:
	# 	container.create_item_aio(body=generic)

def get_db():
	client = CosmosClient(endpoint, key)
	database_name = 'MockHeroesDatabase'
	res = client.get_database_client(database_name).list_containers()
	r= client.get_database_client('lols').list_containers()
	x = client.get_database_client.three

	print(res)
	print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
	print(r)
	print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")

	# for i in res:
	# 	print(i)
	for i in res:
		print("CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC")
		print(i)

# asyncio.run(createaio())

# creation()

import uuid

def get_test_item():
    async_item = {
    'id': 'Async_' + str(uuid.uuid4()),
    'address': {
        'state': 'WA',
        'city': 'Redmond',
        'street': '1 Microsoft Way'
    },
    'test_object': True
    }
    return async_item

def create_test():
    client = cosmos_client.CosmosClient(endpoint, key)
    db = client.create_database(id="AsyncDB")
    container = db.create_container(
        id="AsyncContainer",
		partition_key=PartitionKey(path="/id"))
    ids = []
    for i in range(20):
        body = get_test_item()
        print(body.get("id"))
        ids.append(body.get("id"))
        container.create_item(body=body)
    return ids

async def async_read_test():
	# ids = create_test()
	client = CosmosClient(endpoint, key)
	# db = client.get_database_client(id="AsyncDB")
	# container = db.get_container_client(id="AsyncContainer")
	# print(container.read())



asyncio.run(async_read_test())