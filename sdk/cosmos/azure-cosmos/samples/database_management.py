# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions

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

def find_database(client, id):
    print('1. Query for Database')

    databases = list(client.query_databases({
        "query": "SELECT * FROM r WHERE r.id=@id",
        "parameters": [
            { "name":"@id", "value": id }
        ]
    }))

    if len(databases) > 0:
        print('Database with id \'{0}\' was found'.format(id))
    else:
        print('No database with id \'{0}\' was found'. format(id))


def create_database(client, id):
    print("\n2. Create Database")

    try:
        client.create_database(id=id)
        print('Database with id \'{0}\' created'.format(id))

    except exceptions.CosmosResourceExistsError:
        print('A database with id \'{0}\' already exists'.format(id))

    print("\n2.8 Create Database - With auto scale settings")

    try:
        client.create_database(
            id=id,
            offer_throughput=ThroughputProperties(auto_scale_max_throughput=5000, auto_scale_increment_percent=0))
        print('Database with id \'{0}\' created'.format(id))

    except exceptions.CosmosResourceExistsError:
        print('A database with id \'{0}\' already exists'.format(id))


def read_database(client, id):
    print("\n3. Get a Database by id")

    try:
        database = client.get_database_client(id)
        database.read()
        print('Database with id \'{0}\' was found, it\'s link is {1}'.format(id, database.database_link))

    except exceptions.CosmosResourceNotFoundError:
        print('A database with id \'{0}\' does not exist'.format(id))


def list_databases(client):
    print("\n4. List all Databases on an account")

    print('Databases:')

    databases = list(client.list_databases())

    if not databases:
        return

    for database in databases:
        print(database['id'])


def delete_database(client, id):
    print("\n5. Delete Database")

    try:
        client.delete_database(id)

        print('Database with id \'{0}\' was deleted'.format(id))

    except exceptions.CosmosResourceNotFoundError:
        print('A database with id \'{0}\' does not exist'.format(id))


def run_sample():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )
    try:
        # query for a database
        find_database(client, DATABASE_ID)

        # create a database
        create_database(client, DATABASE_ID)

        # get a database using its id
        read_database(client, DATABASE_ID)

        # list all databases on an account
        list_databases(client)

        # delete database by id
        delete_database(client, DATABASE_ID)

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
        print("\nrun_sample done")

if __name__ == '__main__':
    run_sample()
