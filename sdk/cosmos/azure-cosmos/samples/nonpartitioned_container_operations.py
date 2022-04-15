# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See LICENSE.txt in the project root for
# license information.
# -------------------------------------------------------------------------

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
import requests
import json
from urllib.parse import quote as urllib_quote
import azure.cosmos.auth as auth
import azure.cosmos.partition_key as partition_key
import datetime

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
# Sample - demonstrates the basic CRUD operations on a Item resource in a non partitioned container,
# for Azure Cosmos using Python SDK > v4.0.0 with API version > 2018-12-31
# ----------------------------------------------------------------------------------------------------------

HOST = config.settings['host']
MASTER_KEY = config.settings['master_key']
DATABASE_ID = config.settings['database_id']
CONTAINER_ID = config.settings['container_id']


def create_nonpartitioned_container(db):
    # Create a non partitioned container using the rest API and older version
    client = requests.Session()
    base_url_split = HOST.split(":");
    resource_url = base_url_split[0] + ":" + base_url_split[1] + ":" + base_url_split[2].split("/")[
        0] + "//dbs/" + db.id + "/colls/"
    verb = "post"
    resource_id_or_fullname = "dbs/" + db.id
    resource_type = "colls"
    data = '{"id":"mycoll"}'

    headers = {}
    headers["x-ms-version"] = "2018-09-17"
    headers["x-ms-date"] = (datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'))
    headers['authorization'] = get_authorization(db.client_connection, verb,
                                                        resource_id_or_fullname, resource_type, headers)
    response = client.request(verb,
                                resource_url,
                                data=data,
                                headers=headers,
                                timeout=60,
                                stream=False,
                                verify=False)

    data = response.content
    data = data.decode('utf-8')
    data = json.loads(data)
    created_container = db.get_container_client("mycoll")

    # Create a document in the non partitioned container using the rest API and older version
    resource_url = base_url_split[0] + ":" + base_url_split[1] + ":" + base_url_split[2].split("/")[0] \
                    + "//dbs/" + db.id + "/colls/" + created_container.id + "/docs/"
    resource_id_or_fullname = "dbs/" + db.id + "/colls/" + created_container.id
    resource_type = "docs"
    data = json.dumps(get_sales_order('SaledOrder0'))

    headers['authorization'] = get_authorization(db.client_connection, verb,
                                                        resource_id_or_fullname, resource_type, headers)
    response = client.request(verb,
                                resource_url,
                                data=data,
                                headers=headers,
                                timeout=60,
                                stream=False,
                                verify=False)

    data = response.content
    data = data.decode('utf-8')
    data = json.loads(data)
    created_document = data
    return created_container, "SaledOrder0"


def get_authorization(client, verb, resource_id_or_fullname, resource_type, headers):
    authorization = auth.GetAuthorizationHeader(
        cosmos_client_connection=client,
        verb=verb,
        path='',
        resource_id_or_fullname=resource_id_or_fullname,
        is_name_based=True,
        resource_type=resource_type,
        headers=headers)

    # urllib.quote throws when the input parameter is None
    if authorization:
        # -_.!~*'() are valid characters in url, and shouldn't be quoted.
        authorization = urllib_quote(authorization, '-_.!~*\'()')

    return authorization


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

    # Note that Reads require a partition key to be spcified.
    response = container.read_item(doc_id, partition_key=partition_key.NonePartitionKeyValue)

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
            {"name": "@id", "value": doc_id}
        ],
        enable_cross_partition_query=True
    ))

    print('Item queried by Id {0}'.format(items[0].get("id")))


def replace_item(container, doc_id):
    print('\n1.5 Replace an Item\n')

    read_item = container.read_item(doc_id, partition_key=partition_key.NonePartitionKeyValue)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = container.replace_item(item=read_item, body=read_item)

    print('Replaced Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))


def upsert_item(container, doc_id):
    print('\n1.6 Upserting an item\n')

    read_item = container.read_item(doc_id, partition_key=partition_key.NonePartitionKeyValue)
    read_item['subtotal'] = read_item['subtotal'] + 1
    response = container.upsert_item(body=read_item)

    print('Upserted Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))


def delete_item(container, doc_id):
    print('\n1.7 Deleting Item by Id\n')

    response = container.delete_item(item=doc_id, partition_key=partition_key.NonePartitionKeyValue)

    print('Deleted item\'s Id is {0}'.format(doc_id))


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


def get_sales_order_v2(item_id):
    # notice new fields have been added to the sales order
    order2 = {'id': item_id,
                'account_number': 'Account2',
                'purchase_order_number': 'PO15428132599',
                'order_date': datetime.date(2005, 7, 11).strftime('%c'),
                'due_date': datetime.date(2005, 7, 21).strftime('%c'),
                'shipped_date': datetime.date(2005, 7, 15).strftime('%c'),
                'subtotal': 6107.0820,
                'tax_amount': 586.1203,
                'freight': 183.1626,
                'discount_amt': 1982.872,
                'total_due': 4893.3929,
                'items': [
                    {'order_qty': 3,
                    'product_code': 'A-123',  # notice how in item details we no longer reference a ProductId
                    'product_name': 'Product 1',  # instead we have decided to denormalise our schema and include
                    'currency_symbol': '$',  # the Product details relevant to the Order on to the Order directly
                    'currecny_code': 'USD',
                    # this is a typical refactor that happens in the course of an application
                    'unit_price': 17.1,
                    # that would have previously required schema changes and data migrations etc.
                    'line_price': 5.7
                    }
                ],
                'ttl': 60 * 60 * 24 * 30
                }

    return order2


def run_sample():
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    try:
        # setup database for this sample
        try:
            db = client.create_database(id=DATABASE_ID)
        except exceptions.CosmosResourceExistsError:
            db = client.get_database_client(DATABASE_ID)

        # setup container for this sample
        try:
            container, document = create_nonpartitioned_container(db)
            print('Container with id \'{0}\' created'.format(CONTAINER_ID))

        except exceptions.CosmosResourceExistsError:
            print('Container with id \'{0}\' was found'.format(CONTAINER_ID))

        # Read Item created in non partitioned container using older API version
        read_item(container, document)
        create_items(container)
        read_items(container)
        query_items(container, 'SalesOrder1')
        replace_item(container, 'SalesOrder1')
        upsert_item(container, 'SalesOrder1')
        delete_item(container, 'SalesOrder1')

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
