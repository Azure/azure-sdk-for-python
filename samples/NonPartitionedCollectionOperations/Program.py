#The MIT License (MIT)
#Copyright (c) 2018 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import requests
import six
import json
import uuid
from six.moves.urllib.parse import quote as urllib_quote
import azure.cosmos.auth as auth
import azure.cosmos.partition_key as partition_key
import datetime

import samples.Shared.config as cfg

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

HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']
CONTAINER_ID = cfg.settings['container_id']


class IDisposable(cosmos_client.CosmosClient):
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj  # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None


class ItemManagement:
    @staticmethod
    def CreateNonPartitionedCollection(db):
        # Create a non partitioned collection using the rest API and older version
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
        headers['authorization'] = ItemManagement.get_authorization(db.client_connection, verb,
                                                         resource_id_or_fullname, resource_type, headers)
        response = client.request(verb,
                                  resource_url,
                                  data=data,
                                  headers=headers,
                                  timeout=60,
                                  stream=False,
                                  verify=False)

        data = response.content
        if not six.PY2:
            # python 3 compatible: convert data from byte to unicode string
            data = data.decode('utf-8')
        data = json.loads(data)
        created_collection = db.get_container(data['id'])

        # Create a document in the non partitioned collection using the rest API and older version
        resource_url = base_url_split[0] + ":" + base_url_split[1] + ":" + base_url_split[2].split("/")[0] \
                       + "//dbs/" + db.id + "/colls/" + created_collection.id + "/docs/"
        resource_id_or_fullname = "dbs/" + db.id + "/colls/" + created_collection.id
        resource_type = "docs"
        data = json.dumps(ItemManagement.GetSalesOrder('SaledOrder0'))

        headers['authorization'] = ItemManagement.get_authorization(db.client_connection, verb,
                                                         resource_id_or_fullname, resource_type, headers)
        response = client.request(verb,
                                  resource_url,
                                  data=data,
                                  headers=headers,
                                  timeout=60,
                                  stream=False,
                                  verify=False)

        data = response.content
        if not six.PY2:
            # python 3 compatible: convert data from byte to unicode string
            data = data.decode('utf-8')
        data = json.loads(data)
        created_document = data
        return created_collection, created_document

    @staticmethod
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

    @staticmethod
    def CreateItems(container):
        print('Creating Items')
        print('\n1.1 Create Item\n')

        # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
        # This can be saved as JSON as is without converting into rows/columns.
        sales_order = ItemManagement.GetSalesOrder("SalesOrder1")
        container.create_item(body=sales_order)

        # As your app evolves, let's say your object has a new schema. You can insert SalesOrderV2 objects without any
        # changes to the database tier.
        sales_order2 = ItemManagement.GetSalesOrderV2("SalesOrder2")
        container.create_item(body=sales_order2)

    @staticmethod
    def ReadItem(container, doc_id):
        print('\n1.2 Reading Item by Id\n')

        # Note that Reads require a partition key to be spcified.
        response = container.get_item(id=doc_id, partition_key=partition_key.NonePartitionKeyValue)

        print('Item read by Id {0}'.format(doc_id))
        print('Account Number: {0}'.format(response.get('account_number')))
        print('Subtotal: {0}'.format(response.get('subtotal')))

    @staticmethod
    def ReadItems(container):
        print('\n1.3 - Reading all items in a container\n')

        # NOTE: Use MaxItemCount on Options to control how many items come back per trip to the server
        #       Important to handle throttles whenever you are doing operations such as this that might
        #       result in a 429 (throttled request)
        item_list = list(container.list_items(max_item_count=10))

        print('Found {0} items'.format(item_list.__len__()))

        for doc in item_list:
            print('Item Id: {0}'.format(doc.get('id')))

    @staticmethod
    def QueryItems(container, doc_id):
        print('\n1.4 Querying for an  Item by Id\n')

        # enable_cross_partition_query should be set to True as the collection is partitioned
        items = list(container.query_items(
            query="SELECT * FROM r WHERE r.id=@id",
            parameters=[
                {"name": "@id", "value": doc_id}
            ],
            enable_cross_partition_query=True
        ))

        print('Item queried by Id {0}'.format(items[0].get("id")))

    @staticmethod
    def ReplaceItem(container, doc_id):
        print('\n1.5 Replace an Item\n')

        read_item = container.get_item(id=doc_id, partition_key=partition_key.NonePartitionKeyValue)
        read_item['subtotal'] = read_item['subtotal'] + 1
        response = container.replace_item(item=read_item, body=read_item)

        print('Replaced Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))

    @staticmethod
    def UpsertItem(container, doc_id):
        print('\n1.6 Upserting an item\n')

        read_item = container.get_item(id=doc_id, partition_key=partition_key.NonePartitionKeyValue)
        read_item['subtotal'] = read_item['subtotal'] + 1
        response = container.upsert_item(body=read_item)

        print('Upserted Item\'s Id is {0}, new subtotal={1}'.format(response['id'], response['subtotal']))

    @staticmethod
    def DeleteItem(container, doc_id):
        print('\n1.7 Deleting Item by Id\n')

        response = container.delete_item(item=doc_id, partition_key=partition_key.NonePartitionKeyValue)

        print('Deleted item\'s Id is {0}'.format(doc_id))

    @staticmethod
    def GetSalesOrder(item_id):
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

    @staticmethod
    def GetSalesOrderV2(item_id):
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
    with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})) as client:
        try:
            # setup database for this sample
            try:
                db = client.create_database(id=DATABASE_ID)

            except errors.HTTPFailure as e:
                if e.status_code == 409:
                    pass
                else:
                    raise errors.HTTPFailure(e.status_code)

            # setup container for this sample
            try:
                container, document = ItemManagement.CreateNonPartitionedCollection(db)
                print('Container with id \'{0}\' created'.format(CONTAINER_ID))

            except errors.HTTPFailure as e:
                if e.status_code == 409:
                    print('Container with id \'{0}\' was found'.format(CONTAINER_ID))
                else:
                    raise errors.HTTPFailure(e.status_code)

            # Read Item created in non partitioned collection using older API version
            ItemManagement.ReadItem(container, document['id'])
            ItemManagement.CreateItems(container)
            ItemManagement.ReadItems(container)
            ItemManagement.QueryItems(container, 'SalesOrder1')
            ItemManagement.ReplaceItem(container, 'SalesOrder1')
            ItemManagement.UpsertItem(container, 'SalesOrder1')
            ItemManagement.DeleteItem(container, 'SalesOrder1')

            # cleanup database after sample
            try:
                client.delete_database(db)

            except errors.CosmosError as e:
                if e.status_code == 404:
                    pass
                else:
                    raise errors.HTTPFailure(e.status_code)

        except errors.HTTPFailure as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))

        finally:
            print("\nrun_sample done")


if __name__ == '__main__':
    try:
        run_sample()

    except Exception as e:
        print("Top level Error: args:{0}, message:N/A".format(e.args))
