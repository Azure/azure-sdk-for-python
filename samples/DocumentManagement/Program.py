import pydocumentdb.documents as documents
import pydocumentdb.document_client as document_client
import pydocumentdb.errors as errors
import datetime

import config as cfg

# ----------------------------------------------------------------------------------------------------------
# Prerequistes - 
# 
# 1. An Azure DocumentDB account - 
#    https:#azure.microsoft.com/en-us/documentation/articles/documentdb-create-account/
#
# 2. Microsoft Azure DocumentDB PyPi package - 
#    https://pypi.python.org/pypi/pydocumentdb/
# ----------------------------------------------------------------------------------------------------------
# Sample - demonstrates the basic CRUD operations on a Database resource for Azure DocumentDB
#
# 1. Query for Database (QueryDatabases)
#
# 2. Create Database (CreateDatabase)
#
# 3. Get a Database by its Id property (ReadDatabase)
#
# 4. List all Database resources on an account (ReadDatabases)
#
# 5. Delete a Database given its Id property (DeleteDatabase)
# ----------------------------------------------------------------------------------------------------------

HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']
COLLECTION_ID = cfg.settings['collection_id']

database_link = 'dbs/' + DATABASE_ID
collection_link = database_link + '/colls/' + COLLECTION_ID

class IDisposable:
    """ A context manager to automatically close an object with a close method
    in a with statement. """

    def __init__(self, obj):
        self.obj = obj

    def __enter__(self):
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

class DocumentManagement:
    
    @staticmethod
    def CreateDocuments(client):
        print('Creating Documents')

        # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
        # This can be saved as JSON as is without converting into rows/columns.
        sales_order = DocumentManagement.GetSalesOrder("DOC-1234")
        client.CreateDocument(collection_link, sales_order)

        # As your app evolves, let's say your object has a new schema. You can insert SalesOrderV2 objects without any 
        # changes to the database tier.
        sales_order2 = DocumentManagement.GetSalesOrderV2("DOC-3412")
        client.CreateDocument(collection_link, sales_order2)

    @staticmethod
    def GetSalesOrder(document_id):
        order1 = {'id' : document_id,
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

    @staticmethod
    def GetSalesOrderV2(document_id):
        # notice new fields have been added to the sales order
        order2 = {'id' : document_id,
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

def run_sample():
    with IDisposable(document_client.DocumentClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        try:
			# setup database for this sample
            try:
                client.CreateDatabase({"id": DATABASE_ID})

            except errors.DocumentDBError as e:
                if e.status_code == 409:
                    pass
                else:
                    raise errors.HTTPFailure(e.status_code)

            # setup collection for this sample
            try:
                client.CreateCollection(database_link, {"id": COLLECTION_ID})
                print('Collection with id \'{0}\' created'.format(COLLECTION_ID))

            except errors.DocumentDBError as e:
                if e.status_code == 409:
                    print('Collection with id \'{0}\' was found'.format(COLLECTION_ID))
                else:
                    raise errors.HTTPFailure(e.status_code)

            DocumentManagement.CreateDocuments(client)

        except errors.HTTPFailure as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))
        
        finally:
            print("\nrun_sample done")

if __name__ == '__main__':
    try:
        run_sample()

    except Exception as e:
            print("Top level Error: args:{0}, message:N/A".format(e.args))