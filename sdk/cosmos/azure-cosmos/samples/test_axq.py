import time
import random

import unittest
from unittest.mock import Mock, MagicMock, patch

from azure.cosmos.cosmos_client import CosmosClient as SyncClient
from azure.cosmos.partition_key import PartitionKey

connstring = ""
DATABASE_ID = 'integrateddbbb'
CONTAINER_ID = 'containerid'

import uuid


def get_test_item():
    async_item = {
        'id': 'Async_' + str(uuid.uuid4()),
        'test_object': True,
        'lastName': 'Smith',
        'attr1': random.randint(0, 50)
    }
    return async_item


def quick_test():
    print("starting")
    client = SyncClient.from_connection_string(conn_str=connstring)
    db = client.create_database_if_not_exists(DATABASE_ID)
    cont = db.create_container_if_not_exists(CONTAINER_ID, partition_key=PartitionKey(path="/id"))
    body = get_test_item()
    cont.create_item(body=body)

    @patch.object(cont.client_connection, '_CosmosClientConnection__Get')
    def get_headers():
        cont.read_item(item=body["id"], partition_key=body["id"], max_integrated_cache_staleness_in_ms=(1000 * 60))

    get_headers()

    client.delete_database(DATABASE_ID)


#
#     db = client.create_database_if_not_exists(id=DATABASE_ID)
#     container = db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path="/id"))
#
#     body = get_test_item()
#     container.create_item(body=body)
#
#     container.read_item(item=body["id"], partition_key=body["id"], max_integrated_cache_staleness_in_ms=(1000 * 60))
#     print(client.client_connection.last_response_headers)
#     assert client.client_connection.last_response_headers["x-ms-cosmos-cachehit"] == 'False'
#     assert int(client.client_connection.last_response_headers['x-ms-request-charge']) > 0
#
#     container.read_item(item=body["id"], partition_key=body["id"])
#     print(client.client_connection.last_response_headers)
#     assert client.client_connection.last_response_headers["x-ms-cosmos-cachehit"] == 'True'
#     assert int(client.client_connection.last_response_headers['x-ms-request-charge']) == 0
#
#     body = get_test_item()
#     container.create_item(body)
#     item_id = body["id"]
#     query = 'SELECT * FROM c'
#
#     # Initialize cache for single partition query read, and verify there is a cost to the query call
#     q = container.query_items(query=query, partition_key=item_id, max_integrated_cache_staleness_in_ms=(1000 * 30))
#     print(len(list(q)))
#     print(client.client_connection.last_response_headers)
#
#     q = container.query_items(query=query, partition_key=item_id, max_integrated_cache_staleness_in_ms=(1000 * 30))
#     print(len(list(q)))
#     print(client.client_connection.last_response_headers)
#
#     q = container.read_all_items(max_integrated_cache_staleness_in_ms=(1000 * 30))
#     print(client.client_connection.last_response_headers)
#
#     client.delete_database(DATABASE_ID)
#
#
if __name__ == '__main__':
    quick_test()
