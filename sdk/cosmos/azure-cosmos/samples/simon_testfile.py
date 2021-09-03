import sys
from time import time
sys.path.append(r"C:\Users\simonmoreno\Repos\azure-sdk-for-python\sdk\cosmos\azure-cosmos")


import asyncio
import time
from azure.cosmos.aio.cosmos_client import CosmosClient as AsyncClient
from azure.cosmos.cosmos_client import CosmosClient as SyncClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

endpoint = 'https://simonmoreno-sql.documents.azure.com:443/'
key = 'ix7V0n09yDyiUarBkQnDRAqBwkxXMM6iGq7FlDHmHRlHZPUDRnBu55Vx2gwzd2Mkh6Qyrc8VnJWR6djgnkl8cw=='

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

async def async_read_test(db_name, cont_name, num):
	ids = create_test(db_name, cont_name, num)
	client = AsyncClient(endpoint, key)
	if client: print(client)
	db = client.get_database_client(db_name)
	if db: print(db)
	x = await db.read()
	print(x)
	await client.close()

async def with_read_test(db_name, cont_name, item_name):
	async with AsyncClient(endpoint, key) as client:
		print(client)
		db = client.get_database_client(db_name)
		if db: print(db)
		x = await db.read()
		print(x)
		cont = db.get_container_client(cont_name)
		if cont: print(cont)
		x = await cont.read()
		print(x)
		x = await cont.read_item(item=item_name, partition_key=item_name)
		print(x)

def timed_sync(db2, cont2, num, ids):
    client = SyncClient(endpoint, key)
    db = client.get_database_client(db2)
    cont = db.get_container_client(cont2)
    start = time.time()
    for id in ids:
        x = cont.read_item(item=id, partition_key=id)
        if not x:
            print("Error retrieving item {}".format(id))
    print("Sync client retrieved {} items in {} seconds".format(num, time.time() - start))

async def timed_async(db1, cont1, num, ids):
	async with AsyncClient(endpoint, key) as client:
		db = client.get_database_client(db1)
		cont = db.get_container_client(cont1)
		start = time.time()
		for id in ids:
			x = await cont.read_item(item=id, partition_key=id)
			if not x:
				print("Error retrieving item {}".format(id))
		print("Async client retrieved {} items in {} seconds".format(num, time.time() - start))

async def main():
    db = "db01"
    cont = "c01"
    num = 100000
    ids = create_test(db, cont, num)
    timed_sync(db,cont,num,ids)
    await timed_async(db,cont,num,ids)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())