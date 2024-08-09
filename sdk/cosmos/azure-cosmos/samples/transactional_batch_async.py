# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from azure.cosmos.aio import CosmosClient
import azure.cosmos.exceptions as exceptions
from azure.cosmos.http_constants import StatusCodes
from azure.cosmos.partition_key import PartitionKey
import datetime

import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
#
# 1. An Azure Cosmos account -
#    https://learn.microsoft.com/azure/cosmos-db/nosql/quickstart-portal#create-account
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates Transactional Batch for Azure Cosmos DB Python SDK async
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = "batch_container"


async def execute_item_batch(database, container):
    print('\n1.11 Executing Batch Item operations\n')

    # We create three items to use for the sample. These are not part of the batch operations
    await container.create_item(get_sales_order("read_item"))
    await container.create_item(get_sales_order("delete_item"))
    await container.create_item(get_sales_order("replace_item"))
 
    # We create our batch operations
    create_item_operation = ("create", (get_sales_order("create_item"),))
    upsert_item_operation = ("upsert", (get_sales_order("upsert_item"),))
    read_item_operation = ("read", ("read_item",))
    delete_item_operation = ("delete", ("delete_item",))
    replace_item_operation = ("replace", ("replace_item", {"id": "replace_item", 'account_number': 'Account1',
                                                           "message": "item was replaced"}))
    replace_item_if_match_operation = ("replace",
                                       ("replace_item", {"id": "replace_item", 'account_number': 'Account1',
                                                         "message": "item was replaced"}),
                                       {"if_match_etag": container.client_connection.last_response_headers.get("etag")})
    replace_item_if_none_match_operation = ("replace",
                                            ("replace_item", {"id": "replace_item", 'account_number': 'Account1',
                                                              "message": "item was replaced"}),
                                            {"if_none_match_etag":
                                                 container.client_connection.last_response_headers.get("etag")})

    # Put our operations into a list
    batch_operations = [
        create_item_operation,
        upsert_item_operation,
        read_item_operation,
        delete_item_operation,
        replace_item_operation,
        # This below operation fails with status code 412, causing batch to fail and all operations to roll back
        replace_item_if_match_operation, # -> Comment this line out to see batch operations succeeding.
        replace_item_if_none_match_operation]

    # Run that list of operations
    try:
        # Batch results are returned as a list of item operation results - or raise a CosmosBatchOperationError if
        # one of the operations failed within your batch request.
        batch_results = await container.execute_item_batch(batch_operations=batch_operations, partition_key="Account1")
        print("\nResults for the batch operations: {}\n".format(batch_results))

    # For error handling, use try/ except with CosmosBatchOperationError and use the information in the
    # error returned for your application debugging, making it easy to pinpoint the failing operation
    except exceptions.CosmosBatchOperationError as e:
        error_operation_index = e.error_index
        error_operation_response = e.operation_responses[error_operation_index]
        error_operation = batch_operations[error_operation_index]
        print("\nError operation: {}, error operation response: {}\n".format(error_operation, error_operation_response))
        print("\nAn error occurred in the batch operation. All operations have been rolled back.\n")

    
    # You can also use this logic to read directly from a file into the batch you'd like to create:
    # with open("file_name.txt", "r") as data_file:
    #    container.execute_item_batch([("upsert", (t,)) for t in data_file.readlines()])


def get_sales_order(item_id):
    order1 = {'id': item_id,
              'account_number': 'Account1',
              'purchase_order_number': 'PO18009186470',
              'order_date': datetime.date(2005, 1, 10).strftime('%c'),
              'subtotal': 419.4589,
              'tax_amount': 12.5838,
              'freight': 472.3108,
              'total_due': 985.018,
              'items': [
                  {'order_qty': 1,
                   'product_id': 100,
                   'unit_price': 418.4589,
                   'line_price': 418.4589
                   }
              ],
              'ttl': 60 * 60 * 24 * 30
              }

    return order1


async def run_sample():
    async with CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        try:
            # setup database for this sample
            db = await client.create_database_if_not_exists(id=DATABASE_ID)

            # setup container for this sample
            container = await db.create_container_if_not_exists(id="batch_container",
                                                              partition_key=PartitionKey(path='/account_number'))
            print('Container with id \'{0}\' created'.format(CONTAINER_ID))

            await execute_item_batch(db, container)

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
