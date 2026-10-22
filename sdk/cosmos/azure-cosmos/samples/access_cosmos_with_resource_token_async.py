# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import azure.cosmos.documents as documents

import asyncio
import config
import json
from typing import Dict, Any

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://learn.microsoft.com/azure/cosmos-db/create-sql-api-python#create-a-database-account
#
# 2. Microsoft Azure Cosmos
#    pip install azure-cosmos>=4.0.0
# ----------------------------------------------------------------------------------------------------------
# Sample - how to get and use resource token that allows restricted access to data
# ----------------------------------------------------------------------------------------------------------
# Note:
#
# This sample creates a Container to your database account.
# Each time a Container is created the account will be billed for 1 hour of usage based on
# the provisioned throughput (RU/s) of that account.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings["host"]
MASTER_KEY = config.settings["master_key"]
DATABASE_ID = config.settings["database_id"]
CONTAINER_ID = config.settings["container_id"]
PARTITION_KEY = PartitionKey(path="/username")

# User that you want to give access to
USERNAME, USERNAME_2 = "user", "user2"

CONTAINER_ALL_PERMISSION = "CONTAINER_ALL_PERMISSION"
PARTITION_READ_PERMISSION = "PARTITION_READ_PERMISSION"
DOCUMENT_ALL_PERMISSION = "DOCUMENT_ALL_PERMISSION"


async def create_user_if_not_exists(db, username):
    try:
        user = await db.create_user(body={"id": username})
    except exceptions.CosmosResourceExistsError:
        user = db.get_user_client(username)

    return user


async def create_permission_if_not_exists(user, permission_definition):
    try:
        permission = await user.create_permission(permission_definition)
    except exceptions.CosmosResourceExistsError:
        permission = await user.read_permission(permission_definition["id"])

    return permission


async def token_client_upsert(container, username, item_id):
    try:
        await container.upsert_item(
            {
                "id": item_id,
                "username": username,
                "msg": "This is a message for " + username,
            }
        )
    except exceptions.CosmosHttpResponseError:
        print("Error in upserting item with id '{0}'.".format(item_id))


async def token_client_read_all(container):
    try:
        items = container.read_all_items()
        async for i in items:
            print(i)
    except exceptions.CosmosResourceNotFoundError:
        print("Cannot read items--container '{0}' not found.".format(container.id))
    except exceptions.CosmosHttpResponseError:
        print("Error in reading items in container '{0}'.".format(container.id))


async def token_client_read_item(container, username, item_id):
    try:
        item = await container.read_item(item=item_id, partition_key=username)
        print(item)
    except exceptions.CosmosResourceNotFoundError:
        print("Cannot read--item with id '{0}' not found.".format(item_id))
    except exceptions.CosmosHttpResponseError:
        print("Error in reading item with id '{0}'.".format(item_id))


async def token_client_delete(container, username, item_id):
    try:
        await container.delete_item(item=item_id, partition_key=username)
    except exceptions.CosmosResourceNotFoundError:
        print("Cannot delete--item with id '{0}' not found.".format(item_id))
    except exceptions.CosmosHttpResponseError:
        print("Error in deleting item with id '{0}'.".format(item_id))


async def token_client_query(container, username):
    try:
        async for item in container.query_items(
            query="SELECT * FROM my_container c WHERE c.username=@username",
            parameters=[{"name": "@username", "value": username}],
            partition_key=username,
        ):
            print(json.dumps(item, indent=True))
    except exceptions.CosmosHttpResponseError:
        print("Error in querying item(s)")


async def run_sample():
    async with CosmosClient(HOST, MASTER_KEY) as client:

        try:
            try:
                db = await client.create_database(DATABASE_ID)
            except exceptions.CosmosResourceExistsError:
                db = client.get_database_client(DATABASE_ID)

            try:
                container = await db.create_container(
                    id=CONTAINER_ID, partition_key=PARTITION_KEY
                )
            except exceptions.CosmosResourceExistsError:
                container = db.get_container_client(CONTAINER_ID)

            user = await create_user_if_not_exists(db, USERNAME)

            # Permission to perform operations on all items inside a container
            permission_definition: Dict[str, Any] = {
                "id": CONTAINER_ALL_PERMISSION,
                "permissionMode": documents.PermissionMode.All,
                "resource": container.container_link,
            }

            permission = await create_permission_if_not_exists(user, permission_definition)
            token = {}
            token[container.container_link] = permission.properties["_token"]

            # Use token to connect to database
            # If you initialize the asynchronous client without using 'async with' in your context,
            # make sure to close the client once you're done using it
            token_client = CosmosClient(HOST, token)
            token_db = token_client.get_database_client(DATABASE_ID)
            token_container = token_db.get_container_client(CONTAINER_ID)

            ITEM_1_ID, ITEM_2_ID, ITEM_3_ID = "1", "2", "3"

            # Update or insert item if not exists
            await token_client_upsert(token_container, USERNAME, ITEM_1_ID)
            await token_client_upsert(token_container, USERNAME, ITEM_2_ID)
            await token_client_upsert(token_container, USERNAME_2, ITEM_3_ID)

            # Read all items in the container, across all partitions
            await token_client_read_all(token_container)

            # Read specific item
            await token_client_read_item(token_container, USERNAME, ITEM_2_ID)

            # Query for items in a certain partition
            await token_client_query(token_container, USERNAME_2)

            # Delete an item
            await token_client_delete(token_container, USERNAME, ITEM_2_ID)

            # Give user read-only permission, for a specific partition
            user_2 = await create_user_if_not_exists(db, USERNAME_2)
            permission_definition = {
                "id": PARTITION_READ_PERMISSION,
                "permissionMode": documents.PermissionMode.Read,
                "resource": container.container_link,
                "resourcePartitionKey": [USERNAME_2],
            }
            permission = await create_permission_if_not_exists(user_2, permission_definition)
            read_token = {}
            read_token[container.container_link] = permission.properties["_token"]

            # Closing current token client in order to re-initialize with read_token below:
            await token_client.close()

            # Use token to connect to database
            # If you initialize the asynchronous client without using 'async with' make sure to close it once you're done
            token_client = CosmosClient(HOST, read_token)
            token_db = token_client.get_database_client(DATABASE_ID)
            token_container = token_db.get_container_client(CONTAINER_ID)

            # Fails since this client has access to only items with partition key USERNAME_2 (ie. "user2")
            await token_client_read_all(token_container)

            # Ok to read item(s) with partition key "user2"
            await token_client_read_item(token_container, USERNAME_2, ITEM_3_ID)

            # Can't upsert or delete since it's read-only
            await token_client_upsert(token_container, USERNAME_2, ITEM_3_ID)

            # Give user CRUD permissions, only for a specific item
            item_3 = await token_container.read_item(item=ITEM_3_ID, partition_key=USERNAME_2)
            permission_list = user_2.list_permissions()
            async for p in permission_list:
                await user_2.delete_permission(p.get('id'))
            user_2_permissions = [permission async for permission in user_2.list_permissions()]
            assert len(user_2_permissions) == 0

            permission_definition = {
                "id": DOCUMENT_ALL_PERMISSION,
                "permissionMode": documents.PermissionMode.All,
                "resource": str(item_3.get('_self')) #this identifies the item with id "3"
            }

            permission = await create_permission_if_not_exists(user_2, permission_definition)

            item_token = {}
            item_token[container.container_link] = permission.properties["_token"]

            # Closing current token client in order to re-initialize with item_token below:
            await token_client.close()

            # Use token to connect to database
            token_client = CosmosClient(HOST, item_token)
            token_db = token_client.get_database_client(DATABASE_ID)
            token_container = token_db.get_container_client(CONTAINER_ID)

            # Fails since this client only has access to a specific item
            await token_client_read_all(token_container)

            # Fails too, for same reason
            await token_client_read_item(token_container, USERNAME, ITEM_1_ID)

            # Ok to perform operations on that specific item
            await token_client_read_item(token_container, USERNAME_2, ITEM_3_ID)
            await token_client_delete(token_container, USERNAME_2, ITEM_3_ID)

            # Cleaning up and closing current token client
            await token_client.delete_database(DATABASE_ID)
            await token_client.close()  

        except exceptions.CosmosHttpResponseError as e:
            print("\nrun_sample has caught an error. {0}".format(e.message))

        finally:
            print("\nrun_sample done")


if __name__ == "__main__":
    asyncio.run(run_sample())
