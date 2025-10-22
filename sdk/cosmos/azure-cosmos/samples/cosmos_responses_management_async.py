# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import uuid

from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.cosmos import ThroughputProperties

import asyncio
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
# Sample - demonstrates the basic CRUD operations for Control Plane responses for Azure Cosmos
#
# 1. Create Database
#    1.1 - Basic Create Database
#    1.2 - Create Database if not previously existing
#    1.3 - Create Database if not previously existing
#    1.4 - Database Read
#    1.5 - Database Replace Throughput
#
# 2. Create Container
#    2.1 - Basic Create Container
#    2.2 - Create container if not previously existing
#    2.3 - Create container if not previously existing
#    2.4 - Container Read
#    2.5 - Container Replace Throughput
#
# ----------------------------------------------------------------------------------------------------------
# Note -
#
# Running this sample will create (and delete) multiple Containers on your account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id'] + str(uuid.uuid4())
CONTAINER_ID = config.settings['container_id'] + str(uuid.uuid4())


async def create_db(client, id):
    # create database with return properties parameter set to true
    print("\n1.1 Create Database")

    try:
        response_properties = await client.create_database(id=id, return_properties=True)
        print('Database with id \'{0}\' created'.format(id))
        print(response_properties[1].get_response_headers())
    except exceptions.CosmosResourceExistsError:
        print('A database with id \'{0}\' already exists'.format(id))


async def create_db_if_not_exists(client, id):
    print("\n1.2 Create Database if not exists")

    try:
        response_properties = await client.create_database_if_not_exists(id=id, return_properties=True)
        print('Database with id \'{0}\' created or retrieved'.format(id))
        print(response_properties[1].get_response_headers())
    except exceptions.CosmosHttpResponseError as e:
        print('Error creating database: {0}'.format(e.message))


async def create_db_if_exists(client, id):
    print("\n1.3 Get Database if exists")

    try:
        response_properties = await client.create_database_if_not_exists(id=id, return_properties=True)
        print('Database with id \'{0}\' found'.format(id))
        print(response_properties[1].get_response_headers())
    except exceptions.CosmosResourceNotFoundError:
        print('Database with id \'{0}\' does not exist'.format(id))


async def read_db(client, id):
    print("\n1.4 Read Database")

    try:
        database = client.get_database_client(id)
        properties = await database.read()
        print('Database with id \'{0}\' was found'.format(id))
    except exceptions.CosmosResourceNotFoundError:
        print('A database with id \'{0}\' does not exist'.format(id))


async def replace_throughput_db(client, id):
    print("\n1.5 Replace Database Throughput")

    try:
        database = await client.create_database(id=id+"1", offer_throughput=400)
        replace_throughput_value = 500
        properties = await database.replace_throughput(replace_throughput_value)
        print('Database throughput changed to 800 RU/s')
        print(properties.get_response_headers())
    except exceptions.CosmosResourceNotFoundError:
        print('Database with id \'{0}\' does not exist'.format(id))
    except exceptions.CosmosHttpResponseError as e:
        print('Error changing database throughput: {0}'.format(e.message))


async def create_container(db, id):
    """ Execute basic container creation.
    This will create containers with 400 RUs with different indexing, partitioning, and storage options """

    partition_key = PartitionKey(path='/id', kind='Hash')
    print("\n2.1 Create Container - Basic")

    try:
        response_properties = await db.create_container(id=id, partition_key=partition_key, return_properties=True)
        print('Container with id \'{0}\' created'.format(id))
        print(response_properties[1].get_response_headers())
    except exceptions.CosmosResourceExistsError:
        print('A container with id \'{0}\' already exists'.format(id))


async def create_container_if_not_exists(db, id):
    print("\n2.2 Create Container if not exists")

    partition_key = PartitionKey(path='/id', kind='Hash')
    try:
        response_properties = await db.create_container_if_not_exists(id=id, partition_key=partition_key, return_properties=True)
        print('Container with id \'{0}\' created or retrieved'.format(id))
        print(response_properties[1].get_response_headers())
    except exceptions.CosmosHttpResponseError as e:
        print('Error creating container: {0}'.format(e.message))


async def create_container_if_exists(db, id):
    print("\n2.3 Get Container if exists")

    try:
        response_properties = await db.create_container_if_not_exists(id=id, return_properties=True)
        print('Container with id \'{0}\' found'.format(id))
        print(response_properties[1].get_response_headers())
    except exceptions.CosmosResourceNotFoundError:
        print('Container with id \'{0}\' does not exist'.format(id))


async def read_container(db, id):
    print("\n2.4 Get a Container by id")

    try:
        container = db.get_container_client(id)
        properties = await container.read()
        print('Container with id \'{0}\' was found, it\'s link is {1}'.format(container.id, container.container_link))
    except exceptions.CosmosResourceNotFoundError:
        print('A container with id \'{0}\' does not exist'.format(id))


async def replace_throughput_container(db, id):
    print("\n2.5 Replace Container Throughput")

    try:
        container = await db.create_container(id=id,  partition_key=PartitionKey(path="/company"), offer_throughput=400)
        replace_throughput_value = 500
        properties = await container.replace_throughput(replace_throughput_value)
        # Set new throughput to 600 RU/s
        new_throughput = ThroughputProperties(offer_throughput=600)
        print('Container throughput changed to 600 RU/s')
        print(properties.get_response_headers())
    except exceptions.CosmosResourceNotFoundError:
        print('Container with id \'{0}\' does not exist'.format(id))
    except exceptions.CosmosHttpResponseError as e:
        print('Error changing container throughput: {0}'.format(e.message))


async def run_sample():
    async with CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        try:
            # setup database for this sample
            try:
                throughput_properties = ThroughputProperties(500)
                db = await client.create_database(id=DATABASE_ID, offer_throughput=throughput_properties)

            except exceptions.CosmosResourceExistsError:
                db = client.get_database_client(DATABASE_ID)

            # demonstrate database operations
            print("\n=== Database Operations ===")

            # create a database
            await create_db(client, DATABASE_ID + "_demo1")

            # create a database if it doesn't exist already
            await create_db_if_not_exists(client, DATABASE_ID + "_demo2")

            # read database information if the database already exists
            await create_db_if_exists(client, DATABASE_ID)

            # read from database
            await read_db(client, DATABASE_ID)

            # replace throughput for database
            await replace_throughput_db(client, DATABASE_ID)

            # demonstrate container operations
            print("\n=== Container Operations ===")

            # create a container
            await create_container(db, CONTAINER_ID)

            # create container if not exists
            await create_container_if_not_exists(db, CONTAINER_ID + "_demo")

            # get a container using its id
            await read_container(db, CONTAINER_ID)

            # replace container throughput
            await replace_throughput_container(db, CONTAINER_ID + "demo")

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
    asyncio.run(run_sample())