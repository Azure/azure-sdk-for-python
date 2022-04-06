# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.identity.aio import ClientSecretCredential, DefaultAzureCredential
import config
import asyncio

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https://docs.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
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


async def create_sample_resources():
    print("creating sample resources")
    async with CosmosClient(HOST, MASTER_KEY) as client:
        db = await client.create_database(DATABASE_ID)
        await db.create_container(id=CONTAINER_ID, partition_key=PARTITION_KEY)


async def delete_sample_resources():
    print("deleting sample resources")
    async with CosmosClient(HOST, MASTER_KEY) as client:
        await client.delete_database(DATABASE_ID)


async def run_sample():
    # Since Azure Cosmos DB data plane SDK does not cover management operations, we have to create our resources
    # with a master key authenticated client for this sample.
    await create_sample_resources()

    # With this done, you can use your AAD service principal id and secret to create your ClientSecretCredential.
    # The async ClientSecretCredentials, like the async client, also have a context manager,
    # and as such should be used with the `async with` keywords.
    async with ClientSecretCredential(
            tenant_id=TENANT_ID,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET) as aad_credentials:

        # Use your credentials to authenticate your client.
        async with CosmosClient(HOST, aad_credentials) as aad_client:
            print("Showed ClientSecretCredential, now showing DefaultAzureCredential")

    # You can also utilize DefaultAzureCredential rather than directly passing in the id's and secrets.
    # This is the recommended method of authentication, and uses environment variables rather than in-code strings.
    async with DefaultAzureCredential() as aad_credentials:

        # Use your credentials to authenticate your client.
        async with CosmosClient(HOST, aad_credentials) as aad_client:

            # Do any R/W data operations with your authorized AAD client.
            db = aad_client.get_database_client(DATABASE_ID)
            container = db.get_container_client(CONTAINER_ID)

            print("Container info: " + str(container.read()))
            await container.create_item(get_test_item(879))
            print("Point read result: " + str(container.read_item(item='Item_0', partition_key='Item_0')))
            query_results = [item async for item in
                             container.query_items(query='select * from c', partition_key='Item_0')]
            assert len(query_results) == 1
            print("Query result: " + str(query_results[0]))
            await container.delete_item(item='Item_0', partition_key='Item_0')

            # Attempting to do management operations will return a 403 Forbidden exception.
            try:
                await aad_client.delete_database(DATABASE_ID)
            except exceptions.CosmosHttpResponseError as e:
                assert e.status_code == 403
                print("403 error assertion success")

    # To clean up the sample, we use a master key client again to get access to deleting containers/ databases.
    await delete_sample_resources()
    print("end of sample")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sample())
