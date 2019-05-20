import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.partition_key as partition_key
import datetime
import uuid
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
# Sample - demonstrates how to consume the Change Feed and iterate on the results.
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
        return self.obj # bound to target

    def __exit__(self, exception_type, exception_val, trace):
        # extra cleanup in here
        self = None

class ChangeFeedManagement:
    
    @staticmethod
    def CreateItems(container, size):
        print('Creating Items')

        for i in range(1, size):
            c = str(uuid.uuid4())
            item_definition = {'id': 'item' + c,
                                   'address': {'street': '1 Microsoft Way'+c,
                                            'city': 'Redmond'+c,
                                            'state': 'WA',
                                            'zip code': 98052
                                            }
                                  }

            created_item = container.create_item(body=item_definition)

    @staticmethod
    def ReadChangeFeed(container):
        print('\nReading Change Feed from the beginning\n')

        # For a particular Partition Key Range we can use partition_key_range_id]
        # 'is_start_from_beginning = True' will read from the beginning of the history of the container
        # If no is_start_from_beginning is specified, the read change feed loop will pickup the items that happen while the loop / process is active
        response = container.query_items_change_feed(is_start_from_beginning=True)
        for doc in response:
            print(doc)

        print('\nFinished reading all the change feed\n')

def run_sample():
    with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )) as client:
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
                container = db.create_container(
                    id=CONTAINER_ID,
                    partition_key=partition_key.PartitionKey(path='/address/state', kind=documents.PartitionKind.Hash)
                )
                print('Container with id \'{0}\' created'.format(CONTAINER_ID))

            except errors.HTTPFailure as e:
                if e.status_code == 409:
                    print('Container with id \'{0}\' was found'.format(CONTAINER_ID))
                else:
                    raise errors.HTTPFailure(e.status_code)

            ChangeFeedManagement.CreateItems(container, 100)
            ChangeFeedManagement.ReadChangeFeed(container)

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
