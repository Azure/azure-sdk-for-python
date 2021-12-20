import time
import random
from azure.cosmos.cosmos_client import CosmosClient as SyncClient
from azure.cosmos.partition_key import PartitionKey

endpoint = ''
key = ''
DATABASE_ID = 'dbid'
CONTAINER_ID = 'containerid'

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
        'lastName': 'Smith',
        'attr1': random.randint(0, 100)
    }
    return async_item


def partition_split_test():
    client = SyncClient(endpoint, key)
    db = client.create_database_if_not_exists(DATABASE_ID)
    container = db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path="/id"))
    print("creating items")
    start = time.time()
    for i in range(15000):
        body = get_test_item()
        container.create_item(body=body)
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
    while True:
        ret_list = list()
        try:
            query = 'SELECT * FROM  c WHERE c.attr1="' + str(random.randint(0, 100)) + '" order by c.attr1'
            ret_list.append(list(container.query_items(query=query, enable_cross_partition_query=True)))
            success += 1
            if success == 2000 or success == 4000:  # Error should happen at around 2.6k query requests made
                print("Successful queries: {}".format(success))
            if success == 5000:
                print("5k queries succeeded - there's either no error or it's not being raised properly")
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


def main():
    partition_split_test()


if __name__ == "__main__":
    main()
