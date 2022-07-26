# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.aio.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https://azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Container resource for Azure Cosmos
#
# 1. Query for Container
#
# 2. Create Container
#    2.1 - Basic Create
#    2.2 - Create container with custom IndexPolicy
#    2.3 - Create container with provisioned throughput set
#    2.4 - Create container with unique key
#    2.5 - Create Container with partition key V2
#    2.6 - Create Container with partition key V1
#    2.7 - Create Container with analytical store enabled
#
# 3. Manage Container Provisioned Throughput
#    3.1 - Get Container provisioned throughput (RU/s)
#    3.2 - Change provisioned throughput (RU/s)
#
# 4. Get a Container by its Id property
#
# 5. List all Container resources in a Database
#
# 6. Delete Container
# ----------------------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create (and delete) multiple Containers on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']

async def find_container(db, id):
    print('1. Query for Container')

    # Because the asynchronous client returns an asynchronous iterator object for methods that use
    # return several containers using queries, we do not need to await the function. However, attempting
    # to cast this object into a list directly will throw an error; instead, iterate over the containers
    # to populate your list using an async for loop like shown here or in the list_containers() method
    query_containers_response = db.query_containers(
        {
            "query": "SELECT * FROM r WHERE r.id=@id",
            "parameters": [
                { "name":"@id", "value": id }
            ]
        }
    )
    containers = [container async for container in query_containers_response]

    if len(containers) > 0:
        print('Container with id \'{0}\' was found'.format(id))
    else:
        print('No container with id \'{0}\' was found'. format(id))

    # Alternatively, you can directly iterate over the asynchronous iterator without building a separate
    # list if you don't need the ordering or indexing capabilities
    async for container in query_containers_response:
        print(container['id'])


async def create_container(db, id):
    """ Execute basic container creation.
    This will create containers with 400 RUs with different indexing, partitioning, and storage options """

    partition_key = PartitionKey(path='/id', kind='Hash')
    print("\n2.1 Create Container - Basic")

    try:
        await db.create_container(id=id, partition_key=partition_key)
        print('Container with id \'{0}\' created'.format(id))

    except exceptions.CosmosResourceExistsError:
        print('A container with id \'{0}\' already exists'.format(id))

    # Alternatively, you can also use the create_container_if_not_exists method to avoid using a try catch
    # This method attempts to read the container first, and based on the result either creates or returns
    # the existing container. Due to the additional overhead from attempting a read, it is recommended
    # to use the create_container() method if you know the container doesn't already exist.
    await db.create_container_if_not_exists(id=id, partition_key=partition_key)

    print("\n2.2 Create Container - With custom index policy")

    coll = {
        "id": id+"_container_custom_index_policy",
        "indexingPolicy": {
            "automatic": False
        }
    }

    container = await db.create_container_if_not_exists(
        id=coll['id'],
        partition_key=partition_key,
        indexing_policy=coll['indexingPolicy']
    )
    properties = await container.read()
    print('Container with id \'{0}\' created'.format(container.id))
    print('IndexPolicy Mode - \'{0}\''.format(properties['indexingPolicy']['indexingMode']))
    print('IndexPolicy Automatic - \'{0}\''.format(properties['indexingPolicy']['automatic']))

    print("\n2.3 Create Container - With custom provisioned throughput")

    try:
        container = await db.create_container(
            id=id+"_container_custom_throughput",
            partition_key=partition_key,
            offer_throughput=400
        )
        print('Container with id \'{0}\' created'.format(container.id))

    except exceptions.CosmosResourceExistsError:
        print('A container with id \'{0}\' already exists'.format(coll['id']))

    print("\n2.4 Create Container - With Unique keys")

    try:
        container = await db.create_container(
            id= id+"_container_unique_keys",
            partition_key=partition_key,
            unique_key_policy={'uniqueKeys': [{'paths': ['/field1/field2', '/field3']}]}
        )
        properties = await container.read()
        unique_key_paths = properties['uniqueKeyPolicy']['uniqueKeys'][0]['paths']
        print('Container with id \'{0}\' created'.format(container.id))
        print('Unique Key Paths - \'{0}\', \'{1}\''.format(unique_key_paths[0], unique_key_paths[1]))

    except exceptions.CosmosResourceExistsError:
        print('A container with id \'container_unique_keys\' already exists')

    print("\n2.5 Create Container - With Partition key V2 (Default)")

    try:
        container = await db.create_container(
            id=id+"_container_partition_key_v2",
            partition_key=PartitionKey(path='/id', kind='Hash')
        )
        properties = await container.read()
        print('Container with id \'{0}\' created'.format(container.id))
        print('Partition Key - \'{0}\''.format(properties['partitionKey']))

    except exceptions.CosmosResourceExistsError:
        print('A container with id \'container_partition_key_v2\' already exists')

    print("\n2.6 Create Container - With Partition key V1")

    try:
        container = await db.create_container(
            id=id+"_container_partition_key_v1",
            partition_key=PartitionKey(path='/id', kind='Hash', version=1)
        )
        properties = await container.read()
        print('Container with id \'{0}\' created'.format(container.id))
        print('Partition Key - \'{0}\''.format(properties['partitionKey']))

    except exceptions.CosmosResourceExistsError:
        print('A container with id \'container_partition_key_v1\' already exists')
    except Exception:
        print("Skipping this step, account does not have Synapse Link activated")

    print("\n2.7 Create Container - With analytical store enabled") 
    
    if 'localhost:8081' in HOST:
        print("Skipping step since emulator does not support this yet")
    else:
        try:
            container = await db.create_container(
                id=id+"_container_analytical_store",
                partition_key=PartitionKey(path='/id', kind='Hash'),analytical_storage_ttl=-1

            )
            properties = await container.read()
            print('Container with id \'{0}\' created'.format(container.id))
            print('Partition Key - \'{0}\''.format(properties['partitionKey']))

        except exceptions.CosmosResourceExistsError:
            print('A container with id \'_container_analytical_store\' already exists')
        except Exception:
            print('Creating container with analytical storage can only happen in synapse link activated accounts, skipping step')

    print("\n2.8 Create Container - With auto scale settings")

    try:
        container = await db.create_container(
            id=id+"_container_auto_scale_settings",
            partition_key=partition_key,
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0)
        )
        print('Container with id \'{0}\' created'.format(container.id))

    except exceptions.CosmosResourceExistsError:
        print('A container with id \'{0}\' already exists'.format(coll['id']))



async def manage_provisioned_throughput(db, id):
    print("\n3.1 Get Container provisioned throughput (RU/s)")

    # A Container's Provisioned Throughput determines the performance throughput of a container.
    # A Container is loosely coupled to Offer through the Offer's offerResourceId
    # Offer.offerResourceId == Container._rid
    # Offer.resource == Container._self

    try:
        # read the container, so we can get its _self
        container = db.get_container_client(id)

        # now use its _self to query for throughput offers
        offer = await container.get_throughput()

        print('Found Offer \'{0}\' for Container \'{1}\' and its throughput is \'{2}\''.format(offer.properties['id'], container.id, offer.properties['content']['offerThroughput']))

    except exceptions.CosmosResourceExistsError:
        print('A container with id \'{0}\' does not exist'.format(id))

    print("\n3.2 Change Provisioned Throughput of Container")

    #The Provisioned Throughput of a container controls the throughput allocated to the Container

    #The following code shows how you can change Container's throughput
    offer = await container.replace_throughput(offer.offer_throughput + 100)
    print('Replaced Offer. Provisioned Throughput is now \'{0}\''.format(offer.properties['content']['offerThroughput']))


async def read_container(db, id):
    print("\n4. Get a Container by id")

    try:
        container = db.get_container_client(id)
        await container.read()
        print('Container with id \'{0}\' was found, it\'s link is {1}'.format(container.id, container.container_link))

    except exceptions.CosmosResourceNotFoundError:
        print('A container with id \'{0}\' does not exist'.format(id))


async def list_containers(db):
    print("\n5. List all Container in a Database")

    print('Containers:')

    # Because the asynchronous client returns an asynchronous iterator object for methods that use
    # return several containers using queries, we do not need to await the function. However, attempting
    # to cast this object into a list directly will throw an error; instead, iterate over the containers
    # to populate your list using an async for loop like shown here or in the find_container() method
    container_list = db.list_containers()
    containers = [container async for container in container_list]

    if len(containers) == 0:
        return

    for container in containers:
        print(container['id'])

    # Alternitavely, you can directly iterate over the asynchronous iterator without building a separate
    # list if you don't need the ordering or indexing capabilities
    async for container in container_list:
        print(container['id'])


async def delete_container(db, id):
    print("\n6. Delete Container")

    try:
        await db.delete_container(id)
        print('Container with id \'{0}\' was deleted'.format(id))

    except exceptions.CosmosResourceNotFoundError:
        print('A container with id \'{0}\' does not exist'.format(id))


async def run_sample():

    async with cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        try:
            db = await client.create_database_if_not_exists(id=DATABASE_ID)

            # query for a container
            await find_container(db, CONTAINER_ID)

            # create a container
            await create_container(db, CONTAINER_ID)

            # get & change Provisioned Throughput of container
            await manage_provisioned_throughput(db, CONTAINER_ID)

            # get a container using its id
            await read_container(db, CONTAINER_ID)

            # list all container on an account
            await list_containers(db)

            # delete container by id
            await delete_container(db, CONTAINER_ID)

            # cleanup database after sample
            try:
                await client.delete_database(db)

            except exceptions.CosmosResourceNotFoundError:
                pass

        except exceptions.CosmosHttpResponseError as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))

        finally:
                print("\nrun_sample done")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())

