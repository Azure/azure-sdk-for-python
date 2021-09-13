import sys
from time import time
sys.path.append(r"C:\Users\simonmoreno\Repos\azure-sdk-for-python\sdk\cosmos\azure-cosmos")


import asyncio
import time
from azure.cosmos.aio.cosmos_client import CosmosClient as AsyncClient
from azure.cosmos.cosmos_client import CosmosClient as SyncClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

endpoint = ''
key = ''

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

def create_test(db_name, cont_name, num):
    client = SyncClient(endpoint, key)
    db = client.create_database(id=db_name)
    container = db.create_container(
        id=cont_name,
		partition_key=PartitionKey(path="/id"))
    ids = []
    for i in range(num):
        body = get_test_item()
        ids.append(body.get("id"))
        container.create_item(body=body)
    print("Created {} items in {} DB successfully".format(num, db_name))
    return ids

def timed_sync_create(db_name, cont_name, num):
    client = SyncClient(endpoint, key)
    db = client.create_database(id=db_name)
    container = db.create_container(
        id=cont_name,
		partition_key=PartitionKey(path="/id"))
    ids = []
    start = time.time()
    for i in range(num):
        body = get_test_item()
        ids.append(body.get("id"))
        container.create_item(body=body)
    print("Sync client created {} items in {} seconds".format(num, time.time() - start))
    return ids

async def timed_async_create(db_name, cont_name, num):
    async with AsyncClient(endpoint, key) as client:
        db = await client.create_database_if_not_exists(id=db_name)
        cont = await db.create_container_if_not_exists(
            id=cont_name,
            partition_key=PartitionKey(path="/id"))
        ids = []
        start = time.time()
        for i in range(num):
            body = get_test_item()
            ids.append(body.get("id"))
            await cont.create_item(body=body)
    print("Async client created {} items in {} seconds".format(num, time.time() - start))
    return ids

def timed_sync_read(db2, cont2, num, ids):
    client = SyncClient(endpoint, key)
    db = client.get_database_client(db2)
    cont = db.get_container_client(cont2)
    start = time.time()
    for id in ids:
        x = cont.read_item(item=id, partition_key=id)
        if not x:
            print("Error retrieving item {}".format(id))
    print("Sync client retrieved {} items in {} seconds".format(num, time.time() - start))

async def timed_async_read(db1, cont1, num, ids):
	async with AsyncClient(endpoint, key) as client:
		db = client.get_database_client(db1)
		cont = db.get_container_client(cont1)
		start = time.time()
		for id in ids:
			x = await cont.read_item(item=id, partition_key=id)
			if not x:
				print("Error retrieving item {}".format(id))
		print("Async client retrieved {} items in {} seconds".format(num, time.time() - start))

async def read_tests():
    db = "db01"
    cont = "c01"
    num = 1000
    ids = create_test(db, cont, num)
    timed_sync_read(db,cont,num,ids)
    await timed_async_read(db,cont,num,ids)

async def create_tests():
    db1, db2 = "db01", "db02"
    cont1, cont2 = "c01", "c02"
    num = 10
    ids1 = timed_sync_create(db1,cont1,num)
    ids2 = await timed_async_create(db2,cont2,num)
    print(len(ids1) == len(ids2))

def user_test():
    client = SyncClient(endpoint, key)
    db = client.get_database_client("xusud")
    use = db.get_user_client(user="testid")
    data = use.read()
    print(data)
    perms = use.list_permissions()
    print(list(perms))

async def main():
    # await read_tests()
    await create_tests()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())