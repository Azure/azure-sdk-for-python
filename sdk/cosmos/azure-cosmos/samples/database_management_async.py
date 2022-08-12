# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.aio.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Database resource for Azure Cosmos
#
# 1. Query for Database (QueryDatabases)
#
# 2. Create Database (CreateDatabase)
#
# 3. Get a Database by its Id property (ReadDatabase)
#
# 4. List all Database resources on an account (ReadDatabases)
#
# 5. Delete a Database given its Id property (DeleteDatabase)
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']

async def find_database(client, id):
    print('1. Query for Database')

    # Because the asynchronous client returns an asynchronous iterator object for methods that use
    # return several databases using queries, we do not need to await the function. However, attempting
    # to cast this object into a list directly will throw an error; instead, iterate over the databases
    # to populate your list using an async for loop like shown here or in the list_databases() method
    query_databases_response = client.query_databases({
        "query": "SELECT * FROM r WHERE r.id=@id",
        "parameters": [
            { "name":"@id", "value": id }
        ]
    })

    databases = [database async for database in query_databases_response]

    if len(databases) > 0:
        print('Database with id \'{0}\' was found'.format(id))
    else:
        print('No database with id \'{0}\' was found'. format(id))

    # Alternitavely, you can directly iterate over the asynchronous iterator without building a separate
    # list if you don't need the ordering or indexing capabilities
    async for database in query_databases_response:
        print(database['id'])


async def create_database(client, id):
    print("\n2. Create Database")

    try:
        await client.create_database(id=id)
        print('Database with id \'{0}\' created'.format(id))

    except exceptions.CosmosResourceExistsError:
        print('A database with id \'{0}\' already exists'.format(id))

    print("\n2.8 Create Database - With auto scale settings")

    try:
        await client.create_database(
            id=id,
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0))
        print('Database with id \'{0}\' created'.format(id))

    except exceptions.CosmosResourceExistsError:
        print('A database with id \'{0}\' already exists'.format(id))

    # Alternatively, you can also use the create_database_if_not_exists method to avoid using a try catch
    # This method attempts to read the database first, and based on the result either creates or returns
    # the existing database. Due to the additional overhead from attempting a read, it is recommended
    # to use the create_database() method if you know the database doesn't already exist.
    await client.create_database_if_not_exists(id=id)


async def read_database(client, id):
    print("\n3. Get a Database by id")

    try:
        database = client.get_database_client(id)
        await database.read()
        print('Database with id \'{0}\' was found, it\'s link is {1}'.format(id, database.database_link))

    except exceptions.CosmosResourceNotFoundError:
        print('A database with id \'{0}\' does not exist'.format(id))


async def list_databases(client):
    print("\n4. List all Databases on an account")

    print('Databases:')

    # Because the asynchronous client returns an asynchronous iterator object for methods that use
    # return several databases using queries, we do not need to await the function. However, attempting
    # to cast this object into a list directly will throw an error; instead, iterate over the databases
    # to populate your list using an async for loop like shown here or in the find_database() method
    list_databases_response = client.list_databases()
    databases = [database async for database in list_databases_response]

    if len(databases) == 0:
        return

    for database in databases:
        print(database['id'])

    # Alternitavely, you can directly iterate over the asynchronous iterator without building a separate
    # list if you don't need the ordering or indexing capabilities
    async for database in list_databases_response:
        print(database['id'])


async def delete_database(client, id):
    print("\n5. Delete Database")

    try:
        await client.delete_database(id)
        print('Database with id \'{0}\' was deleted'.format(id))

    except exceptions.CosmosResourceNotFoundError:
        print('A database with id \'{0}\' does not exist'.format(id))


async def run_sample():
    async with cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        try:
            # query for a database
            await find_database(client, DATABASE_ID)

            # create a database
            await create_database(client, DATABASE_ID)

            # get a database using its id
            await read_database(client, DATABASE_ID)

            # list all databases on an account
            await list_databases(client)

            # delete database by id
            await delete_database(client, DATABASE_ID)

        except exceptions.CosmosHttpResponseError as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))

        finally:
            print("\nrun_sample done")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
