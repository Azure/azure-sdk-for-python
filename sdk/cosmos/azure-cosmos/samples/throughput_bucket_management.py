# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import uuid
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic throughput bucket operations at the client, database, container and item levels.
#
# 1. Setting throughput buckets at the Client Level
#
# 2. Setting Throughput Buckets at the Database Level
#    2.1 - Create and Delete Database
#
# 3. Setting Throughput Buckets at the Container Level
#    3.1 - Create container
#    3.2 - Query Container
#
# 4. Setting Throughput Buckets at the Item Level
#    4.1 - Read Item
#    4.2 - Create Item
# ----------------------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create (and delete) multiple Databases and Containers on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

# Applies throughput bucket 1 to all requests from a client application
def create_client_with_throughput_bucket(host=HOST, master_key=MASTER_KEY):
    cosmos_client.CosmosClient(host, master_key,
        throughput_bucket=1)

# Applies throughput bucket 2 to create and delete a database
def create_and_delete_database_with_throughput_bucket(client):
    created_db = client.create_database_if_not_exists(
        "test_db" + str(uuid.uuid4()),
        throughput_bucket=2)

    client.delete_database(
        created_db.id,
        throughput_bucket=2)

# Applies throughput bucket 3 to create a container
def create_container_with_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)

    created_container = database.create_container(
        str(uuid.uuid4()),
        PartitionKey(path="/pk"),
        throughput_bucket=3)

    database.delete_container(created_container.id)

# Applies throughput bucket 3 for requests to query containers
def query_containers_with_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)

    query = 'SELECT * from c'
    database.query_containers(
        query=query,
        throughput_bucket=3)

# Applies throughput bucket 4 for read item requests
def container_read_item_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)
    created_container = database.create_container(
        str(uuid.uuid4()),
        PartitionKey(path="/pk"))
    created_document = created_container.create_item(body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'})

    created_container.read_item(
         item=created_document['id'],
         partition_key="mypk",
         throughput_bucket=4)

    database.delete_container(created_container.id)

# Applies throughput bucket 5 for create item requests
def container_create_item_throughput_bucket(client):
    database = client.get_database_client(DATABASE_ID)

    created_container = database.create_container(
        str(uuid.uuid4()),
        PartitionKey(path="/pk"))

    created_container.create_item(
        body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
        throughput_bucket=5)

    database.delete_container(created_container.id)

def run_sample():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )
    client.create_database_if_not_exists(id=DATABASE_ID)
    try:
        # creates client
        create_client_with_throughput_bucket()

        # creates and deletes a database
        create_and_delete_database_with_throughput_bucket(client)

        # create a container
        create_container_with_throughput_bucket(client)

        # queries containers in a database
        query_containers_with_throughput_bucket(client)

        # reads an item from a container
        container_read_item_throughput_bucket(client)

        # writes an item to a container
        container_create_item_throughput_bucket(client)

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
        print("\nrun_sample done")

if __name__ == '__main__':
    run_sample()
