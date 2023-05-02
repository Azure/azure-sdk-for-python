# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import datetime

import config

# ----------------------------------------------------------------------------------------------------------
# Prerequisites -
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


def create_items(container):
    print('Creating Items')
    print('\n1.1 Create Item\n')

    # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
    # This can be saved as JSON as is without converting into rows/columns.
    sales_order = get_sales_order("SalesOrder1")
    container.create_item(body=sales_order)

    # As your app evolves, let's say your object has a new schema. You can insert SalesOrderV2 objects without any
    # changes to the database tier.
    sales_order2 = get_sales_order_v2("SalesOrder2")
    container.create_item(body=sales_order2)


def read_item(container, doc_id):
    print('\n1.2 Reading Item by Id\n')

    # Note that Reads require a partition key to be specified.
    response = container.read_item(item=doc_id, partition_key=doc_id)

    print('Item read by Id {0}'.format(doc_id))
    print('Account Number: {0}'.format(response.get('account_number')))
    print('Subtotal: {0}'.format(response.get('subtotal')))


def read_items(container):
    print('\n1.3 - Reading all items in a container\n')

    # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
    #       Important to handle throttles whenever you are doing operations such as this that might
    #       result in a 429 (throttled request)
    item_list = list(container.read_all_items(max_item_count=10))

    print('Found {0} items'.format(item_list.__len__()))

    for doc in item_list:
        print('Item Id: {0}'.format(doc.get('id')))


def query_items(container, doc_id):
    print('\n1.4 Querying for an  Item by Id\n')

    # enable_cross_partition_query should be set to True as the container is partitioned
    items = list(container.query_items(
        query="SELECT * FROM r WHERE r.id=@id",
        parameters=[
            { "name":"@id", "value": doc_id }
        ],
        enable_cross_partition_query=True
    ))

    print('Item queried by Id {0}'.format(items[0].get("id")))


def replace_item(container, doc_id):
    print('\n1.5 Replace an Item\n')

    read_item = container.read_item(item=doc_id, partition_key=doc_id)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = container.replace_item(item=read_item, body=read_item)

    print('Replaced Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))


def upsert_item(container, doc_id):
    print('\n1.6 Upserting an item\n')

    read_item = container.read_item(item=doc_id, partition_key=doc_id)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = container.upsert_item(body=read_item)

    print('Upserted Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))

def patch_item(container, doc_id):
    print('\n1.7 Patching Item by Id\n')

    operations = [
        {"op": "add", "path": "/favorite_color", "value": "red"},
        {"op": "remove", "path": "/ttl"},
        {"op": "replace", "path": "/tax_amount", "value": 14},
        {"op": "set", "path": "/items/0/discount", "value": 20.0512},
        {"op": "incr", "path": "/total_due", "value": 5},
        {"op": "move", "from": "/freight", "path": "/service_addition"}
    ]

    response = container.patch_item(item=doc_id, partition_key=doc_id, patch_operations=operations)
    print('Patched Item\'s Id is {0}, new path favorite color={1}, removed path ttl={2}, replaced path tax_amount={3},'
          ' set path for item at index 0 of discount={4}, increase in path total_due, new total_due={5}, move from path freight={6}'
          ' to path service_addition={7}'.format(response["id"], response["favorite_color"], response.get("ttl"),
                                                 response["tax_amount"], response["items"][0].get("discount"),
                                                 response["total_due"], response.get("freight"), response["service_addition"]))

def delete_item(container, doc_id):
    print('\n1.8 Deleting Item by Id\n')

    response = container.delete_item(item=doc_id, partition_key=doc_id)

    print('Deleted item\'s Id is {0}'.format(doc_id))


def delete_all_items_by_partition_key(db, partitionkey):
    print('\n1.8 Deleting all Items by Partition Key\n')

    # A container with a partition key that is different from id is needed
    container = db.create_container_if_not_exists(id="Partition Key Delete Container",
                                                  partition_key=PartitionKey(path='/company'))
    sales_order_company_A1 = get_sales_order("SalesOrderCompanyA1")
    sales_order_company_A1["company"] = partitionkey
    container.upsert_item(sales_order_company_A1)

    print("\nUpserted Item is {} with Partition Key: {}".format(sales_order_company_A1["id"], partitionkey))

    sales_order_company_A2 = get_sales_order("SalesOrderCompanyA2")
    sales_order_company_A2["company"] = partitionkey
    container.upsert_item(sales_order_company_A2)

    print("\nUpserted Item is {} with Partition Key: {}".format(sales_order_company_A2["id"], partitionkey))

    sales_order_company_B1 = get_sales_order("SalesOrderCompanyB1")
    sales_order_company_B1["company"] = "companyB"
    container.upsert_item(sales_order_company_B1)

    print("\nUpserted Item is {} with Partition Key: {}".format(sales_order_company_B1["id"], "companyB"))

    item_list = list(container.read_all_items(max_item_count=10))

    print('Found {0} items'.format(item_list.__len__()))

    for doc in item_list:
        print('Item Id: {0}; Partition Key: {1}'.format(doc.get('id'), doc.get("company")))

    print("\nDelete all items for Partition Key: {}\n".format(partitionkey))

    container.delete_all_items_by_partition_key(partitionkey)
    item_list = list(container.read_all_items())

    print('Found {0} items'.format(item_list.__len__()))

    for doc in item_list:
        print('Item Id: {0}; Partition Key: {1}'.format(doc.get('id'), doc.get("company")))

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
                    'currency_code' : 'USD',       # this is a typical refactor that happens in the course of an application
                    'unit_price' : 17.1,           # that would have previously required schema changes and data migrations etc.
                    'line_price' : 5.7
                }
                ],
            'ttl' : 60 * 60 * 24 * 30
            }

    return order2

def run_sample():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )
    try:
        # setup database for this sample
        db = client.create_database_if_not_exists(id=DATABASE_ID)
        # setup container for this sample
        container = db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path='/id', kind='Hash'))

        create_items(container)
        read_item(container, 'SalesOrder1')
        read_items(container)
        query_items(container, 'SalesOrder1')
        replace_item(container, 'SalesOrder1')
        upsert_item(container, 'SalesOrder1')
        patch_item(container, 'SalesOrder1')
        delete_item(container, 'SalesOrder1')
        delete_all_items_by_partition_key(db, "CompanyA")

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

