import sys
sys.path.append(r"C:\Users\simonmoreno\Repos\azure-sdk-for-python\sdk\cosmos\azure-cosmos")

import uuid
import asyncio
import azure.cosmos.cosmos_client as SyncClient
import azure.cosmos.aio.cosmos_client as AsyncClient
from azure.cosmos import PartitionKey, database, partition_key

url = 'https://simonmoreno-sql1.documents.azure.com:443/'
k = 'SXXGlx0lzKiZRjF4rQzpfDDMHC7N50GE0s2GQdlNlQxQmOfVdMTg8HWSKKIsODPD15daOrSDOgb3EzktZ67dCQ=='
url1='https://localhost:8081'
k1='C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=='
db_name='testi5'
c_name='c23'

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

def get_test_item2():
    async_item = {
    'id': 'AsyncBoy',
    'address': {
        'state': 'WA',
        'city': 'Redmond',
        'street': '1 Microsoft Way'
    },
    'test_object': True,
    'lastName': 'Smith'
    }
    return async_item

async def get_query_types():
    client = AsyncClient.CosmosClient(url, k)
    db = await client.create_database_if_not_exists(id=db_name)
    container = await db.create_container_if_not_exists(id=c_name, partition_key=PartitionKey(path="/lastName"))
    for i in range(25):
        await container.create_item(get_test_item())

    w = container.query_items_change_feed()
    print(type(w))

    await client.delete_database(db_name)
    await client.close()

async def qte():
    client = AsyncClient.CosmosClient(url, k)
    db = await client.create_database_if_not_exists(id=db_name)
    container = await db.create_container_if_not_exists(id=c_name, partition_key=PartitionKey(path="/lastName"))
    for i in range(29):
        await container.create_item(get_test_item())

    res = container.query_items(query="select * from c")
    # rus = container.list_conflicts()
    # lis = [item async for item in res]
    # print(len(lis))


    triger_body = {  
    "body": "function updateMetadata() {\r\n    var context = getContext();\r\n    var collection = context.getCollection();\r\n    var response = context.getResponse();\r\n   }",  
    "id": "PostTrigger-UpdateMetaAll4",  
    "triggerOperation": "All",  
    "triggerType": "Post"}

    c = container.scripts.list_triggers()

    

    x = await container.scripts.create_trigger(body=triger_body)

    print(await container.scripts.get_trigger("PostTrigger-UpdateMetaAll4"))

    y = await container.create_item(body = get_test_item2(), post_trigger_include='PostTrigger-UpdateMetaAll4')
    

    await client.delete_database(db_name)
    await client.close()
    print("done")


def stest():
    client = SyncClient.CosmosClient(url1,k1)
    db = client.create_database_if_not_exists(id=db_name)
    container = db.create_container_if_not_exists(id=c_name, partition_key=PartitionKey(path="/id"))
    container.create_item(get_test_item2())
    for i in range(10):
        container.create_item(get_test_item())
    # x = list(container.query_items(query="select * from c", partition_key="AsyncBoy"))
    # print(len(x))
    # x = list(container.query_items(query="select * from c"))
    # print(len(x))
    # x = list(container.read_all_items())
    # print(len(x))
    x = container.read_item(item="AsyncBoy", partition_key="AsyncBoy")
    print(x)
    print(type(x))
    return None

def stest2():
    client = SyncClient.CosmosClient(url1,k1)
    db = client.create_database_if_not_exists(id=db_name)
    container = db.create_container_if_not_exists(id=c_name, partition_key=PartitionKey(path="/id"))
    print(list(container.list_conflicts()))

async def atest():
    client = AsyncClient.CosmosClient(url, k)
    db = await client.create_database_if_not_exists(id=db_name)
    container = await db.create_container_if_not_exists(id=c_name, partition_key=PartitionKey(path="/id"))
    db.query_containers(query="select * from c")
    print("---------------------------------------")
    print(client.client_connection.last_response_headers)
    print("---------------------------------------")
    for i in range(25):
        await container.create_item(get_test_item())
    x = container.read_all_items()
    count = 0
    async for i in x:
        count+=1
    print(count)
    y = await container.query_items(query="select * from c")
    count = 0
    async for i in y:
        count+=1
    print(count)
    # c = await container.query_items(query="select * from c")
    print("---------------------------------------")
    print(client.client_connection.last_response_headers)
    await client.delete_database(db_name)
    await client.close()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(qte())
