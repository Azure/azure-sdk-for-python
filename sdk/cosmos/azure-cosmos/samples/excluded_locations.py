# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.cosmos import CosmosClient
from azure.cosmos.partition_key import PartitionKey
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://learn.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
#
# 2. Microsoft Azure Cosmos
#    pip install azure-cosmos>=4.3.0b4
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to use excluded locations in client level and request level
# ----------------------------------------------------------------------------------------------------------
# Note:
# This sample creates a Container to your database account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]

TENANT_ID = config.settings["tenant_id"]
CLIENT_ID = config.settings["client_id"]
CLIENT_SECRET = config.settings["client_secret"]

DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]
PARTITION_KEY = PartitionKey(path="/id")


def get_test_item(num):
    test_item = {
        'id': 'Item_' + str(num),
        'test_object': True,
        'lastName': 'Smith'
    }
    return test_item

def clean_up_db(client):
    try:
        client.delete_database(DATABASE_ID)
    except Exception as e:
        pass

def excluded_locations_client_level_sample():
    preferred_locations = ['West US 3', 'West US', 'East US 2']
    excluded_locations = ['West US 3', 'West US']
    client = CosmosClient(
                HOST,
                MASTER_KEY,
                preferred_locations=preferred_locations,
                excluded_locations=excluded_locations
    )
    clean_up_db(client)

    db = client.create_database(DATABASE_ID)
    container = db.create_container(id=CONTAINER_ID, partition_key=PARTITION_KEY)

    # For write operations with single master account, write endpoint will be the default endpoint,
    # since preferred_locations or excluded_locations are ignored and used
    container.create_item(get_test_item(0))

    # For read operations, read endpoints will be 'preferred_locations' - 'excluded_locations'.
    # In our sample, ['West US 3', 'West US', 'East US 2'] - ['West US 3', 'West US'] => ['East US 2'],
    # therefore 'East US 2' will be the read endpoint, and items will be read from 'East US 2' location
    item = container.read_item(item='Item_0', partition_key='Item_0')

    clean_up_db(client)

def excluded_locations_request_level_sample():
    preferred_locations = ['West US 3', 'West US', 'East US 2']
    excluded_locations_on_client = ['West US 3', 'West US']
    excluded_locations_on_request = ['West US 3']
    client = CosmosClient(
                HOST,
                MASTER_KEY,
                preferred_locations=preferred_locations,
                excluded_locations=excluded_locations_on_client
    )
    clean_up_db(client)

    db = client.create_database(DATABASE_ID)
    container = db.create_container(id=CONTAINER_ID, partition_key=PARTITION_KEY)

    # For write operations with single master account, write endpoint will be the default endpoint,
    # since preferred_locations or excluded_locations are ignored and used
    container.create_item(get_test_item(0))

    # For read operations, read endpoints will be 'preferred_locations' - 'excluded_locations'.
    # However, in our sample, since the excluded_locations` were passed with the read request, the `excluded_location`
    # will be replaced with the locations from request, ['West US 3']. The `excluded_locations` on request always takes
    # the highest priority!
    # With the excluded_locations on request, the read endpoints will be ['West US', 'East US 2']
    #   ['West US 3', 'West US', 'East US 2'] - ['West US 3'] => ['West US', 'East US 2']
    # Therefore, items will be read from 'West US' or 'East US 2' location
    item = container.read_item(item='Item_0', partition_key='Item_0', excluded_locations=excluded_locations_on_request)

    clean_up_db(client)

if __name__ == "__main__":
    # excluded_locations_client_level_sample()
    excluded_locations_request_level_sample()
