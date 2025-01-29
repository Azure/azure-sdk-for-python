# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from datetime import datetime, timezone

import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import azure.cosmos.partition_key as partition_key
import uuid

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https:#azure.microsoft.com/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates how to consume the Change Feed and iterate on the results.
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


def create_items(container, size):
    print('Creating Items')

    for i in range(1, size):
        c = str(uuid.uuid4())
        item_definition = {'id': 'item' + c,
                           'address': {'street': '1 Microsoft Way' + c,
                                       'city': 'Redmond' + c,
                                       'state': 'WA',
                                       'zip code': 98052
                                       }
                           }

        created_item = container.create_item(body=item_definition)


def read_change_feed(container):
    print('\nReading Change Feed from the beginning\n')

    # For a particular Partition Key Range we can use partition_key_range_id]
    # 'is_start_from_beginning = True' will read from the beginning of the history of the container
    # If no is_start_from_beginning is specified, the read change feed loop will pickup the items that happen while the loop / process is active
    response = container.query_items_change_feed(is_start_from_beginning=True)
    for doc in response:
        print(doc)

    print('\nFinished reading all the change feed\n')


def read_change_feed_with_start_time(container, start_time):
    time = start_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    print('\nReading Change Feed from start time of {}\n'.format(time))

    # You can read change feed from a specific time.
    # You must pass in a datetime object for the start_time field.
    response = container.query_items_change_feed(start_time=start_time)
    for doc in response:
        print(doc)

    print('\nFinished reading all the change feed from start time of {}\n'.format(time))


def read_change_feed_with_continuation(container, continuation):
    print('\nReading change feed from continuation\n')

    # You can read change feed from a specific continuation token.
    # You must pass in a valid continuation token.
    response = container.query_items_change_feed(continuation=continuation)
    for doc in response:
        print(doc)

    print('\nFinished reading all the change feed from continuation\n')

def delete_all_items(container):
    print('\nDeleting all item\n')

    for item in container.query_items(query='SELECT * FROM c', enable_cross_partition_query=True):
        # Deleting the current item
        container.delete_item(item, partition_key=item['address']['state'])

    print('Deleted all items')

def read_change_feed_with_all_versions_and_delete_mode(container):
    change_feed_mode = "AllVersionsAndDeletes"
    print("\nReading change feed with 'AllVersionsAndDeletes' mode.\n")

    # You can read change feed with a specific change feed mode.
    # You must pass in a valid change feed mode: ["LatestVersion", "AllVersionsAndDeletes"].
    response = container.query_items_change_feed(mode=change_feed_mode)
    for doc in response:
        print(doc)

    print("\nFinished reading all the change feed with 'AllVersionsAndDeletes' mode.\n")

def read_change_feed_with_all_versions_and_delete_mode_from_continuation(container, continuation):
    change_feed_mode = "AllVersionsAndDeletes"
    print("\nReading change feed with 'AllVersionsAndDeletes' mode.\n")

    # You can read change feed with a specific change feed mode from a specific continuation token.
    # You must pass in a valid change feed mode: ["LatestVersion", "AllVersionsAndDeletes"].
    # You must pass in a valid continuation token.
    response = container.query_items_change_feed(mode=change_feed_mode, continuation=continuation)
    for doc in response:
        print(doc)

    print("\nFinished reading all the change feed with 'AllVersionsAndDeletes' mode.\n")

def run_sample():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    try:
        # setup database for this sample
        try:
            db = client.create_database(id=DATABASE_ID)
        except exceptions.CosmosResourceExistsError:
            raise RuntimeError("Database with id '{}' already exists".format(DATABASE_ID))

        # setup container for this sample
        try:
            container = db.create_container(
                id=CONTAINER_ID,
                partition_key=partition_key.PartitionKey(path='/address/state', kind=documents.PartitionKind.Hash)
            )
            print('Container with id \'{0}\' created'.format(CONTAINER_ID))

        except exceptions.CosmosResourceExistsError:
            raise RuntimeError("Container with id '{}' already exists".format(CONTAINER_ID))

        # Create items
        create_items(container, 100)
        # Timestamp post item creations
        timestamp = datetime.now(timezone.utc)
        # Create more items after time stamp
        create_items(container, 50)
        # Read change feed from beginning
        read_change_feed(container)
        # Read Change Feed from timestamp
        read_change_feed_with_start_time(container, timestamp)
        # Delete all items from container
        delete_all_items(container)
        # Read change feed with 'AllVersionsAndDeletes' mode
        read_change_feed_with_all_versions_and_delete_mode(container)
        continuation_token = container.client_connection.last_response_headers['etag']
        # Read change feed with 'AllVersionsAndDeletes' mode after create item
        create_items(container, 10)
        read_change_feed_with_all_versions_and_delete_mode_from_continuation(container,continuation_token)
        # Read change feed with 'AllVersionsAndDeletes' mode after create/delete item
        delete_all_items(container)
        read_change_feed_with_all_versions_and_delete_mode_from_continuation(container,continuation_token)

        # cleanup database after sample
        try:
            client.delete_database(db)
        except exceptions.CosmosResourceNotFoundError:
            pass

    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))

    finally:
        print("\nrun_sample done")


if __name__ == '__main__':
    run_sample()
