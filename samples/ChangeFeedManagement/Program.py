import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
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
# Sample - demonstrates how to consume the Change Feed and iterate on the results.
# ----------------------------------------------------------------------------------------------------------

HOST = cfg.settings['host']
MASTER_KEY = cfg.settings['master_key']
DATABASE_ID = cfg.settings['database_id']
COLLECTION_ID = cfg.settings['collection_id']

database_link = 'dbs/' + DATABASE_ID
collection_link = database_link + '/colls/' + COLLECTION_ID

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
    def CreateDocuments(client):
        print('Creating Documents')

        for i in range(1, 1000):
            c = str(i)
            document_definition = {'id': 'document'+ c,
                                'address': {'street': '1 Microsoft Way'+c,
                                            'city': 'Redmond'+c,
                                            'state': 'WA',
                                            'zip code': 98052
                                            }
                                }

            created_document = client.CreateItem(
                collection_link,
                document_definition)

    @staticmethod
    def ReadFeed(client):
        print('\nReading Change Feed from the beginning\n')

        options = {}
        # For a particular Partition Key Range we can use options['partitionKeyRangeId']
        options["startFromBeginning"] = True
        # Start from beginning will read from the beginning of the history of the collection
        # If no startFromBeginning is specified, the read change feed loop will pickup the documents that happen while the loop / process is active
        response = client.QueryItemsChangeFeed(collection_link, options)
        for doc in response:
            print(doc)

        print('\nFinished reading all the change feed\n')

    @staticmethod
    def ReadFeedForTime(client, time):
        print('\nReading Change Feed from point in time\n')

        options = {}
        # Define a point in time to start reading the feed from
        options["startTime"] = time
        response = client.QueryItemsChangeFeed(collection_link, options)
        for doc in response:
            print(doc)

        print('\nFinished reading all the changes from point in time\n')

def run_sample():
    with IDisposable(cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )) as client:
        try:
            # setup database for this sample
            try:
                client.CreateDatabase({"id": DATABASE_ID})

            except errors.HTTPFailure as e:
                if e.status_code == 409:
                    pass
                else:
                    raise errors.HTTPFailure(e.status_code)

            # setup collection for this sample

            collection_definition = {   'id': CONTAINER_ID, 
                                    'partitionKey': 
                                    {   
                                        'paths': ['/address/state'],
                                        'kind': documents.PartitionKind.Hash
                                    }
                                }

            try:
                client.CreateContainer(database_link, collection_definition)
                print('Collection with id \'{0}\' created'.format(COLLECTION_ID))

            except errors.HTTPFailure as e:
                if e.status_code == 409:
                    print('Collection with id \'{0}\' was found'.format(COLLECTION_ID))
                else:
                    raise errors.HTTPFailure(e.status_code)

            ChangeFeedManagement.CreateDocuments(client)
            ChangeFeedManagement.ReadFeed(client)
            time = datetime.datetime.now()
            ChangeFeedManagement.CreateDocuments(client)
            ChangeFeedManagement.ReadFeedForTime(client, time)

        except errors.HTTPFailure as e:
            print('\nrun_sample has caught an error. {0}'.format(e.message))
        
        finally:
            print("\nrun_sample done")

if __name__ == '__main__':
    try:
        run_sample()

    except Exception as e:
            print("Top level Error: args:{0}, message:N/A".format(e.args))
