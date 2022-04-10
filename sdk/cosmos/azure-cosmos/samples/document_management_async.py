# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.aio.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime

import asyncio
import config

# ----------------------------------------------------------------------------------------------------------
# Prerequistes -
#
# 1. An Azure Cosmos account -
#    https:#azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure Cosmos PyPi package -
#    https://pypi.python.org/pypi/azure-cosmos/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Item resource for Azure Cosmos
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


async def create_items(container):
    print('Creating Items')
    print('\n1.1 Create Item\n')

    # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
    # This can be saved as JSON as is without converting into rows/columns.
    sales_order = get_sales_order("SalesOrder1")
    await container.create_item(body=sales_order)

    # As your app evolves, let's say your object has a new schema. You can insert SalesOrderV2 objects without any
    # changes to the database tier.
    sales_order2 = get_sales_order_v2("SalesOrder2")
    await container.create_item(body=sales_order2)


async def read_item(container, doc_id):
    print('\n1.2 Reading Item by Id\n')

    # Note that Reads require a partition key to be spcified.
    response = await container.read_item(item=doc_id, partition_key=doc_id)

    print('Item read by Id {0}'.format(doc_id))
    print('Account Number: {0}'.format(response.get('account_number')))
    print('Subtotal: {0}'.format(response.get('subtotal')))


async def read_items(container):
    print('\n1.3 - Reading all items in a container\n')

    # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
    #       Important to handle throttles whenever you are doing operations such as this that might
    #       result in a 429 (throttled request)
    read_all_items_response = container.read_all_items(max_item_count=10)

    # The asynchronous client returns an asynchronous iterator object for methods that
    # return several items, so attempting to cast this object into a list directly will
    # throw an error; instead, iterate over the items using an async for loop like shown
    # here and in the query_items() method below. We also do not await read_all() because
    # it doesn't deal with partition key logic the way query_items() does
    item_list = [item async for item in read_all_items_response]

    print('Found {0} items'.format(item_list.__len__()))

    for doc in item_list:
        print('Item Id: {0}'.format(doc.get('id')))

    # Alternitavely, you can directly iterate over the asynchronous iterator without building a separate
    # list if you don't need the ordering or indexing capabilities
    async for item in read_all_items_response:
        print(item.get('id'))


async def query_items(container, doc_id):
    print('\n1.4 Querying for an  Item by Id\n')

    # enable_cross_partition_query should be set to True as the container is partitioned
    # In this case, we do have to await the asynchronous iterator object since logic
    # within the query_items() method makes network calls to verify the partition key
    # deifnition in the container
    query_items_response = container.query_items(
        query="SELECT * FROM r WHERE r.id=@id",
        parameters=[
            { "name":"@id", "value": doc_id }
        ],
        enable_cross_partition_query=True
    )

    items = [item async for item in query_items_response]

    print('Item queried by Id {0}'.format(items[0].get("id")))


async def replace_item(container, doc_id):
    print('\n1.5 Replace an Item\n')

    read_item = await container.read_item(item=doc_id, partition_key=doc_id)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = await container.replace_item(item=read_item, body=read_item)

    print('Replaced Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))


async def upsert_item(container, doc_id):
    print('\n1.6 Upserting an item\n')

    read_item = await container.read_item(item=doc_id, partition_key=doc_id)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = await container.upsert_item(body=read_item)

    print('Upserted Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))


async def delete_item(container, doc_id):
    print('\n1.7 Deleting Item by Id\n')

    await container.delete_item(item=doc_id, partition_key=doc_id)

    print('Deleted item\'s Id is {0}'.format(doc_id))


def get_sales_order(item_id):
    order1 = {'id' : item_id,
            'account_number' : 'Account1',
            'purchase_order_number' : 'PO18009186470',
            'order_date' : datetime.date(2005,1,10).strftime('%c'),
            'subtotal' : 419.4589,
            'tax_amount' : 12.5838,
            'freight' : 472.3108,
            'total_due' : 985.018,
            'items' : [
                {'order_qty' : 1,
                    'product_id' : 100,
                    'unit_price' : 418.4589,
                    'line_price' : 418.4589
                }
                ],
            'ttl' : 60 * 60 * 24 * 30
            }

    return order1


def get_sales_order_v2(item_id):
    # notice new fields have been added to the sales order
    order2 = {'id' : item_id,
            'account_number' : 'Account2',
            'purchase_order_number' : 'PO15428132599',
            'order_date' : datetime.date(2005,7,11).strftime('%c'),
            'due_date' : datetime.date(2005,7,21).strftime('%c'),
            'shipped_date' : datetime.date(2005,7,15).strftime('%c'),
            'subtotal' : 6107.0820,
            'tax_amount' : 586.1203,
            'freight' : 183.1626,
            'discount_amt' : 1982.872,
            'total_due' : 4893.3929,
            'items' : [
                {'order_qty' : 3,
                    'product_code' : 'A-123',      # notice how in item details we no longer reference a ProductId
                    'product_name' : 'Product 1',  # instead we have decided to denormalise our schema and include
                    'currency_symbol' : '$',       # the Product details relevant to the Order on to the Order directly
                    'currecny_code' : 'USD',       # this is a typical refactor that happens in the course of an application
                    'unit_price' : 17.1,           # that would have previously required schema changes and data migrations etc.
                    'line_price' : 5.7
                }
                ],
            'ttl' : 60 * 60 * 24 * 30
            }

    return order2

async def run_sample():
    async with cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY}) as client:
        try:
            # setup database for this sample
            db = await client.create_database_if_not_exists(id=DATABASE_ID)

            # setup container for this sample
            container = await db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path='/id', kind='Hash'))
            print('Container with id \'{0}\' created'.format(CONTAINER_ID))

            await create_items(container)
            await read_item(container, 'SalesOrder1')
            await read_items(container)
            await query_items(container, 'SalesOrder1')
            await replace_item(container, 'SalesOrder1')
            await upsert_item(container, 'SalesOrder1')
            await delete_item(container, 'SalesOrder1')

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

