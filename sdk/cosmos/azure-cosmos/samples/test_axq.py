import time
import random
import asyncio
import uuid
from azure.cosmos.aio.cosmos_client import CosmosClient as AsyncClient
from azure.cosmos.partition_key import PartitionKey

endpoint = ''
key = ''
DATABASE_ID = 'dbid'
CONTAINER_ID = 'containerid'


def get_test_item():
    async_item = {
        'id': 'Async_' + str(uuid.uuid4()),
        'address': {
            'state': 'WA',
            'city': 'Redmond',
            'street': '1 Microsoft Way'
        },
        'test_object': True,
        'lastName': 'Smith',
        'attr1': random.randint(0, 100)
    }
    return async_item


async def partition_split_test():
    async with AsyncClient(endpoint, key) as client:
        db = await client.create_database_if_not_exists(DATABASE_ID)
        container = await db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path="/id"))
        print("creating items")
        start = time.time()
        for i in range(15000):
            body = get_test_item()
            await container.create_item(body=body)
            if i == 5000 or i == 10000:
                print("created 5k items")
        print("15k items took {} seconds".format(time.time() - start))
        success, errors = 0, 0
        print("--------------------------------")
        print("created items, waiting 4m before queries")
        print("change offer to 11k manually")
        print("--------------------------------")
        time.sleep(240)
        print("now starting queries")
        body, i = None, None
        ret_list = list()
        while True:
            try:
                curr = str(random.randint(0, 100))
                query = 'SELECT * FROM  c WHERE c.attr1="' + curr + '" order by c.attr1'
                curr_list = [item async for item in container.query_items(query=query, enable_cross_partition_query=True)]
                ret_list.append((curr, curr_list))
                success += 1
                if success == 1000:
                    print("1000 queries succeeded - there's either no error or it's not being raised properly")
                    print("list length: {}".format(len(ret_list)))
                    for ret in ret_list:
                        curr = ret[0]
                        for results in ret[1]:
                            id_number = results['id'].split("_")[1]
                            assert id_number == curr  # verify that all results match their randomly generated ids
                    print("validation succeeded for all results")
                    return
                # Use breakpoint to stop execution, change provisioned RUs on container
                # Increase to >10k RUs causes partition split (11k to be safe)
            except Exception as e:
                print("final successes: {}".format(success))
                print("returned error to main test file")
                print(e)
                errors += 1
                print("Successes: {}, Errors: {}".format(success, errors))
                raise


async def main():
    await partition_split_test()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
