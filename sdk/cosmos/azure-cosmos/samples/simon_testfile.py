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
    'test_object': True,
    'lastName': 'Smith'
    }
    return async_item

async def async_crud_test():
    db_name = "crudAsync"
    cont_name = "cont"
    ttl = 200
    async with AsyncClient(endpoint, key) as client:
        db = await client.create_database(db_name)
        print("Created DB, now reading and attempting create_if_not_exist")

        await db.read()
        db = await client.create_database_if_not_exists(db_name)
        print("Create if not exist had no problems, deleting DB now")

        await client.delete_database(db_name)
        print("DB deleted, now attempting read")
        try:
            await db.read()
        except:
            print("Error returned successfully for reading DB")

        print("Re-creating DB for testing container methods")
        db = await client.create_database_if_not_exists(db_name)
        cont = await db.create_container(id=cont_name, partition_key=PartitionKey(path="/lastName"))
        print("Created container, now reading and attempting create_if_not_exists")

        c = await cont.read()
        cont = await db.create_container_if_not_exists(id=cont_name, partition_key=PartitionKey(path="/lastName"))
        print("Create if not exist had no problems, replacing and deleting container now")

        assert c.get('defaultTtl') is None
        await db.replace_container(container=cont_name, partition_key=PartitionKey(path='/lastName'), default_ttl=ttl)
        c = await cont.read()
        assert c.get('defaultTtl') == 200
        print("Container properties changed, now deleting")

        await db.delete_container(cont_name)
        print("Container deleted, now attempting read")
        try:
            await cont.read()
        except:
            print("Error returned succesfully")

        print("Re-creating container for testing item methods")
        cont = await db.create_container_if_not_exists(id=cont_name, partition_key=PartitionKey(path="/lastName"))

        body1 = get_test_item()
        await cont.create_item(body=body1)
        print("Created item, now reading and then upserting/replacing")

        body2 = get_test_item()
        await cont.upsert_item(body=body1)
        # Check here for read all items and verify there is still only 1 left after upsert
        await cont.replace_item(item=body1["id"], body=body2)
        print("Item replaced, now attempting read")

        try:
            await cont.read_item(item=body1.get("id"), partition_key=body1.get("lastName"))
        except:
            print("Error returned succesfully, reading and deleting replaced item now")

        await cont.read_item(item=body2.get("id"), partition_key=body2.get("lastName"))
        await cont.delete_item(item=body2.get("id"), partition_key=body2.get("lastName"))
        print("Item deleted, now attempting read")

        try:
            await cont.read_item(item=body2.get("id"), partition_key=body2.get("lastName"))
        except:
            print("Error returned succesfully, cleaning up account now")
        await client.delete_database(db_name)
        try:
            await db.read()
        except:
            print("All cleaned up")

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
    u = db.get_user_client(user="testid")
    data = u.read()
    print(data)
    perms = u.list_permissions()
    print(list(perms))

async def qta():
    async with AsyncClient(endpoint, key) as client:
        db = await client.create_database_if_not_exists("qta")
        cont = await db.create_container_if_not_exists(id="qtac", partition_key=PartitionKey(path="/id"))
        itemId = "Async_e402afa6-badf-43f2-8ddd-83776221cb3a"
        print("attempting query")

        y = await cont.read_offer()
        print(type(y))
        print(y)
        print(y.properties)
        print(y.offer_throughput)

        print("replacing")
        x = await cont.replace_throughput(throughput=400)
        print(type(x))
        print(x.properties)
        print(x.offer_throughput)

        z = cont.list_conflicts()
        print(type(z))
        print(z)

        # query = "SELECT * FROM c WHERE c.id=@id"
        # items = cont.query_items(
        #     query=query,
        #     parameters=[{"name":"@id", "value": itemId}],
        #     enable_cross_partition_query=True)

        # async for item in items:
        #     print(item)


        # x = cont.read_all_items()
        # #async for item in items
        # #
        # async for item in x:
        #     print(item)

def qt():
    client = SyncClient(endpoint, key)
    db = client.create_database_if_not_exists(id="qt")
    container = db.create_container_if_not_exists(
        id="qtc",
		partition_key=PartitionKey(path="/id"))

# async def read_all():
#     async with AsyncClient(endpoint, key) as client:
#         db = await client.create_database_if_not_exists("readall")
#         cont = await db.create_container_if_not_exists("cont", PartitionKey(path='/lastName'))
#         for i in range(5):
#             await cont.create_item(body=get_test_item())
#         c = await cont.read_all_items()
#         print(await c.__anext__())
#         print(type(c))

async def main():
    # await read_tests()
    # await async_crud_test()
    await qta()
    qt()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())