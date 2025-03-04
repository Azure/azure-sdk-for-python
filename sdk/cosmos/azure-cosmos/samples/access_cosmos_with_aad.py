# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.cosmos import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.identity import ClientSecretCredential, DefaultAzureCredential
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
# Sample - demonstrates how to authenticate and use your database account using AAD credentials
# Read more about operations allowed for this authorization method: https://aka.ms/cosmos-native-rbac
# ----------------------------------------------------------------------------------------------------------
# Note:
# This sample creates a Container to your database account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------
# <configureConnectivity>
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


def create_sample_resources():
    print("creating sample resources")
    client = CosmosClient(HOST, MASTER_KEY)
    db = client.create_database(DATABASE_ID)
    db.create_container(id=CONTAINER_ID, partition_key=PARTITION_KEY)


def delete_sample_resources():
    print("deleting sample resources")
    client = CosmosClient(HOST, MASTER_KEY)
    client.delete_database(DATABASE_ID)


def run_sample():
    # Since Azure Cosmos DB data plane SDK does not cover management operations, we have to create our resources
    # with a master key authenticated client for this sample.
    create_sample_resources()

    # With this done, you can use your AAD service principal id and secret to create your ClientSecretCredential.
    aad_client_secret_credentials = ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET)

    # You can also utilize DefaultAzureCredential rather than directly passing in the id's and secrets.
    # This is the recommended method of authentication, and uses environment variables rather than in-code strings.
    aad_credentials = DefaultAzureCredential()

    # Use your credentials to authenticate your client.
    aad_client = CosmosClient(HOST, aad_credentials)

    # Do any R/W data operations with your authorized AAD client.
    db = aad_client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)

    print("Container info: " + str(container.read()))
    container.create_item(get_test_item(0))
    print("Point read result: " + str(container.read_item(item='Item_0', partition_key='Item_0')))
    query_results = list(container.query_items(query='select * from c', partition_key='Item_0'))
    assert len(query_results) == 1
    print("Query result: " + str(query_results[0]))
    container.delete_item(item='Item_0', partition_key='Item_0')

    # Attempting to do management operations will return a 403 Forbidden exception.
    try:
        aad_client.delete_database(DATABASE_ID)
    except exceptions.CosmosHttpResponseError as e:
        assert e.status_code == 403
        print("403 error assertion success")

    # To clean up the sample, we use a master key client again to get access to deleting containers and databases.
    delete_sample_resources()
    print("end of sample")


if __name__ == "__main__":
    run_sample()
