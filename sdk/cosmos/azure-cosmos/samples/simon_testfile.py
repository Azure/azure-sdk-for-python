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

async def async_crud_test():
    db_name = "asyncccc"
    cont_name = "contttt"
    async with AsyncClient(endpoint, key) as client:
        db = await client.create_database(db_name)
        print("Created DB, now reading and attempting create_if_not_exist")
        print(await db.read())
        db = await client.create_database_if_not_exists(db_name)
        print("Create if not exist had no problems, deleting DB now")
        await client.delete_database(db_name)
        print("DB deleted, now attempting read")
        try:
            await db.read()
        except:
            print("Error returned successfully for reading DB")
        print("Re-creating DB for testing container")
        db = await client.create_database(db_name)
        cont = await db.create_container(id=cont_name, partition_key=PartitionKey(path="/id"))
        print("Created CONT, now reading and attempting create_if_not_exists")
        await cont.read()
        cont = await db.create_container_if_not_exists(id=cont_name, partition_key=PartitionKey(path="/id"))
        print("Create if not exist had no problems, deleting CONT now")
        await db.delete_container(cont_name)
        print("CONT deleted, now attempting read")
        try:
            await cont.read()
        except:
            print("Error returned succesfully")
        print("Re-creating CONT for testing items")
        cont = await db.create_container_if_not_exists(id=cont_name, partition_key=PartitionKey(path="/id"))
        body = get_test_item()
        await cont.create_item(body=body)
        print("created item, now reading")
        await cont.read_item(item=body.get("id"), partition_key=body.get("id"))
        print("now deleting item and attempting to read")
        await cont.delete_item(item=body.get("id"), partition_key=body.get("id"))
        try:
            await cont.read_item(item=body.get("id"), partition_key=body.get("id"))
        except:
            print("item delete failed successfully, now cleaning up")
        await client.delete_database(db_name)

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
    ids2 = await timed_async_create(db1,cont1,num)
    print(len(ids1) == len(ids2))

def user_test():
    client = SyncClient(endpoint, key)
    db = client.get_database_client("xusud")
    use = db.get_user_client(user="testid")
    data = use.read()
    print(data)
    perms = use.list_permissions()
    print(list(perms))

def wrong_test():
    client = SyncClient(endpoint, key)
    db = client.get_database_client("db01")
    cont = db.get_container_client("c01")
    cont.read()
    cont.read_item(item="Async_c7997ca0-69c8-46f3-a9a3-5d85f50bafdf")

async def main():
    # await read_tests()
    await async_crud_test()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())